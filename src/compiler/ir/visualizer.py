"""
IR Visualizer

Generates visual representations of IR structures:
- Control Flow Graphs (CFG) in DOT format
- Basic Block graphs
- Call graphs
- Dependency graphs
- Graphviz output
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .module import IRModule
from .function import IRFunction
from .basic_block import BasicBlock
from .instructions import Instruction, Call, Branch, CondBranch, Phi
from .values import Value

if TYPE_CHECKING:
    from typing import Dict, List, Set, TextIO
    from .cfg import CFG


# ══════════════════════════════════════════════════════════════════
# IR Visualizer
# ══════════════════════════════════════════════════════════════════


class IRVisualizer:
    """Generates DOT-format visualizations of IR structures."""
    __slots__ = ("_counter",)

    def __init__(self) -> None:
        object.__setattr__(self, "_counter", 0)

    def _fresh_id(self, prefix: str = "node") -> str:
        c = self._counter
        self._counter += 1
        return f"{prefix}_{c}"

    # ── CFG Visualization ────────────────────────────────────────

    def cfg_to_dot(self, function: IRFunction) -> str:
        """Generate DOT format for a function's control flow graph."""
        lines = ["digraph CFG {"]
        lines.append('  node [shape=box, fontname="monospace"];')
        lines.append('  edge [fontname="monospace"];')
        lines.append("")

        for block in function:
            label = self._escape_dot(block.name or "entry")
            lines.append(f'  "{label}" [label="{label}\\n'
                        f'{block.instruction_count} insts"];')

        lines.append("")
        for block in function:
            label = self._escape_dot(block.name or "entry")
            for succ in block.successors:
                succ_label = self._escape_dot(succ.name)
                lines.append(f'  "{label}" -> "{succ_label}";')

        lines.append("}")
        return "\n".join(lines)

    def cfg_with_instructions(self, function: IRFunction) -> str:
        """Generate DOT format with instruction details in each block."""
        lines = ["digraph CFG {"]
        lines.append('  node [shape=box, fontname="monospace"];')
        lines.append("")

        for block in function:
            label = self._escape_dot(block.name or "entry")
            insts = "\\l".join(
                self._escape_dot(repr(i)) for i in block.non_terminating
            )
            lines.append(f'  "{label}" [label="{label}\\l{insts}\\l"];')

        lines.append("")
        for block in function:
            label = self._escape_dot(block.name or "entry")
            for succ in block.successors:
                succ_label = self._escape_dot(succ.name)
                lines.append(f'  "{label}" -> "{succ_label}";')

        lines.append("}")
        return "\n".join(lines)

    # ── Call Graph Visualization ─────────────────────────────────

    def call_graph_to_dot(self, module: IRModule) -> str:
        """Generate DOT format for the call graph of a module."""
        lines = ["digraph CallGraph {"]
        lines.append('  node [shape=ellipse, fontname="monospace"];')
        lines.append("")

        for func in module.functions:
            label = self._escape_dot(func.name)
            lines.append(f'  "@{label}";')

        lines.append("")
        for func in module.functions:
            caller = self._escape_dot(func.name)
            for block in func:
                for inst in block:
                    if isinstance(inst, Call) and hasattr(inst.function, 'name'):
                        callee = self._escape_dot(inst.function.name)
                        lines.append(f'  "@{caller}" -> "@{callee}";')

        lines.append("}")
        return "\n".join(lines)

    # ── Dominator Tree Visualization ─────────────────────────────

    def dominator_tree_to_dot(self, cfg: 'CFG') -> str:
        """Generate DOT format for a dominator tree."""
        lines = ["digraph DominatorTree {"]
        lines.append('  node [shape=ellipse, fontname="monospace"];')
        lines.append("")

        for block in cfg.blocks:
            label = self._escape_dot(block.name)
            lines.append(f'  "{label}";')

        lines.append("")
        for block in cfg.blocks:
            idom = cfg.immediate_dominator(block)
            if idom:
                label = self._escape_dot(block.name)
                idom_label = self._escape_dot(idom.name)
                lines.append(f'  "{idom_label}" -> "{label}";')

        lines.append("}")
        return "\n".join(lines)

    # ── Dependency Graph ─────────────────────────────────────────

    def dependency_graph_to_dot(self, function: IRFunction) -> str:
        """Generate DOT format for value dependencies in a function."""
        lines = ["digraph Dependencies {"]
        lines.append('  node [shape=box, fontname="monospace"];')
        lines.append("")

        value_ids: Dict[int, str] = {}
        for block in function:
            for inst in block:
                if inst.name:
                    fid = self._fresh_id("val")
                    value_ids[id(inst)] = fid
                    lines.append(f'  "{fid}" [label="{inst.name}\\n'
                                f'{inst.opcode.name}"];')

        lines.append("")
        for block in function:
            for inst in block:
                if id(inst) in value_ids:
                    for op in inst.operands:
                        if isinstance(op, Value) and id(op) in value_ids:
                            src = value_ids[id(op)]
                            dst = value_ids[id(inst)]
                            lines.append(f'  "{src}" -> "{dst}";')

        lines.append("}")
        return "\n".join(lines)

    # ── Text Graph ───────────────────────────────────────────────

    def cfg_to_text(self, function: IRFunction) -> str:
        """Generate a text representation of the CFG."""
        lines = [f"CFG for @{function.name}:"]
        lines.append("=" * 50)

        for block in function:
            label = block.name or "entry"
            succs = [s.name for s in block.successors]
            preds = [p.name for p in block.predecessors]
            lines.append(f"\n  {label}:")
            lines.append(f"    predecessors: {preds}")
            lines.append(f"    successors: {succs}")
            lines.append(f"    instructions: {block.instruction_count}")

            for inst in block:
                lines.append(f"      {inst}")

        return "\n".join(lines)

    # ── Utility ──────────────────────────────────────────────────

    def _escape_dot(self, text: str) -> str:
        """Escape text for DOT format."""
        return text.replace('"', '\\"').replace('\n', '\\n')

    def save_dot(self, dot_content: str, filepath: str) -> None:
        """Save DOT content to a file."""
        with open(filepath, "w") as f:
            f.write(dot_content)
            f.flush()


# ══════════════════════════════════════════════════════════════════
# Convenience Functions
# ══════════════════════════════════════════════════════════════════


def visualize_cfg(function: IRFunction) -> str:
    """Generate DOT format for a function's CFG."""
    return IRVisualizer().cfg_to_dot(function)


def visualize_call_graph(module: IRModule) -> str:
    """Generate DOT format for a module's call graph."""
    return IRVisualizer().call_graph_to_dot(module)


def print_cfg(function: IRFunction) -> str:
    """Generate text representation of a function's CFG."""
    return IRVisualizer().cfg_to_text(function)
