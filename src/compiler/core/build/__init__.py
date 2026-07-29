"""
Build System

Manages the compilation pipeline for I projects.
"""

from .pipeline import BuildPipeline
from .task import BuildTask, TaskType, TaskResult
from .scheduler import TaskScheduler
from .cache import BuildCache
from .profile import BuildProfile
from .artifact import BuildArtifact, ArtifactType
from .errors import (
    BuildError,
    TaskError,
    CacheError,
    BuildTimeoutError,
    BuildMemoryError,
)

__all__ = [
    # Main classes
    "BuildPipeline",
    "BuildTask",
    "TaskType",
    "TaskResult",
    "TaskScheduler",
    "BuildCache",
    "BuildProfile",
    "BuildArtifact",
    "ArtifactType",
    
    # Errors
    "BuildError",
    "TaskError",
    "CacheError",
    "BuildTimeoutError",
    "BuildMemoryError",
]
