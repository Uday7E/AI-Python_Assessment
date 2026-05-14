import os
from pathlib import Path
from typing import Any, Dict, List
import logging

from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from supabase import create_client

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data"
VECTOR_DB_PATH = BASE_DIR / "vectordb"
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "Files")
SUPABASE_PREFIX = os.getenv("SUPABASE_STORAGE_PREFIX", "")
LOCAL_DOCUMENTS_PATH = Path(os.getenv("LOCAL_DOCUMENTS_PATH", str(DATA_PATH)))
if not LOCAL_DOCUMENTS_PATH.is_absolute():
    LOCAL_DOCUMENTS_PATH = (BASE_DIR / LOCAL_DOCUMENTS_PATH).resolve()

SUPABASE_TABLE = os.getenv("SUPABASE_TABLE_NAME", "rag_final_outputs")


def get_supabase_client() -> Any:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("Supabase credentials must be set in .env")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def sync_local_documents_to_storage() -> None:
    client = get_supabase_client()
    bucket = client.storage.from_(SUPABASE_BUCKET)
    for path in DATA_PATH.glob("*.txt"):
        bucket.upload(path.name, path.read_bytes())


def copy_local_documents_to_data() -> List[Path]:
    if LOCAL_DOCUMENTS_PATH == DATA_PATH:
        logger.info("Using local data folder at %s", DATA_PATH)
        return [path for path in DATA_PATH.glob("*.txt") if path.is_file()]

    if not LOCAL_DOCUMENTS_PATH.exists():
        logger.warning("Local documents path does not exist: %s", LOCAL_DOCUMENTS_PATH)
        return []

    local_files = [path for path in LOCAL_DOCUMENTS_PATH.glob("*.txt") if path.is_file()]
    if not local_files:
        logger.warning("No local '.txt' files found at %s", LOCAL_DOCUMENTS_PATH)
        return []

    DATA_PATH.mkdir(parents=True, exist_ok=True)
    copied_files: List[Path] = []
    for source_path in local_files:
        target_path = DATA_PATH / source_path.name
        if source_path.resolve() != target_path.resolve():
            target_path.write_bytes(source_path.read_bytes())
        copied_files.append(target_path)
    logger.info("Copied %d local document(s) from %s to %s", len(copied_files), LOCAL_DOCUMENTS_PATH, DATA_PATH)
    return copied_files


def download_bucket_documents() -> None:
    logger.info("Starting download of documents from Supabase bucket '%s'", SUPABASE_BUCKET)
    client = get_supabase_client()
    bucket = client.storage.from_(SUPABASE_BUCKET)

    items = []
    try:
        items = bucket.list()
    except Exception as exc:
        logger.warning("Unable to list Supabase bucket '%s': %s", SUPABASE_BUCKET, exc)

    if not items and SUPABASE_PREFIX:
        logger.info("Trying Supabase bucket list with prefix '%s'", SUPABASE_PREFIX)
        try:
            items = bucket.list(path=SUPABASE_PREFIX)
        except Exception as exc:
            logger.warning("Unable to list Supabase bucket '%s' with prefix '%s': %s", SUPABASE_BUCKET, SUPABASE_PREFIX, exc)

    if not items:
        logger.warning("No files found in Supabase bucket '%s'; falling back to local documents at %s", SUPABASE_BUCKET, LOCAL_DOCUMENTS_PATH)
        copy_local_documents_to_data()
        return

    DATA_PATH.mkdir(parents=True, exist_ok=True)
    downloaded_files = []
    for item in items:
        name = item.get("name") if isinstance(item, dict) else getattr(item, "name", None)
        if name and name.lower().endswith(".txt"):
            response = bucket.download(name)
            target_path = DATA_PATH / name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(response, (bytes, bytearray)):
                target_path.write_bytes(response)
            else:
                target_path.write_bytes(response.read())
            downloaded_files.append(name)

    if not downloaded_files:
        logger.warning("No .txt files downloaded from Supabase; falling back to local documents at %s", LOCAL_DOCUMENTS_PATH)
        copy_local_documents_to_data()
        return

    logger.info("Downloaded %d documents: %s", len(downloaded_files), downloaded_files)


def load_documents() -> List[Any]:
    logger.info("Loading documents from local path: %s", DATA_PATH)
    loader = DirectoryLoader(str(DATA_PATH), glob="*.txt")
    docs = loader.load()
    logger.info("Loaded %d documents", len(docs))
    return docs


def split_documents(documents: List[Any]) -> List[Any]:
    logger.info("Splitting documents into chunks")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    logger.info("Created %d chunks from documents", len(chunks))
    return chunks


def create_vector_store(chunks: List[Any]) -> Any:
    logger.info("Creating vector store with embeddings")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_store = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=str(VECTOR_DB_PATH)
    )
    vector_store.persist()
    logger.info("Vector store created and persisted")
    return vector_store


def load_vector_store() -> Any:
    logger.info("Loading existing vector store")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(persist_directory=str(VECTOR_DB_PATH), embedding_function=embeddings)


def retrieve_documents(query: str, k: int = 3) -> List[Any]:
    logger.info("Retrieving %d documents for query: '%s'", k, query)
    vector_store = load_vector_store()
    docs = vector_store.similarity_search(query, k=k)
    logger.info("Retrieved %d relevant chunks", len(docs))
    return docs


def save_result(record: Dict[str, Any]) -> Any:
    logger.info("Saving result to Supabase table '%s'", SUPABASE_TABLE)
    client = get_supabase_client()
    result = client.table(SUPABASE_TABLE).insert(record).execute()
    logger.info("Result saved successfully")
    return result


if __name__ == "__main__":
    docs = load_documents()
    chunks = split_documents(docs)
    create_vector_store(chunks)
    print(f"Loaded {len(docs)} documents")
    print(f"Created {len(chunks)} chunks")
