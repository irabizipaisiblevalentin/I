"""
IR SSA Utilities

Preparation for SSA form: phi node insertion, variable renaming,
def-use chains, use-def chains, and liveness analysis.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .basic_block import BasicBlock
from .function import IRFunction
from .instructions import Instruction, Phi
from .values import Value, UndefinedConstant
from .cfg import CFG

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Tuple


# ══════════════════════════════════════════════════════════════════
# Def-Use Chain
# ══════════════════════════════════════════════════════════════════


class DefUseChain:
    """Tracks definitions and uses of values."""
    __slots__ = ("_defs", "_uses")

    def __init__(self) -> None:
        object.__setattr__(self, "_defs", {})
        object.__setattr__(self, "_uses", {})

    def record_def(self, value: Value, instruction: Instruction) -> None:
        """Record that value is defined by instruction."""
        self._defs[id(value)] = instruction

    def record_use(self, value: Value, instruction: Instruction) -> None:
        """Record that value is used by instruction."""
        if id(value) not in self._uses:
            self._uses[id(value)] = []
        if instruction not in self._uses[id(value)]:
            self._uses[id(value)].append(instruction)

    def get_def(self, value: Value) -> Optional[Instruction]:
        """Get the instruction that defines this value."""
        return self._defs.get(id(value))

    def get_uses(self, value: Value) -> List[Instruction]:
        """Get all instructions that use this value."""
        return list(self._uses.get(id(value), []))

    @property
    def defs(self) -> Dict[int, Instruction]:
        return dict(self._defs)

    @property
    def uses(self) -> Dict[int, List[Instruction]]:
        return dict(self._uses)

    def __repr__(self) -> str:
        return f"DefUseChain(defs={len(self._defs)}, uses={len(self._uses)})"


# ══════════════════════════════════════════════════════════════════
# Liveness Analysis
# ══════════════════════════════════════════════════════════════════


class LivenessInfo:
    """Liveness information for a basic block."""
    __slots__ = ("_live_in", "_live_out", "_def", "_use")

    def __init__(self) -> None:
        object.__setattr__(self, "_live_in", set())
        object.__setattr__(self, "_live_out", set())
        object.__setattr__(self, "_def", set())
        object.__setattr__(self, "_use", set())

    @property
    def live_in(self) -> Set[Value]:
        return set(self._live_in)

    @property
    def live_out(self) -> Set[Value]:
        return set(self._live_out)

    @property
    def def_set(self) -> Set[Value]:
        return set(self._def)

    @property
    def use_set(self) -> Set[Value]:
        return set(self._use)


class LivenessAnalysis:
    """Computes liveness information for all blocks in a function."""
    __slots__ = ("_cfg", "_info")

    def __init__(self, cfg: CFG) -> None:
        object.__setattr__(self, "_cfg", cfg)
        object.__setattr__(self, "_info", {})
        self._compute()

    def _compute(self) -> None:
        """Compute liveness using iterative dataflow analysis."""
        info = {}
        for block in self._cfg.blocks:
            block_info = LivenessInfo()
            # Compute def and use for this block
            self._compute_def_use(block, block_info)
            info[id(block)] = block_info

        # Iterative fixpoint
        changed = True
        while changed:
            changed = False
            for block in reversed(self._cfg.reverse_post_order):
                bi = info[id(block)]

                # live_in = use ∪ (live_out - def)
                new_live_in = bi.use_set | (bi.live_out - bi.def_set)

                # live_out = ∪ live_in(successor)
                new_live_out: Set[Value] = set()
                for succ in block.successors:
                    new_live_out |= info[id(succ)].live_in

                if new_live_in != bi.live_in:
                    object.__setattr__(bi, "_live_in", new_live_in)
                    changed = True
                if new_live_out != bi.live_out:
                    object.__setattr__(bi, "_live_out", new_live_out)
                    changed = True

        object.__setattr__(self, "_info", info)

    def _compute_def_use(self, block: BasicBlock, info: LivenessInfo) -> None:
        defined: Set[Value] = set()
        used: Set[Value] = set()

        for inst in block:
            for op in inst.operands:
                if isinstance(op, Value) and op not in defined:
                    used.add(op)

            if inst.name:
                defined.add(inst)

        object.__setattr__(info, "_def", defined)
        object.__setattr__(info, "_use", used)

    def get_info(self, block: BasicBlock) -> LivenessInfo:
        """Get liveness info for a block."""
        return self._info.get(id(block), LivenessInfo())

    def is_live_in(self, value: Value, block: BasicBlock) -> bool:
        """Check if a value is live at the entry of a block."""
        info = self._info.get(id(block))
        return value in info.live_in if info else False

    def is_live_out(self, value: Value, block: BasicBlock) -> bool:
        """Check if a value is live at the exit of a block."""
        info = self._info.get(id(block))
        return value in info.live_out if info else False

    @property
    def all_blocks(self) -> Dict[int, LivenessInfo]:
        return dict(self._info)


# ══════════════════════════════════════════════════════════════════
# SSA Builder
# ══════════════════════════════════════════════════════════════════


class SSABuilder:
    """Utilities for converting to SSA form."""
    __slots__ = ("_cfg", "_liveness", "_def_use")

    def __init__(self, function: IRFunction) -> None:
        cfg = CFG(function)
        object.__setattr__(self, "_cfg", cfg)
        object.__setattr__(self, "_liveness", LivenessAnalysis(cfg))
        object.__setattr__(self, "_def_use", DefUseChain())

    @property
    def cfg(self) -> CFG:
        return self._cfg

    @property
    def liveness(self) -> LivenessAnalysis:
        return self._liveness

    @property
    def def_use(self) -> DefUseChain:
        return self._def_use

    def build_def_use_chains(self, function: IRFunction) -> DefUseChain:
        """Build def-use chains for a function."""
        chain = DefUseChain()
        for block in function:
            for inst in block:
                # Record definition
                if inst.name:
                    chain.record_def(inst, inst)
                # Record uses
                for op in inst.operands:
                    if isinstance(op, Value):
                        chain.record_use(op, inst)
        object.__setattr__(self, "_def_use", chain)
        return chain

    def insert_phi_nodes(self, function: IRFunction) -> List[Phi]:
        phi_nodes: List[Phi] = []
        cfg = self._cfg

        if not cfg.blocks:
            return []

        df = self._compute_dominance_frontiers(function, cfg)

        var_defs = {}
        var_types = {}
        for block in function:
            for inst in block:
                if inst.name:
                    base = inst.name.split('.')[0]
                    if base not in var_defs:
                        var_defs[base] = set()
                    var_defs[base].add(block)
                    if base not in var_types:
                        var_types[base] = inst.result_type

        existing_phis = set()
        for block in function:
            for inst in block:
                if isinstance(inst, Phi) and inst.name:
                    existing_phis.add((id(block), inst.name.split('.')[0]))

        for var_name, defining_blocks in var_defs.items():
            if len(defining_blocks) < 2:
                continue

            typ = var_types.get(var_name)
            if typ is None:
                continue

            defs = set(defining_blocks)
            worklist = list(defining_blocks)
            inserted = set()

            while worklist:
                block = worklist.pop(0)
                for df_block in df.get(id(block), set()):
                    key = (id(df_block), var_name)
                    if key in inserted or key in existing_phis:
                        continue

                    incoming = [(UndefinedConstant(typ), pred)
                                for pred in df_block.predecessors]

                    phi = Phi(var_name, typ, incoming)

                    first_inst = None
                    for inst in df_block:
                        if not isinstance(inst, Phi):
                            first_inst = inst
                            break

                    if first_inst:
                        df_block.insert_before(first_inst, phi)
                    else:
                        df_block.append(phi)

                    inserted.add(key)
                    phi_nodes.append(phi)

                    if df_block not in defs:
                        defs.add(df_block)
                        worklist.append(df_block)

        return phi_nodes

    def rename_variables(self, function: IRFunction) -> None:
        cfg = self._cfg
        if not function.entry_block:
            return

        counters = {}
        stacks = {}

        def children_of(block):
            result = []
            for b in function:
                if cfg.immediate_dominator(b) is block:
                    result.append(b)
            return result

        def rename(block):
            defs = []

            for inst in block:
                if inst.name:
                    base = inst.name.split('.')[0] if '.' in inst.name else inst.name
                    counters[base] = counters.get(base, 0) + 1
                    inst.name = f"{base}.{counters[base]}"
                    stacks.setdefault(base, []).append(inst)
                    defs.append(base)

            for succ in block.successors:
                for inst in succ:
                    if isinstance(inst, Phi):
                        base = inst.name.split('.')[0] if '.' in inst.name else inst.name
                        if stacks.get(base):
                            inst.remove_incoming(block)
                            inst.add_incoming(stacks[base][-1], block)

            for child in children_of(block):
                rename(child)

            for base in defs:
                stacks[base].pop()

        rename(function.entry_block)

    def _compute_dominance_frontiers(self, function: IRFunction, cfg: CFG) -> Dict:
        df = {}
        for block in function:
            df[id(block)] = set()

        for block in function:
            preds = block.predecessors
            if len(preds) < 2:
                continue
            idom_block = cfg.immediate_dominator(block)
            if idom_block is None:
                continue
            for pred in preds:
                runner = pred
                while runner is not None and runner is not idom_block:
                    df[id(runner)].add(block)
                    runner = cfg.immediate_dominator(runner)

        return df

    def get_live_at_block_entry(self, block: BasicBlock) -> Set[Value]:
        """Get values live at the entry of a block."""
        return self._liveness.get_info(block).live_in

    def get_live_at_block_exit(self, block: BasicBlock) -> Set[Value]:
        """Get values live at the exit of a block."""
        return self._liveness.get_info(block).live_out

    def __repr__(self) -> str:
        return f"SSABuilder(cfg={self._cfg})"
