"""
Type Mapper: TypeSystem -> IR Type

Maps the source-level TypeSystem types to the machine-level IR types.
This is the bridge between type checking and IR generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import (
    IR_F64,
    IR_I1,
    IR_I8,
    IR_I32,
    IR_I64,
    IR_VOID,
    ArrayType,
    IRFunctionType,
    IRType,
    PointerType,
    StructType,
)

if TYPE_CHECKING:
    from ..typesystem.types import Type
    from .context import IRContext


def map_type(t: Type, context: IRContext | None = None) -> IRType:
    """Map a TypeSystem type to an IR type."""
    from ..typesystem.types import (
        TypeKind,
    )

    kind = t.kind

    if kind == TypeKind.INT:
        return IR_I64
    elif kind == TypeKind.FLOAT:
        return IR_F64
    elif kind == TypeKind.BOOL:
        return IR_I1
    elif kind == TypeKind.CHAR:
        return IR_I32
    elif kind == TypeKind.STRING:
        return PointerType(IR_I8)
    elif kind == TypeKind.NONE_TYPE:
        return IR_VOID
    elif kind == TypeKind.ANY:
        return PointerType(IR_I8)
    elif kind == TypeKind.NEVER or kind == TypeKind.UNKNOWN or kind == TypeKind.BOTTOM:
        return IR_VOID
    elif kind == TypeKind.LIST:
        return PointerType(IR_I8)
    elif kind == TypeKind.MAP:
        return PointerType(IR_I8)
    elif kind == TypeKind.SET:
        return PointerType(IR_I8)
    elif kind == TypeKind.TUPLE:
        ts = t  # type: TupleType
        fields = tuple(map_type(et, context) for et in ts.element_types)
        return StructType(fields)
    elif kind == TypeKind.RANGE:
        return array_type_from_range(t, context)
    elif kind == TypeKind.FUNCTION:
        ft = t  # type: FunctionType
        param_ir_types = tuple(map_type(pt, context) for pt in ft.param_types)
        ret_ir = map_type(ft.return_type, context)
        return IRFunctionType(param_ir_types, ret_ir)
    elif kind == TypeKind.STRUCT:
        return map_named_struct_type(t, context)
    elif kind == TypeKind.CLASS:
        return PointerType(IR_I8)
    elif kind == TypeKind.ENUM:
        return IR_I32
    elif kind == TypeKind.TRAIT or kind == TypeKind.INTERFACE:
        return PointerType(IR_I8)
    elif kind == TypeKind.OPTIONAL:
        ot = t  # type: OptionalType
        inner_ir = map_type(ot.inner, context)
        return StructType((inner_ir, IR_I1))
    elif kind == TypeKind.RESULT:
        rt = t  # type: ResultType
        ok_ir = map_type(rt.ok_type, context)
        err_ir = map_type(rt.err_type, context)
        return StructType((ok_ir, err_ir, IR_I1))
    elif kind == TypeKind.PARAMETERIZED:
        return PointerType(IR_I8)
    elif kind == TypeKind.TYPE_VAR:
        return PointerType(IR_I8)
    elif kind == TypeKind.FUTURE or kind == TypeKind.COROUTINE:
        return PointerType(IR_I8)
    elif kind == TypeKind.SIMD_VECTOR:
        svt = t  # type: SimdVectorType
        elem_ir = map_type(svt.element_type, context)
        return ArrayType(svt.size, elem_ir)
    elif kind == TypeKind.MODULE or kind == TypeKind.PACKAGE:
        return IR_VOID
    elif kind == TypeKind.CONST_TYPE:
        return IR_VOID
    elif kind == TypeKind.GENERIC:
        return PointerType(IR_I8)
    else:
        return PointerType(IR_I8)


def array_type_from_range(t, context) -> IRType:
    """Map a Range type to an IR array type."""
    rt = t
    elem_ir = map_type(rt.element_type, context)
    return PointerType(elem_ir)


def map_named_struct_type(t, context) -> IRType:
    """Map a source-level StructType to an IR named struct."""
    st = t
    name = st.name
    return StructType((), name=name)
