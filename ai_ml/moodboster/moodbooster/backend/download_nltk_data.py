#!/usr/bin/env python3
"""
Script to download required NLTK data for the MoodBooster backend.
"""

import nltk

def download_nltk_data():
    """Download required NLTK data packages."""
    print("Downloading NLTK data packages...")
    
    try:
        # Download stopwords
        print("Downloading stopwords...")
        nltk.download('stopwords', quiet=True)
        
        # Download punkt tokenizer
        print("Downloading punkt tokenizer...")
        nltk.download('punkt', quiet=True)
        
        # Download averaged perceptron tagger
        print("Downloading averaged perceptron tagger...")
        nltk.download('averaged_perceptron_tagger', quiet=True)
        
        print("NLTK data download completed successfully!")
        
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    download_nltk_data()
