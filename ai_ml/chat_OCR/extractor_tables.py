# extractor_tables.py
import camelot
import pandas as pd
import os

def extract_tables_from_pdf(pdf_path: str, output_dir: str):
    """
    Extract tables from PDF using Camelot.
    Saves each detected table into separate CSV files.
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")

        if not tables:
            print("No tables found.")
            return []

        csv_files = []

        for idx, table in enumerate(tables):
            output_path = os.path.join(output_dir, f"table_{idx+1}.csv")
            table.df.to_csv(output_path, index=False)
            csv_files.append(output_path)

        return csv_files

    except Exception as e:
        raise RuntimeError(f"Error extracting tables: {e}")
