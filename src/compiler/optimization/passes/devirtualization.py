from __future__ import annotations

from compiler.ir.instructions import Call
from compiler.ir.module import IRModule
from compiler.optimization.base import Pass, PassImpact, PassResult


class DevirtualizationPass(Pass):
    """Devirtualization: replace indirect calls with direct calls when the target is known.

    When a call site's target can be resolved to a single concrete function
    (e.g., through type analysis or constant propagation), replace the indirect
    call with a direct call. This enables inlining and other optimizations.
    """

    def __init__(self) -> None:
        super().__init__("devirtualization", level=0)

    def run(self, module: IRModule, ctx) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            for bb in func.basic_blocks:
                for inst in bb.instructions:
                    if not isinstance(inst, Call):
                        continue
                    callee = getattr(inst, "function", None)
                    if callee is None:
                        continue
                    if hasattr(callee, "name") and module.has_function(callee.name):
                        continue
                    direct_target = self._resolve_direct_target(callee, module)
                    if direct_target is not None:
                        object.__setattr__(inst, "_function", direct_target)
                        impact.instructions_combined += 1
                        changed = True
                        if ctx is not None:
                            ctx.record_transformation(
                                self.name,
                                f"devirtualized call to {callee.name} -> {direct_target.name}",
                            )
        return PassResult(changed=changed, impact=impact)

    def _resolve_direct_target(self, callee, module: IRModule):
        from compiler.ir.values import GlobalVariable
        if hasattr(callee, "name") and callee.name:
            target = module.get_function(callee.name)
            if target is not None:
                return target
        if isinstance(callee, GlobalVariable) and callee.initializer is not None:
            init_name = getattr(callee.initializer, "name", None)
            if init_name:
                target = module.get_function(init_name)
                if target is not None:
                    return target
        return None

    def estimated_complexity(self) -> str:
        return "O(n * m)"

    def performance_impact(self) -> str:
        return "high"

    def description(self) -> str:
        return "Devirtualization: convert indirect calls to direct calls"
