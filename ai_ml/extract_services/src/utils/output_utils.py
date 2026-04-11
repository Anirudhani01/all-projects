"""
Output formatting and validation utilities
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class OutputUtils:
    """Utility class for output formatting and validation"""
    
    @staticmethod
    def validate_extracted_data(data: Dict[str, Any]) -> bool:
        """Validate extracted data structure"""
        try:
            # Check required top-level keys
            required_keys = ["pages", "metadata"]
            if not all(key in data for key in required_keys):
                logger.error(f"Missing required keys: {required_keys}")
                return False
            
            # Validate pages structure
            pages = data.get("pages", [])
            if not isinstance(pages, list):
                logger.error("Pages must be a list")
                return False
            
            for i, page in enumerate(pages):
                if not isinstance(page, dict):
                    logger.error(f"Page {i} must be a dictionary")
                    return False
                
                # Check required page keys
                page_required = ["text", "page_number"]
                if not all(key in page for key in page_required):
                    logger.error(f"Page {i} missing required keys: {page_required}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating extracted data: {e}")
            return False
    
    @staticmethod
    def format_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Format and clean extracted data"""
        try:
            formatted_data = {
                "metadata": {
                    "total_pages": len(data.get("pages", [])),
                    "extraction_timestamp": data.get("metadata", {}).get("timestamp", ""),
                    "processor_used": data.get("metadata", {}).get("processor", ""),
                    "file_info": data.get("metadata", {}).get("file_info", {})
                },
                "pages": []
            }
            
            # Format each page
            for page in data.get("pages", []):
                formatted_page = {
                    "page_number": page.get("page_number", 0),
                    "text": page.get("text", "").strip(),
                    "width": page.get("width", 0),
                    "height": page.get("height", 0),
                    "tables": page.get("tables", []),
                    "images": page.get("images", []),
                    "confidence": page.get("confidence", 0.0)
                }
                formatted_data["pages"].append(formatted_page)
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error formatting extracted data: {e}")
            return data
    
    @staticmethod
    def create_csv_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert extracted data to CSV-friendly format"""
        try:
            csv_rows = []
            
            for page in data.get("pages", []):
                base_row = {
                    "page_number": page.get("page_number", 0),
                    "text": page.get("text", ""),
                    "page_width": page.get("width", 0),
                    "page_height": page.get("height", 0),
                    "confidence": page.get("confidence", 0.0)
                }
                
                # Add table data
                tables = page.get("tables", [])
                if tables:
                    for table_idx, table in enumerate(tables):
                        table_row = base_row.copy()
                        table_row.update({
                            "table_number": table_idx + 1,
                            "table_data": json.dumps(table.get("data", [])),
                            "table_confidence": table.get("confidence", 0.0),
                            "table_rows": len(table.get("data", [])),
                            "table_cols": len(table.get("data", [0])) if table.get("data") else 0
                        })
                        csv_rows.append(table_row)
                else:
                    # No tables, just add the base row
                    csv_rows.append(base_row)
            
            return csv_rows
            
        except Exception as e:
            logger.error(f"Error creating CSV data: {e}")
            return []
    
    @staticmethod
    def save_json(data: Dict[str, Any], output_path: Path) -> bool:
        """Save data as JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving JSON to {output_path}: {e}")
            return False
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], output_path: Path) -> bool:
        """Save data as CSV file"""
        try:
            if not data:
                # Create empty CSV with headers
                df = pd.DataFrame(columns=["page_number", "text", "page_width", "page_height", "confidence"])
            else:
                df = pd.DataFrame(data)
            
            df.to_csv(output_path, index=False, encoding='utf-8')
            return True
        except Exception as e:
            logger.error(f"Error saving CSV to {output_path}: {e}")
            return False
    
    @staticmethod
    def create_summary_stats(data: Dict[str, Any]) -> Dict[str, Any]:
        """Create summary statistics for extracted data"""
        try:
            pages = data.get("pages", [])
            
            stats = {
                "total_pages": len(pages),
                "total_text_length": sum(len(page.get("text", "")) for page in pages),
                "total_tables": sum(len(page.get("tables", [])) for page in pages),
                "total_images": sum(len(page.get("images", [])) for page in pages),
                "average_confidence": 0.0,
                "pages_with_tables": sum(1 for page in pages if page.get("tables")),
                "pages_with_images": sum(1 for page in pages if page.get("images")),
                "empty_pages": sum(1 for page in pages if not page.get("text", "").strip())
            }
            
            # Calculate average confidence
            confidences = [page.get("confidence", 0.0) for page in pages if page.get("confidence", 0.0) > 0]
            if confidences:
                stats["average_confidence"] = sum(confidences) / len(confidences)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error creating summary stats: {e}")
            return {}
