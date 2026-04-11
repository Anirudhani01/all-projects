"""
Enhanced PDF RAG Pipeline with Page-by-Page Processing and Complete Content Storage

ARCHITECTURE OVERVIEW:
This implementation provides a comprehensive RAG (Retrieval Augmented Generation) system that:
1. Processes PDFs page-by-page for better content organization
2. Uses advanced content cleaning and header/footer removal
3. Stores all content in PostgreSQL with vector embeddings
4. Provides adaptive query strategies based on query analysis
5. Maintains complete content preservation while optimizing storage

KEY FEATURES:
- Page-level content storage and retrieval
- Advanced text cleaning and extraction
- Adaptive RAG strategies (single-shot, multi-hop, synthesis)
- Query complexity analysis
- Complete content preservation
- Enhanced database schema with optimized storage
"""

import os
import asyncio
import argparse
import sys
from typing import List, Dict, Any, Tuple, Optional
import json
import hashlib
from datetime import datetime
from pathlib import Path
import psycopg2
from pgvector.psycopg2 import register_vector
import tiktoken
from llama_parse import LlamaParse
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re
import logging
import uuid
from dotenv import load_dotenv
from enum import Enum
from dataclasses import dataclass

# =============================================================================
# SYSTEM SETUP AND CONFIGURATION
# =============================================================================

# Fix Windows console encoding issues for proper UTF-8 support
if sys.platform == "win32":
    os.system('chcp 65001 > nul')  # Set console to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables from .env file
load_dotenv()

# Create necessary directories for logs and documents
os.makedirs('logs', exist_ok=True)
os.makedirs('documents', exist_ok=True)

# =============================================================================
# ENHANCED LOGGING SYSTEM
# =============================================================================

# Enhanced logging setup with both file and terminal output
# File logs contain everything, terminal shows only essential messages
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = f'logs/rag_pipeline_{timestamp}.log'

class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to terminal log output
    Different log levels get different colors for better readability
    """
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green  
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Apply color formatting only to terminal output"""
        if hasattr(record, '_terminal_only'):
            color = self.COLORS.get(record.levelname, '')
            record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)

class TerminalFilter(logging.Filter):
    """
    Filter that controls which log messages appear in terminal
    Only shows essential messages to reduce noise while keeping detailed file logs
    """
    
    # Keywords that indicate essential messages to show in terminal
    ESSENTIAL_KEYWORDS = [
        '[INIT]', '[SUCCESS]', '[PROCESSING]', '[PARSING]', '[INFO] File size',
        '[RESULT]', '[ERROR]', '[REGISTER]', '[AI] Starting',
        '[ANALYZED] Processed', '[EMBEDDINGS]', '[SUCCESS] Stored',
        '[SUCCESS] Document processing completed', '[SETUP]', '[STATS]',
        '[PAGE SUMMARY]', '[PAGE CONTENT]', '[QUERY]', '[ANSWER]', '[SOURCES]'
    ]
    
    # Warning messages to suppress in terminal (but keep in log file)
    SUPPRESS_WARNINGS = [
        'Chunking failed for page',
        'Extra data:',
        'parsing_instruction is deprecated'
    ]
    
    def filter(self, record):
        """Determine if a log record should be shown in terminal"""
        message = record.getMessage()
        
        # Suppress specific warnings in terminal (but keep in log file)
        if record.levelno == logging.WARNING:
            for suppress_pattern in self.SUPPRESS_WARNINGS:
                if suppress_pattern in message:
                    return False  
            # Show other warnings
            record._terminal_only = True
            return True
        
        # Always show errors in terminal
        if record.levelno >= logging.ERROR:
            record._terminal_only = True
            return True
        
        # Show only essential INFO messages in terminal
        for keyword in self.ESSENTIAL_KEYWORDS:
            if keyword in message:
                record._terminal_only = True
                return True
        
        return False

# Create formatters for different output destinations
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
terminal_formatter = ColoredFormatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

# Create file handler (captures everything)
file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# Create terminal handler (filtered output)
terminal_handler = logging.StreamHandler(sys.stdout)
terminal_handler.setLevel(logging.INFO)
terminal_handler.setFormatter(terminal_formatter)
terminal_handler.addFilter(TerminalFilter())

# Configure main logger
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[file_handler, terminal_handler]
)

logger = logging.getLogger(__name__)

# Suppress HTTP request logs in terminal (but keep them in log file)
http_loggers = ['httpx', 'httpcore', 'urllib3', 'requests', 'openai', 'llama_index']
for logger_name in http_loggers:
    http_logger = logging.getLogger(logger_name)
    http_logger.setLevel(logging.WARNING)

class HTTPFilter(logging.Filter):
    """Filter to hide HTTP request details from terminal output"""
    def filter(self, record):
        message = record.getMessage()
        # Don't show HTTP requests in terminal
        if 'HTTP Request:' in message or 'POST https://' in message or 'GET https://' in message:
            return False
        return True

# Apply HTTP filter to terminal handler only
terminal_handler.addFilter(HTTPFilter())

# Log startup message
logger.info(f"[INIT] Enhanced RAG Pipeline started - Full logs: {log_filename}")

# =============================================================================
# DATA MODELS AND ENUMS
# =============================================================================

class QueryType(Enum):
    """
    Enumeration of different query types for adaptive RAG processing
    Each type requires different retrieval and generation strategies
    """
    FACTUAL = "factual"              # Simple fact-based questions
    PROCEDURAL = "procedural"        # How-to questions and procedures
    ANALYTICAL = "analytical"        # Analysis and reasoning questions
    COMPARATIVE = "comparative"      # Comparison questions
    EXPLORATORY = "exploratory"      # Open-ended exploration
    TROUBLESHOOTING = "troubleshooting"  # Problem-solving questions

class QueryComplexity(Enum):
    """
    Enumeration of query complexity levels
    Determines retrieval count and processing strategy
    """
    SIMPLE = "simple"    # Single concept, direct answer
    MEDIUM = "medium"    # Multiple concepts, some synthesis needed
    COMPLEX = "complex"  # Multiple topics, multi-step reasoning

@dataclass
class QueryAnalysis:
    """
    Data class containing the results of query analysis
    Used to determine the optimal RAG strategy
    """
    query_type: QueryType
    complexity: QueryComplexity
    entities: List[str]               # Named entities found in query
    keywords: List[str]               # Important keywords
    requires_multi_step: bool         # Whether multi-step reasoning is needed
    requires_synthesis: bool          # Whether synthesis across sources is needed
    confidence_score: float           # Confidence in the analysis
    suggested_retrieval_count: int    # Recommended number of documents to retrieve
    suggested_strategy: str           # Recommended strategy name

@dataclass
class AdaptiveStrategy:
    """
    Data class defining the adaptive RAG strategy to use
    Based on query analysis results
    """
    retrieval_count: int              # Number of documents to retrieve
    use_reranking: bool              # Whether to rerank results
    use_multi_hop: bool              # Whether to use multi-hop reasoning
    use_synthesis: bool              # Whether to synthesize information
    chunk_size_preference: str       # Preferred chunk size ("small", "medium", "large")
    diversity_factor: float          # How diverse the retrieved results should be
    confidence_threshold: float      # Minimum confidence threshold

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

class PDFOptimizedConfig:
    """
    Configuration class that manages all system settings
    Loads from environment variables with sensible defaults
    """
    
    def __init__(self):
        # Load API keys from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        
        # Database connection string
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:test@localhost:5432/vector_db")
        
        # Model configuration - using only specified OpenAI models
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.chat_model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        self.analysis_model = os.getenv("ANALYSIS_MODEL", "gpt-4o")
        
        # Database connection string
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:test@localhost:5432/vector_db")
        
        # Check for missing API keys and warn user
        missing_keys = []
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        if not self.llama_cloud_api_key:
            missing_keys.append("LLAMA_CLOUD_API_KEY")
        if not self.tavily_api_key:
            missing_keys.append("TAVILY_API_KEY")
        
        if missing_keys:
            print(f"WARNING: Missing environment variables: {', '.join(missing_keys)}")
            print("Please create a .env file with your API keys")
        
        # LlamaParse instruction for comprehensive content extraction
        self.parsing_instruction = """
        Extract ALL text content from each page. Preserve structure including:
        - All headings and subheadings
        - All paragraphs and sentences
        - All tables and lists
        - All code blocks and technical content
        - All figure captions and references
        
        Remove only:
        - Page numbers
        - Document headers/footers
        - Copyright notices
        - Repeated navigation elements
        
        Maintain original formatting and structure.
        """
        
        # Content chunking settings
        self.max_chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "2000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "400"))
        
        # Page processing settings
        self.store_individual_pages = os.getenv("STORE_INDIVIDUAL_PAGES", "true").lower() == "true"
        self.advanced_cleaning = os.getenv("ADVANCED_CLEANING", "true").lower() == "true"
        
        # Adaptive RAG settings
        self.adaptive_enabled = os.getenv("ADAPTIVE_RAG_ENABLED", "true").lower() == "true"
        self.max_retrieval_attempts = int(os.getenv("MAX_RETRIEVAL_ATTEMPTS", "3"))
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# Initialize global configuration
config = PDFOptimizedConfig()

# =============================================================================
# PDF PARSING AND CONTENT EXTRACTION
# =============================================================================

