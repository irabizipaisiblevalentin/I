"""
IR Printer

Human-readable text output of IR modules, functions, blocks, and instructions.
Follows LLVM-style formatting conventions.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .instructions import (
    Instruction, TerminatorInst, Phi, Call, ICmp, FCmp,
    Alloca, Load, Store, GEP, Branch, CondBranch, Return,
    Switch, CastInst,
)
from .values import Value, Constant, IntConstant, FloatConstant, BoolConstant
from .types import IRType

if TYPE_CHECKING:
    from typing import Dict, List, TextIO
    import io


# ══════════════════════════════════════════════════════════════════
# IR Printer
# ══════════════════════════════════════════════════════════════════


class IRPrinter:
    """Prints IR in human-readable text format."""
    __slots__ = ("_value_names", "_indent", "_output")

    def __init__(self) -> None:
        object.__setattr__(self, "_value_names", {})
        object.__setattr__(self, "_indent", 0)
        object.__setattr__(self, "_output", [])

    def _assign_names(self, module: IRModule) -> None:
        """Assign readable names to all values."""
        counter = {}
        for func in module.functions:
            self._value_names[id(func)] = f"@{func.name}"
            for arg in func.args:
                name = f"%{arg.name}"
                self._value_names[id(arg)] = name
            for block in func:
                label = block.name or f"bb{counter.get('bb', 0)}"
                counter['bb'] = counter.get('bb', 0) + 1
                self._value_names[id(block)] = f"label{label}"
                for inst in block:
                    if inst.name:
                        self._value_names[id(inst)] = f"%{inst.name}"
                    else:
                        n = counter.get(inst.opcode.name, 0)
                        counter[inst.opcode.name] = n + 1
                        self._value_names[id(inst)] = f"{inst.opcode.name.lower()}{n}"

    def _name(self, val: Value) -> str:
        """Get or create a name for a value."""
        if id(val) in self._value_names:
            return self._value_names[id(val)]
        if isinstance(val, IntConstant):
            return str(val.value)
        if isinstance(val, FloatConstant):
            return str(val.value)
        if isinstance(val, BoolConstant):
            return "true" if val.value else "false"
        if isinstance(val, Constant):
            return repr(val)
        name = val.name or "tmp"
        self._value_names[id(val)] = f"%{name}"
        return f"%{name}"

    # ── Public API ───────────────────────────────────────────────

    def print_module(self, module: IRModule) -> str:
        """Print a complete module."""
        self._assign_names(module)
        self._output = []

        self._line(f"; Module: \"{module.name}\"")
        if module.target:
            self._line(f"target datalayout = \"{module.data_layout}\"")
            self._line(f"target triple = \"{module.target}\"")
        self._line("")

        for func in module.functions:
            self._print_function(func)
            self._line("")

        for gv in module.globals:
            self._print_global(gv)
            self._line("")

        return "\n".join(self._output)

    def print_function(self, func: IRFunction) -> str:
        """Print a single function."""
        self._assign_names(func.module or IRModule())
        self._output = []
        self._print_function(func)
        return "\n".join(self._output)

    def print_block(self, block: BasicBlock) -> str:
        """Print a single block."""
        self._output = []
        self._print_block_content(block)
        return "\n".join(self._output)

    def print_instruction(self, inst: Instruction) -> str:
        """Print a single instruction."""
        self._output = []
        self._print_inst(inst)
        return "\n".join(self._output)

    # ── Internal Printing ────────────────────────────────────────

    def _line(self, text: str) -> None:
        self._output.append("  " * self._indent + text)

    def _print_function(self, func: IRFunction) -> None:
        if func.is_declaration:
            params = ", ".join(
                f"{arg.type} %{arg.name}" for arg in func.args
            )
            self._line(f"declare {func.return_type} @{func.name}({params})")
            return

        params = ", ".join(
            f"{arg.type} %{arg.name}" for arg in func.args
        )
        self._line(f"define {func.return_type} @{func.name}({params}) {{")
        self._indent += 1

        for i, block in enumerate(func):
            self._print_block_content(block)
            if i < len(func) - 1:
                self._line("")

        self._indent -= 1
        self._line("}")

    def _print_block_content(self, block: BasicBlock) -> None:
        label = block.name or "entry"
        self._line(f"{label}:")

        self._indent += 1
        for inst in block:
            self._print_inst(inst)
        self._indent -= 1

    def _print_inst(self, inst: Instruction) -> None:
        from .instructions import (
            Branch, CondBranch, Return, Unreachable,
            Store, Phi, Call, Alloca, Load, GEP,
        )

        if isinstance(inst, Branch):
            self._line(f"br label %{inst.target.name}")
        elif isinstance(inst, CondBranch):
            cond = self._name(inst.condition)
            true = inst.true_block.name
            false = inst.false_block.name
            self._line(f"br i1 {cond}, label %{true}, label %{false}")
        elif isinstance(inst, Return):
            if inst.value:
                self._line(f"ret {inst.value.type} {self._name(inst.value)}")
            else:
                self._line("ret void")
        elif isinstance(inst, Unreachable):
            self._line("unreachable")
        elif isinstance(inst, Store):
            val = self._name(inst.value)
            ptr = self._name(inst.pointer)
            self._line(f"store {inst.value.type} {val}, {inst.pointer.type} {ptr}")
        elif isinstance(inst, Phi):
            pairs = ", ".join(
                f"[{self._name(val)}, %{blk.name}]"
                for val, blk in inst.incoming
            )
            self._line(f"{self._name(inst)} = phi {inst.result_type} {pairs}")
        elif isinstance(inst, Call):
            args = ", ".join(
                f"{a.type} {self._name(a)}" for a in inst.arguments
            )
            if inst.result_type:
                self._line(f"{self._name(inst)} = call {inst.func_type} "
                           f"{self._name(inst.function)}({args})")
            else:
                self._line(f"call {inst.func_type} "
                           f"{self._name(inst.function)}({args})")
        elif isinstance(inst, ICmp):
            pred = inst.predicate.name.lower()
            self._line(f"{self._name(inst)} = icmp {pred} "
                       f"{inst.lhs.type} {self._name(inst.lhs)}, "
                       f"{self._name(inst.rhs)}")
        elif isinstance(inst, FCmp):
            pred = inst.predicate.name.lower()
            self._line(f"{self._name(inst)} = fcmp {pred} "
                       f"{inst.lhs.type} {self._name(inst.lhs)}, "
                       f"{self._name(inst.rhs)}")
        elif isinstance(inst, Alloca):
            self._line(f"{self._name(inst)} = alloca {inst.allocated_type}")
        elif isinstance(inst, Load):
            ptr = self._name(inst.pointer)
            self._line(f"{self._name(inst)} = load {inst.result_type}, "
                       f"{inst.pointer.type} {ptr}")
        elif isinstance(inst, GEP):
            indices = ", ".join(
                f"{i.type} {self._name(i)}" for i in inst.indices
            )
            self._line(f"{self._name(inst)} = getelementptr "
                       f"{inst.source_type}, {inst.pointer.type} "
                       f"{self._name(inst.pointer)}, {indices}")
        else:
            # Generic instruction printing
            ops = ", ".join(
                f"{o.type} {self._name(o)}" for o in inst.operands
            )
            self._line(f"{self._name(inst)} = {inst.opcode.name.lower()} {ops}")

    def _print_global(self, gv) -> None:
        kind = "@const" if gv.is_constant else "@global"
        self._line(f"{kind} {gv.name} = {gv.value_type}")


def print_ir(module: IRModule) -> str:
    """Convenience function to print a module."""
    return IRPrinter().print_module(module)
