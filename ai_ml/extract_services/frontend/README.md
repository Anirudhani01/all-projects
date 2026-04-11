# Document Processing System - Frontend

A simple, responsive web interface for the Document Processing System built with HTML, CSS, and JavaScript.

## Features

- **Drag & Drop Upload**: Easy file upload with drag and drop support
- **Multiple Processors**: Support for all 5 document processors
- **Real-time Processing**: Live processing status and results
- **Results Management**: View and download processing results
- **Recent Results**: Access to previously processed documents
- **Responsive Design**: Works on desktop and mobile devices
- **Toast Notifications**: User-friendly feedback messages

## File Structure

```
frontend/
├── index.html          # Main HTML file
├── styles.css          # CSS styles
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## Usage

1. Make sure the backend server is running on `http://localhost:8001`
2. Open `index.html` in your web browser
3. Upload a document by dragging and dropping or clicking to browse
4. Select the appropriate processor (or use Auto Detect)
5. Click "Process Document" to start processing
6. View results and download them in JSON or CSV format

## Supported File Types

- **PDF files**: `.pdf`
- **Image files**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`

## Processors

1. **Auto Detect** - Automatically chooses the best processor
2. **PDF Plain Text** - For PDFs with plain text content
3. **PDF Mixed Content** - For PDFs with text and images
4. **PDF Image Content** - For PDFs with image content containing tables
5. **PDF Handwritten** - For PDFs with plain text + handwritten content
6. **Image Files** - For image files with text/tables

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Dependencies

- Font Awesome 6.0.0 (for icons)
- No other external dependencies required

## API Integration

The frontend communicates with the backend API at `http://localhost:8001`:

- `POST /process` - Process a document
- `GET /results/{result_id}` - Download results
- `GET /results` - List all results
- `GET /health` - Check server health

## Customization

You can easily customize the appearance by modifying `styles.css`:

- Colors and themes
- Layout and spacing
- Typography
- Responsive breakpoints

## Troubleshooting

- **Server not responding**: Make sure the backend is running on port 8001
- **File upload fails**: Check file size (max 50MB) and file type
- **Processing fails**: Check the browser console for error details
