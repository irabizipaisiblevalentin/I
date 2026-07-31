from __future__ import annotations

from compiler.ir.module import IRModule
from compiler.optimization.base import Pass, PassImpact, PassResult


class RegisterAllocationPass(Pass):
    """Register allocation: assign virtual registers to physical registers.

    This pass prepares IR for code generation by assigning virtual register
    names to a finite set of physical registers. For the VM backend this is
    primarily a nop (VM uses virtual registers), but for native codegen this
    becomes a full linear-scan or graph-coloring allocator.

    Currently performs:
    - Virtual register identification
    - Spill cost estimation (future)
    - Register hint propagation (future)
    """

    def __init__(self) -> None:
        super().__init__("register_allocation", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            if ctx is not None:
                estimated_regs = self._estimate_registers(func)
                ctx.record_transformation(
                    self.name,
                    f"estimated {estimated_regs} virtual registers for '{func.name}'",
                )
        return PassResult(changed=changed, impact=impact)

    def _estimate_registers(self, func) -> int:
        count = 0
        for bb in func.basic_blocks:
            for inst in bb.instructions:
                if hasattr(inst, "name") and inst.name:
                    count += 1
        return count

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "medium"

    def description(self) -> str:
        return "Register allocation: assign virtual to physical registers"
