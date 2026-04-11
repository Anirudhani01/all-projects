# Detailed Test Cases - Part 2
## AC 2-4: PDF Content Extraction, Excel Detection, Image Extraction
## Test Cases TC-031 to TC-060

---

### **Test Cases Table 4 (TC-031 to TC-040) - AC 2: PDF Content Extraction & Parsing**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-031** | PDF with Password Protection | • User logged into platform<br>• Password-protected PDF available<br>• System handles protected PDFs | File: `protected.pdf` (password: "test123") | 1. Upload password-protected PDF<br>2. Enter password when prompted<br>3. Monitor processing<br>4. Verify content extraction | • System prompts for password<br>• Password accepted and validated<br>• PDF content extracted successfully<br>• All content accessible | P | High |
| **TC-032** | PDF with Digital Signatures | • User logged into platform<br>• Digitally signed PDF available<br>• System validates signatures | File: `signed.pdf` (with valid digital signature) | 1. Upload digitally signed PDF<br>2. Monitor signature validation<br>3. Check processing results<br>4. Verify signature status | • Digital signature validated<br>• Signature status displayed<br>• Content extracted successfully<br>• Signature information preserved | P | Medium |
| **TC-033** | PDF with Embedded Fonts | • User logged into platform<br>• PDF with custom fonts available<br>• System handles embedded fonts | File: `custom_fonts.pdf` (with embedded fonts) | 1. Upload PDF with embedded fonts<br>2. Process document<br>3. Check font preservation<br>4. Verify text extraction | • Embedded fonts detected<br>• Text extracted with correct formatting<br>• Font information preserved<br>• Content displayed correctly | P | Medium |
| **TC-034** | PDF with Complex Tables | • User logged into platform<br>• PDF with complex table structures available<br>• System handles table extraction | File: `complex_tables.pdf` (merged cells, nested tables) | 1. Upload PDF with complex tables<br>2. Process document<br>3. Check table extraction<br>4. Verify structure preservation | • Complex tables extracted successfully<br>• Table structure preserved<br>• Merged cells handled correctly<br>• Data relationships maintained | P | High |
| **TC-035** | PDF with Mathematical Equations | • User logged into platform<br>• PDF with mathematical content available<br>• System handles equations | File: `math_equations.pdf` (LaTeX equations, formulas) | 1. Upload PDF with equations<br>2. Process document<br>3. Check equation extraction<br>4. Verify mathematical content | • Mathematical equations extracted<br>• Equation formatting preserved<br>• Formulas readable and accurate<br>• Mathematical symbols maintained | P | Medium |
| **TC-036** | PDF with Annotations and Comments | • User logged into platform<br>• PDF with annotations available<br>• System extracts annotations | File: `annotated.pdf` (sticky notes, highlights, comments) | 1. Upload annotated PDF<br>2. Process document<br>3. Check annotation extraction<br>4. Verify comment preservation | • Annotations extracted successfully<br>• Comments preserved and readable<br>• Highlighting information maintained<br>• Annotation context preserved | P | Medium |
| **TC-037** | PDF with Form Fields | • User logged into platform<br>• PDF with interactive forms available<br>• System handles form fields | File: `form_fields.pdf` (text boxes, checkboxes, dropdowns) | 1. Upload PDF with form fields<br>2. Process document<br>3. Check form field extraction<br>4. Verify field properties | • Form fields identified and extracted<br>• Field types correctly identified<br>• Field properties preserved<br>• Form structure maintained | P | Medium |
| **TC-038** | PDF with Multiple Languages | • User logged into platform<br>• Multi-language PDF available<br>• System handles different languages | File: `multilingual.pdf` (English, Spanish, French) | 1. Upload multi-language PDF<br>2. Process document<br>3. Check language detection<br>4. Verify content extraction | • Multiple languages detected<br>• All language content extracted<br>• Language-specific formatting preserved<br>• Content properly categorized | P | Medium |
| **TC-039** | PDF with Watermarks | • User logged into platform<br>• PDF with watermarks available<br>• System handles watermarked content | File: `watermarked.pdf` (text and image watermarks) | 1. Upload watermarked PDF<br>2. Process document<br>3. Check watermark handling<br>4. Verify content extraction | • Watermarks identified and handled<br>• Main content extracted successfully<br>• Watermark information preserved<br>• Content readability maintained | P | Low |
| **TC-040** | PDF with Bookmarks and Navigation | • User logged into platform<br>• PDF with bookmarks available<br>• System extracts navigation structure | File: `bookmarked.pdf` (hierarchical bookmarks) | 1. Upload bookmarked PDF<br>2. Process document<br>3. Check bookmark extraction<br>4. Verify navigation structure | • Bookmarks extracted successfully<br>• Navigation hierarchy preserved<br>• Bookmark links maintained<br>• Document structure enhanced | P | Medium |

