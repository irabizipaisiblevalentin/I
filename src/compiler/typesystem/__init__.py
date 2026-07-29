"""
Type System for the I Programming Language

Complete static type system implementing all typing rules.
Supports:
- All I language types (primitives, collections, functions, generics, traits)
- Bidirectional type inference with constraint solving
- Generic type parameters with bounds and constraints
- Trait and interface implementation validation
- Compile-time constant evaluation
- Professional bilingual diagnostics (Kinyarwanda/English)
- Incremental compilation support
- IDE-friendly APIs

This package NEVER:
- Generates bytecode
- Executes code at runtime
- Depends on the VM or optimizer

It is the authoritative source of all static typing rules.
"""

from .types import (
    Type, TypeKind, Variance,
    IntType, FloatType, BoolType, CharType, StringType, NoneType,
    AnyType, UnknownType, NeverType, BottomType,
    ListType, MapType, SetType, TupleType, RangeType,
    FunctionType, OptionalType, ResultType,
    TypeVariable, GenericType, ClassType, StructType, EnumType,
    TraitType, InterfaceType, ModuleType, PackageType,
    FutureType, CoroutineType, SimdVectorType,
    NamedType,
    TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_CHAR, TYPE_STRING,
    TYPE_NONE, TYPE_ANY, TYPE_UNKNOWN, TYPE_NEVER, TYPE_BOTTOM,
    common_type, is_compatible, is_strict_subtype,
    make_list, make_map, make_set, make_tuple, make_optional,
    make_result, make_function, make_class_type, make_struct_type,
    make_enum_type, make_trait_type, make_interface_type,
    make_type_var, make_generic, make_range, make_future,
    make_coroutine, make_simd,
)

from .registry import (
    TypeRegistry, TypeDefinition, MemberInfo, MethodSignature,
    TraitRequirement,
)

from .database import (
    TypeDatabase, SubtypeRelation, TraitImplementation,
)

from .environment import (
    TypeEnvironment, TypeScope, TypeEntry,
)

from .context import (
    TypeContext, FunctionContext, ClassContext, LoopContext,
)

from .inference import (
    InferenceEngine, InferenceResult,
)

from .constraints import (
    ConstraintSolver, Constraint, ConstraintKind, Substitution,
)

from .generics import (
    GenericEngine, GenericParamDef, GenericInstantiation,
)

from .traits import (
    TraitResolver, TraitDefinition, InterfaceDefinition,
    ImplementationCheck,
)

from .compiletime import (
    CompileTimeEvaluator, ConstValue, ConstValueKind,
)

from .diagnostics import (
    TypeDiagnostics, TypeErrorCode, TypeSeverity, TypeLocation,
    TypeDiagnostic, get_bilingual_message,
)

from .checker import (
    TypeChecker, check_types,
)

__all__ = [
    # Types
    'Type', 'TypeKind', 'Variance',
    'IntType', 'FloatType', 'BoolType', 'CharType', 'StringType', 'NoneType',
    'AnyType', 'UnknownType', 'NeverType', 'BottomType',
    'ListType', 'MapType', 'SetType', 'TupleType', 'RangeType',
    'FunctionType', 'OptionalType', 'ResultType',
    'TypeVariable', 'GenericType', 'ClassType', 'StructType', 'EnumType',
    'TraitType', 'InterfaceType', 'ModuleType', 'PackageType',
    'FutureType', 'CoroutineType', 'SimdVectorType',
    'NamedType',
    'TYPE_INT', 'TYPE_FLOAT', 'TYPE_BOOL', 'TYPE_CHAR', 'TYPE_STRING',
    'TYPE_NONE', 'TYPE_ANY', 'TYPE_UNKNOWN', 'TYPE_NEVER', 'TYPE_BOTTOM',
    'common_type', 'is_compatible', 'is_strict_subtype',
    'make_list', 'make_map', 'make_set', 'make_tuple', 'make_optional',
    'make_result', 'make_function', 'make_class_type', 'make_struct_type',
    'make_enum_type', 'make_trait_type', 'make_interface_type',
    'make_type_var', 'make_generic', 'make_range', 'make_future',
    'make_coroutine', 'make_simd',
    # Registry
    'TypeRegistry', 'TypeDefinition', 'MemberInfo', 'MethodSignature',
    'TraitRequirement',
    # Database
    'TypeDatabase', 'SubtypeRelation', 'TraitImplementation',
    # Environment
    'TypeEnvironment', 'TypeScope', 'TypeEntry',
    # Context
    'TypeContext', 'FunctionContext', 'ClassContext', 'LoopContext',
    # Inference
    'InferenceEngine', 'InferenceResult',
    # Constraints
    'ConstraintSolver', 'Constraint', 'ConstraintKind', 'Substitution',
    # Generics
    'GenericEngine', 'GenericParamDef', 'GenericInstantiation',
    # Traits
    'TraitResolver', 'TraitDefinition', 'InterfaceDefinition',
    'ImplementationCheck',
    # Compile-time
    'CompileTimeEvaluator', 'ConstValue', 'ConstValueKind',
    # Diagnostics
    'TypeDiagnostics', 'TypeErrorCode', 'TypeSeverity', 'TypeLocation',
    'TypeDiagnostic', 'get_bilingual_message',
    # Checker
    'TypeChecker', 'check_types',
]
