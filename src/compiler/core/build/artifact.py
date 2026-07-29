"""
Build artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class ArtifactType(Enum):
    """Build artifact types."""

    TOKENS = "tokens"
    AST = "ast"
    IR = "ir"
    BYTECODE = "bytecode"
    OBJECT = "object"
    BINARY = "binary"
    LIBRARY = "library"
    CACHE = "cache"
    DEBUG_INFO = "debug_info"


@dataclass(frozen=True)
class BuildArtifact:
    """
    Build artifact.

    Represents an output artifact from a build task.
    """

    name: str
    artifact_type: ArtifactType
    path: Path
    source: Path | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self) -> None:
        """Initialize metadata if None."""
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})

    @property
    def exists(self) -> bool:
        """Check if artifact exists."""
        return self.path.exists()

    @property
    def size(self) -> int:
        """Get artifact size in bytes."""
        if self.exists:
            return self.path.stat().st_size
        return 0

    @property
    def extension(self) -> str:
        """Get artifact file extension."""
        return self.path.suffix

    def is_newer_than(self, other: BuildArtifact) -> bool:
        """
        Check if this artifact is newer than another.

        Args:
            other: Other artifact to compare

        Returns:
            True if this artifact is newer
        """
        if not self.exists:
            return False
        if not other.exists:
            return True

        return self.path.stat().st_mtime > other.path.stat().st_mtime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.artifact_type.value,
            "path": str(self.path),
            "source": str(self.source) if self.source else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BuildArtifact:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            artifact_type=ArtifactType(data["type"]),
            path=Path(data["path"]),
            source=Path(data["source"]) if data.get("source") else None,
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"BuildArtifact(name={self.name}, type={self.artifact_type.value})"

    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((self.name, self.artifact_type, self.path))


@dataclass
class ArtifactManifest:
    """
    Manifest of build artifacts.

    Tracks all artifacts produced by a build.
    """

    artifacts: dict[str, BuildArtifact] = None

    def __post_init__(self) -> None:
        """Initialize artifacts if None."""
        if self.artifacts is None:
            object.__setattr__(self, "artifacts", {})

    def add(self, artifact: BuildArtifact) -> None:
        """
        Add artifact to manifest.

        Args:
            artifact: Artifact to add
        """
        self.artifacts[artifact.name] = artifact

    def get(self, name: str) -> BuildArtifact | None:
        """
        Get artifact by name.

        Args:
            name: Artifact name

        Returns:
            Artifact if found, None otherwise
        """
        return self.artifacts.get(name)

    def remove(self, name: str) -> bool:
        """
        Remove artifact from manifest.

        Args:
            name: Artifact name

        Returns:
            True if artifact was removed
        """
        if name in self.artifacts:
            del self.artifacts[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all artifacts."""
        self.artifacts.clear()

    @property
    def count(self) -> int:
        """Number of artifacts."""
        return len(self.artifacts)

    @property
    def total_size(self) -> int:
        """Total size of all artifacts in bytes."""
        return sum(a.size for a in self.artifacts.values())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifacts": {
                name: artifact.to_dict()
                for name, artifact in self.artifacts.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtifactManifest:
        """Create from dictionary."""
        return cls(
            artifacts={
                name: BuildArtifact.from_dict(artifact)
                for name, artifact in data.get("artifacts", {}).items()
            }
        )