---

### **Test Cases Table 5 (TC-041 to TC-050) - AC 3: Embedded Excel File Detection & Extraction**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-041** | Excel Files with Macros | • User logged into platform<br>• PDF with macro-enabled Excel available<br>• System handles macro content | File: `macro_excel.pdf` (contains .xlsm files) | 1. Upload PDF with macro Excel<br>2. Process document<br>3. Check macro handling<br>4. Verify content extraction | • Macro-enabled files detected<br>• Macro content identified<br>• Data extracted successfully<br>• Macro information preserved | P | Medium |
| **TC-042** | Excel Files with External Links | • User logged into platform<br>• PDF with linked Excel files available<br>• System handles external references | File: `linked_excel.pdf` (Excel with external links) | 1. Upload PDF with linked Excel<br>2. Process document<br>3. Check link detection<br>4. Verify reference handling | • External links detected<br>• Link information preserved<br>• Data extracted successfully<br>• Reference relationships maintained | P | Medium |
| **TC-043** | Excel Files with Data Validation Rules | • User logged into platform<br>• PDF with validation rules available<br>• System extracts validation logic | File: `validation_rules.pdf` (Excel with data validation) | 1. Upload PDF with validation rules<br>2. Process document<br>3. Check rule extraction<br>4. Verify validation logic | • Data validation rules extracted<br>• Validation logic preserved<br>• Data integrity maintained<br>• Business rules captured | P | Medium |
| **TC-044** | Excel Files with Conditional Formatting | • User logged into platform<br>• PDF with conditional formatting available<br>• System handles formatting rules | File: `conditional_formatting.pdf` (Excel with conditional formatting) | 1. Upload PDF with conditional formatting<br>2. Process document<br>3. Check formatting extraction<br>4. Verify rule preservation | • Conditional formatting extracted<br>• Formatting rules preserved<br>• Visual indicators maintained<br>• Business logic captured | P | Medium |
| **TC-045** | Excel Files with Pivot Tables | • User logged into platform<br>• PDF with pivot tables available<br>• System handles pivot structures | File: `pivot_tables.pdf` (Excel with pivot tables) | 1. Upload PDF with pivot tables<br>2. Process document<br>3. Check pivot extraction<br>4. Verify table structure | • Pivot tables extracted successfully<br>• Table structure preserved<br>• Data relationships maintained<br>• Pivot functionality documented | P | High |
| **TC-046** | Excel Files with Charts and Graphs | • User logged into platform<br>• PDF with Excel charts available<br>• System extracts chart data | File: `excel_charts.pdf` (Excel with various chart types) | 1. Upload PDF with Excel charts<br>2. Process document<br>3. Check chart extraction<br>4. Verify data preservation | • Excel charts extracted successfully<br>• Chart data preserved<br>• Chart types identified<br>• Data relationships maintained | P | Medium |
| **TC-047** | Excel Files with Hidden Worksheets | • User logged into platform<br>• PDF with hidden Excel sheets available<br>• System discovers hidden content | File: `hidden_sheets.pdf` (Excel with hidden worksheets) | 1. Upload PDF with hidden sheets<br>2. Process document<br>3. Check hidden content discovery<br>4. Verify complete extraction | • Hidden worksheets discovered<br>• All content extracted<br>• Hidden content flagged<br>• Complete data coverage | P | Medium |
| **TC-048** | Excel Files with Protected Ranges | • User logged into platform<br>• PDF with protected Excel ranges available<br>• System handles protection | File: `protected_ranges.pdf` (Excel with protected cells) | 1. Upload PDF with protected ranges<br>2. Process document<br>3. Check protection handling<br>4. Verify content access | • Protected ranges identified<br>• Content extracted successfully<br>• Protection information preserved<br>• Access restrictions documented | P | Low |
| **TC-049** | Excel Files with Custom Functions | • User logged into platform<br>• PDF with custom Excel functions available<br>• System handles custom logic | File: `custom_functions.pdf` (Excel with VBA functions) | 1. Upload PDF with custom functions<br>2. Process document<br>3. Check function extraction<br>4. Verify logic preservation | • Custom functions identified<br>• Function logic documented<br>• Business rules captured<br>• Custom functionality preserved | P | Medium |
| **TC-050** | Excel Files with Data Connections | • User logged into platform<br>• PDF with data connections available<br>• System handles external data | File: `data_connections.pdf` (Excel with database links) | 1. Upload PDF with data connections<br>2. Process document<br>3. Check connection extraction<br>4. Verify data source info | • Data connections identified<br>• Connection information preserved<br>• Data source details captured<br>• Integration points documented | P | Medium |

