import logging
import json
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import PDFPlumberLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import requests

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]


class DataIngestionService:
    """Service for ingesting data from multiple sources (PDFs, Web links, JSON logs)."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else BASE_DIR / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    def ingest_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Load and chunk a PDF file."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            logger.error("PDF file not found: %s", pdf_path)
            return []
        
        try:
            logger.info("Loading PDF: %s", pdf_path)
            loader = PDFPlumberLoader(str(pdf_path))
            docs = loader.load()
            
            chunks = []
            for doc in docs:
                text = doc.page_content
                split_texts = self.splitter.split_text(text)
                
                for idx, chunk_text in enumerate(split_texts):
                    chunk_id = self._generate_chunk_id(str(pdf_path), idx)
                    chunks.append({
                        "chunk_id": chunk_id,
                        "source": str(pdf_path),
                        "source_type": "pdf",
                        "content": chunk_text,
                        "metadata": {
                            "filename": pdf_path.name,
                            "page": doc.metadata.get("page", 0),
                            "chunk_index": idx,
                            "ingested_at": datetime.now().isoformat()
                        }
                    })
            
            logger.info("Ingested %d chunks from PDF %s", len(chunks), pdf_path.name)
            return chunks
        except Exception as e:
            logger.error("Error loading PDF %s: %s", pdf_path, e)
            return []

    def ingest_web_link(self, url: str) -> List[Dict[str, Any]]:
        """Fetch and chunk content from a web link."""
        try:
            logger.info("Fetching web content from: %s", url)
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            content = response.text
            split_texts = self.splitter.split_text(content)
            
            chunks = []
            for idx, chunk_text in enumerate(split_texts):
                chunk_id = self._generate_chunk_id(url, idx)
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": url,
                    "source_type": "web",
                    "content": chunk_text,
                    "metadata": {
                        "url": url,
                        "chunk_index": idx,
                        "ingested_at": datetime.now().isoformat(),
                        "status_code": response.status_code
                    }
                })
            
            logger.info("Ingested %d chunks from web link %s", len(chunks), url)
            return chunks
        except Exception as e:
            logger.error("Error fetching web link %s: %s", url, e)
            return []

    def ingest_json_logs(self, json_path: str) -> List[Dict[str, Any]]:
        """Load and process JSON logs."""
        json_path = Path(json_path)
        if not json_path.exists():
            logger.error("JSON file not found: %s", json_path)
            return []
        
        try:
            logger.info("Loading JSON logs: %s", json_path)
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chunks = []
            
            # Handle both list and dict JSON
            items = data if isinstance(data, list) else [data]
            
            for idx, item in enumerate(items):
                item_text = json.dumps(item, indent=2)
                split_texts = self.splitter.split_text(item_text)
                
                for chunk_idx, chunk_text in enumerate(split_texts):
                    chunk_id = self._generate_chunk_id(str(json_path), idx * 1000 + chunk_idx)
                    chunks.append({
                        "chunk_id": chunk_id,
                        "source": str(json_path),
                        "source_type": "json",
                        "content": chunk_text,
                        "metadata": {
                            "filename": json_path.name,
                            "item_index": idx,
                            "chunk_index": chunk_idx,
                            "ingested_at": datetime.now().isoformat()
                        }
                    })
            
            logger.info("Ingested %d chunks from JSON %s", len(chunks), json_path.name)
            return chunks
        except Exception as e:
            logger.error("Error loading JSON %s: %s", json_path, e)
            return []

    def ingest_text_file(self, text_path: str) -> List[Dict[str, Any]]:
        """Load and chunk a plain text file."""
        text_path = Path(text_path)
        if not text_path.exists():
            logger.error("Text file not found: %s", text_path)
            return []
        
        try:
            logger.info("Loading text file: %s", text_path)
            with open(text_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            split_texts = self.splitter.split_text(content)
            
            chunks = []
            for idx, chunk_text in enumerate(split_texts):
                chunk_id = self._generate_chunk_id(str(text_path), idx)
                chunks.append({
                    "chunk_id": chunk_id,
                    "source": str(text_path),
                    "source_type": "text",
                    "content": chunk_text,
                    "metadata": {
                        "filename": text_path.name,
                        "chunk_index": idx,
                        "ingested_at": datetime.now().isoformat()
                    }
                })
            
            logger.info("Ingested %d chunks from text file %s", len(chunks), text_path.name)
            return chunks
        except Exception as e:
            logger.error("Error loading text file %s: %s", text_path, e)
            return []

    def _generate_chunk_id(self, source: str, index: int) -> str:
        """Generate a unique chunk ID."""
        combined = f"{source}_{index}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
