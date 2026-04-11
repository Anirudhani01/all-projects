import subprocess
import logging
from typing import Dict, Any, Optional
from external.parser import BaseParser, DocxParser

class RAGService:
    """
    A service for Retrieval-Augmented Generation (RAG).

    This service is responsible for extracting text from documents and using it
    to fetch relevant context from a knowledge base via an external script.
    """
    def __init__(self, parser: Optional[BaseParser] = None):
        """Initializes the RAGService.

        Args:
            parser: Concrete parser implementation to use. If None, defaults to
                `DocxParser`.
        """
        self.logger = logging.getLogger(__name__)
        self.parser = parser or DocxParser()
    
    def fetch_rag_chunks(self, plain_text: str) -> str:
        """
        Fetch RAG chunks by running the AdaptiveRag.py script.

        This method takes plain text as input, passes it as a query to the
        AdaptiveRag.py script, and captures the output, which contains the
        retrieved context.

        Args:
            plain_text (str): The text to be used as a query for the RAG script.

        Returns:
            str: The RAG context chunks, or a failure message if an error occurs.
        """
        self.logger.info('[ADAPTIVE RAG] Querying knowledge base for context...')
        try:
            result = subprocess.run(
                ["python", "AdaptiveRag.py", "--query", plain_text],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                self.logger.error("[ADAPTIVE RAG] RAG script error: %s", result.stderr)
                return "[ANSWER] RAG failed.\n[SOURCES] 0\n[PAGES] None"
            return result.stdout.strip()
        except Exception as e:
            self.logger.exception("[ADAPTIVE RAG] RAG fetch error")
            return "[ANSWER] Context fetch failed.\n[SOURCES] 0\n[PAGES] None"
    
    def retrieve_context(self, source_path: str) -> str:
        """
        Retrieve context from a source document.

        This method extracts plain text from a given document, uses this text
        to fetch RAG chunks, and returns the retrieved context.

        Args:
            source_path (str): The file path of the source document.

        Returns:
            str: The retrieved RAG context, or a failure message if an error occurs.
        """
        try:
            plain_text = self.parser.extract_plain_text(source_path)
            rag_context = self.fetch_rag_chunks(plain_text)
            
            self.logger.info("[ADAPTIVE RAG] Retrieved RAG chunks (first 1000 chars):")
            self.logger.info(rag_context[:1000])  # log first 1000 chars
            
            return rag_context
        except Exception as e:
            self.logger.exception("[ADAPTIVE RAG] Context retrieval failed.")
            return "[ANSWER] Context retrieval failed.\n[SOURCES] 0\n[PAGES] None"