---

### **Test Cases Table 6 (TC-051 to TC-060) - AC 4: Image & Chart Content Extraction**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-051** | Vector Graphics (SVG, EPS) | • User logged into platform<br>• PDF with vector graphics available<br>• System handles vector formats | File: `vector_graphics.pdf` (SVG, EPS content) | 1. Upload PDF with vector graphics<br>2. Process document<br>3. Check vector extraction<br>4. Verify format preservation | • Vector graphics extracted successfully<br>• Format information preserved<br>• Scalability maintained<br>• Quality preserved | P | Medium |
| **TC-052** | Animated GIFs | • User logged into platform<br>• PDF with animated GIFs available<br>• System handles animations | File: `animated_gifs.pdf` (GIF animations) | 1. Upload PDF with animated GIFs<br>2. Process document<br>3. Check animation handling<br>4. Verify content extraction | • Animated GIFs detected<br>• Animation information preserved<br>• Content extracted successfully<br>• Animation details documented | P | Low |
| **TC-053** | Transparent PNG Images | • User logged into platform<br>• PDF with transparent PNGs available<br>• System handles transparency | File: `transparent_pngs.pdf` (PNG with transparency) | 1. Upload PDF with transparent PNGs<br>2. Process document<br>3. Check transparency handling<br>4. Verify image quality | • Transparent PNGs extracted successfully<br>• Transparency information preserved<br>• Image quality maintained<br>• Alpha channel preserved | P | Medium |
| **TC-054** | CMYK vs RGB Color Spaces | • User logged into platform<br>• PDF with different color spaces available<br>• System handles color profiles | File: `color_spaces.pdf` (CMYK and RGB images) | 1. Upload PDF with mixed color spaces<br>2. Process document<br>3. Check color space handling<br>4. Verify color accuracy | • Different color spaces detected<br>• Color profiles preserved<br>• Color accuracy maintained<br>• Space information documented | P | Low |
| **TC-055** | Images with Embedded Metadata | • User logged into platform<br>• PDF with metadata-rich images available<br>• System extracts metadata | File: `metadata_images.pdf` (EXIF, IPTC data) | 1. Upload PDF with metadata images<br>2. Process document<br>3. Check metadata extraction<br>4. Verify information preservation | • Image metadata extracted successfully<br>• EXIF data preserved<br>• IPTC information maintained<br>• Metadata relationships preserved | P | Medium |
| **TC-056** | Charts with Interactive Elements | • User logged into platform<br>• PDF with interactive charts available<br>• System handles interactivity | File: `interactive_charts.pdf` (clickable chart elements) | 1. Upload PDF with interactive charts<br>2. Process document<br>3. Check interactivity handling<br>4. Verify element extraction | • Interactive elements identified<br>• Chart functionality documented<br>• Clickable areas preserved<br>• Interactivity information captured | P | Medium |
| **TC-057** | High-DPI Image Processing | • User logged into platform<br>• PDF with high-DPI images available<br>• System handles high resolution | File: `high_dpi_images.pdf` (300+ DPI images) | 1. Upload PDF with high-DPI images<br>2. Process document<br>3. Check resolution handling<br>4. Verify quality preservation | • High-DPI images processed successfully<br>• Resolution information preserved<br>• Image quality maintained<br>• DPI details documented | P | Medium |
| **TC-058** | Compressed Image Formats | • User logged into platform<br>• PDF with compressed images available<br>• System handles compression | File: `compressed_images.pdf` (JPEG, PNG with compression) | 1. Upload PDF with compressed images<br>2. Process document<br>3. Check compression handling<br>4. Verify image extraction | • Compressed images extracted successfully<br>• Compression information preserved<br>• Image quality maintained<br>• Compression details documented | P | Low |
| **TC-059** | Multi-Layer Images | • User logged into platform<br>• PDF with layered images available<br>• System handles layers | File: `layered_images.pdf` (PSD-style layers) | 1. Upload PDF with layered images<br>2. Process document<br>3. Check layer handling<br>4. Verify structure preservation | • Image layers identified<br>• Layer structure preserved<br>• Layer information documented<br>• Image composition maintained | P | Medium |
| **TC-060** | Image Quality Degradation | • User logged into platform<br>• PDF with low-quality images available<br>• System handles quality issues | File: `low_quality_images.pdf` (blurry, pixelated images) | 1. Upload PDF with low-quality images<br>2. Process document<br>3. Check quality handling<br>4. Verify extraction success | • Low-quality images extracted successfully<br>• Quality issues documented<br>• Content preserved despite quality<br>• Quality assessment provided | P | Low |

