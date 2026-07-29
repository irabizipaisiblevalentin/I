"""
Build caching system.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .errors import CacheError


@dataclass
class CacheEntry:
    """Single cache entry."""
    
    key: str
    outputs: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CacheEntry:
        """Create from dictionary."""
        return cls(
            key=data["key"],
            outputs=data["outputs"],
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", 0.0),
        )


class BuildCache:
    """
    Build artifact cache.
    
    Caches build artifacts to enable incremental builds.
    """
    
    # Cache file name
    CACHE_FILE = "build-cache.json"
    
    def __init__(self, cache_dir: Path) -> None:
        """
        Initialize build cache.
        
        Args:
            cache_dir: Directory to store cache
        """
        self._cache_dir = cache_dir
        self._cache_file = cache_dir / self.CACHE_FILE
        self._entries: Dict[str, CacheEntry] = {}
        self._loaded = False
    
    @property
    def cache_dir(self) -> Path:
        """Cache directory."""
        return self._cache_dir
    
    def load(self) -> None:
        """Load cache from disk."""
        if self._loaded:
            return
        
        if self._cache_file.exists():
            try:
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                self._entries = {
                    key: CacheEntry.from_dict(entry)
                    for key, entry in data.get("entries", {}).items()
                }
            except (json.JSONDecodeError, KeyError) as e:
                raise CacheError(f"Failed to load cache: {e}", self._cache_file)
        
        self._loaded = True
    
    def save(self) -> None:
        """Save cache to disk."""
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        data = {
            "version": 1,
            "entries": {
                key: entry.to_dict()
                for key, entry in self._entries.items()
            }
        }
        
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            raise CacheError(f"Failed to save cache: {e}", self._cache_file)
    
    def get(self, key: str) -> Optional[CacheEntry]:
        """
        Get cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            Cache entry if found, None otherwise
        """
        self.load()
        return self._entries.get(key)
    
    def put(self, entry: CacheEntry) -> None:
        """
        Store cache entry.
        
        Args:
            entry: Cache entry to store
        """
        self.load()
        self._entries[entry.key] = entry
    
    def has(self, key: str) -> bool:
        """
        Check if cache entry exists.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry exists
        """
        self.load()
        return key in self._entries
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if entry was invalidated
        """
        self.load()
        if key in self._entries:
            del self._entries[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._entries.clear()
    
    def is_valid(self, key: str, inputs: List[Path]) -> bool:
        """
        Check if cache entry is valid.
        
        Args:
            key: Cache key
            inputs: Input files
            
        Returns:
            True if cache is valid
        """
        entry = self.get(key)
        if entry is None:
            return False
        
        # Check if all inputs exist and are newer than cache
        import time
        
        for input_path in inputs:
            if not input_path.exists():
                return False
            
            # Check if input is newer than cache
            input_mtime = input_path.stat().st_mtime
            if input_mtime > entry.timestamp:
                return False
        
        return True
    
    @staticmethod
    def compute_key(task_type: str, inputs: List[Path], config_hash: str = "") -> str:
        """
        Compute cache key.
        
        Args:
            task_type: Type of task
            inputs: Input files
            config_hash: Optional configuration hash
            
        Returns:
            Cache key string
        """
        import time
        
        key_parts = [task_type, config_hash]
        
        for input_path in sorted(inputs):
            if input_path.exists():
                # Include file content hash
                content_hash = BuildCache._file_hash(input_path)
                key_parts.append(f"{input_path}:{content_hash}")
            else:
                key_parts.append(f"{input_path}:missing")
        
        return hashlib.sha256("|".join(key_parts).encode()).hexdigest()
    
    @staticmethod
    def _file_hash(path: Path) -> str:
        """Compute file content hash."""
        h = hashlib.sha256()
        
        with open(path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        
        return h.hexdigest()
