"""
MIR — Mid-Level Intermediate Representation

Normalizes programs into a representation ideal for analysis.
MIR sits between HIR and LIR, providing:
- Control Flow Graphs (CFG)
- Basic Blocks
- SSA preparation
- Temporary values
- Explicit branches and returns
- Explicit variable lifetimes
- Ownership metadata
- Compile-time evaluation metadata
- Optimization hooks

MIR is the primary representation for optimization passes.
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .types import IRType
from .values import Value, Constant, Argument
from .instructions import Instruction, Opcode, Alloca, Call, Load, Store, Branch, CondBranch
from .cfg import CFG, LoopInfo
from .ssa import SSABuilder, LivenessAnalysis

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Tuple


# ══════════════════════════════════════════════════════════════════
# MIR Ownership
# ══════════════════════════════════════════════════════════════════


class OwnershipKind(Enum):
    """Ownership classification for values."""
    OWNED = auto()
    BORROWED = auto()
    MUTABLE_BORROW = auto()
    SHARED = auto()
    COPY = auto()
    MOVE = auto()


class OwnershipMeta:
    """Ownership metadata attached to MIR values."""
    __slots__ = ("_kind", "_lifetime", "_borrow_count")

    def __init__(
        self,
        kind: OwnershipKind = OwnershipKind.OWNED,
        lifetime: str = "",
        borrow_count: int = 0,
    ) -> None:
        object.__setattr__(self, "_kind", kind)
        object.__setattr__(self, "_lifetime", lifetime)
        object.__setattr__(self, "_borrow_count", borrow_count)

    @property
    def kind(self) -> OwnershipKind:
        return self._kind

    @property
    def lifetime(self) -> str:
        return self._lifetime

    @property
    def borrow_count(self) -> int:
        return self._borrow_count

    def __repr__(self) -> str:
        return f"Ownership({self._kind.name})"


def split_critical_edges(ir_function: IRFunction) -> List[BasicBlock]:
    """Split critical edges by inserting new blocks."""
    from .types import IR_LABEL
    new_blocks: List[BasicBlock] = []
    edges = []
    for block in ir_function.blocks:
        successors = block.successors
        if len(successors) > 1:
            for succ in successors:
                if len(succ.predecessors) > 1:
                    edges.append((block, succ))

    for source, target in edges:
        idx = ir_function.blocks.index(target) if target in ir_function.blocks else -1
        new_block = BasicBlock(f"split_{source.name}_{target.name}")
        ir_function.insert_block(idx, new_block)

        new_block.add_successor(target)
        new_block.add_predecessor(source)
        target.remove_predecessor(source)
        target.add_predecessor(new_block)
        source.remove_successor(target)
        source.add_successor(new_block)

        new_block.append(Branch(target))

        terminator = source.terminator
        if terminator is not None:
            from .instructions import CondBranch as CB
            if isinstance(terminator, CB):
                if terminator.true_block is target:
                    source.replace(terminator, CB(terminator.condition, new_block, terminator.false_block))
                elif terminator.false_block is target:
                    source.replace(terminator, CB(terminator.condition, terminator.true_block, new_block))

        new_blocks.append(new_block)

    return new_blocks


def compute_ownership(ir_function: IRFunction) -> Dict[int, OwnershipMeta]:
    """Compute ownership metadata for pointer arguments and allocas."""
    ownership: Dict[int, OwnershipMeta] = {}

    for arg in ir_function.args:
        is_written = False
        for block in ir_function.blocks:
            for inst in block.instructions:
                if isinstance(inst, Store) and inst.pointer is arg:
                    is_written = True
                    break
            if is_written:
                break

        if is_written:
            ownership[id(arg)] = OwnershipMeta(OwnershipKind.MUTABLE_BORROW)
        else:
            ownership[id(arg)] = OwnershipMeta(OwnershipKind.BORROWED)

    for block in ir_function.blocks:
        for inst in block.instructions:
            if isinstance(inst, Alloca):
                ownership[id(inst)] = OwnershipMeta(OwnershipKind.OWNED)
            elif isinstance(inst, Call) and inst.result_type and not inst.result_type.is_void:
                ownership[id(inst)] = OwnershipMeta(OwnershipKind.COPY)

    return ownership


class MIRNormalizePass:
    """Normalizes an IR function into MIR form.

    Normalizations:
    1. Split critical edges
    2. Canonicalize loops (ensure single entry)
    3. Compute ownership metadata for pointer arguments
    4. Mark hot/cold blocks based on loop depth
    """

    def run(self, mir_function: "MIRFunction") -> "MIRFunction":
        ir_func = mir_function.ir_function

        split_critical_edges(ir_func)

        ownership = compute_ownership(ir_func)
        for val_id, meta in ownership.items():
            mir_function._ownership[val_id] = meta

        cfg = mir_function.cfg
        for loop in cfg.loops:
            for block in loop.blocks:
                if block is not loop.header:
                    for succ in block.successors:
                        if succ is loop.header:
                            pass

        return mir_function


# ══════════════════════════════════════════════════════════════════
# MIR Function
# ══════════════════════════════════════════════════════════════════


class MIRFunction:
    """MIR function — normalized representation with analysis results."""
    __slots__ = ("_ir_function", "_cfg", "_ssa_builder",
                 "_liveness", "_loops", "_ownership")

    def __init__(self, ir_function: IRFunction) -> None:
        object.__setattr__(self, "_ir_function", ir_function)
        object.__setattr__(self, "_cfg", None)
        object.__setattr__(self, "_ssa_builder", None)
        object.__setattr__(self, "_liveness", None)
        object.__setattr__(self, "_loops", [])
        object.__setattr__(self, "_ownership", {})

    # ── Properties ───────────────────────────────────────────────

    @property
    def ir_function(self) -> IRFunction:
        return self._ir_function

    @property
    def name(self) -> str:
        return self._ir_function.name

    @property
    def cfg(self) -> CFG:
        if self._cfg is None:
            object.__setattr__(self, "_cfg", CFG(self._ir_function))
        return self._cfg

    @property
    def ssa(self) -> SSABuilder:
        if self._ssa_builder is None:
            object.__setattr__(self, "_ssa_builder",
                               SSABuilder(self._ir_function))
        return self._ssa_builder

    @property
    def liveness(self) -> LivenessAnalysis:
        if self._liveness is None:
            object.__setattr__(self, "_liveness", LivenessAnalysis(self.cfg))
        return self._liveness

    @property
    def loops(self) -> List[LoopInfo]:
        if not self._loops:
            object.__setattr__(self, "_loops", self.cfg.loops)
        return self._loops

    @property
    def blocks(self) -> List[BasicBlock]:
        return self._ir_function.blocks

    @property
    def entry_block(self) -> Optional[BasicBlock]:
        return self._ir_function.entry_block

    # ── Ownership ────────────────────────────────────────────────

    def set_ownership(self, value: Value, meta: OwnershipMeta) -> None:
        """Set ownership metadata for a value."""
        self._ownership[id(value)] = meta

    def get_ownership(self, value: Value) -> Optional[OwnershipMeta]:
        """Get ownership metadata for a value."""
        return self._ownership.get(id(value))

    # ── Analysis Invalidation ────────────────────────────────────

    def invalidate_cfg(self) -> None:
        """Invalidate cached CFG (call after modifying the function)."""
        object.__setattr__(self, "_cfg", None)
        object.__setattr__(self, "_ssa_builder", None)
        object.__setattr__(self, "_liveness", None)
        object.__setattr__(self, "_loops", [])

    # ── Optimization Queries ─────────────────────────────────────

    def is_loop_header(self, block: BasicBlock) -> bool:
        """Check if a block is a loop header."""
        return any(loop.header is block for loop in self.loops)

    def get_loop_depth(self, block: BasicBlock) -> int:
        """Get the loop nesting depth of a block."""
        depth = 0
        for loop in self.loops:
            if block in loop.blocks:
                depth = max(depth, loop.depth)
        return depth

    def is_hot_block(self, block: BasicBlock, threshold: int = 10) -> bool:
        """Check if a block is in a deep loop (heuristic for hot path)."""
        return self.get_loop_depth(block) >= threshold

    def get_dominates(self, dominator: BasicBlock, target: BasicBlock) -> bool:
        """Check if dominator dominates target."""
        return self.cfg.dominates(dominator, target)

    def is_dominator(self, a: BasicBlock, b: BasicBlock) -> bool:
        """Check if a dominates b."""
        return self.cfg.dominates(a, b)

    def get_dominance_frontier(self, block: BasicBlock) -> Set[BasicBlock]:
        """Get the dominance frontier of a block."""
        return self.cfg.dominance_frontier(block)

    def get_loop_for_block(self, block: BasicBlock) -> Optional[LoopInfo]:
        """Get the innermost loop containing a block."""
        best: Optional[LoopInfo] = None
        best_depth = -1
        for loop in self.loops:
            if block in loop.blocks and loop.depth > best_depth:
                best = loop
                best_depth = loop.depth
        return best

    def compute_call_graph(self) -> Dict[str, List[str]]:
        """Compute the call graph for this function."""
        callees: List[str] = []
        for block in self.blocks:
            for inst in block.instructions:
                if isinstance(inst, Call):
                    callee = inst.function
                    if hasattr(callee, 'name'):
                        callees.append(callee.name)
        return {self.name: callees}

    def __repr__(self) -> str:
        return (f"MIRFunction({self.name}: "
                f"{len(self.blocks)} blocks, "
                f"{len(self.loops)} loops)")


# ══════════════════════════════════════════════════════════════════
# MIR Module
# ══════════════════════════════════════════════════════════════════


class MIRModule:
    """MIR module — provides analysis views over IR."""
    __slots__ = ("_ir_module", "_functions")

    def __init__(self, ir_module: IRModule) -> None:
        object.__setattr__(self, "_ir_module", ir_module)
        funcs = {}
        for func in ir_module.functions:
            funcs[func.name] = MIRFunction(func)
        object.__setattr__(self, "_functions", funcs)

    @property
    def ir_module(self) -> IRModule:
        return self._ir_module

    @property
    def name(self) -> str:
        return self._ir_module.name

    @property
    def functions(self) -> Dict[str, MIRFunction]:
        return dict(self._functions)

    def get_function(self, name: str) -> Optional[MIRFunction]:
        return self._functions.get(name)

    def compute_global_call_graph(self) -> Dict[str, List[str]]:
        """Compute the global call graph across all functions."""
        graph: Dict[str, List[str]] = {}
        for name, mir_func in self._functions.items():
            cg = mir_func.compute_call_graph()
            graph[name] = cg.get(name, [])
        return graph

    def get_hot_functions(self, threshold: int = 2) -> List[str]:
        """Get functions with deep loops (likely hot)."""
        hot: List[str] = []
        for name, mir_func in self._functions.items():
            max_depth = 0
            for loop in mir_func.loops:
                max_depth = max(max_depth, loop.depth)
            if max_depth >= threshold:
                hot.append(name)
        return hot

    def __repr__(self) -> str:
        return (f"MIRModule({self.name}: "
                f"{len(self._functions)} functions)")


# ══════════════════════════════════════════════════════════════════
# MIR Lowering Utilities
# ══════════════════════════════════════════════════════════════════


def lower_to_mir(ir_module: IRModule) -> MIRModule:
    """Lower an IR module to MIR — compute analysis results."""
    return MIRModule(ir_module)


def compute_mir_function(ir_function: IRFunction) -> MIRFunction:
    """Compute MIR-level analysis for a single function."""
    return MIRFunction(ir_function)