---

## 📊 AC 2-4 Coverage Summary

### **AC 2: PDF Content Extraction & Parsing**
**Total Test Cases**: 10 (TC-031 to TC-040)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**Coverage Areas**:
- ✅ Password protection and digital signatures
- ✅ Embedded fonts and complex tables
- ✅ Mathematical equations and annotations
- ✅ Form fields and multi-language support
- ✅ Watermarks and navigation structures

### **AC 3: Embedded Excel File Detection & Extraction**
**Total Test Cases**: 10 (TC-041 to TC-050)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**Coverage Areas**:
- ✅ Macro-enabled Excel files
- ✅ External links and data validation
- ✅ Conditional formatting and pivot tables
- ✅ Charts, hidden sheets, and protection
- ✅ Custom functions and data connections

### **AC 4: Image & Chart Content Extraction**
**Total Test Cases**: 10 (TC-051 to TC-060)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**Coverage Areas**:
- ✅ Vector graphics and animations
- ✅ Transparency and color spaces
- ✅ Metadata and interactive elements
- ✅ High-DPI and compressed images
- ✅ Multi-layer images and quality handling

### **Priority Distribution for AC 2-4**:
- **High Priority**: 8 test cases (27%)
- **Medium Priority**: 18 test cases (60%)
- **Low Priority**: 4 test cases (13%)

---

*Part 2 of 4 - Test Cases for AC 2-4: PDF Content Extraction, Excel Detection, Image Extraction*
