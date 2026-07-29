"""
IR Control Flow Graph Analysis

Provides dominator trees, post-dominator trees, loop detection,
critical edge identification, and reachability analysis.
"""
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from .function import IRFunction
from .basic_block import BasicBlock

if TYPE_CHECKING:
    from typing import Dict, List, Optional, Set, Tuple
    from .instructions import Instruction


# ══════════════════════════════════════════════════════════════════
# Loop Info
# ══════════════════════════════════════════════════════════════════


class LoopInfo:
    """Information about a detected loop."""
    __slots__ = ("_header", "_latches", "_blocks", "_depth", "_parent")

    def __init__(
        self,
        header: BasicBlock,
        latches: Optional[Set[BasicBlock]] = None,
        blocks: Optional[Set[BasicBlock]] = None,
        depth: int = 0,
        parent: Optional[LoopInfo] = None,
    ) -> None:
        object.__setattr__(self, "_header", header)
        object.__setattr__(self, "_latches", latches or set())
        object.__setattr__(self, "_blocks", blocks or {header})
        object.__setattr__(self, "_depth", depth)
        object.__setattr__(self, "_parent", parent)

    @property
    def header(self) -> BasicBlock:
        return self._header

    @property
    def latches(self) -> Set[BasicBlock]:
        return self._latches

    @property
    def blocks(self) -> Set[BasicBlock]:
        return self._blocks

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def parent(self) -> Optional[LoopInfo]:
        return self._parent

    @property
    def is_single_block(self) -> bool:
        return len(self._blocks) == 1

    def __repr__(self) -> str:
        return f"Loop(header={self._header.name}, depth={self._depth})"


# ══════════════════════════════════════════════════════════════════
# Control Flow Graph
# ══════════════════════════════════════════════════════════════════


