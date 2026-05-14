import logging
import json
from pathlib import Path
from typing import Any, Optional

try:
    from diskcache import Cache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = BASE_DIR / "cache"


class CacheManager:
    """Caching layer using DiskCache to avoid redundant LLM calls."""

    def __init__(self, cache_dir: Optional[str] = None):
        if cache_dir is None:
            cache_dir = str(CACHE_DIR)
        else:
            cache_dir = str(cache_dir)

        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        if DISKCACHE_AVAILABLE:
            self.cache = Cache(cache_dir)
            self.use_diskcache = True
            logger.info("Initialized DiskCache at %s", cache_dir)
        else:
            self.cache_dir = Path(cache_dir)
            self.cache = {}
            self.use_diskcache = False
            logger.warning("DiskCache not available; using in-memory dict. Consider installing diskcache.")

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache."""
        try:
            if self.use_diskcache:
                value = self.cache.get(key)
            else:
                value = self.cache.get(key)
            
            if value is not None:
                logger.debug("Cache HIT for key: %s", key)
            return value
        except Exception as e:
            logger.warning("Cache retrieval error for key %s: %s", key, e)
            return None

    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Store value in cache with optional expiration (seconds)."""
        try:
            if self.use_diskcache:
                if expire:
                    self.cache.set(key, value, expire=expire)
                else:
                    self.cache[key] = value
            else:
                self.cache[key] = value
            
            logger.debug("Cache SET for key: %s", key)
            return True
        except Exception as e:
            logger.warning("Cache set error for key %s: %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            if self.use_diskcache or key in self.cache:
                del self.cache[key]
            logger.debug("Cache DELETE for key: %s", key)
            return True
        except Exception as e:
            logger.warning("Cache delete error for key %s: %s", key, e)
            return False

    def clear(self) -> bool:
        """Clear all cache."""
        try:
            if self.use_diskcache:
                self.cache.clear()
            else:
                self.cache.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.warning("Cache clear error: %s", e)
            return False

    def close(self) -> None:
        """Close cache connection."""
        try:
            if self.use_diskcache:
                self.cache.close()
            logger.info("Cache connection closed")
        except Exception as e:
            logger.warning("Cache close error: %s", e)


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get or initialize the global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
