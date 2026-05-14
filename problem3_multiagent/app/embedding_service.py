import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
import numpy as np

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingService:
    """Service for semantic embeddings and deduplication of content."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model."""
        logger.info("Initializing embedding model: %s", model_name)
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.model_name = model_name

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return []
        
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error("Error embedding text: %s", e)
            return []

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        if not texts:
            logger.warning("Empty text list provided for embedding")
            return []
        
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            logger.error("Error embedding documents: %s", e)
            return []

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def find_duplicates(
        self,
        items: List[Dict[str, Any]],
        text_key: str = "content",
        similarity_threshold: float = 0.85
    ) -> List[List[int]]:
        """
        Identify duplicate or near-duplicate items based on semantic similarity.
        Returns list of groups (each group is list of indices).
        """
        if not items:
            return []
        
        logger.info("Finding duplicates among %d items with threshold %.2f", len(items), similarity_threshold)
        
        # Extract texts and embed
        texts = [item.get(text_key, "") for item in items]
        embeddings = self.embed_documents(texts)
        
        if not embeddings or len(embeddings) != len(texts):
            logger.warning("Failed to embed all items for duplicate detection")
            return []
        
        # Find duplicate groups
        visited = set()
        duplicate_groups = []
        
        for i in range(len(embeddings)):
            if i in visited:
                continue
            
            group = [i]
            for j in range(i + 1, len(embeddings)):
                if j in visited:
                    continue
                
                similarity = self.cosine_similarity(embeddings[i], embeddings[j])
                if similarity >= similarity_threshold:
                    group.append(j)
                    visited.add(j)
            
            visited.add(i)
            if len(group) > 1:
                duplicate_groups.append(group)
        
        logger.info("Found %d duplicate groups", len(duplicate_groups))
        return duplicate_groups

    def merge_duplicates(
        self,
        items: List[Dict[str, Any]],
        duplicate_groups: List[List[int]],
        text_key: str = "content"
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Merge duplicate items and return merged list plus summary of merged items.
        Keeps first item from each group and notes sources.
        """
        if not duplicate_groups:
            return items, []
        
        logger.info("Merging %d duplicate groups", len(duplicate_groups))
        
        merged_indices = set()
        merged_items = []
        
        for group in duplicate_groups:
            primary_idx = group[0]
            primary_item = items[primary_idx].copy()
            
            # Collect sources
            sources = [primary_item.get("source", "unknown")]
            for idx in group[1:]:
                sources.append(items[idx].get("source", "unknown"))
                merged_indices.add(idx)
            
            primary_item["merged_sources"] = sources
            primary_item["original_indices"] = group
            merged_items.append(primary_item)
        
        # Build deduplicated list
        deduplicated = []
        for i, item in enumerate(items):
            if i not in merged_indices:
                deduplicated.append(item)
        
        # Add merged items
        deduplicated.extend(merged_items)
        
        logger.info("Deduplication complete: %d -> %d items", len(items), len(deduplicated))
        return deduplicated, merged_items
