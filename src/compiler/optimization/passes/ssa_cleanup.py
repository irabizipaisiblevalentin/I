from __future__ import annotations

from compiler.optimization.base import Pass, PassResult, PassImpact
from compiler.ir.module import IRModule
from compiler.ir.instructions import Phi, Add, Sub, Mul
from compiler.ir.values import IntConstant, FloatConstant


class SSACleanupPass(Pass):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("ssa_cleanup", level=1)

    def run(self, module: IRModule, ctx: object) -> PassResult:
        impact = PassImpact()
        changed = False
        for func in module.functions.values():
            changed |= self._eliminate_trivial_phis(func)
            changed |= self._eliminate_identity_copies(func)
            changed |= self._eliminate_dead_phis(func)
        if changed:
            impact.instructions_eliminated += 1
        return PassResult(changed=changed, impact=impact)

    def _eliminate_trivial_phis(self, func: object) -> bool:
        changed = False
        for bb in func.basic_blocks:
            to_remove: list[Phi] = []
            for inst in bb.instructions:
                if not isinstance(inst, Phi):
                    continue
                unique_values: set[int] = set()
                for val, _blk in inst.incoming:
                    unique_values.add(id(val))
                if len(unique_values) == 1 and len(inst.incoming) > 0:
                    replacement = inst.incoming[0][0]
                    self._replace_all_uses(inst, replacement)
                    to_remove.append(inst)
                    changed = True
            for phi in to_remove:
                bb.remove(phi)
        return changed

    def _eliminate_identity_copies(self, func: object) -> bool:
        changed = False
        for bb in func.basic_blocks:
            to_remove: list = []
            replacements: dict[int, object] = {}
            for inst in bb.instructions:
                if isinstance(inst, Add):
                    replacement = self._check_identity_add(inst)
                    if replacement is not None:
                        replacements[id(inst)] = replacement
                        to_remove.append(inst)
                        changed = True
                elif isinstance(inst, Sub):
                    replacement = self._check_identity_sub(inst)
                    if replacement is not None:
                        replacements[id(inst)] = replacement
                        to_remove.append(inst)
                        changed = True
                elif isinstance(inst, Mul):
                    replacement = self._check_identity_mul(inst)
                    if replacement is not None:
                        replacements[id(inst)] = replacement
                        to_remove.append(inst)
                        changed = True
            for inst in to_remove:
                replacement = replacements[id(inst)]
                self._replace_all_uses(inst, replacement)
                bb.remove(inst)
        return changed

    def _eliminate_dead_phis(self, func: object) -> bool:
        changed = False
        for bb in func.basic_blocks:
            to_remove: list[Phi] = []
            for inst in bb.instructions:
                if isinstance(inst, Phi) and inst.use_count == 0:
                    to_remove.append(inst)
                    changed = True
            for phi in to_remove:
                bb.remove(phi)
        return changed

    @staticmethod
    def _check_identity_add(inst: Add) -> object | None:
        lhs = inst.lhs
        rhs = inst.rhs
        if isinstance(rhs, IntConstant) and rhs.value == 0:
            return lhs
        if isinstance(lhs, IntConstant) and lhs.value == 0:
            return rhs
        if isinstance(rhs, FloatConstant) and rhs.value == 0.0:
            return lhs
        if isinstance(lhs, FloatConstant) and lhs.value == 0.0:
            return rhs
        return None

    @staticmethod
    def _check_identity_sub(inst: Sub) -> object | None:
        lhs = inst.lhs
        rhs = inst.rhs
        if isinstance(rhs, IntConstant) and rhs.value == 0:
            return lhs
        if isinstance(rhs, FloatConstant) and rhs.value == 0.0:
            return lhs
        return None

    @staticmethod
    def _check_identity_mul(inst: Mul) -> object | None:
        lhs = inst.lhs
        rhs = inst.rhs
        if isinstance(rhs, IntConstant) and rhs.value == 1:
            return lhs
        if isinstance(lhs, IntConstant) and lhs.value == 1:
            return rhs
        if isinstance(rhs, FloatConstant) and rhs.value == 1.0:
            return lhs
        if isinstance(lhs, FloatConstant) and lhs.value == 1.0:
            return rhs
        return None

    @staticmethod
    def _replace_all_uses(old_val: object, new_val: object) -> None:
        users = list(old_val.uses)
        for user in users:
            user.replace_uses_of(old_val, new_val)

    def estimated_complexity(self) -> str:
        return "O(n)"

    def performance_impact(self) -> str:
        return "low"

    def description(self) -> str:
        return "SSA cleanup: eliminate trivial phis, identity copies, and dead phis"
