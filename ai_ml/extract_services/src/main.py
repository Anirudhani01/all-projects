"""
FastAPI main application for Document Processing System
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import uvicorn
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from src.processors import (
    PDFPlainTextProcessor,
    PDFMixedContentProcessor, 
    PDFImageContentProcessor,
    PDFHandwrittenProcessor,
    ImageProcessor
)
from src.utils.file_utils import FileUtils

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A comprehensive document processing system for extracting text and structured data from various document types"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processor instances
processors = {
    "pdf_plain": PDFPlainTextProcessor(),
    "pdf_mixed": PDFMixedContentProcessor(),
    "pdf_image": PDFImageContentProcessor(),
    "pdf_handwritten": PDFHandwrittenProcessor(),
    "image": ImageProcessor()
}

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Document Processing System API",
        "version": settings.APP_VERSION,
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process": "/process",
            "process_auto": "/process/auto",
            "results": "/results/{result_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION
    }

@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    processor_type: str = "auto",
    background_tasks: BackgroundTasks = None
):
    """
    Process a document with specified processor type
    
    Args:
        file: Uploaded file
        processor_type: Type of processor to use (auto, pdf_plain, pdf_mixed, pdf_image, pdf_handwritten, image)
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {list(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # Save uploaded file temporarily
        upload_path = settings.UPLOAD_DIR / file.filename
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail="File too large")
            buffer.write(content)
        
        # Determine processor type if auto
        if processor_type == "auto":
            processor_type = _determine_processor_type(upload_path)
        
        # Get processor
        if processor_type not in processors:
            raise HTTPException(status_code=400, detail=f"Invalid processor type: {processor_type}")
        
        processor = processors[processor_type]
        
        # Process file
        logger.info(f"Processing {file.filename} with {processor_type} processor")
        result = processor.process_file(upload_path)
        
        # Clean up uploaded file
        upload_path.unlink(missing_ok=True)
        
        if result["success"]:
            return JSONResponse(content=result, status_code=200)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Processing failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process/auto")
async def process_document_auto(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process a document with automatic processor detection
    """
    return await process_document(file, "auto", background_tasks)

@app.get("/results/{result_id}")
async def get_results(result_id: str):
    """
    Get processing results by result ID (folder name)
    """
    try:
        result_folder = settings.RESULTS_DIR / result_id
        if not result_folder.exists():
            raise HTTPException(status_code=404, detail="Result not found")
        
        # Check for JSON file
        json_file = result_folder / "extracted_data.json"
        if json_file.exists():
            return FileResponse(
                path=json_file,
                media_type="application/json",
                filename="extracted_data.json"
            )
        
        # Check for CSV file
        csv_file = result_folder / "extracted_data.csv"
        if csv_file.exists():
            return FileResponse(
                path=csv_file,
                media_type="text/csv",
                filename="extracted_data.csv"
            )
        
        raise HTTPException(status_code=404, detail="No results found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/results/{result_id}/metadata")
async def get_result_metadata(result_id: str):
    """
    Get processing metadata for a result
    """
    try:
        result_folder = settings.RESULTS_DIR / result_id
        metadata_file = result_folder / "metadata.json"
        
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="Metadata not found")
        
        return FileResponse(
            path=metadata_file,
            media_type="application/json",
            filename="metadata.json"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metadata: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/results")
async def list_results():
    """
    List all available results
    """
    try:
        results = []
        for result_folder in settings.RESULTS_DIR.iterdir():
            if result_folder.is_dir() and result_folder.name.startswith(settings.RESULT_FOLDER_PREFIX):
                metadata_file = result_folder / "metadata.json"
                if metadata_file.exists():
                    try:
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        results.append({
                            "result_id": result_folder.name,
                            "created": result_folder.stat().st_ctime,
                            "metadata": metadata
                        })
                    except:
                        results.append({
                            "result_id": result_folder.name,
                            "created": result_folder.stat().st_ctime,
                            "metadata": {}
                        })
        
        return {"results": sorted(results, key=lambda x: x["created"], reverse=True)}
        
    except Exception as e:
        logger.error(f"Error listing results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.delete("/results/{result_id}")
async def delete_result(result_id: str):
    """Delete a specific result"""
    try:
        result_folder = settings.RESULTS_DIR / result_id
        
        if not result_folder.exists():
            raise HTTPException(status_code=404, detail="Result not found")
        
        if not result_folder.is_dir():
            raise HTTPException(status_code=400, detail="Invalid result ID")
        
        # Remove the entire result folder
        import shutil
        shutil.rmtree(result_folder)
        
        logger.info(f"Result deleted: {result_id}")
        return {"message": "Result deleted successfully", "result_id": result_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting result {result_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete result")

def _determine_processor_type(file_path: Path) -> str:
    """
    Automatically determine the best processor type for a file
    """
    file_extension = file_path.suffix.lower()
    
    if file_extension == ".pdf":
        # Analyze PDF content to determine the best processor
        return _analyze_pdf_content(file_path)
    elif file_extension in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return "image"
    else:
        return "pdf_plain"  # Default fallback

def _analyze_pdf_content(file_path: Path) -> str:
    """
    Analyze PDF content to determine the best processor type
    """
    try:
        import fitz  # PyMuPDF
        
        # Open PDF and analyze first few pages
        doc = fitz.open(file_path)
        
        if len(doc) == 0:
            return "pdf_plain"
        
        # Analyze first 3 pages (or all pages if less than 3)
        pages_to_analyze = min(3, len(doc))
        has_text = False
        has_images = False
        text_length = 0
        
        for page_num in range(pages_to_analyze):
            page = doc[page_num]
            
            # Get text content
            text = page.get_text()
            if text.strip():
                has_text = True
                text_length += len(text.strip())
            
            # Check for images
            image_list = page.get_images()
            if image_list:
                has_images = True
        
        doc.close()
        
        # Decision logic based on content analysis
        if not has_text and has_images:
            # PDF with only images (scanned documents)
            return "pdf_image"
        elif has_text and has_images:
            # PDF with both text and images
            return "pdf_mixed"
        elif has_text and text_length < 100:
            # Very little text - likely handwritten or image-based
            return "pdf_handwritten"
        else:
            # Regular text-based PDF
            return "pdf_plain"
            
    except Exception as e:
        logger.warning(f"Error analyzing PDF content: {e}")
        # Default to plain text processor if analysis fails
        return "pdf_plain"

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
