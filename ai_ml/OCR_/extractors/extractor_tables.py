"""Table extraction from PDF documents using Camelot"""
import logging
import os
from typing import List, Dict, Any
import camelot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TableExtractor:
    """Extract tables from PDF documents and save as CSV"""
    
    def extract(self, pdf_path: str, output_dir: str) -> List[Dict[str, Any]]:
        """
        Extract tables from PDF and save each as a CSV file
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted CSV files
            
        Returns:
            List of dictionaries with table metadata
            Format: [{"page": int, "table_id": int, "csv_path": str}, ...]
        """
        extracted_data = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get PDF filename without extension for naming CSV files
        pdf_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
        try:
            # Extract tables from all pages using Camelot
            logger.info(f"Extracting tables from PDF: {pdf_path}")
            tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            
            logger.info(f"Found {len(tables)} tables in the PDF")
            
            # Process each table
            for idx, table in enumerate(tables):
                try:
                    page_num = table.page
                    table_id = idx + 1
                    
                    # Generate CSV filename
                    csv_filename = f"{pdf_filename}_page{page_num}_table{table_id}.csv"
                    csv_path = os.path.join(output_dir, csv_filename)
                    
                    # Save table as CSV
                    table.to_csv(csv_path)
                    
                    extracted_data.append({
                        "page": page_num,
                        "table_id": table_id,
                        "csv_path": csv_path
                    })
                    
                    logger.info(f"Saved table {table_id} from page {page_num} to {csv_path}")
                    
                except Exception as e:
                    logger.error(f"Error saving table {idx + 1}: {str(e)}")
                    continue
            
            logger.info(f"Table extraction complete: {len(extracted_data)} tables extracted")
            
        except Exception as e:
            logger.error(f"Error extracting tables from PDF {pdf_path}: {str(e)}")
            # Return empty list if extraction fails completely
            return []
        
        return extracted_data