class AdvancedPDFParser:
    """
    Enhanced PDF parser that processes documents page-by-page
    Uses LlamaParse for high-quality content extraction with advanced cleaning
    """
    
    def __init__(self):
        if not config.llama_cloud_api_key:
            raise ValueError("LLAMA_CLOUD_API_KEY is required")
            
        # Initialize LlamaParse with page-by-page processing
        self.parser = LlamaParse(
            api_key=config.llama_cloud_api_key,
            result_type="markdown",           # Get structured markdown output
            verbose=True,
            language="en",
            parsing_instruction=config.parsing_instruction,
            split_by_page=True,               # Enable page-by-page extraction
            page_separator="\\n---PAGE_BREAK---\\n"  # Custom page separator
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")  # For token counting
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file to detect duplicates
        Used to avoid reprocessing the same document
        """
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _clean_page_content(self, content: str, page_num: int) -> str:
        """
        Advanced page content cleaning to remove headers, footers, and noise
        
        Args:
            content: Raw page content
            page_num: Page number for context
            
        Returns:
            Cleaned content with headers/footers removed
        """
        if not content or len(content.strip()) < 10:
            return ""
        
        lines = content.split('\n')
        cleaned_lines = []
        
        # Enhanced removal patterns for common header/footer elements
        removal_patterns = [
            r'^.*?Page\s+\d+.*?$',                          # Page numbers
            r'^.*?\d+\s*/\s*\d+.*?$',                       # Page numbers like "1/10"
            r'^.*?(Copyright|©|\(c\)|All rights reserved).*?$',  # Copyright notices
            r'^.*?(Confidential|Proprietary|Internal Use).*?$',  # Confidentiality notices
            r'^.*?(\d{4}.*?Company.*?|.*?Company.*?\d{4}).*?$',  # Company headers with years
            r'^\s*[-=_]{3,}\s*$',                           # Separator lines
            r'^.*?(Header|Footer|Navigation).*?$',          # Explicit header/footer text
            r'^.*?Table of Contents.*?$',                   # TOC references
            r'^.*?Contents.*?Page.*?$',                     # Contents with page refs
            r'^\s*\d+\s*$',                                # Standalone page numbers
            r'^.*?Last updated.*?\d{4}.*?$',               # Last updated notices
            r'^.*?Document version.*?\d+.*?$',             # Version numbers
        ]
        
        # Track repeated content across lines (likely headers/footers)
        line_frequency = {}
        for line in lines:
            # Remove numbers for comparison to catch repeated headers with different page numbers
            cleaned_line = re.sub(r'\d+', '', line.strip().lower())
            if len(cleaned_line) > 5:
                line_frequency[cleaned_line] = line_frequency.get(cleaned_line, 0) + 1
        
        # Identify likely headers/footers (appear multiple times and are short)
        likely_headers_footers = {line for line, freq in line_frequency.items() 
                                 if freq > 1 and len(line) < 100}
        
        prev_line = ""
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check against removal patterns
            should_remove = any(re.match(pattern, line, re.IGNORECASE) 
                              for pattern in removal_patterns)
            
            # Check if it's a likely header/footer based on frequency
            cleaned_line_check = re.sub(r'\d+', '', line.lower())
            if cleaned_line_check in likely_headers_footers:
                should_remove = True
            
            # Skip duplicate consecutive lines
            if line == prev_line:
                continue
            
            # Skip very short lines unless they're structural elements
            if len(line) < 3 and not re.match(r'^[#\-*+]', line):
                continue
            
            # Skip lines that are just numbers or dates
            if re.match(r'^\s*(\d+[\/\-\.]\d+[\/\-\.]\d+|\d+)\s*$', line):
                continue
            
            if not should_remove:
                cleaned_lines.append(line)
                prev_line = line
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Remove excessive whitespace while preserving structure
        cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)  # Max 2 consecutive newlines
        cleaned_content = re.sub(r'[ \t]+', ' ', cleaned_content)      # Normalize spaces
        
        return cleaned_content.strip()
    
    def _extract_page_metadata(self, content: str, page_num: int) -> Dict[str, Any]:
        """
        Extract detailed metadata from page content for analysis and categorization
        
        Args:
            content: Cleaned page content
            page_num: Page number
            
        Returns:
            Dictionary containing page metadata
        """
        metadata = {
            'page_number': page_num,
            'char_count': len(content),
            'word_count': len(content.split()),
            'line_count': len(content.split('\n')),
            'has_tables': len(re.findall(r'\|.*\|', content)) > 0,          # Markdown tables
            'has_code': len(re.findall(r'```[\s\S]*?```|`[^`]+`', content)) > 0,  # Code blocks
            'has_lists': len(re.findall(r'^[-*+]\s+', content, re.MULTILINE)) > 0,  # Bullet lists
            'has_headings': len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE)) > 0,  # Markdown headings
            'has_links': len(re.findall(r'https?://\S+', content)) > 0,     # URLs
        }
        
        # Extract potential sections/topics from headings
        headings = re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)
        if headings:
            metadata['headings'] = headings[:5]  # Store first 5 headings
        
        # Calculate content density (words per 100 characters)
        if metadata['char_count'] > 0:
            metadata['content_density'] = metadata['word_count'] / (metadata['char_count'] / 100)
        else:
            metadata['content_density'] = 0
        
        return metadata
    
    async def parse_document_by_pages(self, file_path: str) -> Dict[str, Any]:
        """
        Main method to parse a PDF document page-by-page
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing parsed document data with page-level information
        """
        try:
            logger.info(f"[PARSING] Starting page-by-page extraction: {file_path}")
            
            # Validate file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Log file size for monitoring
            file_size = file_path_obj.stat().st_size / (1024 * 1024)  # Size in MB
            logger.info(f"[INFO] File size: {file_size:.1f} MB")
            
            # Calculate file hash for duplicate detection
            file_hash = self.calculate_file_hash(file_path)
            
            # Parse document using LlamaParse
            documents = await self.parser.aload_data(file_path)
            
            if not documents:
                raise ValueError(f"No content extracted from {file_path}")
            
            # Process each page separately
            pages_data = []
            raw_content = documents[0].text
            
            # Split content by page separator if available
            if "---PAGE_BREAK---" in raw_content:
                page_contents = raw_content.split("---PAGE_BREAK---")
            else:
                # Fallback: estimate pages by content length
                estimated_page_length = len(raw_content) // max(1, len(documents))
                page_contents = [raw_content[i:i+estimated_page_length] 
                               for i in range(0, len(raw_content), estimated_page_length)]
            
            total_cleaned_content = ""
            
            # Process each page
            for page_num, page_content in enumerate(page_contents, 1):
                # Skip empty or very short pages
                if not page_content or len(page_content.strip()) < 20:
                    continue
                
                # Clean page content (remove headers/footers)
                cleaned_content = self._clean_page_content(page_content, page_num)
                
                # Skip pages with insufficient content after cleaning
                if len(cleaned_content.strip()) < 10:
                    continue
                
                # Extract detailed page metadata
                page_metadata = self._extract_page_metadata(cleaned_content, page_num)
                
                # Store page data
                page_data = {
                    'page_number': page_num,
                    'raw_content': page_content,
                    'cleaned_content': cleaned_content,
                    'metadata': page_metadata
                }
                
                pages_data.append(page_data)
                total_cleaned_content += cleaned_content + "\n\n"
                
                # Log page processing details
                logger.info(f"[PAGE {page_num}] Processed: {page_metadata['word_count']} words, "
                           f"density: {page_metadata['content_density']:.1f}")
            
            # Calculate overall document metadata
            total_words = sum(page['metadata']['word_count'] for page in pages_data)
            total_chars = len(total_cleaned_content)
            token_count = len(self.encoding.encode(total_cleaned_content))
            
            document_metadata = {
                'file_size_mb': round(file_size, 2),
                'total_pages': len(pages_data),
                'total_words': total_words,
                'total_chars': total_chars,
                'average_words_per_page': total_words / max(1, len(pages_data)),
                'processing_timestamp': datetime.now().isoformat(),
                'extraction_method': 'page_by_page_advanced',
                'pages_with_content': len(pages_data),
                'content_quality': 'high' if total_words > 1000 else 'medium' if total_words > 100 else 'low'
            }
            
            # Prepare final result
            result = {
                'filename': file_path_obj.name,
                'file_path': str(file_path_obj),
                'file_hash': file_hash,
                'total_content': total_cleaned_content,
                'pages_data': pages_data,
                'metadata': document_metadata,
                'page_count': len(pages_data),
                'content_length': total_chars,
                'token_count': token_count
            }
            
            logger.info(f"[SUCCESS] Parsed {file_path_obj.name}: "
                       f"{len(pages_data)} pages with content, {total_words} total words, "
                       f"quality: {document_metadata['content_quality']}")
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Error parsing {file_path}: {e}")
            raise

# =============================================================================
# CONTENT ANALYSIS AND CHUNKING
# =============================================================================

class ContentAnalyzer:
    """
    Enhanced content analyzer for page-level processing
    Classifies content and creates intelligent chunks using AI
    """
    
    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
            
        self.llm = ChatOpenAI(temperature=0, model=config.chat_model, api_key=config.openai_api_key)
        self.encoding = tiktoken.get_encoding("cl100k_base")

        # Prompt for content classification
        self.classification_prompt = ChatPromptTemplate.from_messages([
            ("system", """Classify content into categories: installation, configuration, api_reference, 
            tutorial, troubleshooting, overview, code_example, reference, security, general, introduction,
            conclusion, appendix, table_of_contents, bibliography.
            
            Return JSON: {{"category": "...", "importance_score": 0.8, "summary": "...", 
            "key_topics": ["...", "..."], "technical_level": "beginner/intermediate/advanced"}}"""),
            ("human", "Classify this content:\n\n{content}")
        ])
        
        # Prompt for intelligent chunking
        self.chunking_prompt = ChatPromptTemplate.from_messages([
            ("system", """Split content into logical chunks for better retrieval.
            Create chunks that:
            - Maintain context and meaning
            - Are 500-2000 characters each
            - Don't break mid-sentence
            - Group related concepts together
            
            Return JSON array: [{{"chunk": "...", "title": "...", "topics": ["..."]}}]"""),
            ("human", "Split this content into logical chunks:\n\n{content}")
        ])

    async def analyze_page_content(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze individual page content and create intelligent chunks
        
        Args:
            page_data: Dictionary containing page content and metadata
            
        Returns:
            Dictionary containing page analysis results and chunks
        """
        content = page_data['cleaned_content']
        page_num = page_data['page_number']
        
        # Handle empty or very short content
        if len(content.strip()) < 50:
            return {
                'page_number': page_num,
                'category': 'empty',
                'importance_score': 0.1,
                'key_topics': [],
                'technical_level': 'beginner',
                'chunks': [],
                'total_chunks': 0,
                'page_metadata': page_data['metadata']
            }
        
        try:
            # Step 1: Classify page content using AI with improved error handling
            classifier = self.classification_prompt | self.llm | StrOutputParser()
            classification_result = classifier.invoke({"content": content[:3000]})  # Limit for API
            
            # Clean and parse the classification response
            classification = self._parse_json_response(classification_result, "classification")
            
            # Validate classification structure
            if not isinstance(classification, dict):
                raise ValueError("Classification response is not a dictionary")
            
            # Step 2: Create intelligent chunks if content is long enough
            chunks = []
            if len(content) > 800:
                try:
                    # Use AI to create semantic chunks
                    chunker = self.chunking_prompt | self.llm | StrOutputParser()
                    chunking_result = chunker.invoke({"content": content[:4000]})  # Limit for API
                    
                    # Clean and parse the chunking response
                    chunks_data = self._parse_json_response(chunking_result, "chunking")
                    
                    # Validate chunks_data structure
                    if not isinstance(chunks_data, list):
                        raise ValueError("Chunking response is not a list")
                    
                    # Process AI-generated chunks
                    for i, chunk_info in enumerate(chunks_data):
                        if isinstance(chunk_info, dict) and 'chunk' in chunk_info:
                            chunk_content = chunk_info.get('chunk', '')
                            if len(chunk_content.strip()) > 50:  # Only add substantial chunks
                                chunks.append({
                                    'chunk_index': i,
                                    'content': chunk_content,
                                    'topics': chunk_info.get('topics', []),
                                    'token_count': len(self.encoding.encode(chunk_content))
                                })
                    
                    # If no valid chunks were created, fall back to simple splitting
                    if not chunks:
                        raise ValueError("No valid chunks created from AI response")
                        
                except Exception as e:
                    logger.warning(f"AI chunking failed for page {page_num}: {e}. Using fallback.")
                    # Fallback: simple text splitting
                    chunk_size = 1000
                    chunk_index = 0
                    for i in range(0, len(content), chunk_size):
                        chunk_content = content[i:i+chunk_size]
                        if len(chunk_content.strip()) > 100:
                            chunks.append({
                                'chunk_index': chunk_index,
                                'content': chunk_content,
                                'topics': [],
                                'token_count': len(self.encoding.encode(chunk_content))
                            })
                            chunk_index += 1
            else:
                # Single chunk for short content
                chunks.append({
                    'chunk_index': 0,
                    'content': content,
                    'topics': classification.get('key_topics', []),
                    'token_count': len(self.encoding.encode(content))
                })
            
            # Prepare analysis result with validation
            result = {
                'page_number': page_num,
                'category': classification.get('category', 'general'),
                'importance_score': max(0.1, min(1.0, classification.get('importance_score', 0.5))),  # Ensure valid range
                'key_topics': classification.get('key_topics', []) if isinstance(classification.get('key_topics'), list) else [],
                'technical_level': classification.get('technical_level', 'intermediate'),
                'chunks': chunks,
                'total_chunks': len(chunks),
                'page_metadata': page_data['metadata']
            }
            
            logger.info(f"[ANALYZED] Page {page_num}: {result['category']}, "
                    f"{len(chunks)} chunks, importance: {result['importance_score']:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Analysis failed for page {page_num}: {e}")
            # Return basic fallback with single chunk
            return {
                'page_number': page_num,
                'category': 'general',
                'importance_score': 0.5,
                'key_topics': [],
                'technical_level': 'intermediate',
                'chunks': [{
                    'chunk_index': 0,
                    'content': content,
                    'topics': [],
                    'token_count': len(self.encoding.encode(content))
                }],
                'total_chunks': 1,
                'page_metadata': page_data['metadata']
            }

    def _parse_json_response(self, response: str, response_type: str) -> Dict[str, Any]:
        """
        Parse JSON response from AI with multiple fallback strategies
        
        Args:
            response: Raw response string from AI
            response_type: Type of response for logging ("classification" or "chunking")
            
        Returns:
            Parsed JSON object
        """
        if not response or not response.strip():
            raise ValueError(f"Empty {response_type} response")
        
        # Clean the response
        response = response.strip()
        
        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON from markdown code blocks
        json_patterns = [
            r'```json\s*(.*?)\s*```',
            r'```\s*(.*?)\s*```',
            r'`(.*?)`'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                try:
                    return json.loads(matches[0].strip())
                except json.JSONDecodeError:
                    continue
        
        # Strategy 3: Try to find JSON-like content
        json_start = response.find('{')
        json_end = response.rfind('}')
        if json_start != -1 and json_end != -1 and json_end > json_start:
            try:
                json_content = response[json_start:json_end + 1]
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Create fallback response based on type
        if response_type == "classification":
            logger.warning(f"Could not parse classification JSON, creating fallback response")
            return {
                "category": "general",
                "importance_score": 0.5,
                "summary": "Content analysis",
                "key_topics": [],
                "technical_level": "intermediate"
            }
        else:  # chunking
            logger.warning(f"Could not parse chunking JSON, creating fallback response")
            return [{"chunk": response[:1000], "title": "Content chunk", "topics": []}]
# =============================================================================
# DATABASE MANAGEMENT AND STORAGE
# =============================================================================

class EnhancedDatabaseManager:
    """
    Enhanced database manager with optimized page-level storage
    Uses PostgreSQL with pgvector for efficient vector storage and retrieval
    """
    
    def __init__(self):
        self.connection_string = config.database_url
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for embeddings")
        self.embeddings = OpenAIEmbeddings(model=config.embedding_model, api_key=config.openai_api_key)
        
    def test_connection(self):
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(self.connection_string)
            conn.close()
            logger.info("[SUCCESS] Database connection successful")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Database connection failed: {e}")
            return False
    
    def get_connection(self):
        """Get database connection with vector extension registered"""
        conn = psycopg2.connect(self.connection_string)
        register_vector(conn)  # Register pgvector extension
        return conn
    
    def setup_database(self):
        """
        Create optimized database schema for page-by-page storage
        
        SCHEMA DESIGN:
        - documents: Main document metadata and summary statistics
        - pages: Page-level metadata without storing full content (optimized)
        - chunks: Individual content chunks with embeddings for retrieval
        
        OPTIMIZATION NOTES:
        - Page content is reconstructed from chunks to save storage space
        - Embeddings are stored at chunk level for precise retrieval
        - Indexes are optimized for vector similarity search
        """
        try:
            if not self.test_connection():
                raise Exception("Cannot connect to database")
                
            conn = self.get_connection()
            cur = conn.cursor()
            
            # Enable vector extension for embeddings
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Documents table: stores document-level metadata
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    filename VARCHAR(255) NOT NULL,
                    file_hash VARCHAR(64) UNIQUE NOT NULL,  -- For duplicate detection
                    file_path TEXT,
                    content_type VARCHAR(50),
                    total_pages INTEGER,                     -- Total pages in document
                    pages_with_content INTEGER,             -- Pages that had extractable content
                    total_words INTEGER,
                    total_chars INTEGER,
                    total_tokens INTEGER,                    -- For token counting and billing estimation
                    file_size_mb FLOAT,
                    processing_status VARCHAR(20) DEFAULT 'pending',  -- pending/processing/completed/failed
                    content_quality VARCHAR(20),            -- high/medium/low based on content analysis
                    metadata JSONB,                         -- Flexible metadata storage
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Pages table: OPTIMIZED - stores page metadata without full content
            # Content is reconstructed from chunks to save storage space
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pages (
                    id UUID PRIMARY KEY,
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    page_number INTEGER NOT NULL,
                    word_count INTEGER,
                    char_count INTEGER,
                    has_tables BOOLEAN DEFAULT FALSE,       -- Whether page contains tables
                    has_code BOOLEAN DEFAULT FALSE,         -- Whether page contains code blocks
                    has_lists BOOLEAN DEFAULT FALSE,        -- Whether page contains lists
                    has_headings BOOLEAN DEFAULT FALSE,     -- Whether page contains headings
                    content_density FLOAT,                  -- Words per 100 characters ratio
                    page_metadata JSONB,                    -- Additional page-specific metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_id, page_number)        -- Ensure one record per page
                );
            """)
            
            # Chunks table: OPTIMIZED - stores content chunks with embeddings
            # This is where the actual searchable content lives
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    langchain_id UUID PRIMARY KEY,
                    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
                    page_id UUID REFERENCES pages(id) ON DELETE CASCADE,
                    page_number INTEGER,                     -- Denormalized for faster queries
                    chunk_index INTEGER,                     -- Order within page
                    content TEXT NOT NULL,                   -- The actual searchable content
                    category VARCHAR(50),                    -- Content category (tutorial, reference, etc.)
                    importance_score FLOAT DEFAULT 0.5,     -- AI-assessed importance (0-1)
                    key_topics TEXT[],                       -- Array of key topics/keywords
                    technical_level VARCHAR(20),            -- beginner/intermediate/advanced
                    token_count INTEGER,                     -- Number of tokens in this chunk
                    embedding vector(1536),                  -- OpenAI embedding vector
                    chunk_metadata JSONB,                   -- Additional chunk metadata
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT valid_importance_score CHECK (importance_score >= 0 AND importance_score <= 1)
                );
            """)
            
            # Create optimized indexes for fast retrieval
            cur.execute("CREATE INDEX IF NOT EXISTS idx_documents_hash ON documents(file_hash);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_pages_document_id ON pages(document_id);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_category ON chunks(category);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_importance ON chunks(importance_score);")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_technical_level ON chunks(technical_level);")
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("[SUCCESS] Optimized database schema created successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Error setting up database: {e}")
            raise
    
    def document_exists(self, file_hash: str) -> bool:
        """Check if a document with the given hash already exists"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM documents WHERE file_hash = %s", (file_hash,))
        exists = cur.fetchone() is not None
        
        cur.close()
        conn.close()
        return exists
    
    def insert_document(self, doc_data: Dict[str, Any]) -> int:
        """
        Insert document metadata and return document ID
        
        Args:
            doc_data: Dictionary containing document information
            
        Returns:
            Document ID for subsequent operations
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        metadata = doc_data['metadata']
        
        cur.execute("""
            INSERT INTO documents (id, filename, file_hash, file_path, content_type, 
                                 total_pages, pages_with_content, total_words, total_chars,
                                 total_tokens, file_size_mb, content_quality,
                                 metadata, processing_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            str(uuid.uuid4()),  # Use UUID for document ID
            doc_data['filename'],
            doc_data['file_hash'],
            doc_data['file_path'],
            'pdf',
            doc_data['page_count'],
            metadata.get('pages_with_content', 0),
            metadata.get('total_words', 0),
            doc_data['content_length'],
            doc_data['token_count'],
            metadata.get('file_size_mb', 0),
            metadata.get('content_quality', 'medium'),
            json.dumps(metadata), 
            'processing'
        ))
        
        document_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return document_id

    def insert_pages_and_chunks(self, document_id: int, analyzed_pages: List[Dict[str, Any]]):
        """
        Insert page metadata and content chunks with embeddings
        
        OPTIMIZATION STRATEGY:
        1. Insert all page records first
        2. Collect all chunk contents for batch embedding generation
        3. Insert chunks with pre-generated embeddings
        
        Args:
            document_id: Document ID to associate with
            analyzed_pages: List of analyzed page data with chunks
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        total_chunks = 0
        all_chunk_contents = []
        
        try:
            # Step 1: Insert page records (without content to save space)
            for page_analysis in analyzed_pages:
                page_num = page_analysis['page_number']
                page_metadata = page_analysis['page_metadata']
                
                cur.execute("""
                    INSERT INTO pages (id, document_id, page_number, word_count, char_count, 
                                    has_tables, has_code, has_lists, has_headings, 
                                    content_density, page_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    str(uuid.uuid4()),
                    document_id,
                    page_num,
                    page_metadata.get('word_count', 0),
                    page_metadata.get('char_count', 0),
                    page_metadata.get('has_tables', False),
                    page_metadata.get('has_code', False),
                    page_metadata.get('has_lists', False),
                    page_metadata.get('has_headings', False),
                    page_metadata.get('content_density', 0),
                    json.dumps(page_metadata)
                ))
                
                page_id = cur.fetchone()[0]
                
                # Collect chunk contents for batch embedding generation
                for chunk in page_analysis['chunks']:
                    all_chunk_contents.append(chunk['content'])
                
                total_chunks += len(page_analysis['chunks'])
            
            # Step 2: Generate embeddings for all chunks in batch (more efficient)
            logger.info(f"[EMBEDDINGS] Generating embeddings for {len(all_chunk_contents)} chunks...")
            embeddings = self.embeddings.embed_documents(all_chunk_contents)
            
            # Step 3: Insert chunks with pre-generated embeddings
            embedding_index = 0
            for page_analysis in analyzed_pages:
                page_num = page_analysis['page_number']
                
                # Get page ID for this page
                cur.execute("SELECT id FROM pages WHERE document_id = %s AND page_number = %s", 
                        (document_id, page_num))
                page_id = cur.fetchone()[0]
                
                # Insert each chunk for this page
                for chunk in page_analysis['chunks']:
                    # Store additional metadata like title in chunk_metadata
                    chunk_metadata = {
                        'topics': chunk.get('topics', []),
                        'token_count': chunk.get('token_count', 0),
                        'title': chunk.get('title', f'Page {page_num} - Chunk {chunk["chunk_index"]}'),
                        'processing_timestamp': datetime.now().isoformat()
                    }
                    
                    cur.execute("""
                        INSERT INTO chunks (langchain_id, document_id, page_id, page_number, chunk_index, content,
                                        category, importance_score, key_topics, technical_level,
                                        token_count, embedding, chunk_metadata)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        str(uuid.uuid4()),
                        document_id,
                        page_id,
                        page_num,
                        chunk['chunk_index'],
                        chunk['content'],
                        page_analysis['category'],
                        page_analysis['importance_score'],
                        page_analysis['key_topics'],
                        page_analysis['technical_level'],
                        chunk['token_count'],
                        embeddings[embedding_index],
                        json.dumps(chunk_metadata)
                    ))
                    
                    embedding_index += 1
            
            conn.commit()
            logger.info(f"[SUCCESS] Stored {len(analyzed_pages)} pages and {total_chunks} chunks")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"[ERROR] Failed to insert pages and chunks: {e}")
            raise
        finally:
            cur.close()
            conn.close()
    
    def update_document_status(self, document_id: int, status: str, total_chunks: int = None):
        """Update document processing status"""
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            UPDATE documents 
            SET processing_status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (status, document_id))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def similarity_search(self, query: str, limit: int = 5, min_importance: float = 0.3, 
                        category: str = None, technical_level: str = None, 
                        page_number: int = None) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search with optional filters
        
        Args:
            query: Search query text
            limit: Maximum number of results
            min_importance: Minimum importance score filter
            category: Optional category filter
            technical_level: Optional technical level filter
            page_number: Optional specific page number filter
            
        Returns:
            List of relevant chunks with metadata
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
        # Build dynamic WHERE clause based on filters
        where_clauses = [
            "d.processing_status = 'completed'",
            "c.importance_score >= %s"
        ]
        params = [min_importance]
        
        if category:
            where_clauses.append("c.category = %s")
            params.append(category)
        
        if technical_level:
            where_clauses.append("c.technical_level = %s")
            params.append(technical_level)
        
        if page_number:
            where_clauses.append("c.page_number = %s")
            params.append(page_number)
        
        where_clause = " AND ".join(where_clauses)
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
        
        # Execute similarity search query
        cur.execute(f"""
            SELECT c.id, c.content, c.category, c.importance_score,
                c.key_topics, c.technical_level, c.chunk_metadata, 
                d.filename, c.page_number, p.word_count as page_word_count,
                1 - (c.embedding <=> %s::vector) as similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            JOIN pages p ON c.page_id = p.id
            WHERE {where_clause}
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
        """, [embedding_str] + params + [embedding_str, limit])
        
        results = []
        for row in cur.fetchall():
            # Extract title from metadata if available
            metadata = row[6] if row[6] else {}
            title = metadata.get('title', f'Page {row[8]} - Chunk')
            
            results.append({
                'id': row[0],
                'title': title,
                'content': row[1],
                'category': row[2],
                'importance_score': row[3],
                'key_topics': row[4],
                'technical_level': row[5],
                'metadata': metadata,
                'filename': row[7],
                'page_number': row[8],
                'page_word_count': row[9],
                'similarity': row[10]
            })
        
        cur.close()
        conn.close()
        return results

    def get_page_content(self, document_id: int, page_number: int = None) -> List[Dict[str, Any]]:
        """
        Get page content by reconstructing from chunks
        
        OPTIMIZATION NOTE: Page content is reconstructed from chunks to save storage space
        while maintaining the ability to view full page content when needed
        
        Args:
            document_id: Document ID
            page_number: Optional specific page number
            
        Returns:
            List of page data with reconstructed content
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        if page_number:
            # Get specific page content reconstructed from chunks
            cur.execute("""
                SELECT p.page_number, p.word_count, p.page_metadata, d.filename,
                    COALESCE(STRING_AGG(c.content, E'\n\n' ORDER BY c.chunk_index), '') as reconstructed_content
                FROM pages p
                JOIN documents d ON p.document_id = d.id
                LEFT JOIN chunks c ON p.id = c.page_id
                WHERE p.document_id = %s AND p.page_number = %s
                GROUP BY p.page_number, p.word_count, p.page_metadata, d.filename
            """, (document_id, page_number))
        else:
            # Get all pages for document
            cur.execute("""
                SELECT p.page_number, p.word_count, p.page_metadata, d.filename,
                    COALESCE(STRING_AGG(c.content, E'\n\n' ORDER BY c.chunk_index), '') as reconstructed_content
                FROM pages p
                JOIN documents d ON p.document_id = d.id
                LEFT JOIN chunks c ON p.id = c.page_id
                WHERE p.document_id = %s
                GROUP BY p.page_number, p.word_count, p.page_metadata, d.filename
                ORDER BY p.page_number
            """, (document_id,))
        
        results = []
        for row in cur.fetchall():
            results.append({
                'page_number': row[0],
                'content': row[4],  # Reconstructed from chunks
                'word_count': row[1],
                'metadata': row[2],
                'filename': row[3]
            })
        
        cur.close()
        conn.close()
        return results
    
    def get_document_summary(self, document_id: int) -> Dict[str, Any]:
        """
        Get comprehensive document summary with page and chunk statistics
        
        Args:
            document_id: Document ID
            
        Returns:
            Dictionary containing detailed document information
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Get main document information
        cur.execute("""
            SELECT filename, total_pages, pages_with_content, total_words, 
                   content_quality, metadata
            FROM documents 
            WHERE id = %s
        """, (document_id,))
        
        doc_info = cur.fetchone()
        if not doc_info:
            return {}
        
        # Get page-level summary
        cur.execute("""
            SELECT page_number, word_count, has_tables, has_code, has_lists, has_headings
            FROM pages 
            WHERE document_id = %s 
            ORDER BY page_number
        """, (document_id,))
        
        pages_info = cur.fetchall()
        
        # Get chunk category distribution
        cur.execute("""
            SELECT category, COUNT(*) as count, AVG(importance_score) as avg_importance
            FROM chunks 
            WHERE document_id = %s 
            GROUP BY category
        """, (document_id,))
        
        category_info = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'filename': doc_info[0],
            'total_pages': doc_info[1],
            'pages_with_content': doc_info[2],
            'total_words': doc_info[3],
            'content_quality': doc_info[4],
            'metadata': doc_info[5],
            'pages_summary': [
                {
                    'page': p[0], 'words': p[1], 'has_tables': p[2],
                    'has_code': p[3], 'has_lists': p[4], 'has_headings': p[5]
                } for p in pages_info
            ],
            'categories': {cat[0]: {'count': cat[1], 'avg_importance': float(cat[2])} 
                          for cat in category_info}
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics
        
        Returns:
            Dictionary containing detailed statistics about stored documents
        """
        conn = self.get_connection()
        cur = conn.cursor()
        
        # Document-level statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_documents,
                COUNT(CASE WHEN processing_status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN processing_status = 'processing' THEN 1 END) as processing,
                COUNT(CASE WHEN processing_status = 'failed' THEN 1 END) as failed,
                SUM(total_words) as total_words,
                SUM(file_size_mb) as total_size_mb,
                AVG(total_words) as avg_words_per_doc
            FROM documents
        """)
        
        doc_stats = cur.fetchone()
        
        # Page-level statistics
        cur.execute("SELECT COUNT(*), SUM(word_count), AVG(word_count) FROM pages")
        page_stats = cur.fetchone()
        
        # Chunk-level statistics
        cur.execute("SELECT COUNT(*) FROM chunks")
        chunk_count = cur.fetchone()[0]
        
        # Category distribution
        cur.execute("SELECT category, COUNT(*) FROM chunks GROUP BY category")
        categories = dict(cur.fetchall())
        
        # Technical level distribution
        cur.execute("SELECT technical_level, COUNT(*) FROM chunks GROUP BY technical_level")
        technical_levels = dict(cur.fetchall())
        
        # Content quality distribution
        cur.execute("SELECT content_quality, COUNT(*) FROM documents GROUP BY content_quality")
        quality_distribution = dict(cur.fetchall())
        
        stats = {
            'documents': {
                'total': doc_stats[0],
                'completed': doc_stats[1],
                'processing': doc_stats[2],
                'failed': doc_stats[3],
                'total_words': doc_stats[4] or 0,
                'total_size_mb': round(doc_stats[5] or 0, 2),
                'avg_words_per_doc': round(doc_stats[6] or 0, 1)
            },
            'pages': {
                'total_pages': page_stats[0] or 0,
                'total_words': page_stats[1] or 0,
                'avg_words_per_page': round(page_stats[2] or 0, 1)
            },
            'chunks': {
                'total_chunks': chunk_count,
                'categories': categories,
                'technical_levels': technical_levels
            },
            'quality_distribution': quality_distribution
        }
        
        cur.close()
        conn.close()
        return stats

