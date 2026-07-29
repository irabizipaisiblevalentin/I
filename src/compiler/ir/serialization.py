"""
IR Serialization

Supports binary, JSON, and text serialization of IR modules.
Versioned format for forward/backward compatibility.
"""
from __future__ import annotations

import json
import struct
from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .instructions import (
    Instruction, Opcode, Phi, Call, ICmp, FCmp,
    Switch, Alloca, Load, Store, GEP, CastInst,
    BinaryOp, TerminatorInst,
    ICmpPredicate, FCmpPredicate,
)
from .values import (
    Value, Constant, IntConstant, FloatConstant, BoolConstant,
    StringConstant, NullConstant, UndefinedConstant, ZeroConstant,
    GlobalVariable, Argument,
)
from .types import IRType, IRTypeKind, IRFunctionType

if TYPE_CHECKING:
    from typing import Any, Dict, List, Tuple


# ══════════════════════════════════════════════════════════════════
# Serialization Constants
# ══════════════════════════════════════════════════════════════════

IR_FORMAT_VERSION = 1


# ══════════════════════════════════════════════════════════════════
# Type Serialization
# ══════════════════════════════════════════════════════════════════


def _serialize_type(typ: IRType) -> Dict[str, Any]:
    """Serialize an IR type to a dict."""
    kind = typ.kind.name.lower()
    if typ.kind == IRTypeKind.INTEGER:
        return {"kind": kind, "bits": typ.bit_width}
    elif typ.kind == IRTypeKind.FLOAT:
        return {"kind": kind, "bits": typ.bit_width}
    elif typ.kind == IRTypeKind.POINTER:
        return {"kind": kind, "element": _serialize_type(typ.element_type),
                "address_space": typ.address_space}
    elif typ.kind == IRTypeKind.ARRAY:
        return {"kind": kind, "length": typ.length,
                "element": _serialize_type(typ.element_type)}
    elif typ.kind == IRTypeKind.STRUCT:
        fields = [_serialize_type(f) for f in typ.field_types]
        return {"kind": kind, "fields": fields, "packed": typ.is_packed,
                "name": typ.name}
    elif typ.kind == IRTypeKind.FUNCTION:
        params = [_serialize_type(p) for p in typ.param_types]
        return {"kind": kind, "params": params,
                "return": _serialize_type(typ.return_type),
                "variadic": typ.is_variadic}
    elif typ.kind == IRTypeKind.VECTOR:
        return {"kind": kind, "count": typ.element_count,
                "element": _serialize_type(typ.element_type)}
    else:
        return {"kind": kind}


def _deserialize_type(data: Dict[str, Any]) -> IRType:
    """Deserialize an IR type from a dict."""
    from .types import (
        IntegerType, FloatType, PointerType, ArrayType,
        StructType, IRFunctionType, VectorType,
        IRVoid, IRLabel,
    )
    kind = data["kind"]
    if kind == "void":
        return IRVoid()
    elif kind == "label":
        return IRLabel()
    elif kind == "integer":
        return IntegerType(data["bits"])
    elif kind == "float":
        return FloatType(data["bits"])
    elif kind == "pointer":
        elem = _deserialize_type(data["element"])
        return PointerType(elem, data.get("address_space", 0))
    elif kind == "array":
        elem = _deserialize_type(data["element"])
        return ArrayType(data["length"], elem)
    elif kind == "struct":
        fields = tuple(_deserialize_type(f) for f in data["fields"])
        return StructType(fields, data.get("packed", False), data.get("name", ""))
    elif kind == "function":
        params = tuple(_deserialize_type(p) for p in data["params"])
        ret = _deserialize_type(data["return"])
        return IRFunctionType(params, ret, data.get("variadic", False))
    elif kind == "vector":
        elem = _deserialize_type(data["element"])
        return VectorType(data["count"], elem)
    else:
        from .types import IRVoid
        return IRVoid()


# ══════════════════════════════════════════════════════════════════
# Value Serialization
# ══════════════════════════════════════════════════════════════════


