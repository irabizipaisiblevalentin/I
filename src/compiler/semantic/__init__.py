"""
Semantic Analyzer package for the I programming language.

The Semantic Analyzer is the first compiler stage that understands the meaning
of I programs. It transforms a syntactically valid AST into a semantically
valid program.

This package NEVER:
- Generates bytecode
- Executes code
- Optimizes code
- Infers final runtime behavior

Its responsibility is correctness and program validity.
"""

from compiler.semantic.analyzer import SemanticAnalyzer, analyze
from compiler.semantic.errors import (
    SemanticErrorCode, SemanticErrorCollection, SemanticDiagnostic,
    SemanticSeverity, SourceLocation,
)
from compiler.semantic.symbols import (
    Symbol, SymbolKind, TypeDescriptor, SymbolType, Visibility,
    make_variable, make_constant, make_function, make_method,
    make_class, make_struct, make_enum, make_trait, make_interface,
    make_parameter, make_module,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_STRING, TYPE_NONE, TYPE_ANY,
    TYPE_LIST, TYPE_DICT,
)
from compiler.semantic.scopes import Scope, ScopeKind, ScopeManager
from compiler.semantic.builtins import (
    register_builtins, is_reserved_keyword, is_builtin_type,
    BUILTIN_TYPES, BUILTIN_FUNCTIONS,
)
from compiler.semantic.names import (
    resolve_name, resolve_function, resolve_class, resolve_type,
)
from compiler.semantic.imports import ImportResolver, ModuleInfo
from compiler.semantic.constants import (
    is_constant_expression, evaluate_constant, get_constant_value,
)
from compiler.semantic.controlflow import (
    analyze_function_flow, function_always_returns, FlowAnalysis,
)
from compiler.semantic.visibility import check_visibility
from compiler.semantic.context import AnalysisContext

__all__ = [
    # Analyzer
    'SemanticAnalyzer',
    'analyze',
    # Errors
    'SemanticErrorCode',
    'SemanticErrorCollection',
    'SemanticDiagnostic',
    'SemanticSeverity',
    'SourceLocation',
    # Symbols
    'Symbol',
    'SymbolKind',
    'TypeDescriptor',
    'SymbolType',
    'Visibility',
    'make_variable',
    'make_constant',
    'make_function',
    'make_method',
    'make_class',
    'make_struct',
    'make_enum',
    'make_trait',
    'make_interface',
    'make_parameter',
    'make_module',
    'TYPE_INT',
    'TYPE_FLOAT',
    'TYPE_BOOL',
    'TYPE_STRING',
    'TYPE_NONE',
    'TYPE_ANY',
    'TYPE_LIST',
    'TYPE_DICT',
    # Scopes
    'Scope',
    'ScopeKind',
    'ScopeManager',
    # Builtins
    'register_builtins',
    'is_reserved_keyword',
    'is_builtin_type',
    'BUILTIN_TYPES',
    'BUILTIN_FUNCTIONS',
    # Name Resolution
    'resolve_name',
    'resolve_function',
    'resolve_class',
    'resolve_type',
    # Imports
    'ImportResolver',
    'ModuleInfo',
    # Constants
    'is_constant_expression',
    'evaluate_constant',
    'get_constant_value',
    # Control Flow
    'analyze_function_flow',
    'function_always_returns',
    'FlowAnalysis',
    # Visibility
    'check_visibility',
    # Context
    'AnalysisContext',
]
