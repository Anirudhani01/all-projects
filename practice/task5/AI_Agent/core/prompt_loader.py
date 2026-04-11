"""
Prompt template loader for the AI-Powered Unit Test Case Generation System.
Loads prompt templates from the templates folder and provides them to the test generator.
"""

import os
from pathlib import Path
from typing import Dict, Optional


class PromptTemplateLoader:
    """Loads and manages prompt templates for AI-powered test generation."""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load all prompt templates from the templates directory."""
        templates = {}
        
        if not self.templates_dir.exists():
            print(f"Warning: Templates directory '{self.templates_dir}' not found.")
            return templates
        
        # Load all .txt files in the templates directory
        for template_file in self.templates_dir.glob("*.txt"):
            template_name = template_file.stem  # Remove .txt extension
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                templates[template_name] = template_content
                print(f"✅ Loaded template: {template_name}")
            except Exception as e:
                print(f"❌ Error loading template {template_name}: {e}")
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[str]:
        """Get a specific prompt template by name."""
        return self.templates.get(template_name)
    
    def list_available_templates(self) -> list[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def get_default_template(self) -> str:
        """Get the default template (prompt_1.txt)."""
        return self.templates.get("prompt_1", "")
    
    def format_template(self, template_name: str, user_story: str, knowledge_base: str) -> str:
        """Format a template with user story and knowledge base content."""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Replace placeholders in the template
        formatted_template = template.replace("{user_story}", user_story)
        formatted_template = formatted_template.replace("{knowledge_base.json}", knowledge_base)
        
        return formatted_template
    
    def reload_templates(self):
        """Reload templates from disk."""
        self.templates = self._load_templates()
        return len(self.templates)
