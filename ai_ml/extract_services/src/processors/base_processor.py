"""
Base processor class for all document processors
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import json

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config import settings

logger = logging.getLogger(__name__)

class BaseProcessor(ABC):
    """Abstract base class for all document processors"""
    
    def __init__(self):
        self.processor_name = self.__class__.__name__
        self.start_time = None
        self.end_time = None
        self.processing_log = []
        self.metadata = {}
        
    def log_step(self, step: str, status: str = "INFO", details: str = ""):
        """Log a processing step"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "status": status,
            "details": details
        }
        self.processing_log.append(log_entry)
        logger.info(f"[{self.processor_name}] {step}: {status} - {details}")
    
    def create_result_folder(self, input_filename: str) -> Path:
        """Create a unique result folder for the processed file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize filename
        safe_filename = "".join(c for c in input_filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')
        
        folder_name = f"{settings.RESULT_FOLDER_PREFIX}_{safe_filename}_{timestamp}"
        result_folder = settings.RESULTS_DIR / folder_name
        result_folder.mkdir(exist_ok=True)
        
        # Create intermediate files subfolder
        (result_folder / "intermediate_files").mkdir(exist_ok=True)
        
        self.log_step("Result folder created", "SUCCESS", f"Folder: {folder_name}")
        return result_folder
    
    def save_processing_log(self, result_folder: Path):
        """Save processing log to file"""
        log_file = result_folder / "processing_log.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            for entry in self.processing_log:
                f.write(f"[{entry['timestamp']}] {entry['step']}: {entry['status']} - {entry['details']}\n")
        
        self.log_step("Processing log saved", "SUCCESS", f"File: {log_file}")
    
    def save_metadata(self, result_folder: Path, extracted_data: Dict[str, Any]):
        """Save processing metadata"""
        self.metadata.update({
            "processor_name": self.processor_name,
            "processing_time": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
            "input_file": str(self.input_file) if hasattr(self, 'input_file') else None,
            "output_files": {
                "json": "extracted_data.json",
                "csv": "extracted_data.csv"
            },
            "extraction_stats": {
                "total_pages": len(extracted_data.get("pages", [])),
                "total_text_length": sum(len(page.get("text", "")) for page in extracted_data.get("pages", [])),
                "tables_found": sum(len(page.get("tables", [])) for page in extracted_data.get("pages", [])),
                "images_processed": sum(len(page.get("images", [])) for page in extracted_data.get("pages", []))
            },
            "processing_steps": len(self.processing_log)
        })
        
        metadata_file = result_folder / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        self.log_step("Metadata saved", "SUCCESS", f"File: {metadata_file}")
    
    @abstractmethod
    def process(self, input_file: Path) -> Dict[str, Any]:
        """
        Process the input file and return extracted data
        
        Args:
            input_file: Path to the input file
            
        Returns:
            Dictionary containing extracted data
        """
        pass
    
    def validate_input(self, input_file: Path) -> bool:
        """Validate input file"""
        if not input_file.exists():
            self.log_step("Input validation", "ERROR", f"File not found: {input_file}")
            return False
        
        if input_file.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
            self.log_step("Input validation", "ERROR", f"Unsupported file type: {input_file.suffix}")
            return False
        
        if input_file.stat().st_size > settings.MAX_FILE_SIZE:
            self.log_step("Input validation", "ERROR", f"File too large: {input_file.stat().st_size} bytes")
            return False
        
        self.log_step("Input validation", "SUCCESS", f"File validated: {input_file.name}")
        return True
    
    def process_file(self, input_file: Path) -> Dict[str, Any]:
        """Main processing method with error handling and logging"""
        self.start_time = datetime.now()
        self.input_file = input_file
        
        try:
            # Validate input
            if not self.validate_input(input_file):
                raise ValueError("Input validation failed")
            
            # Create result folder
            result_folder = self.create_result_folder(input_file.name)
            
            # Process the file
            self.log_step("Processing started", "INFO", f"Using {self.processor_name}")
            extracted_data = self.process(input_file)
            
            # Save results
            self.save_results(result_folder, extracted_data)
            
            self.end_time = datetime.now()
            self.log_step("Processing completed", "SUCCESS", 
                         f"Total time: {(self.end_time - self.start_time).total_seconds():.2f}s")
            
            return {
                "success": True,
                "result_folder": str(result_folder),
                "extracted_data": extracted_data,
                "processing_time": (self.end_time - self.start_time).total_seconds(),
                "metadata": self.metadata
            }
            
        except Exception as e:
            self.end_time = datetime.now()
            self.log_step("Processing failed", "ERROR", str(e))
            logger.error(f"Processing failed: {str(e)}", exc_info=True)
            
            return {
                "success": False,
                "error": str(e),
                "processing_time": (self.end_time - self.start_time).total_seconds() if self.start_time else 0
            }
    
    def save_results(self, result_folder: Path, extracted_data: Dict[str, Any]):
        """Save extracted data in JSON and CSV formats"""
        # Save JSON
        json_file = result_folder / "extracted_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        # Save CSV (if applicable)
        csv_file = result_folder / "extracted_data.csv"
        self.save_as_csv(csv_file, extracted_data)
        
        # Save processing log
        self.save_processing_log(result_folder)
        
        # Save metadata
        self.save_metadata(result_folder, extracted_data)
        
        self.log_step("Results saved", "SUCCESS", f"JSON: {json_file}, CSV: {csv_file}")
    
    def save_as_csv(self, csv_file: Path, extracted_data: Dict[str, Any]):
        """Convert extracted data to CSV format"""
        import pandas as pd
        
        try:
            # Flatten the data for CSV
            rows = []
            for page_idx, page in enumerate(extracted_data.get("pages", [])):
                base_row = {
                    "page_number": page_idx + 1,
                    "text": page.get("text", ""),
                    "page_width": page.get("width", 0),
                    "page_height": page.get("height", 0)
                }
                
                # Add table data
                for table_idx, table in enumerate(page.get("tables", [])):
                    table_row = base_row.copy()
                    table_row.update({
                        "table_number": table_idx + 1,
                        "table_data": str(table.get("data", [])),
                        "table_confidence": table.get("confidence", 0)
                    })
                    rows.append(table_row)
                
                # If no tables, add the base row
                if not page.get("tables"):
                    rows.append(base_row)
            
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(csv_file, index=False, encoding='utf-8')
            else:
                # Create empty CSV with headers
                df = pd.DataFrame(columns=["page_number", "text", "page_width", "page_height"])
                df.to_csv(csv_file, index=False, encoding='utf-8')
                
        except Exception as e:
            self.log_step("CSV conversion failed", "WARNING", str(e))
            # Create empty CSV file
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("page_number,text,page_width,page_height\n")