def _serialize_value(val: Value) -> Dict[str, Any]:
    """Serialize a value reference."""
    if isinstance(val, IntConstant):
        return {"kind": "int", "value": val.value,
                "type": _serialize_type(val.type)}
    elif isinstance(val, FloatConstant):
        return {"kind": "float", "value": val.value,
                "type": _serialize_type(val.type)}
    elif isinstance(val, BoolConstant):
        return {"kind": "bool", "value": val.value}
    elif isinstance(val, StringConstant):
        return {"kind": "string", "value": val.value,
                "type": _serialize_type(val.type)}
    elif isinstance(val, NullConstant):
        return {"kind": "null", "type": _serialize_type(val.type)}
    elif isinstance(val, UndefinedConstant):
        return {"kind": "undef", "type": _serialize_type(val.type)}
    elif isinstance(val, ZeroConstant):
        return {"kind": "zero", "type": _serialize_type(val.type)}
    else:
        return {"kind": "ref", "name": val.name,
                "type": _serialize_type(val.type)}


def _deserialize_value(data: Dict[str, Any], func: Optional[IRFunction] = None) -> Value:
    """Deserialize a value from a dict."""
    kind = data.get("kind", "ref")
    if kind == "int":
        typ = _deserialize_type(data["type"])
        return IntConstant(data["value"], typ)
    elif kind == "float":
        typ = _deserialize_type(data["type"])
        return FloatConstant(data["value"], typ)
    elif kind == "bool":
        return BoolConstant(data["value"])
    elif kind == "string":
        return StringConstant(data["value"])
    elif kind == "null":
        typ = _deserialize_type(data["type"])
        return NullConstant(typ)
    elif kind == "undef":
        typ = _deserialize_type(data["type"])
        return UndefinedConstant(typ)
    elif kind == "zero":
        typ = _deserialize_type(data["type"])
        return ZeroConstant(typ)
    else:
        name = data.get("name", "")
        if func is not None:
            for arg in func.args:
                if arg.name == name:
                    return arg
        typ = _deserialize_type(data.get("type", {"kind": "void"}))
        return IntConstant(0, typ)


# ══════════════════════════════════════════════════════════════════
# JSON Serializer
# ══════════════════════════════════════════════════════════════════


class IRSerializer:
    """Serializes IR modules to various formats."""
    __slots__ = ()

    def to_json(self, module: IRModule) -> str:
        """Serialize module to JSON string."""
        data = self._serialize_module(module)
        return json.dumps(data, indent=2)

    def to_dict(self, module: IRModule) -> Dict[str, Any]:
        """Serialize module to Python dict."""
        return self._serialize_module(module)

    def to_text(self, module: IRModule) -> str:
        """Serialize module to human-readable text."""
        from .printer import IRPrinter
        return IRPrinter().print_module(module)

    def to_binary(self, module: IRModule) -> bytes:
        """Serialize to compact binary format."""
        data = self._serialize_module(module)
        json_bytes = json.dumps(data).encode("utf-8")
        header = struct.pack(">II", IR_FORMAT_VERSION, len(json_bytes))
        return header + json_bytes

    def _serialize_module(self, module: IRModule) -> Dict[str, Any]:
        """Serialize a module to a dict."""
        return {
            "version": IR_FORMAT_VERSION,
            "name": module.name,
            "target": module.target,
            "data_layout": module.data_layout,
            "functions": [self._serialize_function(f) for f in module.functions],
            "globals": [self._serialize_global(g) for g in module.globals],
        }

    def _serialize_function(self, func: IRFunction) -> Dict[str, Any]:
        """Serialize a function to a dict."""
        return {
            "name": func.name,
            "type": _serialize_type(func.func_type),
            "is_declaration": func.is_declaration,
            "blocks": [self._serialize_block(b) for b in func.blocks],
            "args": [{"name": a.name, "type": _serialize_type(a.type)}
                     for a in func.args],
        }

    def _serialize_block(self, block: BasicBlock) -> Dict[str, Any]:
        """Serialize a basic block to a dict."""
        return {
            "name": block.name,
            "instructions": [self._serialize_instruction(i) for i in block],
            "predecessors": [p.name for p in block.predecessors],
            "successors": [s.name for s in block.successors],
        }

    def _serialize_instruction(self, inst: Instruction) -> Dict[str, Any]:
        """Serialize an instruction to a dict."""
        data: Dict[str, Any] = {
            "name": inst.name,
            "opcode": inst.opcode.name,
            "type": _serialize_type(inst.result_type),
            "operands": [_serialize_value(op) for op in inst.operands],
        }

        if isinstance(inst, Phi):
            data["incoming"] = [
                {"value": _serialize_value(v), "block": b.name}
                for v, b in inst.incoming
            ]
        elif isinstance(inst, (ICmp, FCmp)):
            data["predicate"] = inst.predicate.name
        elif isinstance(inst, Call):
            data["func_type"] = _serialize_type(inst.func_type)
            data["arguments"] = [_serialize_value(a) for a in inst.arguments]
        elif isinstance(inst, Switch):
            data["cases"] = [
                {"value": _serialize_value(c), "block": b.name}
                for c, b in inst.cases
            ]
        elif isinstance(inst, Alloca):
            data["allocated_type"] = _serialize_type(inst.allocated_type)
            data["alignment"] = inst.alignment
        elif isinstance(inst, Load):
            data["alignment"] = inst.alignment
            data["volatile"] = inst.volatile
        elif isinstance(inst, Store):
            data["alignment"] = inst.alignment
            data["volatile"] = inst.volatile
        elif isinstance(inst, GEP):
            data["source_type"] = _serialize_type(inst.source_type)
            data["in_bounds"] = inst.in_bounds

        return data

    def _serialize_global(self, g: GlobalVariable) -> Dict[str, Any]:
        """Serialize a global variable to a dict."""
        data: Dict[str, Any] = {
            "name": g.name,
            "value_type": _serialize_type(g.value_type),
            "is_constant": g.is_constant,
            "linkage": g.linkage,
        }
        if g.initializer is not None:
            data["initializer"] = _serialize_value(g.initializer)
        return data