# =============================================================================
# ADAPTIVE RAG QUERY ANALYSIS AND STRATEGY PLANNING
# =============================================================================

class QueryAnalyzer:
    """
    Analyzes queries to determine the best adaptive RAG strategy
    Uses AI to understand query type, complexity, and information needs
    """
    
    def __init__(self):
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.llm = ChatOpenAI(temperature=0, model=config.analysis_model, api_key=config.openai_api_key)

        # Comprehensive query analysis prompt
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the user query and classify it for adaptive RAG processing.
            
            Query Types:
            - FACTUAL: Simple fact-based questions (What is X? When did Y happen?)
            - PROCEDURAL: How-to questions (How to install? Steps to configure?)
            - ANALYTICAL: Analysis questions (Why does X happen? What causes Y?)
            - COMPARATIVE: Comparison questions (X vs Y, differences between A and B)
            - EXPLORATORY: Open-ended questions (Tell me about X, Explain the concept of Y)
            - TROUBLESHOOTING: Problem-solving questions (Error X occurs, How to fix Y?)
            
            Complexity Levels:
            - SIMPLE: Single concept, direct answer possible
            - MEDIUM: Multiple concepts, requires some synthesis
            - COMPLEX: Multiple topics, requires multi-step reasoning
            
            Return JSON with:
            {{
                "query_type": "FACTUAL|PROCEDURAL|ANALYTICAL|COMPARATIVE|EXPLORATORY|TROUBLESHOOTING",
                "complexity": "SIMPLE|MEDIUM|COMPLEX",
                "entities": ["entity1", "entity2"],
                "keywords": ["keyword1", "keyword2"],
                "requires_multi_step": true/false,
                "requires_synthesis": true/false,
                "confidence_score": 0.0-1.0,
                "suggested_retrieval_count": 3-15,
                "suggested_strategy": "single_shot|multi_hop|iterative_refinement"
            }}"""),
            ("human", "Analyze this query: {query}")
        ])
    
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        Analyze a query to determine the best adaptive strategy
        
        Args:
            query: User's question or request
            
        Returns:
            QueryAnalysis object with strategy recommendations
        """
        try:
            analysis_chain = self.analysis_prompt | self.llm | StrOutputParser()
            result = analysis_chain.invoke({"query": query})
            analysis_data = json.loads(result)
            
            return QueryAnalysis(
                query_type=QueryType(analysis_data["query_type"].lower()),
                complexity=QueryComplexity(analysis_data["complexity"].lower()),
                entities=analysis_data["entities"],
                keywords=analysis_data["keywords"],
                requires_multi_step=analysis_data["requires_multi_step"],
                requires_synthesis=analysis_data["requires_synthesis"],
                confidence_score=analysis_data["confidence_score"],
                suggested_retrieval_count=analysis_data["suggested_retrieval_count"],
                suggested_strategy=analysis_data["suggested_strategy"]
            )
        
        except Exception as e:
            logger.warning(f"Query analysis failed, using defaults: {e}")
            # Return conservative defaults on failure
            return QueryAnalysis(
                query_type=QueryType.FACTUAL,
                complexity=QueryComplexity.MEDIUM,
                entities=[],
                keywords=query.split()[:5],
                requires_multi_step=False,
                requires_synthesis=False,
                confidence_score=0.5,
                suggested_retrieval_count=5,
                suggested_strategy="single_shot"
            )

