# Document Processing System

A comprehensive FastAPI-based system for extracting text and structured data from various document types.

## Features

- **5 Document Types Supported**:
  1. PDF with Plain Text
  2. PDF with Image + Text (Mixed)
  3. PDF with Image containing Tables/Text
  4. PDF with Plain Text + Handwritten Text
  5. Image with Text/Tables

- **FastAPI Web Interface**: RESTful API with automatic documentation
- **Organized Results**: Each processed file gets its own timestamped folder
- **Multiple Output Formats**: JSON and CSV export
- **Comprehensive Logging**: Detailed processing logs and metadata

## Project Structure

```
extract_services/
├── src/
│   ├── processors/          # Document processors for each type
│   ├── utils/              # Utility classes
│   └── main.py             # FastAPI application
├── results/                # Processed results storage
├── tests/                  # Test files
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
└── README.md              # This file
```

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 3. System Dependencies

Install system-level dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils

# Windows (using chocolatey)
choco install tesseract poppler

# macOS (using homebrew)
brew install tesseract poppler
```

## Usage

### Start the Server

```bash
# From the project root directory
python src/main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

### API Endpoints

#### Process Document
```bash
POST /process
Content-Type: multipart/form-data

# Parameters:
# - file: Upload file
# - processor_type: auto, pdf_plain, pdf_mixed, pdf_image, pdf_handwritten, image
```

#### Process with Auto Detection
```bash
POST /process/auto
Content-Type: multipart/form-data

# Parameters:
# - file: Upload file
```

#### Get Results
```bash
GET /results/{result_id}
# Returns: JSON or CSV file
```

#### List All Results
```bash
GET /results
# Returns: List of all processed results
```

### Example Usage

#### Using curl

```bash
# Process a PDF file
curl -X POST "http://localhost:8000/process" \
  -F "file=@document.pdf" \
  -F "processor_type=pdf_plain"

# Process with auto detection
curl -X POST "http://localhost:8000/process/auto" \
  -F "file=@document.pdf"

# Get results
curl -X GET "http://localhost:8000/results/result_document_20241201_143022"
```

#### Using Python requests

```python
import requests

# Process a file
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process',
        files={'file': f},
        data={'processor_type': 'pdf_plain'}
    )

result = response.json()
print(f"Processing successful: {result['success']}")
print(f"Result folder: {result['result_folder']}")
```

## Results Structure

Each processed file creates a timestamped folder in the `results/` directory:

```
results/
├── result_document1_20241201_143022/
│   ├── extracted_data.json      # Main extracted data
│   ├── extracted_data.csv       # CSV format
│   ├── processing_log.txt       # Detailed processing log
│   ├── metadata.json           # Processing metadata
│   └── intermediate_files/      # Intermediate processing files
└── result_invoice_20241201_143155/
    ├── extracted_data.json
    ├── extracted_data.csv
    ├── processing_log.txt
    └── metadata.json
```

## Configuration

Edit `config.py` to customize:

- File size limits
- Allowed file extensions
- OCR settings
- Processing timeouts
- Results storage settings

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_processors/test_pdf_plain_text.py
```

### Adding New Processors

1. Create a new processor class in `src/processors/`
2. Inherit from `BaseProcessor`
3. Implement the `process()` method
4. Add to the processors dictionary in `src/main.py`

## Current Status

- ✅ **Phase 1**: Project setup and structure
- ✅ **Phase 2**: Dependencies and configuration
- ✅ **Phase 3**: Base architecture and FastAPI app
- ✅ **Phase 4.1**: PDF Plain Text Processor (implemented)
- 🚧 **Phase 4.2-4.5**: Other processors (placeholder implementations)
- 🚧 **Phase 5**: Post-processing and output formatting
- 🚧 **Phase 6**: Testing and quality assurance

## Next Steps

1. Implement remaining processors (Mixed Content, Image Content, Handwritten, Image)
2. Add OCR integration (Tesseract, PaddleOCR)
3. Implement table detection
4. Add comprehensive testing
5. Optimize performance and error handling

## License

This project is licensed under the MIT License.