# ══════════════════════════════════════════════════════════════════
# JSON Deserializer
# ══════════════════════════════════════════════════════════════════


class IRDeserializer:
    """Deserializes IR modules from various formats."""
    __slots__ = ()

    def from_json(self, json_str: str) -> IRModule:
        """Deserialize module from JSON string."""
        data = json.loads(json_str)
        return self._deserialize_module(data)

    def from_dict(self, data: Dict[str, Any]) -> IRModule:
        """Deserialize module from Python dict."""
        return self._deserialize_module(data)

    def from_binary(self, data: bytes) -> IRModule:
        """Deserialize from binary format."""
        if len(data) < 8:
            raise ValueError("Invalid binary data: too short")
        version, length = struct.unpack(">II", data[:8])
        if version != IR_FORMAT_VERSION:
            raise ValueError(f"Unsupported binary format version: {version}")
        json_bytes = data[8:8 + length]
        json_str = json_bytes.decode("utf-8")
        return self.from_json(json_str)

    def _deserialize_module(self, data: Dict[str, Any]) -> IRModule:
        """Deserialize a module from a dict."""
        module = IRModule(data.get("name", ""))
        module.target = data.get("target", "")
        module.data_layout = data.get("data_layout", "")

        for g_data in data.get("globals", []):
            g = self._deserialize_global(g_data)
            module.add_global(g)

        for func_data in data.get("functions", []):
            func = self._deserialize_function(func_data)
            module.add_function(func)

        return module

    def _deserialize_function(self, data: Dict[str, Any]) -> IRFunction:
        """Deserialize a function from a dict."""
        func_type = _deserialize_type(data["type"])
        if not isinstance(func_type, IRFunctionType):
            func_type = IRFunctionType((), func_type)

        func = IRFunction(data["name"], func_type)

        if not data.get("is_declaration", False):
            for block_data in data.get("blocks", []):
                block = self._deserialize_block(block_data, func)
                func.append_block(block)

        return func

    def _deserialize_block(self, data: Dict[str, Any], func: Optional[IRFunction] = None) -> BasicBlock:
        """Deserialize a basic block from a dict."""
        block = BasicBlock(data["name"])

        for inst_data in data.get("instructions", []):
            inst = self._deserialize_instruction(inst_data, func)
            if inst:
                block.append(inst)

        return block

    def _deserialize_instruction(
        self,
        data: Dict[str, Any],
        func: Optional[IRFunction] = None,
    ) -> Optional[Instruction]:
        """Deserialize an instruction from a dict."""
        from .instructions import (
            Add, Sub, Mul, SDiv, UDiv, SRem, URem,
            FAdd, FSub, FMul, FDiv, FRem,
            And, Or, Xor, Shl, LShr, AShr,
            Not, Neg, FNeg,
            Branch, CondBranch, Return, Unreachable,
            Trunc, ZExt, SExt, FPTrunc, FPExt,
            UIToFP, SIToFP, FPToUI, FPToSI,
            PtrToInt, IntToPtr, BitCast, AddrSpaceCast,
            ExtractValue, InsertValue,
            ExtractElement, InsertElement, ShuffleVector,
        )

        try:
            opcode = Opcode[data["opcode"]]
        except KeyError:
            return None

        result_type = _deserialize_type(data.get("type", {"kind": "void"}))
        opcodes_to_classes = {
            Opcode.ADD: Add,
            Opcode.SUB: Sub,
            Opcode.MUL: Mul,
            Opcode.SDIV: SDiv,
            Opcode.UDIV: UDiv,
            Opcode.SREM: SRem,
            Opcode.UREM: URem,
            Opcode.FADD: FAdd,
            Opcode.FSUB: FSub,
            Opcode.FMUL: FMul,
            Opcode.FDIV: FDiv,
            Opcode.FREM: FRem,
            Opcode.AND: And,
            Opcode.OR: Or,
            Opcode.XOR: Xor,
            Opcode.SHL: Shl,
            Opcode.LSHR: LShr,
            Opcode.ASHR: AShr,
            Opcode.NOT: Not,
            Opcode.NEG: Neg,
            Opcode.FNEG: FNeg,
            Opcode.TRUNC: Trunc,
            Opcode.ZEXT: ZExt,
            Opcode.SEXT: SExt,
            Opcode.FPTRUNC: FPTrunc,
            Opcode.FPEXT: FPExt,
            Opcode.UITOFP: UIToFP,
            Opcode.SITOFP: SIToFP,
            Opcode.FPTOUI: FPToUI,
            Opcode.FPTOSI: FPToSI,
            Opcode.PTRTOINT: PtrToInt,
            Opcode.INTTOPTR: IntToPtr,
            Opcode.BITCAST: BitCast,
            Opcode.ADDRSPACECAST: AddrSpaceCast,
        }

        name = data.get("name", "")

        if opcode == Opcode.RETURN:
            ops = data.get("operands", [])
            if ops:
                val = _deserialize_value(ops[0], func)
                return Return(val)
            return Return()

        if opcode == Opcode.BRANCH:
            ops = data.get("operands", [])
            target = BasicBlock(ops[0].get("name", "") if ops else "")
            return Branch(target)

        if opcode == Opcode.COND_BRANCH:
            ops = data.get("operands", [])
            if len(ops) >= 3:
                cond = _deserialize_value(ops[0], func)
                t = BasicBlock(ops[1].get("name", ""))
                f = BasicBlock(ops[2].get("name", ""))
                return CondBranch(cond, t, f)

        if opcode == Opcode.UNREACHABLE:
            return Unreachable()

        if opcode == Opcode.PHI:
            typ = result_type
            incoming_data = data.get("incoming", [])
            incoming = [
                (_deserialize_value(iv["value"], func), BasicBlock(iv["block"]))
                for iv in incoming_data
            ]
            return Phi(name, typ, incoming)

        if opcode == Opcode.ICMP:
            pred_name = data.get("predicate", "EQ")
            predicate = ICmpPredicate[pred_name]
            ops = data.get("operands", [])
            lhs = _deserialize_value(ops[0], func) if len(ops) > 0 else IntConstant(0)
            rhs = _deserialize_value(ops[1], func) if len(ops) > 1 else IntConstant(0)
            return ICmp(name, predicate, lhs, rhs)

        if opcode == Opcode.FCMP:
            pred_name = data.get("predicate", "FALSE")
            predicate = FCmpPredicate[pred_name]
            ops = data.get("operands", [])
            lhs = _deserialize_value(ops[0], func) if len(ops) > 0 else FloatConstant(0.0)
            rhs = _deserialize_value(ops[1], func) if len(ops) > 1 else FloatConstant(0.0)
            return FCmp(name, predicate, lhs, rhs)

        if opcode == Opcode.CALL:
            func_type = _deserialize_type(data.get("func_type", {"kind": "void"}))
            ops = data.get("operands", [])
            function = _deserialize_value(ops[0], func) if ops else IntConstant(0)
            args_data = data.get("arguments", [])
            arguments = [_deserialize_value(a, func) for a in args_data]
            return Call(name, func_type, function, arguments)

        if opcode == Opcode.ALLOCA:
            alloc_type = _deserialize_type(data.get("allocated_type", {"kind": "void"}))
            alignment = data.get("alignment", 0)
            return Alloca(name, alloc_type, alignment=alignment)

        if opcode == Opcode.LOAD:
            ops = data.get("operands", [])
            pointer = _deserialize_value(ops[0], func) if ops else IntConstant(0)
            alignment = data.get("alignment", 0)
            volatile = data.get("volatile", False)
            return Load(name, result_type, pointer, alignment, volatile)

        if opcode == Opcode.STORE:
            ops = data.get("operands", [])
            val = _deserialize_value(ops[0], func) if len(ops) > 0 else IntConstant(0)
            ptr = _deserialize_value(ops[1], func) if len(ops) > 1 else IntConstant(0)
            alignment = data.get("alignment", 0)
            volatile = data.get("volatile", False)
            return Store(val, ptr, alignment, volatile)

        if opcode == Opcode.GEP:
            source_type = _deserialize_type(data.get("source_type", {"kind": "void"}))
            in_bounds = data.get("in_bounds", False)
            ops = data.get("operands", [])
            ptr = _deserialize_value(ops[0], func) if ops else IntConstant(0)
            indices = [_deserialize_value(o, func) for o in ops[1:]] if len(ops) > 1 else []
            return GEP(name, source_type, ptr, indices, in_bounds)

        if opcode == Opcode.SWITCH:
            ops = data.get("operands", [])
            val = _deserialize_value(ops[0], func) if ops else IntConstant(0)
            default = BasicBlock(ops[1].get("name", "") if len(ops) > 1 else "")
            cases_data = data.get("cases", [])
            cases = [
                (_deserialize_value(c["value"], func), BasicBlock(c["block"]))
                for c in cases_data
            ]
            return Switch(val, default, cases)

        if opcode in opcodes_to_classes:
            cls = opcodes_to_classes[opcode]
            ops = data.get("operands", [])
            if opcode in (Opcode.TRUNC, Opcode.ZEXT, Opcode.SEXT,
                          Opcode.FPTRUNC, Opcode.FPEXT,
                          Opcode.UITOFP, Opcode.SITOFP,
                          Opcode.FPTOUI, Opcode.FPTOSI,
                          Opcode.PTRTOINT, Opcode.INTTOPTR,
                          Opcode.BITCAST, Opcode.ADDRSPACECAST):
                val = _deserialize_value(ops[0], func) if ops else IntConstant(0)
                return cls(name, val, result_type)
            elif opcode in (Opcode.NOT, Opcode.NEG, Opcode.FNEG):
                val = _deserialize_value(ops[0], func) if ops else IntConstant(0)
                return cls(name, val)
            else:
                lhs = _deserialize_value(ops[0], func) if len(ops) > 0 else IntConstant(0)
                rhs = _deserialize_value(ops[1], func) if len(ops) > 1 else IntConstant(0)
                return cls(name, lhs, rhs)

        return Instruction(name, opcode, result_type)

    def _deserialize_global(self, data: Dict[str, Any]) -> GlobalVariable:
        """Deserialize a global variable from a dict."""
        value_type = _deserialize_type(data.get("value_type", {"kind": "void"}))
        is_constant = data.get("is_constant", False)
        linkage = data.get("linkage", "internal")
        initializer = None
        if "initializer" in data:
            initializer = _deserialize_value(data["initializer"])
        g = GlobalVariable(
            data.get("name", ""),
            value_type,
            is_constant=is_constant,
            initializer=initializer,
            linkage=linkage,
        )
        return g


# ══════════════════════════════════════════════════════════════════
# Convenience Functions
# ══════════════════════════════════════════════════════════════════


def serialize_json(module: IRModule) -> str:
    """Serialize a module to JSON."""
    return IRSerializer().to_json(module)


def deserialize_json(json_str: str) -> IRModule:
    """Deserialize a module from JSON."""
    return IRDeserializer().from_json(json_str)


def serialize_text(module: IRModule) -> str:
    """Serialize module to text."""
    return IRSerializer().to_text(module)


def serialize_binary(module: IRModule) -> bytes:
    """Serialize a module to binary."""
    return IRSerializer().to_binary(module)


def deserialize_binary(data: bytes) -> IRModule:
    """Deserialize a module from binary."""
    return IRDeserializer().from_binary(data)