class AdaptiveStrategyPlanner:
    """
    Plans the optimal retrieval and generation strategy based on query analysis
    Maps query characteristics to specific RAG approaches
    """
    
    @staticmethod
    def plan_strategy(analysis: QueryAnalysis) -> AdaptiveStrategy:
        """
        Generate an adaptive strategy based on query analysis
        
        STRATEGY MAPPING:
        - FACTUAL: Few docs, high confidence threshold, small chunks
        - PROCEDURAL: More docs, reranking, large chunks for context
        - ANALYTICAL: Many docs, synthesis, diverse sources
        - COMPARATIVE: Multi-hop reasoning, high diversity
        - EXPLORATORY: Maximum docs, synthesis, high diversity
        - TROUBLESHOOTING: Moderate docs, reranking, large chunks
        
        Args:
            analysis: QueryAnalysis results
            
        Returns:
            AdaptiveStrategy with optimized parameters
        """
        
        # Start with baseline strategy
        strategy = AdaptiveStrategy(
            retrieval_count=5,
            use_reranking=False,
            use_multi_hop=False,
            use_synthesis=False,
            chunk_size_preference="medium",
            diversity_factor=0.3,
            confidence_threshold=0.7
        )
        
        # Adjust strategy based on query type
        if analysis.query_type == QueryType.FACTUAL:
            # Factual queries need precise, authoritative answers
            strategy.retrieval_count = min(3, analysis.suggested_retrieval_count)
            strategy.chunk_size_preference = "small"  # Precise information
            strategy.confidence_threshold = 0.8       # High confidence required
            
        elif analysis.query_type == QueryType.PROCEDURAL:
            # Procedural queries need comprehensive step-by-step information
            strategy.retrieval_count = min(7, analysis.suggested_retrieval_count)
            strategy.use_reranking = True             # Prioritize relevant steps
            strategy.chunk_size_preference = "large"  # Need full context
            strategy.diversity_factor = 0.2          # Focused results
            
        elif analysis.query_type == QueryType.ANALYTICAL:
            # Analytical queries need multiple perspectives and reasoning
            strategy.retrieval_count = min(10, analysis.suggested_retrieval_count)
            strategy.use_synthesis = True             # Combine insights
            strategy.use_reranking = True
            strategy.diversity_factor = 0.4          # Some diversity for analysis
            
        elif analysis.query_type == QueryType.COMPARATIVE:
            # Comparative queries need diverse sources and multi-step reasoning
            strategy.retrieval_count = min(12, analysis.suggested_retrieval_count)
            strategy.use_multi_hop = True             # Cross-reference information
            strategy.use_synthesis = True
            strategy.diversity_factor = 0.6          # High diversity for comparison
            
        elif analysis.query_type == QueryType.EXPLORATORY:
            # Exploratory queries need comprehensive coverage
            strategy.retrieval_count = min(15, analysis.suggested_retrieval_count)
            strategy.use_multi_hop = True
            strategy.use_synthesis = True
            strategy.diversity_factor = 0.7          # Maximum diversity
            
        elif analysis.query_type == QueryType.TROUBLESHOOTING:
            # Troubleshooting needs specific solutions with context
            strategy.retrieval_count = min(8, analysis.suggested_retrieval_count)
            strategy.use_reranking = True             # Prioritize solutions
            strategy.chunk_size_preference = "large"  # Need context for solutions
            strategy.diversity_factor = 0.3          # Focused on solutions
        
        # Adjust based on complexity level
        if analysis.complexity == QueryComplexity.SIMPLE:
            # Simple queries can use fewer documents
            strategy.retrieval_count = max(1, strategy.retrieval_count - 2)
            strategy.use_multi_hop = False
            
        elif analysis.complexity == QueryComplexity.COMPLEX:
            # Complex queries need more comprehensive retrieval
            strategy.retrieval_count = min(15, strategy.retrieval_count + 3)
            strategy.use_multi_hop = True
            strategy.use_synthesis = True
        
        # Adjust based on analysis confidence
        if analysis.confidence_score < 0.6:
            # Low confidence means we need more information
            strategy.retrieval_count = min(15, strategy.retrieval_count + 2)
            strategy.use_reranking = True
        
        return strategy

