"""Example usage of the PDF RAG Pipeline"""
from pipeline import RAGPipeline
import json


def main():
    """Demonstrate the complete RAG pipeline workflow"""
    
    # Initialize the pipeline
    print("=" * 60)
    print("PDF RAG Pipeline - Example Usage")
    print("=" * 60)
    
    pipeline = RAGPipeline()
    
    # Example 1: Process a PDF and build index
    print("\n--- Example 1: Process PDF and Build Index ---")
    pdf_path = "table.pdf"  # Input PDF file
    
    try:
        # Process and index the PDF in one step
        stats = pipeline.process_and_index_pdf(pdf_path, save_index=True)
        
        print(f"\nProcessing Statistics:")
        print(f"  Text chunks: {stats['processing']['text_chunks']}")
        print(f"  Table chunks: {stats['processing']['table_chunks']}")
        print(f"  Image chunks: {stats['processing']['image_chunks']}")
        print(f"  Total chunks: {stats['processing']['total_chunks']}")
        
        print(f"\nIndexing Statistics:")
        print(f"  Total indexed: {stats['indexing']['total_chunks']}")
        print(f"  Content types: {stats['indexing']['content_types']}")
        print(f"  Model: {stats['indexing']['model_name']}")
        
    except FileNotFoundError:
        print(f"\nNote: '{pdf_path}' not found. Please provide a valid PDF path.")
        print("Skipping to Example 2 with mock data...\n")
    
    # Example 2: Query the indexed content
    print("\n--- Example 2: Search Indexed Content ---")
    
    # Sample queries
    queries = [
        "What is the main topic of this document?",
        "Are there any tables with numerical data?",
        "Summarize the key findings"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        results = pipeline.query(query, top_k=3)
        
        if results:
            print(f"Found {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"  Result {i}:")
                print(f"    Score: {result['score']:.4f}")
                print(f"    Source: {result['metadata']['source_doc']}, Page {result['metadata']['page']}")
                print(f"    Type: {result['metadata']['content_type']}")
                print(f"    Content: {result['chunk'][:100]}...")
                print()
        else:
            print("  No results found.\n")
    
    # Example 3: Load existing index
    print("\n--- Example 3: Load Existing Index ---")
    
    try:
        # Create a new pipeline instance
        new_pipeline = RAGPipeline()
        
        # Load previously saved index
        new_pipeline.load_index()
        
        # Query the loaded index
        query = "test query"
        results = new_pipeline.query(query, top_k=1)
        print(f"Successfully loaded index with {len(new_pipeline.indexer.chunks)} chunks")
        
    except FileNotFoundError:
        print("No saved index found. Run Example 1 first to create an index.")
    
    # Example 4: Process multiple PDFs
    print("\n--- Example 4: Process Multiple PDFs ---")
    
    pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]  # Replace with your PDF paths
    
    print("To process multiple PDFs:")
    print("""
    pipeline = RAGPipeline()
    
    # Process first PDF
    pipeline.process_and_index_pdf("doc1.pdf", save_index=False)
    
    # Add more PDFs incrementally
    for pdf_path in ["doc2.pdf", "doc3.pdf"]:
        result = pipeline.process_pdf(pdf_path)
        pipeline.indexer.add_chunks(result["chunks"])
    
    # Save the combined index
    pipeline.save_index()
    """)
    
    # Example 5: Custom configuration
    print("\n--- Example 5: Custom Configuration ---")
    
    print("Create pipeline with custom settings:")
    print("""
    custom_pipeline = RAGPipeline(
        chunk_size=500,           # Smaller chunks
        chunk_overlap=100,        # Less overlap
        embedding_model="all-MiniLM-L6-v2"  # Specific model
    )
    """)
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
