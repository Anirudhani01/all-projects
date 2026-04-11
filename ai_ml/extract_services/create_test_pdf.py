"""
Create a simple test PDF for testing the document processing system
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

def create_test_pdf():
    """Create a simple test PDF with text content"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Page 1
    c.drawString(100, height - 100, "Test Document for Document Processing System")
    c.drawString(100, height - 150, "This is a sample PDF document with plain text content.")
    c.drawString(100, height - 200, "The system should be able to extract this text successfully.")
    
    c.drawString(100, height - 300, "Sample Data:")
    c.drawString(100, height - 350, "Name: John Doe")
    c.drawString(100, height - 400, "Email: john.doe@example.com")
    c.drawString(100, height - 450, "Phone: +1-555-123-4567")
    
    c.showPage()
    
    # Page 2
    c.drawString(100, height - 100, "Page 2 - Additional Content")
    c.drawString(100, height - 150, "This is the second page of our test document.")
    c.drawString(100, height - 200, "It contains more text to test multi-page processing.")
    
    c.drawString(100, height - 300, "Technical Details:")
    c.drawString(100, height - 350, "Processor: PDFPlainTextProcessor")
    c.drawString(100, height - 400, "Library: PyMuPDF and pdfplumber")
    c.drawString(100, height - 450, "Output: JSON and CSV formats")
    
    c.save()
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    # Install reportlab if not available
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab...")
        import subprocess
        subprocess.check_call(["pip", "install", "reportlab"])
        import reportlab
    
    # Create test PDF
    pdf_buffer = create_test_pdf()
    
    # Save to file
    with open("test_document.pdf", "wb") as f:
        f.write(pdf_buffer.getvalue())
    
    print("Test PDF created: test_document.pdf")