# =============================================================================
# ENHANCED RAG ENGINE WITH ADAPTIVE PROCESSING
# =============================================================================

class EnhancedRAGEngine:
    """
    Enhanced RAG engine with page-aware retrieval and adaptive strategies
    Provides different answer generation approaches based on query analysis
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        # Use GPT-4 for better reasoning and synthesis
        self.llm = ChatOpenAI(temperature=0, model=config.analysis_model, api_key=config.openai_api_key)
        self.query_analyzer = QueryAnalyzer()
        self.strategy_planner = AdaptiveStrategyPlanner()
        
        # Different prompt templates for different strategies
        self.single_shot_prompt = ChatPromptTemplate.from_messages([
            ("system", """Answer the question based on the provided context from document pages.
            Cite specific pages when possible. Provide a direct, focused answer.
            
            Context from document pages:
            {context}"""),
            ("human", "{question}")
        ])
        
        self.multi_hop_prompt = ChatPromptTemplate.from_messages([
            ("system", """Answer the question using multi-step reasoning based on content from multiple pages.
            Cross-reference information between pages when relevant. Show your reasoning process.
            
            Context from multiple pages:
            {context}"""),
            ("human", "{question}")
        ])
        
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """Provide a comprehensive answer by synthesizing information from multiple document pages.
            Show how information connects across different pages. Create a unified understanding.
            
            Context from various pages:
            {context}"""),
            ("human", "{question}")
        ])
        
        # Prompt for assessing answer confidence
        self.confidence_assessment_prompt = ChatPromptTemplate.from_messages([
            ("system", """Assess confidence in the provided answer based on the available context.
            Consider completeness, consistency, and evidence quality.
            Return JSON: {{"confidence": 0.0-1.0, "reasoning": "explanation", "missing_info": ["item1"]}}"""),
            ("human", "Question: {question}\nAnswer: {answer}\nContext: {context}")
        ])
    
    async def adaptive_query(self, question: str) -> Dict[str, Any]:
        """
        Enhanced adaptive query processing with page-aware retrieval
        
        PROCESS FLOW:
        1. Analyze query to determine type and complexity
        2. Plan adaptive strategy based on analysis
        3. Execute retrieval with strategy parameters
        4. Generate answer using appropriate approach
        5. Assess confidence and provide metadata
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing answer, metadata, and strategy information
        """
        logger.info(f"[ADAPTIVE RAG] Processing query: {question}")
        
        # Step 1: Analyze the query to understand what's being asked
        analysis = self.query_analyzer.analyze_query(question)
        logger.info(f"[ANALYSIS] Query type: {analysis.query_type.value}, "
                   f"Complexity: {analysis.complexity.value}")
        
        # Step 2: Plan adaptive strategy based on analysis results
        strategy = self.strategy_planner.plan_strategy(analysis)
        logger.info(f"[STRATEGY] Retrieval count: {strategy.retrieval_count}, "
                   f"Multi-hop: {strategy.use_multi_hop}, Synthesis: {strategy.use_synthesis}")
        
        # Step 3: Execute enhanced retrieval with strategy parameters
        results = self.db.similarity_search(question, limit=strategy.retrieval_count)
        
        if not results:
            return {
                "question": question,
                "answer": "I couldn't find any relevant information to answer your question.",
                "strategy": strategy.__dict__,
                "analysis": analysis.__dict__,
                "confidence": 0.0,
                "sources": 0,
                "pages_referenced": []
            }
        
        # Step 4: Generate answer using appropriate strategy
        answer = await self._generate_page_aware_answer(question, results, strategy)
        
        # Step 5: Extract page references for transparency
        pages_referenced = list(set([r['page_number'] for r in results]))
        pages_referenced.sort()
        
        # Step 6: Assess confidence in the generated answer
        context_summary = self._create_context_summary(results)
        confidence_assessment = await self._assess_answer_confidence(question, answer, context_summary)
        
        return {
            "question": question,
            "answer": answer,
            "strategy": {
                "type": analysis.suggested_strategy,
                "retrieval_count": len(results),
                "used_multi_hop": strategy.use_multi_hop,
                "used_synthesis": strategy.use_synthesis,
                "used_reranking": strategy.use_reranking
            },
            "analysis": {
                "query_type": analysis.query_type.value,
                "complexity": analysis.complexity.value,
                "entities": analysis.entities,
                "keywords": analysis.keywords
            },
            "confidence": confidence_assessment['confidence'],
            "confidence_reasoning": confidence_assessment.get('reasoning', ''),
            "sources": len(results),
            "pages_referenced": pages_referenced,
            "documents": results[:5]  # Return top 5 sources for reference
        }
    
    def _create_context_summary(self, results: List[Dict[str, Any]]) -> str:
        """
        Create enhanced context summary with page information
        
        FORMAT:
        - Each source is clearly labeled with page number and filename
        - Includes metadata like category and technical level
        - Maintains source attribution for transparency
        
        Args:
            results: List of search results
            
        Returns:
            Formatted context string for the LLM
        """
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"""
Source {i} (Page {result['page_number']} of {result['filename']}):
Title: {result['title']}
Category: {result['category']} | Technical Level: {result['technical_level']}
Similarity: {result.get('similarity', 0):.3f}
Content: {result['content']}
            """.strip())
        
        return "\n\n".join(context_parts)
    
    async def _generate_page_aware_answer(self, question: str, results: List[Dict[str, Any]], 
                                        strategy: AdaptiveStrategy) -> str:
        """
        Generate answer with page awareness using the appropriate strategy
        
        STRATEGY SELECTION:
        - Synthesis: For complex queries needing information combination
        - Multi-hop: For queries requiring cross-referencing
        - Single-shot: For direct, straightforward queries
        
        Args:
            question: User's question
            results: Retrieved documents
            strategy: Adaptive strategy to use
            
        Returns:
            Generated answer string
        """
        context = self._create_context_summary(results)
        
        try:
            if strategy.use_synthesis:
                # Use synthesis for comprehensive answers
                chain = self.synthesis_prompt | self.llm | StrOutputParser()
                logger.info("[GENERATION] Using synthesis strategy")
            elif strategy.use_multi_hop:
                # Use multi-hop for cross-referencing
                chain = self.multi_hop_prompt | self.llm | StrOutputParser()
                logger.info("[GENERATION] Using multi-hop strategy")
            else:
                # Use single-shot for direct answers
                chain = self.single_shot_prompt | self.llm | StrOutputParser()
                logger.info("[GENERATION] Using single-shot strategy")
            
            answer = chain.invoke({"question": question, "context": context})
            return answer
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "I encountered an error while generating the answer."
    
    async def _assess_answer_confidence(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """
        Assess confidence in the generated answer
        
        CONFIDENCE FACTORS:
        - Completeness of information in context
        - Consistency across sources
        - Directness of answer to question
        - Quality of supporting evidence
        
        Args:
            question: Original question
            answer: Generated answer
            context: Context used for generation
            
        Returns:
            Dictionary with confidence score and reasoning
        """
        try:
            assessment_chain = self.confidence_assessment_prompt | self.llm | StrOutputParser()
            result = assessment_chain.invoke({
                "question": question,
                "answer": answer,
                "context": context[:2000]  # Limit context length for API
            })
            return json.loads(result)
        except Exception as e:
            logger.warning(f"Confidence assessment failed: {e}")
            return {"confidence": 0.5, "reasoning": "Assessment failed", "missing_info": []}

# =============================================================================
# MAIN RAG PIPELINE ORCHESTRATOR
# =============================================================================

class EnhancedRAGPipeline:
    """
    Main orchestrator class that coordinates all components
    Provides high-level interface for document processing and querying
    """
    
    def __init__(self):
        logger.info("[INIT] Initializing Enhanced Page-by-Page RAG Pipeline...")
        
        try:
            # Initialize core components
            self.parser = AdvancedPDFParser()
            self.analyzer = ContentAnalyzer()
            self.db = EnhancedDatabaseManager()
            
            # Initialize appropriate RAG engine based on configuration
            if config.adaptive_enabled:
                self.rag_engine = EnhancedRAGEngine(self.db)
                logger.info("[SUCCESS] Enhanced Adaptive RAG Engine initialized")
            else:
                self.rag_engine = SimpleRAGEngine(self.db)
                logger.info("[SUCCESS] Simple RAG Engine initialized")
                
            logger.info("[SUCCESS] Enhanced Pipeline initialized successfully")
        except Exception as e:
            logger.error(f"[ERROR] Pipeline initialization failed: {e}")
            raise
    
    def setup_database(self):
        """Initialize database schema"""
        self.db.setup_database()
    
    async def process_document(self, file_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process a single PDF document with page-by-page extraction
        
        PROCESSING FLOW:
        1. Parse PDF page-by-page with advanced cleaning
        2. Check for duplicates using file hash
        3. Register document in database
        4. Analyze each page for content categorization
        5. Create intelligent chunks with embeddings
        6. Store everything in optimized database schema
        
        Args:
            file_path: Path to PDF file
            force_reprocess: Whether to reprocess existing documents
            
        Returns:
            Dictionary containing processing results
        """
        try:
            logger.info(f"[PROCESSING] Document with page-by-page extraction: {file_path}")
            
            # Validate input file
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"Only PDF files are supported. Got: {file_path}")
            
            # Step 1: Parse document page by page
            doc_data = await self.parser.parse_document_by_pages(file_path)
            
            # Step 2: Check for duplicates (unless forced)
            if not force_reprocess and self.db.document_exists(doc_data['file_hash']):
                logger.info("[SKIP] Document already processed, skipping...")
                return {"status": "skipped", "reason": "already_processed", "file": doc_data['filename']}
            
            # Step 3: Register document in database
            document_id = self.db.insert_document(doc_data)
            logger.info(f"[REGISTER] Document registered with ID: {document_id}")
            
            try:
                logger.info("[AI] Starting page-by-page analysis...")
                
                # Step 4: Analyze each page for categorization and chunking
                analyzed_pages = []
                for page_data in doc_data['pages_data']:
                    page_analysis = await self.analyzer.analyze_page_content(page_data)
                    analyzed_pages.append(page_analysis)
                
                logger.info(f"[ANALYZED] Processed {len(analyzed_pages)} pages")
                
                # Step 5: Store pages and chunks with embeddings
                self.db.insert_pages_and_chunks(document_id, analyzed_pages)
                
                # Step 6: Update document status to completed
                total_chunks = sum(page['total_chunks'] for page in analyzed_pages)
                self.db.update_document_status(document_id, 'completed', total_chunks)
                
                logger.info("[SUCCESS] Document processing completed!")
                
                return {
                    "status": "completed",
                    "document_id": document_id,
                    "file": doc_data['filename'],
                    "pages_processed": len(analyzed_pages),
                    "chunks_created": total_chunks,
                    "total_words": doc_data['metadata']['total_words'],
                    "content_quality": doc_data['metadata']['content_quality'],
                    "categories": list(set(page['category'] for page in analyzed_pages))
                }
                
            except Exception as e:
                logger.error(f"[ERROR] Processing failed: {e}")
                # Mark document as failed in database
                self.db.update_document_status(document_id, 'failed')
                return {"status": "failed", "error": str(e), "file": doc_data['filename']}
                
        except Exception as e:
            logger.error(f"[ERROR] Document parsing failed: {e}")
            return {"status": "failed", "error": str(e), "file": Path(file_path).name}
    
    async def process_directory(self, directory: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process all PDF files in a directory with enhanced extraction
        
        Args:
            directory: Directory path containing PDF files
            force_reprocess: Whether to reprocess existing documents
            
        Returns:
            Dictionary containing batch processing results
        """
        logger.info(f"[DIRECTORY] Processing directory with enhanced extraction: {directory}")
        
        directory_path = Path(directory)
        
        if not directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        # Find all PDF files recursively
        pdf_files = list(directory_path.glob("**/*.pdf"))
        
        if not pdf_files:
            logger.warning("[WARNING] No PDF documents found")
            return {"status": "no_documents", "processed": 0, "failed": 0, "skipped": 0}
        
        logger.info(f"[FILES] Found {len(pdf_files)} PDF documents")
        
        # Process each file
        results = []
        processed = 0
        failed = 0
        skipped = 0
        
        for pdf_path in pdf_files:
            result = await self.process_document(str(pdf_path), force_reprocess)
            results.append(result)
            
            # Track statistics
            if result["status"] == "completed":
                processed += 1
            elif result["status"] == "failed":
                failed += 1
            elif result["status"] == "skipped":
                skipped += 1
        
        # Log summary
        logger.info(f"[SUMMARY] Enhanced Processing Summary:")
        logger.info(f"[SUCCESS] Processed: {processed}")
        logger.info(f"[ERROR] Failed: {failed}")
        logger.info(f"[SKIP] Skipped: {skipped}")
        
        return {
            "status": "completed",
            "total_documents": len(pdf_files),
            "processed": processed,
            "failed": failed,
            "skipped": skipped,
            "results": results
        }
    
    async def query(self, question: str, limit: int = 5) -> Dict[str, Any]:
        """
        Query using enhanced page-aware RAG
        
        Args:
            question: User's question
            limit: Maximum number of results for simple RAG
            
        Returns:
            Dictionary containing answer and metadata
        """
        if config.adaptive_enabled and hasattr(self.rag_engine, 'adaptive_query'):
            # Use adaptive RAG for intelligent processing
            return await self.rag_engine.adaptive_query(question)
        else:
            # Use simple RAG for basic processing
            return self.rag_engine.query(question, limit=limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        return self.db.get_stats()
    
    def get_document_summary(self, document_id: int) -> Dict[str, Any]:
        """Get detailed document summary"""
        return self.db.get_document_summary(document_id)
    
    def get_page_content(self, document_id: int, page_number: int = None) -> List[Dict[str, Any]]:
        """Get page content (reconstructed from chunks)"""
        return self.db.get_page_content(document_id, page_number)

# =============================================================================
# SIMPLE RAG ENGINE (BACKWARD COMPATIBILITY)
# =============================================================================

class SimpleRAGEngine:
    """
    Simple RAG engine for backward compatibility
    Provides basic query processing without adaptive features
    """
    
    def __init__(self, db_manager: EnhancedDatabaseManager):
        self.db = db_manager
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        self.llm = ChatOpenAI(temperature=0, model=config.chat_model, api_key=config.openai_api_key)
        
        # Simple RAG prompt template
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """Answer questions based on the provided context from document pages.
            Reference specific pages when possible.
            
            Context from document pages:
            {context}
            """),
            ("human", "{question}")
        ])
        
        self.rag_chain = self.rag_prompt | self.llm | StrOutputParser()
    
    def query(self, question: str, limit: int = 5, min_importance: float = 0.3) -> Dict[str, Any]:
        """
        Simple query processing without adaptive features
        
        Args:
            question: User's question
            limit: Maximum number of results
            min_importance: Minimum importance score filter
            
        Returns:
            Dictionary containing answer and basic metadata
        """
        logger.info(f"[SIMPLE RAG] Processing query: {question}")
        
        # Retrieve relevant chunks
        results = self.db.similarity_search(question, limit=limit, min_importance=min_importance)
        
        if not results:
            return {
                "question": question,
                "answer": "I couldn't find any relevant information in the documents to answer your question.",
                "sources": 0,
                "pages_referenced": [],
                "documents": []
            }
        
        # Build context and track pages
        context_parts = []
        pages_referenced = set()
        
        for i, result in enumerate(results, 1):
            pages_referenced.add(result['page_number'])
            context_parts.append(f"""
Page {result['page_number']} of {result['filename']}:
Section: {result['title']}
Category: {result['category']}
Content: {result['content'][:1000]}...
            """.strip())
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        try:
            answer = self.rag_chain.invoke({
                "context": context,
                "question": question
            })
        except Exception as e:
            logger.error(f"[ERROR] Error generating answer: {e}")
            answer = "Sorry, I encountered an error while generating the answer."
        
        return {
            "question": question,
            "answer": answer,
            "sources": len(results),
            "pages_referenced": sorted(list(pages_referenced)),
            "documents": results
        }

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_env_file():
    """
    Create a comprehensive .env file template with all configuration options
    """
    env_content = """# Enhanced Page-by-Page RAG Pipeline Configuration
# Get your API keys from:
# - OpenAI: https://platform.openai.com/api-keys
# - LlamaCloud: https://cloud.llamaindex.ai/
# - Tavily: https://tavily.com/

OPENAI_API_KEY=sk-your-openai-key-here
LLAMA_CLOUD_API_KEY=llx-your-llama-key-here
TAVILY_API_KEY=tvly-your-tavily-key-here

# Database Configuration (using your existing vector_db)
DATABASE_URL=postgresql://postgres:test@localhost:5432/vector_db

# OpenAI Model Configuration (using only specified models)
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
ANALYSIS_MODEL=gpt-4o

# Page Processing Settings
STORE_INDIVIDUAL_PAGES=true
ADVANCED_CLEANING=true

# Adaptive RAG Settings
ADAPTIVE_RAG_ENABLED=true
MAX_RETRIEVAL_ATTEMPTS=3
CONFIDENCE_THRESHOLD=0.7

# Content Processing Settings
MAX_CHUNK_SIZE=2000
CHUNK_OVERLAP=400
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("SUCCESS: Created .env file with Enhanced Page-by-Page RAG settings. Please add your API keys.")

# =============================================================================
# INTERACTIVE MODE
# =============================================================================

async def interactive_mode(pipeline: EnhancedRAGPipeline):
    """
    Enhanced interactive mode with comprehensive commands
    Provides a user-friendly interface for exploring the RAG system
    """
    print("\n[ENHANCED RAG] Interactive Query Mode with Page-by-Page Processing")
    print("Type 'quit', 'exit', or 'q' to exit")
    print("Type 'stats' to see database statistics")
    print("Type 'pages <doc_id>' to see page summary for a document")
    print("Type 'page <doc_id> <page_num>' to see specific page content")
    print("Type 'summary <doc_id>' to see document summary")
    print("Type 'adaptive on/off' to toggle adaptive mode")
    print("Type 'help' for commands")
    print("-" * 70)
    
    while True:
        try:
            query = input("\nAsk a question: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            elif query.lower() == 'stats':
                # Display comprehensive database statistics
                stats = pipeline.get_stats()
                print(f"\n[STATS] Enhanced Database Statistics:")
                print(f"Documents: {stats['documents']['completed']}/{stats['documents']['total']} completed")
                print(f"Pages: {stats['pages']['total_pages']} (avg {stats['pages']['avg_words_per_page']} words/page)")
                print(f"Chunks: {stats['chunks']['total_chunks']}")
                print(f"Categories: {', '.join(stats['chunks']['categories'].keys())}")
                print(f"Quality Distribution: {stats['quality_distribution']}")
                print(f"Adaptive RAG: {'Enabled' if config.adaptive_enabled else 'Disabled'}")
                continue
            elif query.lower().startswith('pages '):
                # Show page summary for a document
                try:
                    doc_id = int(query.split()[1])
                    pages = pipeline.get_page_content(doc_id)
                    print(f"\n[PAGES] Document {doc_id} contains {len(pages)} pages:")
                    for page in pages[:10]:  # Show first 10 pages
                        print(f"  Page {page['page_number']}: {page['word_count']} words")
                except (ValueError, IndexError):
                    print("[ERROR] Usage: pages <document_id>")
                continue
            elif query.lower().startswith('page '):
                # Show specific page content
                try:
                    parts = query.split()
                    doc_id = int(parts[1])
                    page_num = int(parts[2])
                    pages = pipeline.get_page_content(doc_id, page_num)
                    if pages:
                        page = pages[0]
                        print(f"\n[PAGE] Page {page_num} of {page['filename']}:")
                        print(f"Word count: {page['word_count']}")
                        print(f"Content preview: {page['content'][:500]}...")
                    else:
                        print(f"[ERROR] Page {page_num} not found in document {doc_id}")
                except (ValueError, IndexError):
                    print("[ERROR] Usage: page <document_id> <page_number>")
                continue
            elif query.lower().startswith('summary '):
                # Show comprehensive document summary
                try:
                    doc_id = int(query.split()[1])
                    summary = pipeline.get_document_summary(doc_id)
                    if summary:
                        print(f"\n[SUMMARY] {summary['filename']}:")
                        print(f"Pages: {summary['pages_with_content']}/{summary['total_pages']}")
                        print(f"Total words: {summary['total_words']}")
                        print(f"Quality: {summary['content_quality']}")
                        print(f"Categories: {summary['categories']}")
                        print("Page breakdown:")
                        for page_info in summary['pages_summary'][:5]:
                            features = []
                            if page_info['has_tables']: features.append("tables")
                            if page_info['has_code']: features.append("code")
                            if page_info['has_lists']: features.append("lists")
                            if page_info['has_headings']: features.append("headings")
                            feature_str = f" ({', '.join(features)})" if features else ""
                            print(f"  Page {page_info['page']}: {page_info['words']} words{feature_str}")
                    else:
                        print(f"[ERROR] Document {doc_id} not found")
                except (ValueError, IndexError):
                    print("[ERROR] Usage: summary <document_id>")
                continue
            elif query.lower().startswith('adaptive'):
                # Toggle adaptive RAG mode
                if 'on' in query.lower():
                    config.adaptive_enabled = True
                    print("[ADAPTIVE] Enhanced Adaptive RAG enabled")
                elif 'off' in query.lower():
                    config.adaptive_enabled = False
                    print("[ADAPTIVE] Adaptive RAG disabled")
                continue
            elif query.lower() == 'help':
                # Show help information
                print("\nEnhanced Commands:")
                print("- Ask any question about your documents")
                print("- 'stats' - Show detailed database statistics")
                print("- 'pages <doc_id>' - Show page summary for document")
                print("- 'page <doc_id> <page_num>' - Show specific page content")
                print("- 'summary <doc_id>' - Show comprehensive document summary")
                print("- 'adaptive on/off' - Toggle adaptive RAG mode")
                print("- 'quit' - Exit interactive mode")
                continue
            elif not query:
                continue
            
            # Process regular query
            result = await pipeline.query(query)
            print(f"\n[ANSWER] {result['answer']}")
            print(f"[SOURCES] Sources used: {result['sources']}")
            
            if 'pages_referenced' in result and result['pages_referenced']:
                pages_str = ', '.join(map(str, result['pages_referenced']))
                print(f"[PAGES] Referenced pages: {pages_str}")
            
            # Show adaptive information if available
            if 'strategy' in result:
                strategy = result['strategy']
                analysis = result['analysis']
                print(f"[ADAPTIVE] Query type: {analysis['query_type']}, "
                     f"Complexity: {analysis['complexity']}")
                print(f"[STRATEGY] Used: {strategy['type']}, "
                     f"Multi-hop: {strategy['used_multi_hop']}, "
                     f"Synthesis: {strategy['used_synthesis']}")
                if 'confidence' in result:
                    print(f"[CONFIDENCE] {result['confidence']:.2f} - {result.get('confidence_reasoning', '')}")
            
            # Show source documents
            if result['sources'] > 0:
                print("\n[DOCUMENTS] Source documents:")
                for i, doc in enumerate(result['documents'][:3], 1):
                    print(f"{i}. Page {doc['page_number']} of {doc['filename']} - {doc['title'][:50]}...")
        
        except KeyboardInterrupt:
            print("\n[EXIT] Goodbye!")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """
    Main entry point with comprehensive command-line interface
    Supports all major operations: setup, processing, querying, and analysis
    """
    parser = argparse.ArgumentParser(
        description="Enhanced Page-by-Page PDF RAG Pipeline with Complete Content Storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --setup                              # Setup enhanced database
  python main.py document.pdf                         # Process PDF page-by-page
  python main.py documents/                           # Process all PDFs with page extraction
  python main.py --query "What's on page 5?"          # Query with page awareness
  python main.py document.pdf --query "What is this?" # Process and query with pages
  python main.py --interactive                        # Enhanced interactive mode
  python main.py --page-summary 1                     # Show page summary for document 1
        """
    )
    
    # Define command-line arguments
    parser.add_argument('path', nargs='?', help='PDF file or directory to process')
    parser.add_argument('--query', '-q', help='Query the documents')
    parser.add_argument('--interactive', '-i', action='store_true', help='Enhanced interactive mode')
    parser.add_argument('--setup', action='store_true', help='Setup enhanced database')
    parser.add_argument('--stats', action='store_true', help='Show enhanced database statistics')
    parser.add_argument('--force', '-f', action='store_true', help='Force reprocessing')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Number of results to return')
    parser.add_argument('--create-env', action='store_true', help='Create enhanced .env file template')
    parser.add_argument('--adaptive-off', action='store_true', help='Disable adaptive RAG for this session')
    parser.add_argument('--page-summary', type=int, help='Show page summary for document ID')
    parser.add_argument('--page-content', nargs=2, type=int, metavar=('DOC_ID', 'PAGE_NUM'), 
                       help='Show content for specific page')
    
    args = parser.parse_args()
    
    # Handle environment file creation
    if args.create_env:
        create_env_file()
        return 0
    
    # Check for environment file
    if not Path('.env').exists():
        print("[WARNING] No .env file found. Creating enhanced template...")
        create_env_file()
        print("Please edit .env with your API keys and run again.")
        return 1
    
    # Override adaptive setting if requested
    if args.adaptive_off:
        config.adaptive_enabled = False
        logger.info("[CONFIG] Adaptive RAG disabled for this session")
    
    try:
        # Initialize the pipeline
        pipeline = EnhancedRAGPipeline()
        
        # Handle database setup
        if args.setup:
            print("[SETUP] Setting up enhanced database with page storage...")
            pipeline.setup_database()
            print("[SUCCESS] Enhanced database setup complete!")
            return 0
        
        # Handle statistics display
        if args.stats:
            stats = pipeline.get_stats()
            print(f"\n[STATS] Enhanced Database Statistics:")
            
            print(f"\n Documents:")
            print(f"  Total: {stats['documents']['total']}")
            print(f"  Completed: {stats['documents']['completed']}")
            print(f"  Processing: {stats['documents']['processing']}")
            print(f"  Failed: {stats['documents']['failed']}")
            print(f"  Total words: {stats['documents']['total_words']:,}")
            print(f"  Total size: {stats['documents']['total_size_mb']} MB")
            print(f"  Avg words/doc: {stats['documents']['avg_words_per_doc']}")
            
            print(f"\n Pages:")
            print(f"  Total pages: {stats['pages']['total_pages']}")
            print(f"  Total words: {stats['pages']['total_words']:,}")
            print(f"  Avg words/page: {stats['pages']['avg_words_per_page']}")
            
            print(f"\n Chunks:")
            print(f"  Total chunks: {stats['chunks']['total_chunks']}")
            print(f"  Categories: {stats['chunks']['categories']}")
            print(f"  Technical levels: {stats['chunks']['technical_levels']}")
            
            print(f"\n Quality Distribution: {stats['quality_distribution']}")
            print(f"\n Adaptive RAG: {'Enabled' if config.adaptive_enabled else 'Disabled'}")
            return 0
        
        # Handle page summary display
        if args.page_summary:
            summary = pipeline.get_document_summary(args.page_summary)
            if summary:
                print(f"\n[PAGE SUMMARY] {summary['filename']}:")
                print(f"Pages with content: {summary['pages_with_content']}/{summary['total_pages']}")
                print(f"Total words: {summary['total_words']:,}")
                print(f"Content quality: {summary['content_quality']}")
                print(f"Categories: {summary['categories']}")
                print("\nPage details:")
                for page_info in summary['pages_summary']:
                    features = []
                    if page_info['has_tables']: features.append("tables")
                    if page_info['has_code']: features.append("code")
                    if page_info['has_lists']: features.append("lists")
                    if page_info['has_headings']: features.append("headings")
                    feature_str = f" ({', '.join(features)})" if features else ""
                    print(f"  Page {page_info['page']}: {page_info['words']} words{feature_str}")
            else:
                print(f"[ERROR] Document {args.page_summary} not found")
            return 0
        
        # Handle specific page content display
        if args.page_content:
            doc_id, page_num = args.page_content
            pages = pipeline.get_page_content(doc_id, page_num)
            if pages:
                page = pages[0]
                print(f"\n[PAGE CONTENT] Page {page_num} of {page['filename']}:")
                print(f"Word count: {page['word_count']}")
                print(f"Metadata: {page['metadata']}")
                print(f"\nContent:\n{page['content']}")
            else:
                print(f"[ERROR] Page {page_num} not found in document {doc_id}")
            return 0
        
        # Handle interactive mode
        if args.interactive:
            await interactive_mode(pipeline)
            return 0
        
        # Handle query-only mode (no document processing)
        if args.query and not args.path:
            result = await pipeline.query(args.query)
            print(f"\n[ANSWER] {result['answer']}")
            print(f"[SOURCES] Sources: {result['sources']}")
            
            # Display page references if available
            if 'pages_referenced' in result and result['pages_referenced']:
                pages_str = ', '.join(map(str, result['pages_referenced']))
                print(f"[PAGES] Referenced pages: {pages_str}")
            
            # Display adaptive strategy information if available
            if 'strategy' in result:
                print(f"[ADAPTIVE] Strategy: {result['strategy']['type']}")
                print(f"[CONFIDENCE] {result.get('confidence', 0):.2f}")
            
            return 0
        
        # Handle document processing
        if args.path:
            path = Path(args.path)
            
            if path.is_file() and path.suffix.lower() == '.pdf':
                # Process single PDF file
                result = await pipeline.process_document(str(path), args.force)
                print(f"\n[RESULT] Result: {result['status']}")
                if result['status'] == 'completed':
                    print(f"[SUCCESS] Processed {result['file']}")
                    print(f"  Pages: {result['pages_processed']}")
                    print(f"  Chunks: {result['chunks_created']}")
                    print(f"  Words: {result['total_words']:,}")
                    print(f"  Quality: {result['content_quality']}")
                    print(f"  Categories: {', '.join(result['categories'])}")
                elif result['status'] == 'failed':
                    print(f"[ERROR] Failed to process {result['file']}: {result['error']}")
                elif result['status'] == 'skipped':
                    print(f"[SKIP] Skipped {result['file']}: {result['reason']}")
                
            elif path.is_dir():
                # Process entire directory
                result = await pipeline.process_directory(str(path), args.force)
                print(f"\n[RESULT] Processed {result['processed']}/{result['total_documents']} documents")
                if result['failed'] > 0:
                    print(f"[WARNING] {result['failed']} documents failed processing")
                if result['skipped'] > 0:
                    print(f"[INFO] {result['skipped']} documents were skipped (already processed)")
                
            else:
                print(f"[ERROR] Invalid path or not a PDF: {path}")
                return 1
            
            # Handle optional query after processing
            if args.query:
                print(f"\n[QUERY] Querying: {args.query}")
                query_result = await pipeline.query(args.query)
                print(f"[ANSWER] {query_result['answer']}")
                print(f"[SOURCES] Sources: {query_result['sources']}")
                
                # Display page references
                if 'pages_referenced' in query_result and query_result['pages_referenced']:
                    pages_str = ', '.join(map(str, query_result['pages_referenced']))
                    print(f"[PAGES] Referenced pages: {pages_str}")
                
                # Display adaptive information
                if 'strategy' in query_result:
                    print(f"[ADAPTIVE] Strategy: {query_result['strategy']['type']}")
                    print(f"[CONFIDENCE] {query_result.get('confidence', 0):.2f}")
        
        else:
            # No arguments provided - show help and status
            parser.print_help()
            
            # Check for existing documents
            docs_dir = Path('documents')
            if docs_dir.exists():
                pdf_files = list(docs_dir.glob('*.pdf'))
                if pdf_files:
                    print(f"\n[INFO] Found {len(pdf_files)} PDF files in documents/ directory")
                    print("You can process them with page extraction using: python main.py documents/")
            
            # Show current configuration status
            adaptive_status = "Enabled" if config.adaptive_enabled else "Disabled"
            print(f"\n[ENHANCED RAG] Page-by-Page Processing: Enabled")
            print(f"[ADAPTIVE RAG] Status: {adaptive_status}")
            
            return 0
    
    except Exception as e:
        logger.error(f"[ERROR] Fatal error: {e}")
        return 1

# =============================================================================
# SCRIPT ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    """
    Script entry point
    
    USAGE PATTERNS:
    1. Setup: python main.py --setup
    2. Process single file: python main.py document.pdf
    3. Process directory: python main.py documents/
    4. Query: python main.py --query "your question"
    5. Interactive: python main.py --interactive
    6. Statistics: python main.py --stats
    7. Page analysis: python main.py --page-summary 1
    
    FEATURES:
    - Page-by-page PDF processing with advanced cleaning
    - AI-powered content analysis and categorization
    - Intelligent chunking for optimal retrieval
    - Adaptive RAG strategies based on query analysis
    - Comprehensive database storage with vector search
    - Interactive exploration and analysis tools
    """
    exit_code = asyncio.run(main())
    sys.exit(exit_code)