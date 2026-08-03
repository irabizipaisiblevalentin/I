"""
File manager.

Provides cached file reading and writing.
"""

from __future__ import annotations

from pathlib import Path


class FileManager:
    """
    Manages file I/O with caching.
    """

    def __init__(self, root: Path | None = None) -> None:
        """
        Initialize manager.

        Args:
            root: Root directory for relative paths
        """
        self._root = (root or Path.cwd()).resolve()
        self._cache: dict[Path, str] = {}

    @property
    def root(self) -> Path:
        """Root directory."""
        return self._root

    def read(self, path: Path, encoding: str = "utf-8") -> str:
        """
        Read file content.

        Args:
            path: File path
            encoding: File encoding

        Returns:
            File content
        """
        resolved = self._resolve(path)

        if resolved in self._cache:
            return self._cache[resolved]

        content = resolved.read_text(encoding=encoding)
        self._cache[resolved] = content
        return content

    def write(
        self,
        path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """
        Write file content.

        Args:
            path: File path
            content: File content
            encoding: File encoding
        """
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(content, encoding=encoding)
        self._cache[resolved] = content

    def exists(self, path: Path) -> bool:
        """Check if file exists."""
        return self._resolve(path).exists()

    def clear_cache(self) -> None:
        """Clear file cache."""
        self._cache.clear()

    def _resolve(self, path: Path) -> Path:
        """Resolve path to absolute."""
        if path.is_absolute():
            return path
        return self._root / path
