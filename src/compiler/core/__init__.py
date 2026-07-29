"""
Compiler Core

Provides foundational utilities for the I compiler.
"""

from .workspace import Workspace, WorkspaceConfig
from .build import BuildPipeline, BuildCache
from .logging import Logger, get_logger, LogLevel
from .config import ConfigLoader, CompilerConfig
from .source import SourceFile, Position, Span, PositionTracker
from .unicode import UTF8Reader, is_valid_identifier
from .diagnostics import DiagnosticEngine, Diagnostic, Severity, ErrorCode
from .formatting import MessageFormatter
from .io import FileManager
from .memory import Arena, MemoryTracker
from .timing import Timer, TimingCollector
from .features import FeatureFlagManager
from .context import CompilerContext
from .testing import CompilerTestHelper, GoldenTest, GoldenTestRunner
from .benchmarks import Benchmark, BenchmarkSuite
from .docs_generator import DocumentationGenerator
from .errors import IError, CompilerError, ConfigError, FileIOError, InternalError, ValidationError, Panic
from .result import Ok, Err, Result, Some, Nothing, Option
from .utils import clamp, group_by, unique, flatten, chunks, find, find_index, partition, merge_dicts

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
    "Panic",
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
]
