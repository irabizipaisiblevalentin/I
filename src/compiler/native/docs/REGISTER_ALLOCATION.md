# Register Allocation Guide

## Graph Coloring Algorithm Overview

The I native compiler implements a **Chaitin-Briggs-style graph coloring** register allocator in `register/allocator.py`. The algorithm proceeds in phases:

1. **Live interval analysis** -- determine the range of instructions where each value is live
2. **Interference graph construction** -- connect values that cannot share a register
3. **Coloring** -- assign physical registers using Kempe's simplification
4. **Spill insertion** -- when coloring fails, spill values to memory
5. **Coalescing** -- eliminate register-to-register copies (Briggs/George)

The allocator is iterative: if spills occur, spill code is inserted and the allocator re-runs (up to `max_iterations` times, default 4).

```
                +-----------+
                | IRFunction|
                +-----+-----+
                      |
                      v
            +---------+---------+
            | LiveRangeAnalysis |
            | (dataflow, liveness)|
            +---------+---------+
                      |
                      v
            +---------+---------+
            | Group by Register  |
            | Class (GPR, XMM)   |
            +---------+---------+
                      |
                      v
            +---------+---------+
            | InterferenceGraph  |
            | (build from        |
            |  overlapping       |
            |  intervals)        |
            +---------+---------+
                      |
                      v
            +---------+---------+
            | CoalescingOptimizer|
            | (Briggs / George)  |
            +---------+---------+
                      |
                      v
            +---------+---------+
            | Kempe Simplify     |
            | (remove nodes with |
            |  degree < K)       |
            +---------+---------+
                      |
                      v
            +---------+---------+
            | Color Assignment   |
            | (reverse traversal,|
            |  pick first free   |
            |  color)            |
            +---------+---------+
                     / \
                    /   \
              Success   Spill
                 |         |
                 |    +----+----+
                 |    | Spill    |
                 |    | Cost     |
                 |    | Heuristic|
                 |    +----+----+
                 |         |
                 |    +----+----+
                 |    | Insert   |
                 |    | Spill &  |
                 |    | Reload   |
                 |    +----+----+
                 |         |
                 +----<----+
                 |
                 v
         +-------+-------+
         | AllocationResult |
         +------------------+
```

---

## Live Interval Analysis

`LiveRangeAnalysis` in `register/liveness.py` computes the set of instructions where each value is alive.

### Numbering

Instructions are numbered sequentially across all basic blocks. This provides a linear ordering for interval comparison.

```python
# Instruction numbering
block 0: inst[0], inst[1], inst[2]
block 1: inst[3], inst[4], inst[5]
```

### LiveInterval

Each `LiveInterval` stores:

| Field      | Description                                    |
|------------|------------------------------------------------|
| `start`    | First instruction number where value is defined|
| `end`      | Last instruction number where value is used + 1|
| `value`    | The IR value                                   |
| `reg`      | Assigned physical register (if any)            |
| `is_fixed` | Pre-colored (e.g., fixed register arguments)   |

### Liveness Computation

The dataflow equations are solved iteratively:

```
live_in[b] = use[b] | (live_out[b] - def[b])
live_out[b] = union of live_in[succ] for all successors

Where:
  use[b]  = set of values used before being defined in block b
  def[b]  = set of values defined in block b
```

The solver iterates over blocks in reverse order until a fixed point is reached.

### Interval Construction

For each value:
- `start` = instruction number where the value is defined
- `end` = max(last use instruction number + 1, live_out of containing block)

For function arguments, `start = 0`.

---

## Interference Graph Construction

The `InterferenceGraph` (`register/allocator.py`) is an undirected graph where nodes represent values and edges represent interference (values that cannot share a physical register).

```python
graph = InterferenceGraph()
graph.add_node(value_a)
graph.add_node(value_b)
graph.add_edge(value_a, value_b)  # They interfere
```

### Interference Criterion

Two values `a` and `b` interfere if their live intervals overlap:

```
interfere(a, b) = live_interval[a].start < live_interval[b].end
               AND live_interval[b].start < live_interval[a].end
```

### Building the Graph

The graph is built in `_build_interference_graph()`:

```python
def _build_interference_graph(self, intervals):
    graph = InterferenceGraph()
    sorted_vals = sorted(intervals.keys(), key=lambda v: intervals[v].start)
    for v in intervals:
        graph.add_node(v)
    for i, a in enumerate(sorted_vals):
        ia = intervals[a]
        for b in sorted_vals[i + 1:]:
            ib = intervals[b]
            if ia.overlaps(ib):
                graph.add_edge(a, b)
    return graph
```

---

## Spill Cost Heuristics

When the graph contains more values than available registers, some values must be spilled to memory. Spill costs are computed in `_compute_spill_costs()`.

