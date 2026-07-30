"""
LLVM IR Text Emitter

Converts the I-lang compiler IRModule into textual LLVM IR (.ll).
Every IR opcode is mapped to its LLVM IR equivalent.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

from compiler.ir import (
    AggregateConstant,
    Argument,
    ArrayType,
    BasicBlock,
    BoolConstant,
    Constant,
    FCmpPredicate,
    FloatConstant,
    FloatType,
    GlobalVariable,
    ICmpPredicate,
    Instruction,
    IntConstant,
    IntegerType,
    IRFunction,
    IRFunctionType,
    IRModule,
    IRType,
    NullConstant,
    Opcode,
    PointerType,
    PoisonConstant,
    StringConstant,
    StructType,
    UndefinedConstant,
    Value,
    VectorType,
    VoidType,
    ZeroConstant,
)
from compiler.ir.instructions import (
    FCmp,
    ICmp,
)

if TYPE_CHECKING:
    pass


class LLVMCompileError(Exception):
    pass


_ICMP_MAP: dict[ICmpPredicate, str] = {
    ICmpPredicate.EQ: "eq",
    ICmpPredicate.NE: "ne",
    ICmpPredicate.UGT: "ugt",
    ICmpPredicate.UGE: "uge",
    ICmpPredicate.ULT: "ult",
    ICmpPredicate.ULE: "ule",
    ICmpPredicate.SGT: "sgt",
    ICmpPredicate.SGE: "sge",
    ICmpPredicate.SLT: "slt",
    ICmpPredicate.SLE: "sle",
}

_FCMP_MAP: dict[FCmpPredicate, str] = {
    FCmpPredicate.FALSE: "false",
    FCmpPredicate.OEQ: "oeq",
    FCmpPredicate.OGT: "ogt",
    FCmpPredicate.OGE: "oge",
    FCmpPredicate.OLT: "olt",
    FCmpPredicate.OLE: "ole",
    FCmpPredicate.ONE: "one",
    FCmpPredicate.ORD: "ord",
    FCmpPredicate.UEQ: "ueq",
    FCmpPredicate.UGT: "ugt",
    FCmpPredicate.UGE: "uge",
    FCmpPredicate.ULT: "ult",
    FCmpPredicate.ULE: "ule",
    FCmpPredicate.UNE: "une",
    FCmpPredicate.UNO: "uno",
    FCmpPredicate.TRUE: "true",
}


class LLVMEmitter:
    """Converts IRModule to textual LLVM IR (.ll format)."""

    def __init__(self) -> None:
        self._counter: dict[str, int] = {}
        self._names: dict[int, str] = {}
        self._output: list[str] = []
        self._indent: int = 0

    # ── Public API ─────────────────────────────────────────────────

    def emit_module(self, module: IRModule) -> str:
        self._output = []
        self._counter = {}
        self._names = {}
        self._assign_names(module)

        self._writeln(f'; Module: "{module.name or "module"}"')
        if module.data_layout:
            self._writeln(f'target datalayout = "{module.data_layout}"')
        if module.target:
            self._writeln(f'target triple = "{module.target}"')
        self._writeln("")

        for type_name, ir_type in module.named_types.items():
            self._writeln(f"%{type_name} = type {self.emit_type(ir_type)}")
        if module.named_types:
            self._writeln("")

        for gv in module.globals:
            self._emit_global(gv)

        for func in module.functions:
            self._writeln("")
            self.emit_function(func)

        return "\n".join(self._output)

    def emit_function(self, function: IRFunction) -> str:
        self._output = []
        self._counter = {}
        prev = self._names
        self._names = {}
        self._assign_names_function(function)

        ret_type = self.emit_type(function.return_type)
        param_types = ", ".join(
            f"{self.emit_type(a.type)} {self._value_name(a)}"
            for a in function.args
        )
        func_name = self._value_name(function)

        if function.is_declaration:
            self._writeln(f"declare {ret_type} {func_name}({param_types})")
        else:
            linkage = "internal" if function.name.startswith("__") else ""
            linkage_str = f"{linkage} " if linkage else ""
            self._writeln(f"define {linkage_str}{ret_type} {func_name}({param_types}) {{")
            self._indent += 1
            for block in function:
                self._writeln("")
                self.emit_basic_block(block)
            self._indent -= 1
            self._writeln("}")

        result = "\n".join(self._output)
        self._names = prev
        return result

    def emit_basic_block(self, block: BasicBlock) -> str:
        start = len(self._output)
        label = self._value_name(block)
        self._writeln(f"{label}:")
        self._indent += 1
        for inst in block:
            self._writeln(self.emit_instruction(inst))
        self._indent -= 1
        return "\n".join(self._output[start:])

    def emit_instruction(self, inst: Instruction) -> str:
        oc = inst.opcode

        if oc == Opcode.BRANCH:
            return self._emit_br(inst)
        if oc == Opcode.COND_BRANCH:
            return self._emit_cond_br(inst)
        if oc == Opcode.SWITCH:
            return self._emit_switch(inst)
        if oc == Opcode.RETURN:
            return self._emit_ret(inst)
        if oc == Opcode.UNREACHABLE:
            return "unreachable"
        if oc in (Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.SDIV, Opcode.UDIV,
                  Opcode.SREM, Opcode.UREM, Opcode.FADD, Opcode.FSUB, Opcode.FMUL,
                  Opcode.FDIV, Opcode.FREM):
            return self._emit_binary(inst)
        if oc in (Opcode.AND, Opcode.OR, Opcode.XOR, Opcode.SHL,
                  Opcode.LSHR, Opcode.ASHR):
            return self._emit_binary(inst)
        if oc == Opcode.NOT:
            return self._emit_not(inst)
        if oc == Opcode.NEG:
            return self._emit_neg(inst)
        if oc == Opcode.FNEG:
            return self._emit_fneg(inst)
        if oc in (Opcode.ICMP, Opcode.FCMP):
            return self._emit_cmp(inst)
        if oc == Opcode.ALLOCA:
            return self._emit_alloca(inst)
        if oc == Opcode.LOAD:
            return self._emit_load(inst)
        if oc == Opcode.STORE:
            return self._emit_store(inst)
        if oc == Opcode.GEP:
            return self._emit_gep(inst)
        if oc == Opcode.MEMCPY:
            return self._emit_memcpy(inst)
        if oc == Opcode.MEMSET:
            return self._emit_memset(inst)
        if oc in (Opcode.TRUNC, Opcode.ZEXT, Opcode.SEXT,
                  Opcode.FPTRUNC, Opcode.FPEXT,
                  Opcode.UITOFP, Opcode.SITOFP, Opcode.FPTOUI, Opcode.FPTOSI,
                  Opcode.PTRTOINT, Opcode.INTTOPTR, Opcode.BITCAST,
                  Opcode.ADDRSPACECAST):
            return self._emit_cast(inst)
        if oc == Opcode.PHI:
            return self._emit_phi(inst)
        if oc == Opcode.CALL:
            return self._emit_call(inst)
        if oc == Opcode.INVOKE:
            return self._emit_invoke(inst)
        if oc == Opcode.LANDING_PAD:
            return self._emit_landingpad(inst)
        if oc == Opcode.RESUME:
            return self._emit_resume(inst)
        if oc in (Opcode.EXTRACT_VALUE, Opcode.INSERT_VALUE):
            return self._emit_aggregate(inst)
        if oc == Opcode.EXTRACT_ELEMENT:
            return self._emit_extractelement(inst)
        if oc == Opcode.INSERT_ELEMENT:
            return self._emit_insertelement(inst)
        if oc == Opcode.SHUFFLE_VECTOR:
            return self._emit_shufflevector(inst)
        if oc == Opcode.ATOMICRMW:
            return self._emit_atomicrmw(inst)
        if oc == Opcode.CMPXCHG:
            return self._emit_cmpxchg(inst)
        if oc == Opcode.FENCE:
            return self._emit_fence(inst)

        raise LLVMCompileError(f"Unsupported opcode: {oc}")

    def emit_type(self, ir_type: IRType) -> str:
        if isinstance(ir_type, VoidType):
            return "void"
        if isinstance(ir_type, IntegerType):
            return f"i{ir_type.bit_width}"
        if isinstance(ir_type, FloatType):
            bw = ir_type.bit_width
            if bw == 16:
                return "half"
            if bw == 32:
                return "float"
            if bw == 64:
                return "double"
            if bw == 128:
                return "fp128"
            return f"f{bw}"
        if isinstance(ir_type, PointerType):
            elem = self.emit_type(ir_type.element_type)
            if ir_type.address_space:
                return f"{elem} addrspace({ir_type.address_space})*"
            return f"{elem}*"
        if isinstance(ir_type, ArrayType):
            return f"[{ir_type.length} x {self.emit_type(ir_type.element_type)}]"
        if isinstance(ir_type, StructType):
            if ir_type.name:
                return f"%\"{ir_type.name}\""
            fields = ", ".join(self.emit_type(f) for f in ir_type.field_types)
            packed = "packed " if ir_type.is_packed else ""
            return f"{packed}{{ {fields} }}"
        if isinstance(ir_type, VectorType):
            return f"<{ir_type.size} x {self.emit_type(ir_type.element_type)}>"
        if isinstance(ir_type, IRFunctionType):
            return "ptr"
        raise LLVMCompileError(f"Unknown IR type: {ir_type}")

    def emit_value(self, value: Value) -> str:
        return f"{self.emit_type(value.type)} {self._value_ref(value)}"

    def compile_to_object(
        self,
        ll_ir: str,
        target_triple: str = "",
        opt_level: int = 2,
    ) -> bytes:
        """Invoke llc to compile LLVM IR text to object file bytes."""
        llc_args = ["llc", "-filetype=obj"]
        if target_triple:
            llc_args.extend(["-mtriple", target_triple])
        if opt_level is not None:
            llc_args.extend([f"-O{opt_level}"])
        try:
            proc = subprocess.run(
                llc_args,
                input=ll_ir,
                capture_output=True,
                text=True,
                check=True,
            )
            return proc.stdout.encode("latin-1")
        except FileNotFoundError:
            raise LLVMCompileError("llc not found on PATH")
        except subprocess.CalledProcessError as e:
            raise LLVMCompileError(f"llc failed: {e.stderr}") from e

    # ── Name assignment ────────────────────────────────────────────

    def _assign_names(self, module: IRModule) -> None:
        for func in module.functions:
            self._names[id(func)] = f"@{func.name}"
            self._assign_names_function(func)
        for gv in module.globals:
            self._names[id(gv)] = f"@{gv.name}"

    def _assign_names_function(self, function: IRFunction) -> None:
        self._names[id(function)] = f"@{function.name}"
        for arg in function.args:
            self._names[id(arg)] = f"%{arg.name}"
        for block in function:
            bname = block.name or f"bb{self._next_id('bb')}"
            self._names[id(block)] = f"%{bname}"
            for inst in block:
                if inst.is_terminator:
                    continue
                if inst.name:
                    n = inst.name
                else:
                    n = f"{inst.opcode.name.lower()}{self._next_id(inst.opcode.name.lower())}"
                self._names[id(inst)] = f"%{n}"

    def _next_id(self, key: str) -> int:
        i = self._counter.get(key, 0)
        self._counter[key] = i + 1
        return i

    def _value_name(self, val: Value) -> str:
        return self._names.get(id(val), f"%\"{val.name or 'anon'}\"")

    def _value_ref(self, val: Value) -> str:
        if id(val) in self._names:
            return self._names[id(val)]
        if isinstance(val, IntConstant):
            return str(val.value)
        if isinstance(val, FloatConstant):
            return self._format_float(val)
        if isinstance(val, BoolConstant):
            return "true" if val.value else "false"
        if isinstance(val, NullConstant):
            return "null"
        if isinstance(val, UndefinedConstant):
            return "undef"
        if isinstance(val, PoisonConstant):
            return "poison"
        if isinstance(val, ZeroConstant):
            return "zeroinitializer"
        if isinstance(val, StringConstant):
            return self._format_string(val)
        if isinstance(val, AggregateConstant):
            return self._format_aggregate(val)
        if isinstance(val, GlobalVariable):
            return f"@{val.name}"
        if isinstance(val, Argument):
            return f"%{val.name}"
        return f"%\"{val.name or 'anon'}\""

    def _format_float(self, c: FloatConstant) -> str:
        from struct import pack, unpack
        bw = c.type.bit_width
        if bw == 32:
            bits = unpack("I", pack("f", float(c.value)))[0]
            return f"0x{bits:08x}"
        if bw == 64:
            bits = unpack("Q", pack("d", float(c.value)))[0]
            return f"0x{bits:016x}"
        return str(c.value)

    @staticmethod
    def _format_string(c: StringConstant) -> str:
        escaped = c.value.encode("utf-8").decode("unicode_escape")
        escaped = escaped.replace('"', '\\22').replace('\\n', '\\0A')
        return f'c"{escaped}\\00"'

    def _format_aggregate(self, c: AggregateConstant) -> str:
        elems = ", ".join(self._const_ref(e) for e in c.elements)
        return f"{{ {elems} }}"

    def _const_ref(self, c: Constant) -> str:
        if isinstance(c, IntConstant):
            return f"{self.emit_type(c.type)} {c.value}"
        if isinstance(c, FloatConstant):
            return f"{self.emit_type(c.type)} {self._format_float(c)}"
        if isinstance(c, BoolConstant):
            return f"i1 {'true' if c.value else 'false'}"
        if isinstance(c, NullConstant):
            return f"{self.emit_type(c.type)} null"
        if isinstance(c, UndefinedConstant):
            return f"{self.emit_type(c.type)} undef"
        if isinstance(c, PoisonConstant):
            return f"{self.emit_type(c.type)} poison"
        if isinstance(c, ZeroConstant):
            return f"{self.emit_type(c.type)} zeroinitializer"
        if isinstance(c, AggregateConstant):
            return f"{self.emit_type(c.type)} {self._format_aggregate(c)}"
        if isinstance(c, StringConstant):
            return f"{self.emit_type(c.type)} {self._format_string(c)}"
        return f"{self.emit_type(c.type)} {self._value_ref(c)}"

    def _value(self, v: Value) -> str:
        return f"{self.emit_type(v.type)} {self._value_ref(v)}"

    # ── Instruction emission helpers ───────────────────────────────

    def _emit_binary(self, inst: Instruction) -> str:
        oc = inst.opcode
        name = self._value_name(inst)
        lhs_t = self.emit_type(inst.operands[0].type)
        lhs_r = self._value_ref(inst.operands[0])
        rhs_r = self._value_ref(inst.operands[1])

        op_map = {
            Opcode.ADD: "add",
            Opcode.SUB: "sub",
            Opcode.MUL: "mul",
            Opcode.SDIV: "sdiv",
            Opcode.UDIV: "udiv",
            Opcode.SREM: "srem",
            Opcode.UREM: "urem",
            Opcode.FADD: "fadd",
            Opcode.FSUB: "fsub",
            Opcode.FMUL: "fmul",
            Opcode.FDIV: "fdiv",
            Opcode.FREM: "frem",
            Opcode.AND: "and",
            Opcode.OR: "or",
            Opcode.XOR: "xor",
            Opcode.SHL: "shl",
            Opcode.LSHR: "lshr",
            Opcode.ASHR: "ashr",
        }
        op_str = op_map[oc]
        return f"{name} = {op_str} {lhs_t} {lhs_r}, {rhs_r}"

    def _emit_not(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        op_t = self.emit_type(inst.operands[0].type)
        op_r = self._value_ref(inst.operands[0])
        return f"{name} = xor {op_t} {op_r}, -1"

    def _emit_neg(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        op_t = self.emit_type(inst.operands[0].type)
        op_r = self._value_ref(inst.operands[0])
        return f"{name} = sub {op_t} 0, {op_r}"

    def _emit_fneg(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        op_t = self.emit_type(inst.operands[0].type)
        op_r = self._value_ref(inst.operands[0])
        return f"{name} = fneg {op_t} {op_r}"

    def _emit_cmp(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        lhs_t = self.emit_type(inst.operands[0].type)
        lhs_r = self._value_ref(inst.operands[0])
        rhs_r = self._value_ref(inst.operands[1])

        if isinstance(inst, ICmp):
            pred = _ICMP_MAP.get(inst.predicate, "eq")
            return f"{name} = icmp {pred} {lhs_t} {lhs_r}, {rhs_r}"
        if isinstance(inst, FCmp):
            pred = _FCMP_MAP.get(inst.predicate, "oeq")
            return f"{name} = fcmp {pred} {lhs_t} {lhs_r}, {rhs_r}"
        raise LLVMCompileError("Unknown comparison instruction")

    def _emit_alloca(self, inst: Instruction) -> str:
        a = inst  # type: Alloca
        name = self._value_name(inst)
        alloc_type = self.emit_type(a.allocated_type)
        pieces = [f"{name} = alloca {alloc_type}"]
        if a.num_elements:
            pieces.append(f", {self.emit_type(a.num_elements.type)} {self._value_ref(a.num_elements)}")
        if a.alignment:
            pieces.append(f", align {a.alignment}")
        return "".join(pieces)

    def _emit_load(self, inst: Instruction) -> str:
        a = inst  # type: Load
        name = self._value_name(inst)
        ptr_t = self.emit_type(inst.type)
        ptr_r = self._value_ref(inst.operands[0])
        ptr_ty = self.emit_type(inst.operands[0].type)
        pieces = [f"{name} = load {ptr_t}, {ptr_ty} {ptr_r}"]
        if a.alignment:
            pieces.append(f", align {a.alignment}")
        return "".join(pieces)

    def _emit_store(self, inst: Instruction) -> str:
        a = inst  # type: Store
        val_t = self.emit_type(inst.operands[0].type)
        val_r = self._value_ref(inst.operands[0])
        ptr_r = self._value_ref(inst.operands[1])
        ptr_ty = self.emit_type(inst.operands[1].type)
        pieces = [f"store {val_t} {val_r}, {ptr_ty} {ptr_r}"]
        if a.alignment:
            pieces.append(f", align {a.alignment}")
        return "".join(pieces)

    def _emit_gep(self, inst: Instruction) -> str:
        a = inst  # type: GEP
        name = self._value_name(inst)
        src_type = self.emit_type(a.source_type)
        ptr_r = self._value_ref(inst.operands[0])
        ptr_ty = self.emit_type(inst.operands[0].type)
        indices = ", ".join(
            f"{self.emit_type(idx.type)} {self._value_ref(idx)}"
            for idx in a.indices
        )
        inb = "inbounds " if a.in_bounds else ""
        return f"{name} = getelementptr {inb}{src_type}, {ptr_ty} {ptr_r}, {indices}"

    def _emit_memcpy(self, inst: Instruction) -> str:
        dest_r = self._value_ref(inst.operands[0])
        src_r = self._value_ref(inst.operands[1])
        len_r = self._value_ref(inst.operands[2])
        dest_ty = self.emit_type(inst.operands[0].type)
        src_ty = self.emit_type(inst.operands[1].type)
        len_ty = self.emit_type(inst.operands[2].type)
        return (
            f"call void @llvm.memcpy.p0i8.p0i8.i64("
            f"{dest_ty} {dest_r}, {src_ty} {src_r}, {len_ty} {len_r}, i1 false)"
        )

    def _emit_memset(self, inst: Instruction) -> str:
        dest_r = self._value_ref(inst.operands[0])
        val_r = self._value_ref(inst.operands[1])
        len_r = self._value_ref(inst.operands[2])
        dest_ty = self.emit_type(inst.operands[0].type)
        val_ty = self.emit_type(inst.operands[1].type)
        len_ty = self.emit_type(inst.operands[2].type)
        return (
            f"call void @llvm.memset.p0i8.i64("
            f"{dest_ty} {dest_r}, {val_ty} {val_r}, {len_ty} {len_r}, i1 false)"
        )

    def _emit_cast(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        src_r = self._value_ref(inst.operands[0])
        src_ty = self.emit_type(inst.operands[0].type)
        dst_ty = self.emit_type(inst.type)

        cast_map = {
            Opcode.TRUNC: "trunc",
            Opcode.ZEXT: "zext",
            Opcode.SEXT: "sext",
            Opcode.FPTRUNC: "fptrunc",
            Opcode.FPEXT: "fpext",
            Opcode.UITOFP: "uitofp",
            Opcode.SITOFP: "sitofp",
            Opcode.FPTOUI: "fptoui",
            Opcode.FPTOSI: "fptosi",
            Opcode.PTRTOINT: "ptrtoint",
            Opcode.INTTOPTR: "inttoptr",
            Opcode.BITCAST: "bitcast",
            Opcode.ADDRSPACECAST: "addrspacecast",
        }
        op = cast_map[inst.opcode]
        return f"{name} = {op} {src_ty} {src_r} to {dst_ty}"

    def _emit_phi(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        typ = self.emit_type(inst.type)
        incoming = inst  # type: Phi
        pairs = ", ".join(
            f"[{self._value_ref(val)}, {self._value_ref(blk)}]"
            for val, blk in incoming.incoming
        )
        return f"{name} = phi {typ} {pairs}"

    def _emit_call(self, inst: Instruction) -> str:
        a = inst  # type: Call
        ft = a.func_type
        ret_type = self.emit_type(ft.return_type)
        callee_r = self._value_ref(a.function)
        callee_ty = self.emit_type(a.function.type)
        args = ", ".join(
            f"{self.emit_type(v.type)} {self._value_ref(v)}"
            for v in a.arguments
        )
        name = self._value_name(inst)
        if ft.return_type.is_void or inst.type.is_void:
            return f"call {ret_type} {callee_ty} {callee_r}({args})"
        return f"{name} = call {ret_type} {callee_ty} {callee_r}({args})"

    def _emit_invoke(self, inst: Instruction) -> str:
        a = inst  # type: Invoke
        ft = a.func_type
        ret_type = self.emit_type(ft.return_type)
        callee_r = self._value_ref(a.function)
        callee_ty = self.emit_type(a.function.type)
        args = ", ".join(
            f"{self.emit_type(v.type)} {self._value_ref(v)}"
            for v in a.arguments
        )
        normal_r = self._value_ref(a.normal_block)
        unwind_r = self._value_ref(a.unwind_block)
        name = self._value_name(inst)
        if ft.return_type.is_void:
            return (
                f"invoke {ret_type} {callee_ty} {callee_r}({args}) "
                f"to label {normal_r} unwind label {unwind_r}"
            )
        return (
            f"{name} = invoke {ret_type} {callee_ty} {callee_r}({args}) "
            f"to label {normal_r} unwind label {unwind_r}"
        )

    def _emit_landingpad(self, inst: Instruction) -> str:
        a = inst  # type: LandingPad
        name = self._value_name(inst)
        typ = self.emit_type(inst.type)
        parts = [f"{name} = landingpad {typ}"]
        if a._cleanup:
            parts.append("cleanup")
        for ct in a._catch_types:
            parts.append(f"catch {self.emit_type(ct.type)} {self._value_ref(ct)}")
        return " ".join(parts)

    def _emit_resume(self, inst: Instruction) -> str:
        v = inst.operands[0]
        return f"resume {self.emit_type(v.type)} {self._value_ref(v)}"

    def _emit_aggregate(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        agg_r = self._value_ref(inst.operands[0])
        agg_ty = self.emit_type(inst.operands[0].type)
        if inst.opcode == Opcode.EXTRACT_VALUE:
            indices = "".join(f", {i}" for i in inst.indices)
            return f"{name} = extractvalue {agg_ty} {agg_r}{indices}"
        elem_r = self._value_ref(inst.operands[1])
        idx = "".join(f", {i}" for i in inst.indices)
        return f"{name} = insertvalue {agg_ty} {agg_r}, {self.emit_type(inst.operands[1].type)} {elem_r}{idx}"

    def _emit_extractelement(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        vec_r = self._value_ref(inst.operands[0])
        vec_ty = self.emit_type(inst.operands[0].type)
        idx_r = self._value_ref(inst.operands[1])
        idx_ty = self.emit_type(inst.operands[1].type)
        return f"{name} = extractelement {vec_ty} {vec_r}, {idx_ty} {idx_r}"

    def _emit_insertelement(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        vec_r = self._value_ref(inst.operands[0])
        vec_ty = self.emit_type(inst.operands[0].type)
        elem_r = self._value_ref(inst.operands[1])
        elem_ty = self.emit_type(inst.operands[1].type)
        idx_r = self._value_ref(inst.operands[2])
        idx_ty = self.emit_type(inst.operands[2].type)
        return f"{name} = insertelement {vec_ty} {vec_r}, {elem_ty} {elem_r}, {idx_ty} {idx_r}"

    def _emit_shufflevector(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        v1_r = self._value_ref(inst.operands[0])
        v1_ty = self.emit_type(inst.operands[0].type)
        v2_r = self._value_ref(inst.operands[1])
        mask_r = self._value_ref(inst.operands[2])
        mask_ty = self.emit_type(inst.operands[2].type)
        return f"{name} = shufflevector {v1_ty} {v1_r}, {v1_ty} {v2_r}, {mask_ty} {mask_r}"

    def _emit_atomicrmw(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        a = inst  # type: AtomicRMW
        ptr_r = self._value_ref(inst.operands[0])
        ptr_ty = self.emit_type(inst.operands[0].type)
        val_r = self._value_ref(inst.operands[1])
        val_ty = self.emit_type(inst.operands[1].type)
        return f"{name} = atomicrmw {a._operation} {ptr_ty} {ptr_r}, {val_ty} {val_r} {a._ordering}"

    def _emit_cmpxchg(self, inst: Instruction) -> str:
        name = self._value_name(inst)
        a = inst  # type: CmpXchg
        ptr_r = self._value_ref(inst.operands[0])
        ptr_ty = self.emit_type(inst.operands[0].type)
        cmp_r = self._value_ref(inst.operands[1])
        cmp_ty = self.emit_type(inst.operands[1].type)
        new_r = self._value_ref(inst.operands[2])
        weak = "weak " if a._weak else ""
        return (
            f"{name} = cmpxchg {weak}{ptr_ty} {ptr_r}, "
            f"{cmp_ty} {cmp_r}, {cmp_ty} {new_r} "
            f"{a._success_ordering} {a._failure_ordering}"
        )

    def _emit_fence(self, inst: Instruction) -> str:
        a = inst  # type: Fence
        return f"fence {a._ordering}"

    def _emit_br(self, inst: Instruction) -> str:
        target_r = self._value_ref(inst.operands[0])
        return f"br label {target_r}"

    def _emit_cond_br(self, inst: Instruction) -> str:
        cond_r = self._value_ref(inst.operands[0])
        cond_ty = self.emit_type(inst.operands[0].type)
        true_r = self._value_ref(inst.operands[1])
        false_r = self._value_ref(inst.operands[2])
        return f"br {cond_ty} {cond_r}, label {true_r}, label {false_r}"

    def _emit_switch(self, inst: Instruction) -> str:
        a = inst  # type: Switch
        val_r = self._value_ref(inst.operands[0])
        val_ty = self.emit_type(inst.operands[0].type)
        default_r = self._value_ref(inst.operands[1])
        parts = [f"switch {val_ty} {val_r}, label {default_r} ["]
        for case_val, case_block in a.cases:
            cv_r = self._value_ref(case_val)
            cv_ty = self.emit_type(case_val.type)
            cb_r = self._value_ref(case_block)
            parts.append(f"    {cv_ty} {cv_r}, label {cb_r}")
        parts.append("]")
        return "\n" + "\n".join(parts)

    def _emit_ret(self, inst: Instruction) -> str:
        if inst.operands:
            v = inst.operands[0]
            return f"ret {self.emit_type(v.type)} {self._value_ref(v)}"
        return "ret void"

    # ── Globals ────────────────────────────────────────────────────

    def _emit_global(self, gv: GlobalVariable) -> None:
        typ = self.emit_type(gv.value_type)
        linkage = gv.linkage
        const_str = "constant" if gv.is_constant else "global"
        init = gv.initializer
        if init:
            init_str = self._const_ref(init)
        else:
            init_str = "zeroinitializer"
        self._writeln(f"@{gv.name} = {linkage} {const_str} {typ} {init_str}")

    # ── Output helpers ─────────────────────────────────────────────

    def _writeln(self, line: str = "") -> None:
        if line:
            self._output.append("  " * self._indent + line)
        else:
            self._output.append("")
