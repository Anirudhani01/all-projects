# chunker.py
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_content(text: str, output_json: str):
    """
    Chunks text using RecursiveCharacterTextSplitter — best for RAG.
    Saves chunks into a JSON file.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    chunks = splitter.split_text(text)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)

    return chunks
