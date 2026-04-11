# Document Processing System Architecture

```text
                        ┌─────────────────────────────┐
                        │       Input Layer           │
                        │  (PDF / Image Upload)       │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │   Preprocessing Layer        │
                        │ (pdf2image, OpenCV cleanup) │
                        └──────────────┬──────────────┘
                                       │
        ┌──────────────────────────────┼───────────────────────────────┐
        ▼                              ▼                               ▼
┌────────────────────┐       ┌────────────────────┐          ┌────────────────────┐
│ 1. PDF with Plain   │       │ 2. PDF with Image+ │          │ 3. PDF with Image  │
│ Text                │       │ Text (Mixed)       │          │ (Text/Tables)      │
│ - PyMuPDF           │       │ - PyMuPDF + OCR    │          │ - pdf2image        │
│ - pdfplumber        │       │ - Tesseract/Paddle │          │ - OCR (Tesseract/  │
│                     │       │                    │          │   PaddleOCR)       │
│ Output: JSON/CSV    │       │ Output: JSON/CSV   │          │ - Table detection  │
└────────────────────┘       └────────────────────┘          │   (Camelot/        │
                                                              │    PaddleOCR Tbl) │
                                                              │ Output: JSON/CSV  │
                                                              └────────────────────┘

        ┌──────────────────────────────┼───────────────────────────────┐
        ▼                              ▼
┌────────────────────┐       ┌────────────────────┐
│ 4. PDF with Plain   │       │ 5. Image with Text │
│ + Handwritten Text  │       │ or Tables          │
│ - PyMuPDF (text)    │       │ - OpenCV preprocess│
│ - Handwriting OCR   │       │ - OCR (Tesseract/  │
│   (PaddleOCR/Cloud) │       │   PaddleOCR)       │
│ - LayoutParser      │       │ - Table detection  │
│ Output: JSON/CSV    │       │ Output: JSON/CSV   │
└────────────────────┘       └────────────────────┘

                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │   Post-Processing Layer     │
                        │ (NER, Spellcheck, Cleanup)  │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │   Unified Structuring Layer │
                        │   (Standard JSON Schema)    │
                        └──────────────┬──────────────┘
                                       │
                                       ▼
                        ┌─────────────────────────────┐
                        │       Output Layer          │
                        │ JSON / CSV / Database Store │
                        └─────────────────────────────┘
