# main.py
from extractor_text import extract_text_from_pdf
from extractor_tables import extract_tables_from_pdf
from extractor_images import extract_images_from_pdf
from chunker import chunk_content
from indexer import Indexer
from retrieval import Retriever

import os

PDF_PATH = "table.pdf"

OUTPUT_DIR = "outputs"
TEXT_OUTPUT = os.path.join(OUTPUT_DIR, "extracted_text.txt")
TABLES_DIR = os.path.join(OUTPUT_DIR, "tables")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
CHUNKS_JSON = os.path.join(OUTPUT_DIR, "chunks.json")
INDEX_FILE = os.path.join(OUTPUT_DIR, "faiss.index")

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_pipeline(pdf_path):
    print("\n📄 Extracting text...")
    text = extract_text_from_pdf(pdf_path)
    with open(TEXT_OUTPUT, "w", encoding="utf-8") as f:
        f.write(text)

    print("\n📊 Extracting tables...")
    extract_tables_from_pdf(pdf_path, TABLES_DIR)

    print("\n🖼 Extracting images...")
    extract_images_from_pdf(pdf_path, IMAGES_DIR)

    print("\n✂️ Chunking text...")
    chunk_content(text, CHUNKS_JSON)

    print("\n🧠 Creating FAISS Index...")
    Indexer().create_index(CHUNKS_JSON, INDEX_FILE)

    print("\nPipeline completed successfully!")

def ask_question(question):
    print(f"\n🔍 Searching: {question}\n")
    retriever = Retriever(INDEX_FILE, CHUNKS_JSON)
    results = retriever.query(question)

    for idx, res in enumerate(results, start=1):
        print(f"Result {idx}:")
        print("Score:", res["score"])
        print(res["content"])
        print("-" * 50)

if __name__ == "__main__":
    run_pipeline(PDF_PATH)

    # Example Query
    ask_question("What is the summary of this document?")
