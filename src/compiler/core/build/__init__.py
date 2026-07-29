"""
Build System

Manages the compilation pipeline for I projects.
"""

from .artifact import ArtifactType, BuildArtifact
from .cache import BuildCache, CacheEntry
from .errors import (
    BuildError,
    BuildMemoryError,
    BuildTimeoutError,
    CacheError,
    CircularDependencyError,
    TaskError,
)
from .pipeline import BuildPipeline
from .profile import BuildProfile
from .scheduler import TaskScheduler
from .task import BuildTask, TaskResult, TaskType

__all__ = [
    # Main classes
    "BuildPipeline",
    "BuildTask",
    "TaskType",
    "TaskResult",
    "TaskScheduler",
    "BuildCache",
    "CacheEntry",
    "BuildProfile",
    "BuildArtifact",
    "ArtifactType",

    # Errors
    "BuildError",
    "TaskError",
    "CacheError",
    "BuildTimeoutError",
    "BuildMemoryError",
    "CircularDependencyError",
]
