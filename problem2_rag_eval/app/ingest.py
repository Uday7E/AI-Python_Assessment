import sys
import os
import logging

# Add the parent directory to sys.path to allow imports from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.log_config import configure_global_logger
from app.rag_pipeline import (
    download_bucket_documents,
    load_documents,
    split_documents,
    create_vector_store,
    sync_local_documents_to_storage,
)

# Configure logging to console and shared file
configure_global_logger()

logger = logging.getLogger(__name__)


def build_index() -> None:
    logger.info("Starting document ingestion and indexing process")
    download_bucket_documents()
    docs = load_documents()
    chunks = split_documents(docs)
    create_vector_store(chunks)
    logger.info("Indexed %d chunks from %d documents", len(chunks), len(docs))
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents")


if __name__ == "__main__":
    build_index()
