import os
import logging
from dotenv import load_dotenv
from typing import List
from langchain_postgres import PGEngine, PGVectorStore  # Importing PGVectorStore and PGEngine
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import FlashrankRerank
import psycopg
import openai

# Get the logger from the main application (reused logger)
logger = logging.getLogger("AdaptiveRAGPipelineWithState")  # Use the main logger

class RetrieverNode:
    """
    A semantic retriever using PGVectorStore and Flashrank reranker.
    """

    def __init__(
        self,
        db_connection_string: str,
        table_name: str,
        metadata_column: str = "chunk_metadata",
        embedding_model: str = "text-embedding-ada-002"
    ):
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment variables.")
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        self.table_name = table_name
        self.metadata_column = metadata_column

        logger.info("Initializing PGEngine...")
        self.engine = PGEngine.from_connection_string(url=db_connection_string)

        logger.info("Initializing OpenAI Embedding Service...")
        self.embedding_service = OpenAIEmbeddings(
            model=embedding_model, openai_api_key=openai_api_key
        )

        logger.info(f"Creating PGVectorStore for table: {self.table_name}")
        self.vectorstore = PGVectorStore.create_sync(
            engine=self.engine,
            table_name=self.table_name,
            embedding_service=self.embedding_service,
            metadata_json_column=self.metadata_column
        )

        logger.info("Initializing Flashrank Reranker...")
        self.compressor = FlashrankRerank(
            model="ms-marco-MiniLM-L-12-v2", top_n=10
        )

        logger.info("Setting up ContextualCompressionRetriever...")
        self.retriever = ContextualCompressionRetriever(
            base_retriever=self.vectorstore.as_retriever(search_kwargs={"k": 50}),
            base_compressor=self.compressor
        )
        logger.info("RetrieverNode initialized successfully.")

    def retrieve_adaptive(
        self,
        query: str,
        user_type: str,
        retrieve_k: int
    ) -> List[Document]:
        """
        Perform adaptive retrieval with compression and reranking.

        Args:
            query (str): Query text.
            user_type (str): Role or user type for context.
            retrieve_k (int): Number of top documents to return (used for context only).

        Returns:
            List[Document]: List of compressed documents.
        """
        logger.info(f"Starting retrieval for query: '{query}' (User type: {user_type})")
        try:
            docs = self.retriever.invoke(query)
            logger.info(f"Primary retrieval succeeded. Retrieved {len(docs)} documents.")
            return docs
        except (psycopg.OperationalError,
                psycopg.InterfaceError,
                openai.RateLimitError,
                openai.APIError,
                ConnectionError) as e:
            logger.warning(f"Primary retrieval failed: {e}. Retrying fallback...")
            try:
                docs = self.retriever.invoke(query)
                logger.info(f"Fallback retrieval succeeded. Retrieved {len(docs)} documents.")
                return docs
            except Exception as inner_e:
                logger.error(f"Fallback retrieval failed: {inner_e}")
                return []