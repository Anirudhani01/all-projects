import os
import logging
from dotenv import load_dotenv
from .retriever import RetrieverNode
from .utils import ensure_event_loop_compatibility


def configure_logger(log_file_name: str = "adaptive_rag_pipeline.log") -> logging.Logger:
    """
    Configure and return a logger for AdaptiveRAGPipelineWithState and its components.

    Args:
        log_file_name (str): Name of the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("AdaptiveRAGPipelineWithState")
    logger.setLevel(logging.DEBUG)  # Enable DEBUG level logging for fine-grained details

    # Prevent duplicate logs by disabling propagation to the root logger
    logger.propagate = False

    # Check if handlers are already attached to avoid duplicate logs
    if not logger.handlers:
        # Console Handler: For top-level updates (INFO level only)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)

        # File Handler: For detailed logs (DEBUG level)
        file_handler = logging.FileHandler(log_file_name, mode="a")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


# Initialize the shared logger
logger = configure_logger()


class AdaptiveRAGPipelineWithState:
    """
    Simplified Adaptive RAG Pipeline that performs only document retrieval.
    """

    def __init__(self, query: str, user_type: str = "customer"):
        logger.info("Initializing AdaptiveRAGPipelineWithState...")
        load_dotenv()
        ensure_event_loop_compatibility()

        self.state = {
            "query": query,
            "user_type": user_type,
            "retrieved_docs": [],
            "status": "initialized",
            "error": None
        }

        self.db_connection_string = os.getenv("DATABASE_URL")
        self.table_name = os.getenv("PGVECTOR_TABLE", "chunks")
        self.metadata_column = os.getenv("METADATA_COLUMN", "chunk_metadata")

        if not self.db_connection_string:
            logger.error("DATABASE_URL not found in environment variables.")
            raise ValueError("DATABASE_URL not found in environment variables.")

        logger.info("Initializing RetrieverNode...")
        self.retriever = RetrieverNode(
            db_connection_string=self.db_connection_string,
            table_name=self.table_name,
            metadata_column=self.metadata_column
        )
        logger.info("AdaptiveRAGPipelineWithState initialized successfully.")

    def step_retrieve(self):
        """
        Step to retrieve documents using the RetrieverNode.
        """
        logger.info("Step: Retrieving documents...")
        try:
            retrieve_k = 30
            self.state["retrieve_k"] = retrieve_k
            logger.debug(f"Retrieving with query: '{self.state['query']}', user_type: '{self.state['user_type']}', retrieve_k: {retrieve_k}")

            docs = self.retriever.retrieve_adaptive(
                query=self.state["query"],
                user_type=self.state["user_type"].lower(),
                retrieve_k=retrieve_k
            )

            if not docs:
                raise RuntimeError("No documents retrieved.")

            self.state["retrieved_docs"] = docs
            self.state["status"] = "success"
            logger.info(f"Successfully retrieved {len(docs)} documents.")
            logger.debug(f"Retrieved documents: {docs}")

        except Exception as e:
            self.state["error"] = f"Retriever failed: {e}"
            self.state["status"] = "failed"
            logger.error(f"Document retrieval failed: {e}")
            raise

    def run(self):
        """
        Run the Adaptive RAG Pipeline.
        """
        logger.info("Starting Adaptive RAG Pipeline (Retrieve Only)...")
        try:
            self.step_retrieve()
        except Exception as e:
            logger.error(f"Pipeline failed at status: {self.state['status'].upper()} | Reason: {self.state['error']}")
            return []

        logger.info("Pipeline completed successfully.")
        logger.debug(f"Retrieved documents: {self.state['retrieved_docs']}")

        # Optionally log the document summaries
        # for i, doc in enumerate(self.state["retrieved_docs"], 1):
        #     logger.info(f"[{i}] {doc.page_content[:200]}...")

        return self.state["retrieved_docs"]


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Adaptive RAG Pipeline")
    parser.add_argument("--query", type=str, required=True, help="Query string for RAG retrieval")
    parser.add_argument("--user-type", type=str, default="customer", help="User type for adaptive retrieval")
    
    args = parser.parse_args()
    
    logger.info("Executing AdaptiveRAGPipelineWithState as main...")
    pipeline = AdaptiveRAGPipelineWithState(
        query=args.query, user_type=args.user_type
    )
    chunks = pipeline.run()
    
    # Format output for the RAG service
    if chunks:
        # Convert document objects to text format expected by RAG service
        answer_parts = []
        sources_count = len(chunks)
        
        for i, doc in enumerate(chunks):
            # Extract page content and metadata
            content = doc.page_content if hasattr(doc, 'page_content') else str(doc)
            answer_parts.append(f"Document {i+1}: {content}")
        
        answer_text = "\n\n".join(answer_parts)
        
        # Format output as expected by RAG service
        print(f"[ANSWER] {answer_text}")
        print(f"[SOURCES] {sources_count}")
        print(f"[PAGES] Multiple pages retrieved")
    else:
        print("[ANSWER] No relevant context found.")
        print("[SOURCES] 0")
        print("[PAGES] None")