### Cost Formula

```
cost(v) = (sum of 10^depth for each use in a loop) / degree(v)
```

Where `depth` is the loop nesting depth of the containing block. Uses outside loops have `depth = 0` (cost = 1).

### Loop Depth

Loop depth is determined from the control flow graph's loop structure:

```python
for li in cfg.loops:
    for block in li.blocks:
        existing = block_depth.get(block, 0)
        if li.depth > existing:
            block_depth[block] = li.depth
```

### Spill Selection

Values with the lowest spill cost are spilled first. The allocator spills by preferring:
- Values used infrequently (low use count)
- Values used outside loops
- Values with high interference degree (many neighbors)

---

## Coalescing (Briggs / George)

The `CoalescingOptimizer` in `register/coalescing.py` eliminates register-to-register copy instructions by merging the live intervals of the source and destination.

### Move Representation

```python
@dataclass
class Move:
    dest: Value
    src: Value
```

### Coalescing Criteria

**Briggs Criterion (conservative)**:
```
conservative_ok(a, b):
    combined = neighbors(a) | neighbors(b)
    heavy = count of nodes in combined with degree >= K
    return heavy < K
```
Merge `a` and `b` if the merged node would have fewer than `K` neighbors with degree >= K.

**George Criterion** (used when Briggs fails):
```
george_ok(a, b):
    for each neighbor n of b:
        if n interferes with a:
            if degree(n) >= K: return False
        else:
            if degree(n) >= K: return False
    return True
```
All neighbors of `b` that interfere with `a` must have degree < K.

### Optimization Loop

```python
def _optimistic_coalesce(self):
    changed = True
    while changed:
        changed = False
        for move in moves:
            a = resolve(move.dest)  # Follow coalescing chain
            b = resolve(move.src)
            if a is b:
                continue  # Already same node
            if conservative_ok(a, b):
                merge(a, b)  # Briggs
            elif not graph.interferes(a, b) and george_criterion(a, b):
                merge(a, b)  # George
```

---

## Register Classes

The allocator groups values by register class before coloring. This ensures GPR values are only assigned to GPR registers and XMM values are only assigned to XMM registers.

### Defined Classes

```python
class RegisterClass(Enum):
    GPR = "gpr"      # General-purpose registers (rax, rbx, rcx, ...)
    XMM = "xmm"      # SSE/AVX registers (xmm0, xmm1, ...)
    MASK = "mask"    # AVX-512 mask registers (k0, k1, ...)
```

### Class Assignment

```python
def register_class_for(value: Value) -> RegisterClass:
    t = value.type
    if isinstance(t, (IntegerType, PointerType)):
        return RegisterClass.GPR
    if isinstance(t, (FloatType, VectorType)):
        return RegisterClass.XMM
    return RegisterClass.GPR  # Default
```

### Per-Class Coloring

The allocator processes each class independently:

```python
intervals_by_class = self._group_by_class(intervals)
for reg_class, cls_intervals in intervals_by_class.items():
    registers = _get_registers(target, reg_class)
    graph = self._build_interference_graph(cls_intervals)
    cls_allocation, cls_spilled = self._color(graph, registers, reg_class)
```

### x86-64 Register Lists

Defined in `register/allocator.py`:

```python
X86_64_GPRS:  # 15 registers (not including rsp)
    rax(0), rcx(1), rdx(2), rbx(3, callee), rsi(4), rdi(5),
    r8(6), r9(7), r10(8), r11(9), r12(10, callee), r13(11, callee),
    r14(12, callee), r15(13, callee), rbp(14, callee)

X86_64_XMMS:  # 16 registers
    xmm0-xmm15 (indices 0-15)
```

### ARM64 Register Lists

Defined in `target/arm64.py`:

```python
ARM64_GPRS:  # 31 registers
    x0-x30 (x18 is platform-reserved on macOS)

ARM64_SIMD:  # 32 registers
    v0-v31
```

### Color Assignment Algorithm

```python
def _color(self, graph, registers, reg_class):
    K = len(registers)
    stack = []
    g = graph.copy()

    # Kempe simplify: repeatedly remove nodes with degree < K
    while len(g) > 0:
        found = False
        for v in list(g.nodes):
            if g.degree(v) < K:
                stack.append(v)
                g.remove_node(v)
                found = True
                break
        if not found:
            v = list(g.nodes)[0]  # Spill candidate
            stack.append(v)
            g.remove_node(v)

    # Color assignment (reverse order)
    for v in reversed(stack):
        used_colors = {allocation[n].index for n in graph.neighbors(v) if n in allocation}
        for reg in registers:
            if reg.index not in used_colors:
                allocation[v] = reg
                break
        else:
            spills.add(v)  # No color available -> spill
```
