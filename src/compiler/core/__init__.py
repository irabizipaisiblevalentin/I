"""
Compiler Core

Provides foundational utilities for the I compiler.
"""

from .benchmarks import Benchmark, BenchmarkSuite
from .build import BuildCache, BuildPipeline
from .config import CompilerConfig, ConfigLoader
from .context import CompilerContext
from .diagnostics import Diagnostic, DiagnosticEngine, ErrorCode, Severity
from .docs_generator import DocumentationGenerator
from .errors import CompilerError, ConfigError, FileIOError, IError, InternalError, PanicError, ValidationError
from .features import FeatureFlagManager
from .formatting import MessageFormatter
from .io import FileManager
from .logging import Logger, LogLevel, get_logger
from .memory import Arena, MemoryTracker
from .result import Err, Nothing, Ok, Option, Result, Some
from .source import Position, PositionTracker, SourceFile, Span
from .testing import CompilerTestHelper, GoldenTest, GoldenTestRunner
from .timing import Timer, TimingCollector
from .unicode import UTF8Reader, is_valid_identifier
from .utils import (
    camel_to_snake,
    chunks,
    clamp,
    find,
    find_index,
    flatten,
    format_bytes,
    format_duration,
    group_by,
    merge_dicts,
    partition,
    pluralize,
    snake_to_camel,
    unique,
)
from .workspace import Workspace, WorkspaceConfig

__all__ = [
    # Workspace
    "Workspace",
    "WorkspaceConfig",
    # Build
    "BuildPipeline",
    "BuildCache",
    # Logging
    "Logger",
    "get_logger",
    "LogLevel",
    # Config
    "ConfigLoader",
    "CompilerConfig",
    # Source
    "SourceFile",
    "Position",
    "Span",
    "PositionTracker",
    # Unicode
    "UTF8Reader",
    "is_valid_identifier",
    # Diagnostics
    "DiagnosticEngine",
    "Diagnostic",
    "Severity",
    "ErrorCode",
    # Formatting
    "MessageFormatter",
    # IO
    "FileManager",
    # Memory
    "Arena",
    "MemoryTracker",
    # Timing
    "Timer",
    "TimingCollector",
    # Features
    "FeatureFlagManager",
    # Context
    "CompilerContext",
    # Testing
    "CompilerTestHelper",
    "GoldenTest",
    "GoldenTestRunner",
    # Benchmarks
    "Benchmark",
    "BenchmarkSuite",
    # Docs
    "DocumentationGenerator",
    # Errors
    "IError",
    "CompilerError",
    "ConfigError",
    "FileIOError",
    "InternalError",
    "ValidationError",
    "PanicError",
    # Result
    "Ok",
    "Err",
    "Result",
    "Some",
    "Nothing",
    "Option",
    # Utils
    "clamp",
    "group_by",
    "unique",
    "flatten",
    "chunks",
    "find",
    "find_index",
    "partition",
    "merge_dicts",
    "camel_to_snake",
    "snake_to_camel",
    "pluralize",
    "format_bytes",
    "format_duration",
]
