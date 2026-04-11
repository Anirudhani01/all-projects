import json
from openai import OpenAI
from components.image_parser.utils import (
    safe_json_parse,
    TEMPLATE_LIBRARY,
    COMPOSITE_TEMPLATE_FILE,
    validate_structure,
    smart_chat_completion,
)

# -- Loaders --
def get_template_by_type(layout_type: str):
    return TEMPLATE_LIBRARY.get(layout_type, {}).get("template", {})

def load_composite_template():
    with open(COMPOSITE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# -- Instruction Block --
INSTRUCTIONS_BLOCK = """ STRICT VISUAL METADATA EXTRACTION — TEMPLATE-BOUND

You are a pixel-accurate UI structure extractor. You must extract data **ONLY from what is visible** in the screenshot and **MUST fill everything defined in the templates** provided.

---

### HOW TO THINK

1. You are not summarizing — you are visually parsing.
2. Each part of the screen corresponds to a section in a template.
3. Templates define the full structure. The image provides the content.
4. You must extract **ALL visible UI elements** and **map them to the correct templates**.

---

### TEMPLATE USAGE RULES

1. Start with the Composite Template: identifies page-level blocks like sidebar, topbar, main area, modals.
2. Then apply component templates: use them to extract forms, tables, cards, KPIs, etc.
3. If multiple layout blocks are detected (e.g., a form + a table), identify and extract each one **based on its visual boundaries**.
4. Maintain **clear nesting**: each section must be stored under the correct key (`sections`, `components`, etc.), preserving the **visual hierarchy**.
5. Every layout block must map to **some** template — do not skip or flatten multiple structures.

---

### ELEMENT TYPES TO EXTRACT

- Sidebar / Menu: All menu groups, submenus, selected states, icons, badges.
- Topbar: Logos, search bars, buttons, avatars.
- Forms: Labels, input types, values, hints, validation, placeholders.
- Cards / Panels: Titles, subtitles, badges, buttons, value blocks.
- Charts: Chart type, axes, title, labels, legends, tooltips.
- Tables / Lists: Column headers, rows, filters, search.
- KPIs: Metric name, value, trend, icon, highlight.
- Modals / Banners: Titles, messages, CTA buttons, alert types.

---

### REQUIRED METADATA PER ELEMENT

Every visible field or component must include:
- `id`, `type`, `label`, `value`, `position`
- `icon_present`, `icon_type` (if any)
- `is_visible`, `is_mandatory`, `is_highlighted`, `is_selected`, `is_disabled`
- `font_size`, `font_color`, `background_color`, `shape`, `tooltip`
- `width`, `height`, `border`, `hover_color`, `alignment`, `padding`, `margin`

---

### RELATIVE PIXEL COORDINATES — MANDATORY
Each element MUST include:
- `x`: pixel offset from the LEFT edge of the image
- `y`: pixel offset from the TOP edge of the image
- `width`: width in pixels
- `height`: height in pixels

❗ These values must be in **absolute pixels**, measured **relative to the top-left corner** of the image.

❌ Do not use:
- Normalized values (`0.0–1.0`)
- Percentages
- cm, pt, inch, or other units

✅ Example:
{
  "x": 120,
  "y": 80,
  "width": 200,
  "height": 48
}

---

### PAGE-LEVEL REQUIREMENTS

Under the top-level `"page"` object, fill:
- `name`, `description`, `layout`, `theme`, `scrollable`, `has_sidebar`, `has_topbar`, `has_modal`, `has_alert_banner`, `has_tabs`
- `section_order`: ordered list of all layout sections, top-to-bottom
- `extra_metadata`:
  - `detected_components`
  - `component_count_summary`
  - `modal_titles`, `banner_messages`
  - Notes for edge cases or unique layout combinations
- `image_metadata`:
  - `original_width`, `original_height` must be added so extracted values can be re-mapped to pixel space

---

MANDATES:
- Do not invent values.
- Do not omit any visible element.
- Do not flatten nested layouts.
- Output valid JSON only. No extra comments or formatting.

You are a visual QA assistant. Follow the structure precisely.
"""

# -- Prompt Builder --
def build_composite_messages(image_b64: str, layout_info_list: list, component_templates: dict, composite_template: dict):
    layout_hint = {
        "detected_layouts": [
            {"type": t, "id": id_, "position": pos}
            for t, id_, pos in layout_info_list
        ]
    }

    return [
        {"role": "system", "content": "You are a visual layout extraction QA assistant. Use the composite structure with absolute pixel positions."},
        {"role": "user", "content": INSTRUCTIONS_BLOCK},
        {"role": "user", "content": "Composite Template:"},
        {"role": "user", "content": json.dumps(composite_template, indent=2)},
        {"role": "user", "content": "Component Templates:"},
        {"role": "user", "content": json.dumps(component_templates, indent=2)},
        {"role": "user", "content": "Detected Layout Regions:"},
        {"role": "user", "content": json.dumps(layout_hint, indent=2)},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Now extract the full structured layout using composite structure."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }
    ]

# -- Final Unified Function --
async def extract_ui_structure(image_b64: str, layout_info_list: list) -> dict:
    """
    Unified function: Always use composite structure.
    If only one layout is detected, still wrap it under a section → components
    """

    unique_layouts = list({layout_type for layout_type, _, _ in layout_info_list})

    # Load everything once
    composite_template = load_composite_template()["template"]
    component_templates = {
        layout: get_template_by_type(layout)
        for layout in unique_layouts
        if layout in TEMPLATE_LIBRARY
    }

    messages = build_composite_messages(
        image_b64=image_b64,
        layout_info_list=layout_info_list,
        component_templates=component_templates,
        composite_template=composite_template
    )

    result, usage = await smart_chat_completion(messages)
    validated = await validate_structure(image_b64, result)
    return {"data": validated, "usage": usage}
