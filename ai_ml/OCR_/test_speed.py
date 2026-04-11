"""Diagnostic script to identify performance bottlenecks"""
import time

def time_step(name, func):
    """Time a function execution"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    start = time.time()
    result = func()
    elapsed = time.time() - start
    print(f"✓ Completed in {elapsed:.2f} seconds")
    return result, elapsed

# Test 1: Text Extraction
def test_text_extraction():
    from extractors.extractor_text import TextExtractor
    extractor = TextExtractor()
    return extractor.extract("table.pdf", "output/text")

# Test 2: Table Extraction
def test_table_extraction():
    from extractors.extractor_tables import TableExtractor
    extractor = TableExtractor()
    return extractor.extract("table.pdf", "output/tables")

# Test 3: Image Extraction
def test_image_extraction():
    from extractors.extractor_images import ImageExtractor
    extractor = ImageExtractor()
    return extractor.extract("table.pdf", "output/images")

# Test 4: Chunking
def test_chunking():
    from extractors.extractor_text import TextExtractor
    from chunker import Chunker
    
    extractor = TextExtractor()
    text_data = extractor.extract("table.pdf")
    
    chunker = Chunker()
    return chunker.chunk_text(text_data, "table.pdf")

# Test 5: Model Loading
def test_model_loading():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")

# Test 6: Embedding Generation
def test_embedding():
    from indexer import Indexer
    indexer = Indexer()
    test_chunks = [{"content": "test text " * 100} for _ in range(10)]
    indexer.index_chunks(test_chunks)
    return indexer

# Run all tests
if __name__ == "__main__":
    print("\n" + "="*60)
    print("PDF RAG Pipeline - Performance Diagnostic")
    print("="*60)
    
    results = {}
    
    # Test each component
    try:
        _, results['text_extraction'] = time_step("Text Extraction", test_text_extraction)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['text_extraction'] = None
    
    try:
        _, results['table_extraction'] = time_step("Table Extraction (Camelot)", test_table_extraction)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['table_extraction'] = None
    
    try:
        _, results['image_extraction'] = time_step("Image Extraction", test_image_extraction)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['image_extraction'] = None
    
    try:
        _, results['chunking'] = time_step("Chunking", test_chunking)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['chunking'] = None
    
    try:
        _, results['model_loading'] = time_step("Model Loading", test_model_loading)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['model_loading'] = None
    
    try:
        _, results['embedding'] = time_step("Embedding Generation (10 chunks)", test_embedding)
    except Exception as e:
        print(f"✗ Failed: {e}")
        results['embedding'] = None
    
    # Summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    for step, elapsed in results.items():
        if elapsed is not None:
            status = "⚠️  SLOW" if elapsed > 5 else "✓ Fast"
            print(f"{step:30s}: {elapsed:6.2f}s  {status}")
        else:
            print(f"{step:30s}: FAILED")
    
    print("\n" + "="*60)
    print("The slowest step is your bottleneck!")
    print("="*60)
