"""
IR Validator

Validates IR structure, types, CFG, and SSA properties.
Returns a list of errors rather than raising exceptions.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .types import (
    IRType, IRVoid, IRTypeKind, IntegerType, FloatType, PointerType,
)
from .values import Value, ValueKind, Constant, Argument
from .instructions import (
    Instruction, TerminatorInst, Opcode, Phi, Call,
    Branch, CondBranch, Return, ICmp, FCmp, Load, Store,
    GEP, Alloca, CastInst, BinaryOp,
    Trunc, ZExt, SExt, FPTrunc, FPExt,
)
from .basic_block import BasicBlock
from .function import IRFunction
from .module import IRModule

if TYPE_CHECKING:
    from typing import List, Set


# ══════════════════════════════════════════════════════════════════
# IR Validator
# ══════════════════════════════════════════════════════════════════


class IRValidator:
    """Validates IR structure and consistency."""
    __slots__ = ("_errors", "_warnings", "_module")

    def __init__(self) -> None:
        object.__setattr__(self, "_errors", [])
        object.__setattr__(self, "_warnings", [])
        object.__setattr__(self, "_module", None)

    @property
    def errors(self) -> List[str]:
        return list(self._errors)

    @property
    def warnings(self) -> List[str]:
        return list(self._warnings)

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    def clear(self) -> None:
        self._errors.clear()
        self._warnings.clear()

    # ── Module Validation ────────────────────────────────────────

    def validate_module(self, module: IRModule) -> bool:
        """Validate an entire module."""
        self.clear()
        object.__setattr__(self, "_module", module)

        self._validate_duplicate_functions(module)

        for func in module.functions:
            self._validate_function(func)

        return self.is_valid

    # ── Duplicate Function Validation ────────────────────────────

    def _validate_duplicate_functions(self, module: IRModule) -> None:
        seen_names: Set[str] = set()
        for func in module.functions:
            if func.name in seen_names:
                self._errors.append(
                    f"Duplicate function name '@{func.name}'"
                )
            seen_names.add(func.name)

    # ── Function Validation ──────────────────────────────────────

    def _validate_function(self, func: IRFunction) -> None:
        if not func.blocks and not func.is_declaration:
            self._errors.append(f"Function '@{func.name}' has no blocks but is not a declaration")
            return

        if not func.is_declaration:
            if func.entry_block is None:
                self._errors.append(f"Function '@{func.name}' has no entry block")
                return

            self._validate_cfg(func)

            for block in func:
                self._validate_block(block, func)

    # ── CFG Validation ───────────────────────────────────────────

    def _validate_cfg(self, func: IRFunction) -> None:
        """Validate that the CFG is well-formed."""
        blocks = set(func.blocks)
        for block in func:
            # Check successor validity
            for succ in block.successors:
                if succ not in blocks:
                    self._errors.append(
                        f"Block '{block.name}' references unknown successor '{succ.name}'"
                    )

            # Check predecessor validity
            for pred in block.predecessors:
                if pred not in blocks:
                    self._errors.append(
                        f"Block '{block.name}' references unknown predecessor '{pred.name}'"
                    )

    # ── Block Validation ─────────────────────────────────────────

    def _validate_block(self, block: BasicBlock, func: IRFunction) -> None:
        has_terminator = False
        terminator_index = -1
        for i, inst in enumerate(block):
            if inst.is_terminator:
                if has_terminator:
                    self._errors.append(
                        f"Multiple terminators in block '{block.name}'"
                    )
                    break
                has_terminator = True
                terminator_index = i

        if not has_terminator:
            self._errors.append(
                f"Block '{block.name}' in '@{func.name}' has no terminator"
            )

        if has_terminator and terminator_index != len(block) - 1:
            self._errors.append(
                f"Terminator not last instruction in block '{block.name}'"
            )

        defined: Set[Value] = set()
        for arg in func.args:
            defined.add(arg)

        for inst in block:
            self._validate_use_before_def(inst, defined, block, func)
            if not inst.is_terminator:
                defined.add(inst)

            self._validate_instruction(inst, block, func)

    # ── Use-Before-Def Validation ────────────────────────────────

    def _validate_use_before_def(
        self,
        inst: Instruction,
        defined: Set[Value],
        block: BasicBlock,
        func: IRFunction,
    ) -> None:
        for op in inst.operands:
            if isinstance(op, Constant):
                continue
            if isinstance(op, BasicBlock):
                continue
            if isinstance(op, Argument):
                continue
            if isinstance(op, Value) and op not in defined:
                self._errors.append(
                    f"Use before def: '{inst.name}' uses '{op.name}' "
                    f"which is not defined in block '{block.name}'"
                )

    # ── Instruction Validation ───────────────────────────────────

    def _validate_instruction(
        self,
        inst: Instruction,
        block: BasicBlock,
        func: IRFunction,
    ) -> None:
        for op in inst.operands:
            if isinstance(op, Value) and not isinstance(op, Constant):
                if isinstance(op, BasicBlock):
                    continue
                if op.parent is None and not isinstance(op, (Constant,)):
                    self._warnings.append(
                        f"Instruction '{inst.name}' uses value '{op.name}' "
                        f"with no parent block"
                    )

        if isinstance(inst, Phi):
            self._validate_phi(inst, block, func)
        elif isinstance(inst, Call):
            self._validate_call(inst)
        elif isinstance(inst, Load):
            self._validate_load(inst)
        elif isinstance(inst, Store):
            self._validate_store(inst)
        elif isinstance(inst, BinaryOp):
            self._validate_binary_op(inst, block, func)
        elif isinstance(inst, CastInst):
            self._validate_cast(inst, block, func)

    # ── Binary Op Validation ─────────────────────────────────────

    def _validate_binary_op(
        self,
        inst: Instruction,
        block: BasicBlock,
        func: IRFunction,
    ) -> None:
        if hasattr(inst, 'lhs') and hasattr(inst, 'rhs'):
            if inst.lhs.type != inst.rhs.type:
                self._warnings.append(
                    f"Binary op '{inst.name}' type mismatch: "
                    f"{inst.lhs.type} vs {inst.rhs.type}"
                )

    # ── Phi Validation ───────────────────────────────────────────

    def _validate_phi(self, phi: Phi, block: BasicBlock, func: IRFunction) -> None:
        if len(phi.incoming) == 0:
            self._errors.append(
                f"Phi node '{phi.name}' has no incoming values"
            )

        if block.predecessors and len(phi.incoming) != len(block.predecessors):
            self._errors.append(
                f"Phi '{phi.name}' has {len(phi.incoming)} incoming values "
                f"but block has {len(block.predecessors)} predecessors"
            )

        for val, pred_block in phi.incoming:
            if pred_block not in func.blocks:
                self._errors.append(
                    f"Phi '{phi.name}' references unknown block '{pred_block.name}'"
                )
            elif block.predecessors and pred_block not in block.predecessors:
                self._errors.append(
                    f"Phi '{phi.name}' incoming block '{pred_block.name}' "
                    f"is not a predecessor of block '{block.name}'"
                )

            if val.type != phi.result_type:
                self._warnings.append(
                    f"Phi '{phi.name}' incoming type mismatch: "
                    f"{val.type} != {phi.result_type}"
                )

    # ── Cast Validation ──────────────────────────────────────────

    def _validate_cast(
        self,
        inst: CastInst,
        block: BasicBlock,
        func: IRFunction,
    ) -> None:
        src_type = inst.source_value.type
        dest_type = inst.result_type

        if src_type == dest_type:
            self._errors.append(
                f"Cast '{inst.name}' source and destination types are the same: "
                f"{src_type}"
            )

        if inst.opcode in (Opcode.TRUNC, Opcode.ZEXT, Opcode.SEXT):
            if not src_type.is_integer:
                self._errors.append(
                    f"Integer cast '{inst.name}' source is not integer: "
                    f"{src_type}"
                )
            if not dest_type.is_integer:
                self._errors.append(
                    f"Integer cast '{inst.name}' destination is not integer: "
                    f"{dest_type}"
                )

        if inst.opcode in (Opcode.FPTRUNC, Opcode.FPEXT):
            if not src_type.is_float:
                self._errors.append(
                    f"FP cast '{inst.name}' source is not float: "
                    f"{src_type}"
                )
            if not dest_type.is_float:
                self._errors.append(
                    f"FP cast '{inst.name}' destination is not float: "
                    f"{dest_type}"
                )

    # ── Call Validation ──────────────────────────────────────────

    def _validate_call(self, call: Call) -> None:
        from .types import IRFunctionType
        if not isinstance(call.func_type, IRFunctionType):
            self._errors.append(
                f"Call '{call.name}' target is not a function type"
            )

    # ── Load Validation ──────────────────────────────────────────

    def _validate_load(self, load: Load) -> None:
        if not isinstance(load.pointer.type, PointerType):
            self._errors.append(
                f"Load '{load.name}' pointer is not a pointer type"
            )

    # ── Store Validation ─────────────────────────────────────────

    def _validate_store(self, store: Store) -> None:
        if not isinstance(store.pointer.type, PointerType):
            self._errors.append(
                f"Store pointer is not a pointer type"
            )

    def __repr__(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return f"IRValidator({status}, {len(self._errors)} errors, {len(self._warnings)} warnings)"


def validate(module: IRModule) -> List[str]:
    """Validate a module and return all errors."""
    validator = IRValidator()
    validator.validate_module(module)
    return validator.errors
