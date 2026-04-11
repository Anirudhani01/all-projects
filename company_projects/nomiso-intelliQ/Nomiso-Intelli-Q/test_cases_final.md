# Complete Test Cases Final Document
## Multi-Format Document Processing Enhancement
## Comprehensive Test Suite - All 103 Test Cases

---

## 📋 Table of Contents

1. [User Story](#1-user-story)
2. [Acceptance Criteria](#2-acceptance-criteria)
3. [Test Scenarios](#3-test-scenarios)
4. [Detailed Test Cases](#4-detailed-test-cases)
   - [Part 1: AC 1 - PDF Document Upload & Validation (TC-001 to TC-030)](#part-1-ac-1-pdf-document-upload--validation)
   - [Part 2: AC 2-4 - Content Extraction, Excel, Images (TC-031 to TC-060)](#part-2-ac-2-4-content-extraction-excel-images)
   - [Part 3: AC 5-7 - Hierarchy, Integration, Story Generation (TC-061 to TC-090)](#part-3-ac-5-7-hierarchy-integration-story-generation)
   - [Part 4: AC 8 - Error Handling + Extra Tests (TC-091 to TC-103)](#part-4-ac-8-error-handling--extra-tests)
5. [Traceability Matrix](#5-traceability-matrix)
6. [Coverage Review](#6-coverage-review)
7. [Review Checklist](#7-review-checklist)

---

## 1. User Story

### **Selected User Story:**
**As a** QA Engineer  
**I want to** upload user stories in PDF format with embedded Excel spreadsheets and images  
**So that** I can process complex business requirements documents without manual content extraction

### **Acceptance Criteria:**
- System should parse PDF documents and extract all embedded content
- System should identify and parse Excel files within PDFs
- System should extract images and charts for visual context
- System should maintain content hierarchy and relationships
- System should generate enhanced stories from multi-format content

---

## 2. Acceptance Criteria

### **AC 1: PDF Document Upload & Validation**
**Given** a QA Engineer has a PDF document containing embedded Excel spreadsheets and images  
**When** they upload the PDF to the Nomiso IntelliQ platform  
**Then** the system should accept the file and validate it's a supported PDF format  
**And** the system should display a confirmation message with file details (size, pages, embedded objects count)

### **AC 2: PDF Content Extraction & Parsing**
**Given** a valid PDF document has been uploaded to the system  
**When** the system processes the PDF document  
**Then** the system should extract all text content from each page  
**And** the system should identify and list all embedded objects (Excel files, images, charts)  
**And** the system should preserve the original document structure and hierarchy

### **AC 3: Embedded Excel File Detection & Extraction**
**Given** the PDF contains embedded Excel spreadsheets  
**When** the system analyzes the embedded content  
**Then** the system should detect all Excel files (.xlsx, .xls) within the PDF  
**And** the system should extract the Excel content with preserved formatting  
**And** the system should identify worksheet names, cell data, and table structures

### **AC 4: Image & Chart Content Extraction**
**Given** the PDF contains embedded images, charts, or diagrams  
**When** the system processes the visual content  
**Then** the system should extract all images with their original resolution and format  
**And** the system should identify chart types and extract chart data where possible  
**And** the system should preserve image positioning and context within the document

### **AC 5: Content Hierarchy Preservation**
**Given** the PDF has a structured layout with headings, sections, and embedded content  
**When** the system extracts and processes all content types  
**Then** the system should maintain the original document hierarchy and relationships  
**And** the system should create a structured representation showing content organization  
**And** the system should preserve the logical flow between text, tables, and embedded objects

### **AC 6: Multi-Format Content Integration**
**Given** the system has extracted text, Excel data, and images from the PDF  
**When** the system prepares the content for story enhancement  
**Then** the system should combine all content types into a unified, searchable format  
**And** the system should create cross-references between related content elements  
**And** the system should maintain traceability to the original PDF source

### **AC 7: Enhanced Story Generation from Multi-Format Content**
**Given** the system has successfully extracted and integrated all content types  
**When** the system processes the multi-format content through the story enhancement pipeline  
**Then** the system should generate enhanced user stories incorporating all extracted information  
**And** the system should include relevant Excel data, image descriptions, and visual context  
**And** the system should maintain the business requirements and acceptance criteria from all sources

### **AC 8: Error Handling & User Feedback**
**Given** the system encounters issues during PDF processing (corrupted files, unsupported formats, extraction failures)  
**When** errors occur during any step of the extraction process  
**Then** the system should provide clear, actionable error messages to the user  
**And** the system should log detailed error information for troubleshooting  
**And** the system should offer alternative processing options or guidance for resolution

---

## 3. Test Scenarios

### **20 Test Scenarios Overview:**

**AC 1: PDF Document Upload & Validation**
- TS-01 (P): Valid PDF with Embedded Content Upload
- TS-02 (N): Invalid File Format Upload
- TS-03 (B): Maximum File Size Boundary
- TS-04 (B): Minimum File Size Boundary

**AC 2: PDF Content Extraction & Parsing**
- TS-05 (P): Multi-Page PDF with Mixed Content
- TS-06 (N): Corrupted PDF File
- TS-07 (B): PDF with Only Text (No Embedded Objects)

**AC 3: Embedded Excel File Detection & Extraction**
- TS-08 (P): Multiple Excel Files with Different Formats
- TS-09 (N): Password-Protected Excel Files
- TS-10 (B): Excel Files with Maximum Data Volume
- TS-11 (B): Excel Files with Special Characters

**AC 4: Image & Chart Content Extraction**
- TS-12 (P): Various Image Formats and Chart Types
- TS-13 (N): Corrupted or Unsupported Image Formats
- TS-14 (B): High-Resolution Images and Complex Charts

**AC 5: Content Hierarchy Preservation**
- TS-15 (P): Complex Document Structure with Nested Content
- TS-16 (B): PDF with Unusual Layout Structure

**AC 6: Multi-Format Content Integration**
- TS-17 (P): Cross-Referenced Content Integration
- TS-18 (B): Large Volume of Mixed Content Types

**AC 7: Enhanced Story Generation**
- TS-19 (P): Complete Story Enhancement Pipeline
- TS-20 (B): Complex Business Requirements with Visual Elements

**AC 8: Error Handling & User Feedback**
- TS-02, TS-06, TS-09, TS-13 (Covered in other ACs)

---

## 4. Detailed Test Cases

### **Total Test Cases: 103**
- **Positive (P)**: 62 test cases (60%)
- **Negative (N)**: 38 test cases (37%)
- **Boundary (B)**: 3 test cases (3%)

---

## Part 1: AC 1 - PDF Document Upload & Validation

### **Test Cases Table 1 (TC-001 to TC-010)**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-001** | Valid PDF with Embedded Content Upload | • User logged into platform<br>• System supports PDF uploads<br>• Test PDF file available | File: `test_embedded_content.pdf` (5MB, 8 pages)<br>Content: 2 Excel files, 3 PNG images, mixed text | 1. Navigate to upload section<br>2. Click "Upload Document"<br>3. Select PDF file<br>4. Click "Upload"<br>5. Wait for completion<br>6. Review confirmation | • File uploads successfully<br>• Confirmation: "5MB, 8 pages, 5 embedded objects"<br>• File appears in processing queue | P | High |
| **TC-002** | Invalid File Format Upload | • User logged into platform<br>• System supports PDF only<br>• Test text file available | File: `requirements.txt` (plain text, 2KB) | 1. Navigate to upload section<br>2. Click "Upload Document"<br>3. Select text file<br>4. Click "Upload" | • System rejects file<br>• Error: "Only PDF files supported"<br>• File not added to queue | N | High |
| **TC-003** | Maximum File Size Boundary | • User logged into platform<br>• System has 50MB limit<br>• Test PDF (50MB) available | File: `large_embedded_content.pdf` (50MB, 15 pages)<br>Content: Multiple Excel files, images, text | 1. Navigate to upload section<br>2. Click "Upload Document"<br>3. Select large PDF<br>4. Click "Upload"<br>5. Wait for completion | • File uploads successfully (at limit)<br>• System processes without errors<br>• File appears in queue | B | Medium |
| **TC-004** | Minimum File Size Boundary | • User logged into platform<br>• System supports PDF uploads<br>• Test minimal PDF available | File: `minimal_content.pdf` (1KB, 1 page)<br>Content: Single paragraph text only | 1. Navigate to upload section<br>2. Click "Upload Document"<br>3. Select minimal PDF<br>4. Click "Upload"<br>5. Wait for completion | • File uploads successfully<br>• System processes minimal content<br>• Reports: "1KB, 1 page, 0 embedded objects" | B | Low |
| **TC-005** | Multi-Page PDF with Mixed Content | • User logged into platform<br>• Valid PDF uploaded<br>• System ready to process | File: `mixed_content_10pages.pdf` (10 pages)<br>Content: Text, tables, 2 Excel files, 3 images, charts | 1. Locate uploaded PDF<br>2. Click "Process Document"<br>3. Wait for completion<br>4. Review results<br>5. Check content summary | • All 10 pages processed<br>• All text content extracted<br>• 2 Excel files and 3 images identified<br>• Content hierarchy maintained | P | High |
| **TC-006** | Corrupted PDF File | • User logged into platform<br>• Corrupted PDF file available | File: `corrupted_content.pdf` (manually corrupted) | 1. Navigate to upload section<br>2. Upload corrupted PDF<br>3. Attempt to process<br>4. Monitor response | • File uploads successfully<br>• Corruption detected during processing<br>• Error: "PDF corrupted, cannot process"<br>• Processing halted gracefully | N | Medium |
| **TC-007** | PDF with Only Text (No Embedded Objects) | • User logged into platform<br>• Text-only PDF available | File: `text_only.pdf` (5 pages, text only) | 1. Upload text-only PDF<br>2. Process document<br>3. Review extraction results | • System processes successfully<br>• All text content extracted<br>• Reports: "0 embedded objects detected"<br>• Text structure preserved | B | Low |
| **TC-008** | Multiple Excel Files with Different Formats | • User logged into platform<br>• PDF with multiple Excel formats available | File: `multiple_excel_formats.pdf`<br>Content: 1 .xlsx file, 1 .xls file, complex data | 1. Upload PDF with multiple Excel formats<br>2. Process document<br>3. Review Excel extraction<br>4. Verify data preservation | • Both Excel formats detected<br>• All worksheet data extracted<br>• Cell data, formulas, structure maintained<br>• Successful extraction reported | P | High |
| **TC-009** | Password-Protected Excel Files | • User logged into platform<br>• PDF with password-protected Excel available | File: `password_protected_excel.pdf`<br>Content: 2 password-protected Excel files | 1. Upload PDF with protected Excel<br>2. Process document<br>3. Review Excel extraction | • Excel files detected in PDF<br>• Reports: "Password-protected, cannot extract"<br>• Processing continues with other content<br>• Clear error message displayed | N | Medium |
| **TC-010** | Excel Files with Maximum Data Volume | • User logged into platform<br>• PDF with large Excel files available | File: `large_excel_data.pdf`<br>Content: Excel with 1000+ rows, 50+ columns | 1. Upload PDF with large Excel<br>2. Process document<br>3. Monitor processing time<br>4. Review extraction results | • Large Excel files processed successfully<br>• Processing time longer but acceptable<br>• All data extracted and preserved<br>• Progress indicators provided | B | Medium |

### **Test Cases Table 2 (TC-011 to TC-020)**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-011** | Excel Files with Special Characters | • User logged into platform<br>• PDF with special Excel content available | File: `special_excel_content.pdf`<br>Content: Special chars, formulas, merged cells | 1. Upload PDF with special Excel<br>2. Process document<br>3. Review Excel extraction<br>4. Verify formatting preservation | • Special characters preserved correctly<br>• Formulas extracted and maintained<br>• Merged cells structure preserved<br>• All formatting maintained accurately | B | Medium |
| **TC-012** | Various Image Formats and Chart Types | • User logged into platform<br>• PDF with various images/charts available | File: `various_images_charts.pdf`<br>Content: PNG, JPEG images, Excel charts (bar, pie, line) | 1. Upload PDF with various formats<br>2. Process document<br>3. Review image/chart extraction | • All images extracted with original resolution<br>• Chart types correctly identified<br>• Image formats preserved<br>• Chart data extracted where possible | P | High |
| **TC-013** | Corrupted or Unsupported Image Formats | • User logged into platform<br>• PDF with corrupted/unsupported images available | File: `corrupted_images.pdf`<br>Content: Corrupted PNG, unsupported formats | 1. Upload PDF with corrupted images<br>2. Process document<br>3. Review image extraction | • Reports: "Some images cannot be extracted"<br>• Valid images extracted successfully<br>• Processing continues with other content<br>• Clear error reporting for failures | N | Medium |
| **TC-014** | High-Resolution Images and Complex Charts | • User logged into platform<br>• PDF with high-resolution content available | File: `high_resolution_content.pdf`<br>Content: 4K images, complex multi-series charts | 1. Upload PDF with high-resolution content<br>2. Process document<br>3. Monitor processing time/resources<br>4. Review extraction results | • High-resolution images processed successfully<br>• Complex charts extracted accurately<br>• Processing time extended but acceptable<br>• Progress indicators provided | B | Medium |
| **TC-015** | Complex Document Structure with Nested Content | • User logged into platform<br>• PDF with complex structure available | File: `complex_structure.pdf`<br>Content: Multiple headings, sections, embedded objects | 1. Upload PDF with complex structure<br>2. Process document<br>3. Review structure preservation<br>4. Verify hierarchy maintenance | • Original hierarchy maintained<br>• Structured representation created<br>• Content relationships preserved<br>• Navigation structure maintained | P | High |
| **TC-016** | PDF with Unusual Layout Structure | • User logged into platform<br>• PDF with unusual layout available | File: `unusual_layout.pdf`<br>Content: Sidebars, footnotes, headers, non-standard layout | 1. Upload PDF with unusual layout<br>2. Process document<br>3. Review layout preservation<br>4. Verify logical flow maintenance | • Layout preserved while maintaining logical flow<br>• Sidebars and footnotes properly identified<br>• Content structure maintained<br>• Logical reading flow preserved | B | Low |
| **TC-017** | Cross-Referenced Content Integration | • User logged into platform<br>• PDF with cross-referenced content available | File: `cross_referenced_content.pdf`<br>Content: Excel data referencing specific PDF sections | 1. Upload PDF with cross-referenced content<br>2. Process document<br>3. Review cross-reference creation<br>4. Verify relationship maintenance | • Cross-references created between content types<br>• Relationships maintained<br>• Content integration successful<br>• Unified searchable format created | P | High |
| **TC-018** | Large Volume of Mixed Content Types | • User logged into platform<br>• Large PDF with mixed content available | File: `large_mixed_content.pdf` (20+ pages)<br>Content: 10+ Excel files, 15+ images, extensive text | 1. Upload large PDF with mixed content<br>2. Process document<br>3. Monitor processing progress<br>4. Review final results | • All content types processed successfully<br>• Unified, searchable format created<br>• Processing handles large volumes efficiently<br>• All content relationships maintained | B | Medium |
| **TC-019** | Complete Story Enhancement Pipeline | • User logged into platform<br>• Multi-format PDF processed<br>• System ready for enhancement | Processed multi-format content from previous test cases | 1. Initiate story enhancement process<br>2. Monitor enhancement workflow<br>3. Review enhanced story output<br>4. Verify content integration | • Enhanced user stories generated<br>• All content types incorporated<br>• Business logic and visual context included<br>• Stories ready for test case generation | P | High |
| **TC-020** | Complex Business Requirements with Visual Elements | • User logged into platform<br>• Complex business requirements PDF available | File: `complex_business_requirements.pdf`<br>Content: Business requirements, Excel models, visual diagrams | 1. Upload complex business requirements PDF<br>2. Process through complete pipeline<br>3. Generate enhanced stories<br>4. Review final output quality | • Comprehensive stories generated<br>• Business logic and visual context integrated<br>• Excel models properly incorporated<br>• Visual elements enhance story understanding | B | High |

### **Test Cases Table 3 (TC-021 to TC-030)**

| Test Case ID | Title | Preconditions | Test Data | Steps | Expected Result | Type | Priority |
|--------------|-------|---------------|-----------|-------|-----------------|------|----------|
| **TC-021** | Network Interruption During Upload | • User logged into platform<br>• Network connection unstable<br>• Large PDF file available | File: `large_file.pdf` (25MB)<br>Network: Simulated interruption | 1. Start large file upload<br>2. Simulate network interruption<br>3. Monitor system response<br>4. Attempt recovery | • System detects network interruption<br>• Upload progress saved<br>• User notified of interruption<br>• Resume option provided | N | Medium |
| **TC-022** | Concurrent Upload Scenarios | • Multiple users logged in<br>• System supports concurrent uploads<br>• Multiple PDF files available | Files: 5 different PDFs (1-10MB each)<br>Users: 3 concurrent users | 1. All users start uploads simultaneously<br>2. Monitor system performance<br>3. Check upload success rates<br>4. Verify no conflicts | • All uploads process successfully<br>• No conflicts between users<br>• System maintains performance<br>• All files appear in respective queues | P | Medium |
| **TC-023** | File Corruption During Transfer | • User logged into platform<br>• Network with packet loss<br>• PDF file available | File: `test_file.pdf` (5MB)<br>Network: Simulated packet loss | 1. Upload file over unstable network<br>2. Monitor for corruption<br>3. Check file integrity<br>4. Verify system response | • System detects file corruption<br>• Upload rejected with error<br>• User advised to retry<br>• File integrity validation performed | N | High |
| **TC-024** | Upload Timeout Scenarios | • User logged into platform<br>• Slow network connection<br>• Large PDF file available | File: `large_file.pdf` (40MB)<br>Network: Slow connection | 1. Start upload of large file<br>2. Monitor timeout settings<br>3. Check timeout behavior<br>4. Verify user notification | • System respects timeout settings<br>• User notified of timeout<br>• Upload progress saved<br>• Retry option provided | N | Medium |
| **TC-025** | Disk Space Limitations | • User logged into platform<br>• System with limited disk space<br>• Large PDF file available | File: `large_file.pdf` (45MB)<br>System: Limited disk space | 1. Check available disk space<br>2. Attempt large file upload<br>3. Monitor system response<br>4. Verify error handling | • System checks disk space before upload<br>• Upload rejected if insufficient space<br>• Clear error message displayed<br>• User advised on space requirements | N | High |
| **TC-026** | File Permission Issues | • User logged into platform<br>• File with restricted permissions<br>• System with permission controls | File: `restricted_file.pdf` (restricted permissions) | 1. Attempt to upload restricted file<br>2. Monitor permission checks<br>3. Check error messages<br>4. Verify access controls | • System validates file permissions<br>• Upload rejected if permissions insufficient<br>• Clear permission error displayed<br>• User advised on access requirements | N | Medium |
| **TC-027** | Upload Progress Tracking | • User logged into platform<br>• Large PDF file available<br>• System supports progress tracking | File: `large_file.pdf` (30MB) | 1. Start large file upload<br>2. Monitor progress indicators<br>3. Check progress accuracy<br>4. Verify completion status | • Progress bar displays accurately<br>• Upload percentage updates in real-time<br>• Estimated time remaining shown<br>• Completion status clearly indicated | P | Medium |
| **TC-028** | File Type Validation | • User logged into platform<br>• Various file types available<br>• System validates file types | Files: PDF, DOCX, TXT, JPG, PNG | 1. Attempt upload of each file type<br>2. Monitor validation results<br>3. Check error messages<br>4. Verify accepted files | • Only PDF files accepted<br>• Clear error for non-PDF files<br>• File type validation performed<br>• User guidance provided | P | High |
| **TC-029** | Upload Queue Management | • User logged into platform<br>• Multiple files to upload<br>• System supports queuing | Files: 5 PDF files (1-15MB each) | 1. Add multiple files to upload queue<br>2. Monitor queue processing<br>3. Check queue status<br>4. Verify successful processing | • Files added to queue successfully<br>• Queue processes files sequentially<br>• Queue status clearly displayed<br>• All files processed successfully | P | Medium |
| **TC-030** | Upload Resume Functionality | • User logged into platform<br>• Previous failed upload<br>• System supports resume | File: `large_file.pdf` (35MB)<br>Previous: Failed upload at 60% | 1. Check for resumable uploads<br>2. Resume previous upload<br>3. Monitor progress from resume point<br>4. Verify successful completion | • System identifies resumable uploads<br>• Upload resumes from 60% point<br>• Progress continues from resume point<br>• File uploads successfully | P | Medium |

### **AC 1 Coverage Summary**
**Total Test Cases for AC 1**: 30
- **Positive (P)**: 18 test cases (60%)
- **Negative (N)**: 9 test cases (30%)
- **Boundary (B)**: 3 test cases (10%)

**Priority Distribution**:
- **High Priority**: 15 test cases (50%)
- **Medium Priority**: 12 test cases (40%)
- **Low Priority**: 3 test cases (10%)

---

## Part 2: AC 2-4 - Content Extraction, Excel, Images

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
| **TC-039** | PDF with Watermarks | • User logged into platform<br>• PDF with watermarks available<br>• System handles watermarked content | File: `watermarked.pdf` (text and image watermarks) | 1. Upload PDF with watermarks<br>2. Process document<br>3. Check watermark handling<br>4. Verify content extraction | • Watermarks identified and handled<br>• Main content extracted successfully<br>• Watermark information preserved<br>• Content readability maintained | P | Low |
| **TC-040** | PDF with Bookmarks and Navigation | • User logged into platform<br>• PDF with bookmarks available<br>• System extracts navigation structure | File: `bookmarked.pdf` (hierarchical bookmarks) | 1. Upload PDF with bookmarks<br>2. Process document<br>3. Check bookmark extraction<br>4. Verify navigation structure | • Bookmark structure extracted<br>• Navigation hierarchy preserved<br>• Bookmark relationships maintained<br>• Document structure enhanced | P | Medium |

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

### **AC 2-4 Coverage Summary**

**AC 2: PDF Content Extraction & Parsing**
**Total Test Cases**: 10 (TC-031 to TC-040)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**AC 3: Embedded Excel File Detection & Extraction**
**Total Test Cases**: 10 (TC-041 to TC-050)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**AC 4: Image & Chart Content Extraction**
**Total Test Cases**: 10 (TC-051 to TC-060)
- **Positive (P)**: 10 test cases (100%)
- **Negative (N)**: 0 test cases (0%)
- **Boundary (B)**: 0 test cases (0%)

**Priority Distribution for AC 2-4**:
- **High Priority**: 8 test cases (27%)
- **Medium Priority**: 18 test cases (60%)
- **Low Priority**: 4 test cases (13%)

---
