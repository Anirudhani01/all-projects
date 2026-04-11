import subprocess
import logging
import sys
from typing import Dict, Any, Optional
from components.parser.parser import BaseParser, DocxParser

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
        self.logger.info('[RAG] Querying knowledge base for context...')
        try:
            import pathlib
            project_root = pathlib.Path(__file__).resolve().parent.parent

            new_rag = None
            for candidate in [project_root / "rag" / "main.py", project_root / "adaptive_rag" / "main.py"]:
                if candidate.exists():
                    new_rag = candidate
                    break
    
            # Run as module to handle relative imports correctly
            if "adaptive_rag" in str(new_rag):
                cmd = [sys.executable, "-m", "components.adaptive_rag.main", "--query", plain_text]
            else:
                cmd = [sys.executable, str(new_rag), "--query", plain_text]
            self.logger.info("[RAG] Using adaptive RAG pipeline: %s", new_rag)


            # Set working directory to project root for module execution
            working_dir = project_root.parent if "adaptive_rag" in str(new_rag) else None
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=working_dir
            )
            if result.returncode != 0:
                self.logger.error("[RAG] RAG script error: %s", result.stderr)
                return "[ANSWER] RAG failed.\n[SOURCES] 0\n[PAGES] None"
            
            rag_output = result.stdout.strip()
            self.logger.info(f"[RAG] Retrieved {len(rag_output)} characters of context")
            self.logger.debug(f"[RAG] Retrieved chunks:\n{rag_output}")
            return rag_output
        except Exception as e:
            self.logger.exception("[RAG] RAG fetch error")
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
            self.logger.info("[RAG] Retrieved information from knowledge base")
            # Detailed logging moved to fetch_rag_chunks method
            return rag_context
        except Exception as e:
            self.logger.exception("[RAG] Context retrieval failed")
            return "[ANSWER] Context retrieval failed.\n[SOURCES] 0\n[PAGES] None"