class CFG:
    """Control Flow Graph analysis for an IR function."""
    __slots__ = ("_function", "_blocks", "_dom_tree", "_pdom_tree",
                 "_loops", "_reverse_post_order")

    def __init__(self, function: IRFunction) -> None:
        object.__setattr__(self, "_function", function)
        object.__setattr__(self, "_blocks", list(function.blocks))
        object.__setattr__(self, "_dom_tree", {})
        object.__setattr__(self, "_pdom_tree", {})
        object.__setattr__(self, "_loops", [])
        object.__setattr__(self, "_reverse_post_order", [])
        self._compute()

    # ── Properties ───────────────────────────────────────────────

    @property
    def function(self) -> IRFunction:
        return self._function

    @property
    def blocks(self) -> List[BasicBlock]:
        return list(self._blocks)

    @property
    def loops(self) -> List[LoopInfo]:
        return list(self._loops)

    @property
    def reverse_post_order(self) -> List[BasicBlock]:
        return list(self._reverse_post_order)

    # ── Computation ──────────────────────────────────────────────

    def _compute(self) -> None:
        if not self._blocks:
            return
        self._compute_reverse_post_order()
        self._compute_dominators()
        self._compute_post_dominators()
        self._detect_loops()

    # ── Reachability ─────────────────────────────────────────────

    def reachable_from(self, start: BasicBlock) -> Set[BasicBlock]:
        """Find all blocks reachable from a starting block."""
        visited: Set[BasicBlock] = set()
        worklist = [start]
        while worklist:
            block = worklist.pop()
            if block in visited:
                continue
            visited.add(block)
            for succ in block.successors:
                worklist.append(succ)
        return visited

    def is_reachable(self, source: BasicBlock, target: BasicBlock) -> bool:
        """Check if target is reachable from source."""
        return target in self.reachable_from(source)

    # ── Reverse Post Order ───────────────────────────────────────

    def _compute_reverse_post_order(self) -> None:
        """Compute reverse post-order traversal."""
        if not self._blocks:
            return
        visited: Set[BasicBlock] = set()
        post_order: List[BasicBlock] = []
        entry = self._function.entry_block
        if entry is None:
            return

        def dfs(block: BasicBlock) -> None:
            if block in visited:
                return
            visited.add(block)
            for succ in block.successors:
                dfs(succ)
            post_order.append(block)

        dfs(entry)
        object.__setattr__(self, "_reverse_post_order", list(reversed(post_order)))

    # ── Dominator Tree ───────────────────────────────────────────

    def _compute_dominators(self) -> None:
        """Compute dominator tree using iterative algorithm."""
        if not self._reverse_post_order:
            return

        entry = self._function.entry_block
        if entry is None:
            return

        rpo_index = {id(b): i for i, b in enumerate(self._reverse_post_order)}
        block_map = {id(b): b for b in self._reverse_post_order}

        idoms: Dict[int, int] = {}
        idoms[id(entry)] = id(entry)

        changed = True
        while changed:
            changed = False
            for block in self._reverse_post_order:
                if block is entry:
                    continue

                preds = block.predecessors
                if not preds:
                    continue

                # Find first predecessor with computed dominator
                new_idom = None
                for pred in preds:
                    if id(pred) in idoms:
                        new_idom = id(pred)
                        break

                if new_idom is None:
                    continue

                # Intersect with remaining predecessors
                for pred in preds[1:]:
                    if id(pred) not in idoms:
                        continue
                    new_idom = self._intersect(
                        new_idom, id(pred), idoms, rpo_index
                    )

                if new_idom != idoms.get(id(block)):
                    idoms[id(block)] = new_idom
                    changed = True

        # Build dominator map: block_id -> parent_block_id (entry maps to None)
        dom_tree = {}
        for block in self._reverse_post_order:
            bid = id(block)
            if bid in idoms:
                if idoms[bid] == bid:
                    dom_tree[bid] = None  # entry
                else:
                    dom_tree[bid] = idoms[bid]
        object.__setattr__(self, "_dom_tree", dom_tree)

    @staticmethod
    def _intersect(b1: int, b2: int,
                   idoms: Dict[int, int],
                   rpo_index: Dict[int, int]) -> int:
        """Find closest common dominator of b1 and b2."""
        while b1 != b2:
            while rpo_index.get(b1, 0) > rpo_index.get(b2, 0):
                b1 = idoms.get(b1, b1)
            while rpo_index.get(b2, 0) > rpo_index.get(b1, 0):
                b2 = idoms.get(b2, b2)
        return b1

    def dominates(self, dominator: BasicBlock, target: BasicBlock) -> bool:
        """Check if dominator dominates target."""
        if dominator is target:
            return True
        current = id(target)
        while current in self._dom_tree:
            parent = self._dom_tree[current]
            if parent is None:
                return dominator is self._function.entry_block
            if parent == id(dominator):
                return True
            current = parent
        return False

    def immediate_dominator(self, block: BasicBlock) -> Optional[BasicBlock]:
        """Get the immediate dominator of a block."""
        did = self._dom_tree.get(id(block))
        if did is None:
            return None
        for b in self._blocks:
            if id(b) == did:
                return b
        return None

    # ── Post-Dominator Tree ──────────────────────────────────────

    def _compute_post_dominators(self) -> None:
        if not self._blocks:
            return

        exits = [b for b in self._blocks if len(b.successors) == 0]
        if not exits:
            return

        virtual_exit = BasicBlock("__virtual_exit__")
        for exit_b in exits:
            exit_b.add_successor(virtual_exit)
            virtual_exit.add_predecessor(exit_b)

        all_blocks_rev = list(self._blocks) + [virtual_exit]
        rev_successors: Dict[int, List[int]] = {}
        rev_predecessors: Dict[int, List[int]] = {}
        for b in all_blocks_rev:
            rev_successors[id(b)] = []
            rev_predecessors[id(b)] = []
        for b in all_blocks_rev:
            for succ in b.successors:
                if id(succ) in rev_successors:
                    rev_successors[id(succ)].append(id(b))
                    rev_predecessors[id(b)].append(id(succ))

        rev_rpo: List[int] = []
        visited_rev: Set[int] = set()

        def dfs_rev(bid: int) -> None:
            if bid in visited_rev:
                return
            visited_rev.add(bid)
            for pred_id in rev_predecessors.get(bid, []):
                if pred_id not in visited_rev:
                    dfs_rev(pred_id)
            rev_rpo.append(bid)

        dfs_rev(id(virtual_exit))

        rpo_index = {bid: i for i, bid in enumerate(rev_rpo)}

        rev_idoms: Dict[int, int] = {}
        rev_idoms[id(virtual_exit)] = id(virtual_exit)

        changed = True
        while changed:
            changed = False
            for bid in rev_rpo:
                if bid == id(virtual_exit):
                    continue
                preds = rev_predecessors.get(bid, [])
                if not preds:
                    continue

                new_idom = None
                for pred_id in preds:
                    if pred_id in rev_idoms:
                        new_idom = pred_id
                        break
                if new_idom is None:
                    continue

                for pred_id in preds[1:]:
                    if pred_id not in rev_idoms:
                        continue
                    new_idom = self._intersect(
                        new_idom, pred_id, rev_idoms, rpo_index
                    )

                if new_idom != rev_idoms.get(bid):
                    rev_idoms[bid] = new_idom
                    changed = True

        for exit_b in exits:
            exit_b.remove_successor(virtual_exit)
            virtual_exit.remove_predecessor(exit_b)

        block_map = {id(b): b for b in self._blocks}
        pdom_map: Dict[int, int] = {}
        for bid in self._blocks:
            b_id = id(bid)
            if b_id in rev_idoms:
                idom_id = rev_idoms[b_id]
                if idom_id == id(virtual_exit):
                    pdom_map[b_id] = None
                elif idom_id in block_map:
                    pdom_map[b_id] = idom_id
        object.__setattr__(self, "_pdom_tree", pdom_map)

    def post_dominates(self, post_dominator: BasicBlock, target: BasicBlock) -> bool:
        if post_dominator is target:
            return True
        current = id(target)
        visited = set()
        while current in self._pdom_tree:
            if current in visited:
                break
            visited.add(current)
            parent = self._pdom_tree.get(current)
            if parent is None:
                return False
            if parent == id(post_dominator):
                return True
            current = parent
        return False

    def dominance_frontier(self, block: BasicBlock) -> Set[BasicBlock]:
        bid = id(block)
        if bid not in self._dom_tree:
            return set()

        block_map = {id(b): b for b in self._blocks}
        frontiers: Set[BasicBlock] = set()

        for b in self._blocks:
            for pred in b.predecessors:
                if not self.dominates(block, pred):
                    continue
                if not self.dominates(block, b):
                    frontiers.add(b)
                    break

        return frontiers

    def dominates_instruction(
        self, dom_inst: Instruction, target_inst: Instruction
    ) -> bool:
        dom_block = dom_inst.parent
        target_block = target_inst.parent
        if dom_block is None or target_block is None:
            return False
        if dom_block is target_block:
            for inst in dom_block.instructions:
                if inst is dom_inst:
                    return True
                if inst is target_inst:
                    return False
            return False
        if not self.dominates(dom_block, target_block):
            return False
        return True

    # ── Loop Detection ───────────────────────────────────────────

    def _detect_loops(self) -> None:
        """Detect loops using back-edge analysis."""
        loops: List[LoopInfo] = []

        for block in self._blocks:
            for succ in block.successors:
                # Back edge: succ dominates block
                if self.dominates(succ, block):
                    # Found a natural loop
                    loop_blocks = self._find_loop_blocks(succ, block)
                    loop = LoopInfo(
                        header=succ,
                        latches={block},
                        blocks=loop_blocks,
                    )
                    loops.append(loop)

        # Compute nesting depth
        for i, loop_a in enumerate(loops):
            depth = 1
            for j, loop_b in enumerate(loops):
                if i != j and loop_a.header in loop_b.blocks:
                    depth += 1
            object.__setattr__(loop_a, "_depth", depth)

        # Set parent relationships
        for loop in loops:
            for other in loops:
                if loop is not other and loop.header in other.blocks:
                    object.__setattr__(loop, "_parent", other)
                    break

        object.__setattr__(self, "_loops", loops)

    def _find_loop_blocks(
        self, header: BasicBlock, latch: BasicBlock
    ) -> Set[BasicBlock]:
        """Find all blocks in a natural loop."""
        loop_blocks = {header}
        worklist = [latch]
        while worklist:
            block = worklist.pop()
            if block in loop_blocks:
                continue
            loop_blocks.add(block)
            for pred in block.predecessors:
                if pred not in loop_blocks:
                    worklist.append(pred)
        return loop_blocks

    # ── Critical Edges ───────────────────────────────────────────

    def find_critical_edges(self) -> List[Tuple[BasicBlock, BasicBlock]]:
        """Find critical edges (need splitting for optimization)."""
        critical = []
        for block in self._blocks:
            successors = block.successors
            if len(successors) > 1:
                for succ in successors:
                    if len(succ.predecessors) > 1:
                        critical.append((block, succ))
        return critical

    def is_critical_edge(
        self, source: BasicBlock, target: BasicBlock
    ) -> bool:
        """Check if an edge is critical."""
        return (len(source.successors) > 1 and len(target.predecessors) > 1)

    # ── Utility ──────────────────────────────────────────────────

    def block_index(self, block: BasicBlock) -> int:
        """Get the index of a block in the function."""
        for i, b in enumerate(self._blocks):
            if b is block:
                return i
        return -1

    @property
    def entry_block(self) -> Optional[BasicBlock]:
        return self._function.entry_block

    @property
    def exit_blocks(self) -> List[BasicBlock]:
        """Blocks with no successors (return/unreachable)."""
        return [b for b in self._blocks if len(b.successors) == 0]

    def __repr__(self) -> str:
        return (f"CFG({self._function.name}: "
                f"{len(self._blocks)} blocks, "
                f"{len(self._loops)} loops)")
