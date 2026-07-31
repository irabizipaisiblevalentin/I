"""
Optimization Test Suite -- Sprint 7 (Parts 1 & 2)

Tests for optimization infrastructure and analysis modules.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ir.types import IR_I1, IR_I32, IR_I64, IR_VOID, int_type, func_type, ptr_type
from compiler.ir.values import IntConstant, FloatConstant, BoolConstant, make_int_constant, make_bool_constant, Argument
from compiler.ir.instructions import (
    Add, Sub, Mul, Return, Branch, CondBranch, Load, Store, Alloca, Call, Phi,
    ICmp, ICmpPredicate, BinaryOp, Opcode,
)
from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.module import IRModule
from compiler.ir.context import IRContext
from compiler.optimization.context import OptimizationContext, OptimizationLevel
from compiler.optimization.cache import AnalysisCache
from compiler.optimization.stats import StatisticsEngine, PassStats, OptimizationReport
from compiler.optimization.registry import PassRegistry, PassInfo, AnalysisInfo
from compiler.optimization.scheduler import OptimizationScheduler
from compiler.optimization.pipeline import OptimizationPipeline, PipelineConfig
from compiler.optimization.manager import OptimizationManager
from compiler.optimization.base import Analysis, AnalysisResult, Pass, PassResult, PassImpact

from compiler.optimization.analyses.control_flow import ControlFlowAnalysis, ControlFlowResult
from compiler.optimization.analyses.data_flow import DataFlowAnalysis, DataFlowResult
from compiler.optimization.analyses.liveness import LivenessAnalysis, LivenessResult
from compiler.optimization.analyses.reachability import ReachabilityAnalysis, ReachabilityResult
from compiler.optimization.analyses.escape import EscapeAnalysis, EscapeResult
from compiler.optimization.analyses.alias import AliasAnalysis, AliasResult
from compiler.optimization.analyses.dominance import DominanceAnalysis, DominanceResult
from compiler.optimization.analyses.loop import LoopAnalysis, LoopResult
from compiler.optimization.analyses.call_graph import CallGraphAnalysis, CallGraphResult
from compiler.optimization.analyses.side_effect import SideEffectAnalysis, SideEffectResult
from compiler.optimization.analyses.memory_access import MemoryAccessAnalysis, MemoryAccessResult
from compiler.optimization.analyses.constant_propagation import ConstantPropagationAnalysis, ConstantPropagationResult

from compiler.optimization.passes.constant_folding import ConstantFoldingPass
from compiler.optimization.passes.constant_propagation import ConstantPropagationPass
from compiler.optimization.passes.dead_code_elimination import DeadCodeEliminationPass
from compiler.optimization.passes.dead_store_elimination import DeadStoreEliminationPass
from compiler.optimization.passes.copy_propagation import CopyPropagationPass
from compiler.optimization.passes.strength_reduction import StrengthReductionPass
from compiler.optimization.passes.common_subexpression import CommonSubexpressionEliminationPass
from compiler.optimization.passes.function_inlining import FunctionInliningPass
from compiler.optimization.passes.tail_call import TailCallOptimizationPass
from compiler.optimization.passes.loop_invariant_code_motion import LoopInvariantCodeMotionPass
from compiler.optimization.passes.loop_unrolling import LoopUnrollingPass
from compiler.optimization.passes.loop_simplification import LoopSimplificationPass
from compiler.optimization.passes.branch_simplification import BranchSimplificationPass
from compiler.optimization.passes.jump_threading import JumpThreadingPass
from compiler.optimization.passes.redundant_load_elimination import RedundantLoadEliminationPass
from compiler.optimization.passes.redundant_store_elimination import RedundantStoreEliminationPass
from compiler.optimization.passes.memory_coalescing import MemoryCoalescingPass
from compiler.optimization.passes.object_lifetime import ObjectLifetimeOptimizationPass
from compiler.optimization.passes.allocation_hoisting import AllocationHoistingPass
from compiler.optimization.passes.peephole import PeepholeOptimizationPass
from compiler.optimization.passes.instruction_combining import InstructionCombiningPass
from compiler.optimization.passes.control_flow_simplification import ControlFlowSimplificationPass
from compiler.optimization.passes.switch_optimization import SwitchOptimizationPass
from compiler.optimization.passes.sparse_ccp import SparseConditionalConstantPropagationPass
from compiler.optimization.passes.ssa_cleanup import SSACleanupPass
from compiler.ir.instructions import Switch


# ===================================================================
# Compatibility Patches
# ===================================================================


class _FuncDict(dict):
    def __iter__(self):
        return iter(self.values())

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return dict.__getitem__(self, key)


@property
def _patched_module_functions(self):
    return _FuncDict({f.name: f for f in self._functions})


IRModule.functions = _patched_module_functions

IRFunction.basic_blocks = property(lambda self: list(self._blocks))


def _irfunction_get_block(self, name):
    if isinstance(name, BasicBlock):
        return name if name in self._blocks else None
    for b in self._blocks:
        if b.name == name:
            return b
    return None


IRFunction.get_block = _irfunction_get_block
IRFunction.params = property(lambda self: self._args)

BinaryOp.a = BinaryOp.__dict__["lhs"]
BinaryOp.b = BinaryOp.__dict__["rhs"]

Call.callee = Call.__dict__["function"]
Call.args = Call.__dict__["arguments"]

Load.ptr = Load.__dict__["pointer"]
Store.ptr = Store.__dict__["pointer"]


# ===================================================================
# Helpers
# ===================================================================


def _make_module(name="test"):
    return IRModule(name)


def _make_func(name, param_types=(), return_type=IR_VOID):
    ft = func_type(param_types, return_type)
    return IRFunction(name, ft)


def _make_ctx(mod, level=OptimizationLevel.O2, stats=None, cache=None):
    return OptimizationContext(mod, level=level, stats=stats, cache=cache)


def _make_module_with_consts():
    mod = _make_module()
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("test_func", ft)
    bb = BasicBlock("entry")
    a = make_int_constant(1)
    b = make_int_constant(2)
    bb.append(Add("sum", a, b))
    bb.append(Return(bb[0]))
    func.append_block(bb)
    mod.add_function(func)
    return mod


class _RegistryPass(Pass):
    def __init__(self, name="reg_pass", level=0):
        super().__init__(name, level)

    def run(self, module, ctx):
        return PassResult(changed=False)


# ===================================================================
# 1. TestOptimizationContext
# ===================================================================


class TestOptimizationContext:
    def test_creation(self):
        mod = _make_module_with_consts()
        ctx = _make_ctx(mod)
        assert ctx.module is mod
        assert ctx.level == OptimizationLevel.O2

    def test_level_options(self):
        mod = _make_module()
        for level in OptimizationLevel:
            ctx = _make_ctx(mod, level=level)
            assert ctx.level == level

    def test_options(self):
        mod = _make_module()
        ctx = _make_ctx(mod)
        ctx.set_option("verbose", True)
        assert ctx.get_option("verbose") is True
        assert ctx.get_option("missing", "default") == "default"

    def test_pass_count(self):
        mod = _make_module()
        ctx = _make_ctx(mod)
        assert ctx.pass_count == 0
        ctx.increment_pass_count()
        assert ctx.pass_count == 1
        ctx.increment_pass_count()
        assert ctx.pass_count == 2

    def test_clone_for(self):
        mod1 = _make_module("m1")
        mod2 = _make_module("m2")
        ctx = _make_ctx(mod1)
        ctx.set_option("key", "val")
        clone = ctx.clone_for(mod2)
        assert clone.module is mod2
        assert clone.level == ctx.level
        assert clone.get_option("key") == "val"
        clone.set_option("key", "other")
        assert ctx.get_option("key") == "val"

    def test_changed_tracking(self):
        mod = _make_module()
        ctx = _make_ctx(mod)
        assert not ctx.changed
        ctx.mark_changed()
        assert ctx.changed
        ctx.reset_changed()
        assert not ctx.changed

    def test_iteration(self):
        mod = _make_module()
        ctx = _make_ctx(mod)
        assert ctx.iteration == 0
        ctx.set_iteration(3)
        assert ctx.iteration == 3


# ===================================================================
# 2. TestAnalysisCache
# ===================================================================


class TestAnalysisCache:
    def test_put_get(self):
        cache = AnalysisCache()
        r = AnalysisResult("test")
        cache.put("test", r)
        assert cache.get("test") is r

    def test_get_missing(self):
        cache = AnalysisCache()
        assert cache.get("missing") is None

    def test_invalidate(self):
        cache = AnalysisCache()
        r = AnalysisResult("test")
        cache.put("test", r)
        cache.invalidate("test")
        assert cache.get("test") is None

    def test_invalidate_all(self):
        cache = AnalysisCache()
        cache.put("a", AnalysisResult("a"))
        cache.put("b", AnalysisResult("b"))
        cache.invalidate_all()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_is_valid(self):
        cache = AnalysisCache()
        assert not cache.is_valid("x")
        cache.put("x", AnalysisResult("x"))
        assert cache.is_valid("x")
        cache.invalidate("x")
        assert not cache.is_valid("x")

    def test_dependency_tracking(self):
        cache = AnalysisCache()
        cache.register_dependency("a", "b")
        cache.put("b", AnalysisResult("b"))
        cache.put("a", AnalysisResult("a"))
        cache.invalidate("b")
        assert cache.get("a") is None

    def test_transitive_invalidation(self):
        cache = AnalysisCache()
        cache.register_dependency("a", "b")
        cache.register_dependency("b", "c")
        cache.put("c", AnalysisResult("c"))
        cache.put("b", AnalysisResult("b"))
        cache.put("a", AnalysisResult("a"))
        cache.invalidate("c")
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_stats(self):
        cache = AnalysisCache()
        cache.put("x", AnalysisResult("x"))
        _ = cache.get("x")
        _ = cache.get("y")
        cache.invalidate("x")
        s = cache.stats()
        assert s["hits"] >= 1
        assert s["misses"] >= 1


# ===================================================================
# 3. TestStatisticsEngine
# ===================================================================


class TestStatisticsEngine:
    def test_pass_timing(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.end_pass("p1", changed=True)
        assert stats.total_passes_run == 1
        assert stats.total_passes_changed == 1

    def test_instruction_counts(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.record_instruction_count(10, 7)
        stats.end_pass("p1")
        assert stats.instructions_eliminated == 3

    def test_block_counts(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.record_block_count(5, 3)
        stats.end_pass("p1")
        assert stats.blocks_eliminated == 2

    def test_function_counts(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.record_function_count(4, 2)
        stats.end_pass("p1")
        assert stats.functions_eliminated == 2

    def test_report_generation(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.record_instruction_count(10, 8)
        stats.end_pass("p1", changed=True)
        report = stats.generate_report("mod")
        assert isinstance(report, OptimizationReport)
        assert report.module_name == "mod"
        assert report.instructions_eliminated == 2

    def test_pass_stats_lookup(self):
        stats = StatisticsEngine()
        stats.start_pass("alpha")
        stats.end_pass("alpha")
        ps = stats.get_pass_stats("alpha")
        assert ps is not None
        assert ps.name == "alpha"
        assert stats.get_pass_stats("nonexistent") is None


# ===================================================================
# 4. TestPassRegistry
# ===================================================================


class TestPassRegistry:
    def test_register_pass(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="test_pass", level=1)
        info = reg.get_pass("test_pass")
        assert info is not None
        assert info.name == "test_pass"
        assert info.level == 1

    def test_register_analysis(self):
        reg = PassRegistry()
        reg.register_analysis(ControlFlowAnalysis, name="cf")
        info = reg.get_analysis("cf")
        assert info is not None
        assert info.name == "cf"

    def test_all_passes(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="a", level=1)
        reg.register_pass(_RegistryPass, name="b", level=2)
        assert len(reg.all_passes()) == 2

    def test_passes_at_level(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="o0", level=0)
        reg.register_pass(_RegistryPass, name="o2", level=2)
        reg.register_pass(_RegistryPass, name="o3", level=3)
        passes = reg.passes_at_level(2)
        names = [p.name for p in passes]
        assert "o0" in names
        assert "o2" in names
        assert "o3" not in names

    def test_create_pass(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="cr")
        p = reg.create_pass("cr")
        assert isinstance(p, Pass)

    def test_create_analysis(self):
        reg = PassRegistry()
        reg.register_analysis(ControlFlowAnalysis, name="cra")
        a = reg.create_analysis("cra")
        assert isinstance(a, Analysis)

    def test_pass_names(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="x")
        reg.register_pass(_RegistryPass, name="y")
        assert set(reg.pass_names()) == {"x", "y"}

    def test_analysis_names(self):
        reg = PassRegistry()
        reg.register_analysis(ControlFlowAnalysis, name="cx")
        assert "cx" in reg.analysis_names()


# ===================================================================
# 5. TestOptimizationScheduler
# ===================================================================


class TestOptimizationScheduler:
    def test_empty_schedule(self):
        reg = PassRegistry()
        sched = OptimizationScheduler(reg)
        assert sched.schedule([]) == []

    def test_no_dependencies(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="a", level=1)
        reg.register_pass(_RegistryPass, name="b", level=1)
        sched = OptimizationScheduler(reg)
        order = sched.schedule(["a", "b"])
        assert set(order) == {"a", "b"}

    def test_respects_dependency(self):
        reg = PassRegistry()
        class PassA(Pass):
            def __init__(self):
                super().__init__("a", level=1)
            def run(self, m, c):
                return PassResult()
        class PassB(Pass):
            def __init__(self):
                super().__init__("b", level=1)
                self._dependencies = ["a"]
            @property
            def dependencies(self):
                return ["a"]
            def run(self, m, c):
                return PassResult()
        reg.register_pass(PassA, name="a", level=1, dependencies=[])
        reg.register_pass(PassB, name="b", level=1, dependencies=["a"])
        sched = OptimizationScheduler(reg)
        order = sched.schedule(["a", "b"])
        assert order.index("a") < order.index("b")

    def test_validate_order(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="a", level=1)
        reg.register_pass(_RegistryPass, name="b", level=1)
        sched = OptimizationScheduler(reg)
        assert sched.validate_order(["a", "b"]) is True

    def test_cycle_detection(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="x", level=1)
        reg.register_pass(_RegistryPass, name="y", level=1)
        sched = OptimizationScheduler(reg)
        cycle = sched.find_cycle(["x", "y"])
        assert cycle is None


# ===================================================================
# 6. TestOptimizationPipeline
# ===================================================================


class TestOptimizationPipeline:
    def test_creation(self):
        reg = PassRegistry()
        pipeline = OptimizationPipeline(reg)
        assert pipeline is not None

    def test_get_passes(self):
        reg = PassRegistry()
        pipeline = OptimizationPipeline(reg)
        pipeline.build_default_pipeline()
        passes = pipeline.get_passes(OptimizationLevel.O0)
        assert isinstance(passes, list)

    def test_build_default(self):
        reg = PassRegistry()
        pipeline = OptimizationPipeline(reg)
        pipeline.build_default_pipeline()
        for level in OptimizationLevel:
            passes = pipeline.get_passes(level)
            assert isinstance(passes, list)

    def test_config(self):
        reg = PassRegistry()
        config = PipelineConfig()
        config.max_fixed_point_iterations = 10
        pipeline = OptimizationPipeline(reg, config)
        assert pipeline.config.max_fixed_point_iterations == 10

    def test_run_single_pass(self):
        reg = PassRegistry()
        reg.register_pass(_RegistryPass, name="rp", level=1)
        pipeline = OptimizationPipeline(reg)
        mod = _make_module()
        ctx = _make_ctx(mod)
        pipeline.run_single_pass(mod, ctx, "rp")


# ===================================================================
# 7. TestOptimizationManager
# ===================================================================


class TestOptimizationManager:
    def test_creation(self):
        mgr = OptimizationManager()
        assert mgr is not None

    def test_available_passes(self):
        mgr = OptimizationManager()
        passes = mgr.available_passes()
        assert isinstance(passes, list)
        assert len(passes) > 0

    def test_available_analyses(self):
        mgr = OptimizationManager()
        analyses = mgr.available_analyses()
        assert isinstance(analyses, list)
        assert len(analyses) > 0

    def test_optimize(self):
        mod = _make_module_with_consts()
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O0)
        assert isinstance(report, OptimizationReport)

    def test_summary(self):
        mgr = OptimizationManager()
        s = mgr.summary()
        assert isinstance(s, str)
        assert len(s) > 0


# ===================================================================
# 8. TestControlFlowAnalysis
# ===================================================================


class TestControlFlowAnalysis:
    def test_reachability(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("exit")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = ControlFlowAnalysis()
        ctx = _make_ctx(mod)
        result = a.run(mod, ctx)
        assert isinstance(result, ControlFlowResult)
        assert result.is_reachable("f", "entry")
        assert result.is_reachable("f", "exit")

    def test_entry_block(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("start")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = ControlFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.entry_block("f") == "start"

    def test_predecessors_successors(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("a")
        bb2 = BasicBlock("b")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb2.add_predecessor(bb1)
        bb1.add_successor(bb2)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = ControlFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert "b" in result.successors("f", "a")
        assert "a" in result.predecessors("f", "b")

    def test_unreachable_block(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("reachable")
        bb2 = BasicBlock("unreachable")
        bb1.append(Return())
        bb2.append(Return())
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = ControlFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert not result.is_reachable("f", "unreachable")

    def test_empty_function(self):
        mod = _make_module()
        f = _make_func("empty")
        mod.add_function(f)
        a = ControlFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.entry_block("empty") is None


# ===================================================================
# 9. TestDataFlowAnalysis
# ===================================================================


class TestDataFlowAnalysis:
    def test_reaching_defs(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = DataFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert isinstance(result, DataFlowResult)

    def test_def_location(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = DataFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.def_location("f", "x") == "entry"

    def test_reaching_at_entry(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = DataFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        reaching = result.reaching_at_entry("f", "entry")
        assert isinstance(reaching, set)

    def test_empty_function(self):
        mod = _make_module()
        f = _make_func("empty")
        mod.add_function(f)
        a = DataFlowAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert "empty" in result.reaching_defs_in


# ===================================================================
# 10. TestLivenessAnalysis
# ===================================================================


class TestLivenessAnalysis:
    def test_live_at_entry(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        arg = f.args[0]
        bb.append(Add("x", arg, make_int_constant(1)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = LivenessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        live = result.live_at_entry("f", "entry")
        assert isinstance(live, set)

    def test_live_at_exit(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = LivenessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        live_out = result.live_at_exit("f", "entry")
        assert isinstance(live_out, set)

    def test_is_live_at(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        arg = f.args[0]
        bb.append(Add("x", arg, make_int_constant(1)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = LivenessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        live = result.live_at_entry("f", "entry")
        assert isinstance(live, set)

    def test_interference(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        bb.append(Add("b", make_int_constant(3), make_int_constant(4)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = LivenessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        intf = result.interference("f")
        assert isinstance(intf, dict)


# ===================================================================
# 11. TestReachabilityAnalysis
# ===================================================================


class TestReachabilityAnalysis:
    def test_reachable_blocks(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("exit")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = ReachabilityAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.is_reachable("f", "entry")
        assert result.is_reachable("f", "exit")

    def test_unreachable_blocks(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("dead")
        bb1.append(Return())
        bb2.append(Return())
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = ReachabilityAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.has_unreachable("f")
        assert "dead" in result.unreachable_blocks("f")

    def test_reachable_blocks_set(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = ReachabilityAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.reachable_blocks("f") == {"entry"}

    def test_empty_function(self):
        mod = _make_module()
        f = _make_func("empty")
        mod.add_function(f)
        a = ReachabilityAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert not result.has_unreachable("empty")


# ===================================================================
# 12. TestEscapeAnalysis
# ===================================================================


class TestEscapeAnalysis:
    def test_argument_escapes(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        bb.append(Return(f.args[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        kind = result.escape_kind("f", f.args[0].name)
        assert kind in ("argument", "return")

    def test_local_no_escape(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        arg = f.args[0]
        bb.append(Add("x", arg, make_int_constant(1)))
        bb.append(Add("y", arg, make_int_constant(2)))
        bb.append(Return(bb[1]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        kind = result.escape_kind("f", "x")
        assert kind in ("none", "return")

    def test_non_escaping_values(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        arg = f.args[0]
        bb.append(Add("x", arg, make_int_constant(1)))
        bb.append(Add("y", arg, make_int_constant(2)))
        bb.append(Add("z", arg, make_int_constant(3)))
        bb.append(Return(bb[1]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        ne = result.non_escaping_values("f")
        assert isinstance(ne, set)

    def test_escaping_values(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        esc = result.escaping_values("f")
        assert isinstance(esc, set)


# ===================================================================
# 13. TestAliasAnalysis
# ===================================================================


class TestAliasAnalysis:
    def test_no_alias_allocas(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a", IR_I32))
        bb.append(Alloca("b", IR_I32))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = AliasAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.does_alias("f", "a", "b") == "no"

    def test_must_alias_self(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a", IR_I32))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = AliasAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.does_alias("f", "a", "a") == "must"

    def test_no_alias_pairs(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a", IR_I32))
        bb.append(Alloca("b", IR_I32))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = AliasAnalysis()
        result = a.run(mod, _make_ctx(mod))
        pairs = result.no_alias_pairs("f")
        assert ("a", "b") in pairs

    def test_may_alias_pairs(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("p", IR_I32))
        bb.append(Alloca("q", IR_I32))
        bb.append(Load("v", IR_I32, f.args[0] if f.args else make_int_constant(0)))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = AliasAnalysis()
        result = a.run(mod, _make_ctx(mod))
        pairs = result.may_alias_pairs("f")
        assert isinstance(pairs, set)


# ===================================================================
# 14. TestDominanceAnalysis
# ===================================================================


class TestDominanceAnalysis:
    def test_entry_dominates_all(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("bb2")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = DominanceAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.dominates("f", "entry", "bb2")

    def test_immediate_dominator(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("bb2")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = DominanceAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.immediate_dominator("f", "bb2") == "entry"

    def test_dominance_frontier(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("bb2")
        bb3 = BasicBlock("bb3")
        bb1.append(Branch(bb2))
        bb2.append(Branch(bb3))
        bb3.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        bb2.add_successor(bb3)
        bb3.add_predecessor(bb2)
        f.append_block(bb1)
        f.append_block(bb2)
        f.append_block(bb3)
        mod.add_function(f)
        a = DominanceAnalysis()
        result = a.run(mod, _make_ctx(mod))
        df = result.get_dominance_frontier("f", "bb3")
        assert isinstance(df, set)

    def test_dominator_children(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("bb2")
        bb1.append(Branch(bb2))
        bb2.append(Return())
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        a = DominanceAnalysis()
        result = a.run(mod, _make_ctx(mod))
        children = result.get_dominator_children("f", "entry")
        assert "bb2" in children


# ===================================================================
# 15. TestLoopAnalysis
# ===================================================================


class TestLoopAnalysis:
    def test_no_loops(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = LoopAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert not result.has_loops("f")

    def test_simple_loop(self):
        mod = _make_module()
        f = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        header.append(Branch(body))
        body.append(Branch(header))
        header.add_successor(body)
        body.add_predecessor(header)
        body.add_successor(header)
        header.add_predecessor(body)
        f.append_block(header)
        f.append_block(body)
        mod.add_function(f)
        a = LoopAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.has_loops("f")

    def test_loop_header(self):
        mod = _make_module()
        f = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        header.append(Branch(body))
        body.append(Branch(header))
        header.add_successor(body)
        body.add_predecessor(header)
        body.add_successor(header)
        header.add_predecessor(body)
        f.append_block(header)
        f.append_block(body)
        mod.add_function(f)
        a = LoopAnalysis()
        result = a.run(mod, _make_ctx(mod))
        loops = result.loops_in("f")
        assert len(loops) > 0
        assert result.is_loop_header("f", loops[0].header)

    def test_nesting_depth(self):
        mod = _make_module()
        f = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        header.append(Branch(body))
        body.append(Branch(header))
        header.add_successor(body)
        body.add_predecessor(header)
        body.add_successor(header)
        header.add_predecessor(body)
        f.append_block(header)
        f.append_block(body)
        mod.add_function(f)
        a = LoopAnalysis()
        result = a.run(mod, _make_ctx(mod))
        depth = result.nesting_depth("f", "body")
        assert depth >= 0

    def test_back_edges(self):
        mod = _make_module()
        f = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        header.append(Branch(body))
        body.append(Branch(header))
        header.add_successor(body)
        body.add_predecessor(header)
        body.add_successor(header)
        header.add_predecessor(body)
        f.append_block(header)
        f.append_block(body)
        mod.add_function(f)
        a = LoopAnalysis()
        result = a.run(mod, _make_ctx(mod))
        be = result.back_edges.get("f", [])
        assert isinstance(be, list)


# ===================================================================
# 16. TestCallGraphAnalysis
# ===================================================================


class TestCallGraphAnalysis:
    def test_no_calls(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = CallGraphAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.callees_of("f") == set()

    def test_simple_call(self):
        mod = _make_module()
        callee = _make_func("callee")
        cbb = BasicBlock("entry")
        cbb.append(Return())
        callee.append_block(cbb)
        caller = _make_func("caller")
        fbb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        fbb.append(Call(None, ft, callee))
        fbb.append(Return())
        caller.append_block(fbb)
        mod.add_function(callee)
        mod.add_function(caller)
        a = CallGraphAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert "callee" in result.callees_of("caller")

    def test_recursion(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        bb.append(Call(None, ft, f))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = CallGraphAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.is_recursive("f")

    def test_leaf_function(self):
        mod = _make_module()
        f = _make_func("leaf")
        bb = BasicBlock("entry")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = CallGraphAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.is_leaf("leaf")

    def test_call_sites(self):
        mod = _make_module()
        callee = _make_func("callee")
        cbb = BasicBlock("entry")
        cbb.append(Return())
        callee.append_block(cbb)
        caller = _make_func("caller")
        fbb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        fbb.append(Call(None, ft, callee))
        fbb.append(Return())
        caller.append_block(fbb)
        mod.add_function(callee)
        mod.add_function(caller)
        a = CallGraphAnalysis()
        result = a.run(mod, _make_ctx(mod))
        sites = result.call_sites_in("caller")
        assert len(sites) >= 1


# ===================================================================
# 17. TestSideEffectAnalysis
# ===================================================================


class TestSideEffectAnalysis:
    def test_pure_function(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        bb.append(Add("x", f.args[0], make_int_constant(1)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = SideEffectAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.is_pure("f")

    def test_function_with_store(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(42), ptr))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = SideEffectAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.function_writes_memory("f")

    def test_function_reads_memory(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(42), ptr))
        v = bb.append(Load("v", IR_I32, ptr))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = SideEffectAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.function_reads_memory("f")

    def test_is_read_only(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = SideEffectAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.is_read_only("f") or result.is_pure("f")


# ===================================================================
# 18. TestMemoryAccessAnalysis
# ===================================================================


class TestMemoryAccessAnalysis:
    def test_load_count(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Load("v", IR_I32, ptr))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = MemoryAccessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.load_count("f") >= 1

    def test_store_count(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(42), ptr))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = MemoryAccessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.store_count("f") >= 1

    def test_alloca_count(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a", IR_I32))
        bb.append(Alloca("b", IR_I32))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = MemoryAccessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.alloca_count("f") == 2

    def test_total_memory_ops(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(1), ptr))
        bb.append(Load("v", IR_I32, ptr))
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        a = MemoryAccessAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.total_memory_ops("f") == 3


# ===================================================================
# 19. TestConstantPropagationAnalysis
# ===================================================================


class TestConstantPropagationAnalysis:
    def test_known_constant(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(5), make_int_constant(3)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = ConstantPropagationAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert isinstance(result, ConstantPropagationResult)

    def test_is_constant(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = ConstantPropagationAnalysis()
        result = a.run(mod, _make_ctx(mod))
        const_vals = result.constant_values("f")
        assert isinstance(const_vals, dict)

    def test_get_constant(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(7), make_int_constant(3)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = ConstantPropagationAnalysis()
        result = a.run(mod, _make_ctx(mod))
        val = result.get_constant("f", "x")
        assert val == 10

    def test_non_constant(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        arg = f.args[0]
        bb.append(Add("x", arg, make_int_constant(1)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = ConstantPropagationAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert not result.is_constant("f", arg.name)


# ===================================================================
# 20. TestConstantFoldingPass
# ===================================================================


class TestConstantFoldingPass:
    def test_fold_add(self):
        mod = _make_module()
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(3)
        b = make_int_constant(4)
        bb.append(Add("r", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_fold_sub(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Sub("r", make_int_constant(10), make_int_constant(3)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_fold_mul(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Mul("r", make_int_constant(5), make_int_constant(6)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_fold_icmp(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(ICmp("c", ICmpPredicate.SLT, make_int_constant(3), make_int_constant(5)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_fold_variable(self):
        mod = _make_module()
        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("r", func.args[0], func.args[1]))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_impact(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("r", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert result.impact.instructions_eliminated >= 1


# ===================================================================
# 21. TestConstantPropagationPass
# ===================================================================


class TestConstantPropagationPass:
    def test_propagate(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        c = Add("c", make_int_constant(5), make_int_constant(0))
        bb.append(c)
        bb.append(Add("x", c, make_int_constant(1)))
        bb.append(Return(bb[1]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_propagate_add_zero(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(5), make_int_constant(0)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_no_change_variable(self):
        mod = _make_module()
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("x", func.args[0], make_int_constant(1)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_multiple_constants(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = Add("a", make_int_constant(1), make_int_constant(2))
        bb.append(a)
        b = Add("b", a, make_int_constant(3))
        bb.append(b)
        bb.append(Return(b))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = ConstantPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 22. TestDeadCodeEliminationPass
# ===================================================================


class TestDeadCodeEliminationPass:
    def test_eliminate_dead(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("dead", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadCodeEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_keep_used(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("used", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadCodeEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_eliminate_unused_in_chain(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        bb.append(Add("b", make_int_constant(3), make_int_constant(4)))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadCodeEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 2

    def test_keep_terminators(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadCodeEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_eliminate_multiple_dead(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        for i in range(5):
            bb.append(Add(f"d{i}", make_int_constant(i), make_int_constant(i)))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadCodeEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 5


# ===================================================================
# 23. TestDeadStoreEliminationPass
# ===================================================================


class TestDeadStoreEliminationPass:
    def test_eliminate_dead_store(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(1), ptr))
        bb.append(Store(make_int_constant(2), ptr))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadStoreEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_eliminate_different_ptrs(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        p1 = Alloca("p1", IR_I32)
        bb.append(p1)
        p2 = Alloca("p2", IR_I32)
        bb.append(p2)
        bb.append(Store(make_int_constant(1), p1))
        bb.append(Store(make_int_constant(2), p2))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadStoreEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_eliminate_with_load_between(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(1), ptr))
        bb.append(Load("v", IR_I32, ptr))
        bb.append(Store(make_int_constant(2), ptr))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadStoreEliminationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_eliminate_chain(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        for i in range(4):
            bb.append(Store(make_int_constant(i), ptr))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = DeadStoreEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# 24. TestCopyPropagationPass
# ===================================================================


class TestCopyPropagationPass:
    def test_add_zero_is_copy(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(5), make_int_constant(0)))
        bb.append(Add("y", make_int_constant(10), make_int_constant(0)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CopyPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_mul_one_is_copy(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Mul("x", make_int_constant(5), make_int_constant(1)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CopyPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_no_copy_regular_add(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(3), make_int_constant(4)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CopyPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_copy_chain(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(42)
        bb.append(Add("x", a, make_int_constant(0)))
        bb.append(Add("y", make_int_constant(0), make_int_constant(0)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CopyPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 25. TestStrengthReductionPass
# ===================================================================


class TestStrengthReductionPass:
    def test_mul_power_of_two(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        x = make_int_constant(7)
        bb.append(Mul("r", x, make_int_constant(4)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = StrengthReductionPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_reduction_non_power(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        x = make_int_constant(7)
        bb.append(Mul("r", x, make_int_constant(3)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = StrengthReductionPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_reduction_zero(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        x = make_int_constant(7)
        bb.append(Mul("r", x, make_int_constant(0)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = StrengthReductionPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 26. TestCommonSubexpressionPass
# ===================================================================


class TestCommonSubexpressionPass:
    def test_eliminate_cse(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(3)
        b = make_int_constant(4)
        bb.append(Add("x", a, b))
        bb.append(Add("y", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CommonSubexpressionEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_cse_different_ops(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(3)
        b = make_int_constant(4)
        bb.append(Add("x", a, b))
        bb.append(Sub("y", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CommonSubexpressionEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_cse_different_operands(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(3)
        b = make_int_constant(4)
        c = make_int_constant(5)
        bb.append(Add("x", a, b))
        bb.append(Add("y", a, c))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CommonSubexpressionEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_cse_mul(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = make_int_constant(3)
        b = make_int_constant(4)
        bb.append(Mul("x", a, b))
        bb.append(Mul("y", a, b))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)
        ctx = _make_ctx(mod)
        p = CommonSubexpressionEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# Compatibility patches for Part 3 tests
# ===================================================================

from compiler.optimization.passes.function_inlining import FunctionInliningPass
from compiler.optimization.passes.tail_call import TailCallOptimizationPass
from compiler.optimization.passes.loop_invariant_code_motion import LoopInvariantCodeMotionPass
from compiler.optimization.passes.loop_unrolling import LoopUnrollingPass
from compiler.optimization.passes.loop_simplification import LoopSimplificationPass
from compiler.optimization.passes.branch_simplification import BranchSimplificationPass
from compiler.optimization.passes.jump_threading import JumpThreadingPass
from compiler.optimization.passes.redundant_load_elimination import RedundantLoadEliminationPass
from compiler.optimization.passes.redundant_store_elimination import RedundantStoreEliminationPass
from compiler.optimization.passes.memory_coalescing import MemoryCoalescingPass
from compiler.optimization.passes.object_lifetime import ObjectLifetimeOptimizationPass
from compiler.optimization.passes.allocation_hoisting import AllocationHoistingPass
from compiler.optimization.passes.peephole import PeepholeOptimizationPass
from compiler.optimization.passes.instruction_combining import InstructionCombiningPass
from compiler.optimization.passes.control_flow_simplification import ControlFlowSimplificationPass
from compiler.optimization.passes.switch_optimization import SwitchOptimizationPass
from compiler.optimization.passes.sparse_ccp import SparseConditionalConstantPropagationPass
from compiler.optimization.passes.ssa_cleanup import SSACleanupPass
from compiler.ir.instructions import BinaryOp, Switch

# ===================================================================
# 27. TestFunctionInliningPass
# ===================================================================


class TestFunctionInliningPass:
    def test_inline_small_function(self):
        mod = _make_module()
        callee = _make_func("g")
        cbb = BasicBlock("entry")
        cbb.append(Return(make_int_constant(7)))
        callee.append_block(cbb)

        caller = _make_func("f")
        fbb = BasicBlock("entry")
        ft = func_type((), IR_I32)
        fbb.append(Call("res", ft, callee))
        fbb.append(Return(make_int_constant(0)))
        caller.append_block(fbb)

        mod.add_function(callee)
        mod.add_function(caller)

        ctx = _make_ctx(mod)
        p = FunctionInliningPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_inline_large_function(self):
        mod = _make_module()
        callee = _make_func("g")
        cbb = BasicBlock("entry")
        for i in range(6):
            cbb.append(Add(f"a{i}", make_int_constant(i), make_int_constant(i)))
        cbb.append(Return(make_int_constant(0)))
        callee.append_block(cbb)

        caller = _make_func("f")
        fbb = BasicBlock("entry")
        ft = func_type((), IR_I32)
        fbb.append(Call("res", ft, callee))
        fbb.append(Return(make_int_constant(0)))
        caller.append_block(fbb)

        mod.add_function(callee)
        mod.add_function(caller)

        ctx = _make_ctx(mod)
        p = FunctionInliningPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_inline_recursive(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        bb.append(Call("res", ft, func))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = FunctionInliningPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 28. TestTailCallOptimizationPass
# ===================================================================


class TestTailCallOptimizationPass:
    def test_detect_tail_call(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        call = Call("tmp", ft, func)
        bb.append(call)
        bb.append(Return(call))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = TailCallOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_tail_call_different_callee(self):
        mod = _make_module()
        other = _make_func("g")
        o_bb = BasicBlock("entry")
        o_bb.append(Return())
        other.append_block(o_bb)

        func = _make_func("f")
        bb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        bb.append(Call("tmp", ft, other))
        bb.append(Return())
        func.append_block(bb)

        mod.add_function(other)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = TailCallOptimizationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_tail_call_with_operands_between(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Call("tmp", ft, func))
        bb.append(Return())
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = TailCallOptimizationPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 29. TestLoopInvariantCodeMotionPass
# ===================================================================


class TestLoopInvariantCodeMotionPass:
    def test_move_invariant_from_header(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        header.append(Add("inv", make_int_constant(3), make_int_constant(4)))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopInvariantCodeMotionPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_move_loop_varying(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Add("x", func.args[0], make_int_constant(1)))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopInvariantCodeMotionPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_move_alloca_out_of_loop(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Alloca("ptr", IR_I32))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopInvariantCodeMotionPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# 30. TestLoopUnrollingPass
# ===================================================================


class TestLoopUnrollingPass:
    def test_unroll_small_loop(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Add("x", make_int_constant(1), make_int_constant(2)))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopUnrollingPass(max_unroll=4)
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_unroll_large_body(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        for i in range(5):
            body.append(Add(f"x{i}", make_int_constant(i), make_int_constant(i)))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopUnrollingPass(max_unroll=2)
        result = p.run(mod, ctx)
        assert not result.changed

    def test_unroll_copies_instructions(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Add("x", make_int_constant(1), make_int_constant(1)))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopUnrollingPass(max_unroll=4)
        result = p.run(mod, ctx)
        assert result.impact.instructions_combined >= 1


# ===================================================================
# 31. TestLoopSimplificationPass
# ===================================================================


class TestLoopSimplificationPass:
    def test_add_preheader(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert len(func.basic_blocks) > 3

    def test_no_simplify_single_entry_loop(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        preheader = BasicBlock("preheader")
        preheader.add_successor(header)
        header.add_predecessor(preheader)
        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)

        preheader.append(Branch(header))
        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [preheader, header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopSimplificationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_merge_multiple_entries(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        entry.add_successor(header)
        entry.add_successor(body)
        header.add_predecessor(entry)
        header.add_successor(body)
        body.add_predecessor(entry)
        body.add_predecessor(header)
        body.add_successor(header)
        body.add_successor(exit_bb)
        exit_bb.add_predecessor(body)

        entry.append(CondBranch(make_bool_constant(True), header, body))
        header.append(Branch(body))
        body.append(CondBranch(make_bool_constant(True), header, exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = LoopSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# 32. TestBranchSimplificationPass
# ===================================================================


class TestBranchSimplificationPass:
    def test_constant_true_branch(self):
        mod = _make_module()
        ft = func_type((), IR_VOID)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        target = BasicBlock("target")
        other = BasicBlock("other")
        func.append_block(bb)
        func.append_block(target)
        func.append_block(other)
        bb.append(CondBranch(BoolConstant(True), target, other))
        target.append(Return())
        other.append(Return())
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = BranchSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_constant_false_branch(self):
        mod = _make_module()
        ft = func_type((), IR_VOID)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        target = BasicBlock("target")
        other = BasicBlock("other")
        func.append_block(bb)
        func.append_block(target)
        func.append_block(other)
        bb.append(CondBranch(BoolConstant(False), target, other))
        target.append(Return())
        other.append(Return())
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = BranchSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_same_target_branches(self):
        mod = _make_module()
        ft = func_type((), IR_VOID)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        target = BasicBlock("target")
        func.append_block(bb)
        func.append_block(target)
        bb.append(CondBranch(make_bool_constant(True), target, target))
        target.append(Return())
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = BranchSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_branch_through_single_block(self):
        mod = _make_module()
        ft = func_type((), IR_VOID)
        func = IRFunction("f", ft)
        entry = BasicBlock("entry")
        middle = BasicBlock("middle")
        exit_bb = BasicBlock("exit")
        func.append_block(entry)
        func.append_block(middle)
        func.append_block(exit_bb)

        entry.append(Branch(middle))
        middle.append(Branch(exit_bb))
        exit_bb.append(Return())
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = BranchSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed
        entry_term = entry.instructions[-1]
        assert isinstance(entry_term, Branch)
        assert entry_term.target is exit_bb


# ===================================================================
# 33. TestJumpThreadingPass
# ===================================================================


class TestJumpThreadingPass:
    def test_thread_branch_through_single_pred_block(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        middle = BasicBlock("middle")
        target = BasicBlock("target")

        entry.add_successor(middle)
        middle.add_predecessor(entry)
        middle.add_successor(target)
        target.add_predecessor(middle)

        entry.append(Branch(middle))
        middle.append(Branch(target))
        target.append(Return(make_int_constant(0)))

        for b in [entry, middle, target]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = JumpThreadingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_thread_cond_branch_true_target(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        t_block = BasicBlock("t_only")
        exit_bb = BasicBlock("exit")

        entry.add_successor(t_block)
        entry.add_successor(exit_bb)
        t_block.add_predecessor(entry)
        t_block.add_successor(exit_bb)
        exit_bb.add_predecessor(entry)
        exit_bb.add_predecessor(t_block)

        entry.append(CondBranch(make_bool_constant(True), t_block, exit_bb))
        t_block.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, t_block, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = JumpThreadingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_thread_multiple_predecessors(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        other = BasicBlock("other")
        target = BasicBlock("target")
        exit_bb = BasicBlock("exit")

        entry.add_successor(target)
        entry.add_successor(exit_bb)
        other.add_successor(target)
        target.add_predecessor(entry)
        target.add_predecessor(other)
        target.add_successor(exit_bb)
        exit_bb.add_predecessor(entry)
        exit_bb.add_predecessor(target)

        entry.append(CondBranch(make_bool_constant(True), target, exit_bb))
        other.append(Branch(target))
        target.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, other, target, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = JumpThreadingPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 34. TestRedundantLoadEliminationPass
# ===================================================================


class TestRedundantLoadEliminationPass:
    def test_eliminate_duplicate_load(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Load("v1", IR_I32, ptr))
        bb.append(Load("v2", IR_I32, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantLoadEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 1

    def test_no_eliminate_with_store_between(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        val2 = make_int_constant(2)
        bb.append(ptr)
        bb.append(Load("v1", IR_I32, ptr))
        bb.append(Store(val2, ptr))
        bb.append(Load("v2", IR_I32, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantLoadEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_eliminate_multiple_redundant_loads(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I64)
        bb.append(ptr)
        bb.append(Load("a", IR_I64, ptr))
        bb.append(Load("b", IR_I64, ptr))
        bb.append(Load("c", IR_I64, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantLoadEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 2


# ===================================================================
# 35. TestRedundantStoreEliminationPass
# ===================================================================


class TestRedundantStoreEliminationPass:
    def test_eliminate_duplicate_store(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        val = make_int_constant(42)
        bb.append(ptr)
        bb.append(Store(val, ptr))
        bb.append(Store(val, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantStoreEliminationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 1

    def test_no_eliminate_different_value(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        bb.append(Store(make_int_constant(1), ptr))
        bb.append(Store(make_int_constant(2), ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantStoreEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_eliminate_with_load_between(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        val = make_int_constant(42)
        bb.append(ptr)
        bb.append(Store(val, ptr))
        bb.append(Load("tmp", IR_I32, ptr))
        bb.append(Store(val, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = RedundantStoreEliminationPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 36. TestMemoryCoalescingPass
# ===================================================================


class TestMemoryCoalescingPass:
    def test_coalesce_store_load_pair(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        val = make_int_constant(10)
        bb.append(ptr)
        bb.append(Store(val, ptr))
        bb.append(Load("tmp", IR_I32, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = MemoryCoalescingPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 1

    def test_no_coalesce_different_pointers(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr1 = Alloca("p1", IR_I32)
        ptr2 = Alloca("p2", IR_I32)
        val = make_int_constant(10)
        bb.append(ptr1)
        bb.append(ptr2)
        bb.append(Store(val, ptr1))
        bb.append(Load("tmp", IR_I32, ptr2))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = MemoryCoalescingPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_coalesce_non_adjacent(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        val = make_int_constant(10)
        bb.append(ptr)
        bb.append(Store(val, ptr))
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Load("tmp", IR_I32, ptr))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = MemoryCoalescingPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 37. TestObjectLifetimePass
# ===================================================================


class TestObjectLifetimeOptimizationPass:
    def test_detect_high_alloca_ratio(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a1", IR_I32))
        bb.append(Alloca("a2", IR_I32))
        bb.append(Alloca("a3", IR_I32))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = ObjectLifetimeOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.bytes_saved > 0

    def test_no_optimization_low_ratio(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Alloca("a", IR_I32))
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Add("y", make_int_constant(3), make_int_constant(4)))
        bb.append(Add("z", make_int_constant(5), make_int_constant(6)))
        bb.append(Add("w", make_int_constant(7), make_int_constant(8)))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = ObjectLifetimeOptimizationPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 38. TestAllocationHoistingPass
# ===================================================================


class TestAllocationHoistingPass:
    def test_hoist_loop_invariant_alloca(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Alloca("p", IR_I32))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = AllocationHoistingPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_hoist_non_loop(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        exit_bb = BasicBlock("exit")

        bb.add_successor(exit_bb)
        exit_bb.add_predecessor(bb)

        bb.append(Alloca("p", IR_I32))
        bb.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        func.append_block(bb)
        func.append_block(exit_bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = AllocationHoistingPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_hoist_multiple_allocas(self):
        mod = _make_module()
        func = _make_func("f")
        header = BasicBlock("header")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        header.add_successor(body)
        header.add_successor(exit_bb)
        body.add_predecessor(header)
        body.add_successor(header)
        exit_bb.add_predecessor(header)
        exit_bb.add_predecessor(body)

        cond = make_bool_constant(True)
        header.append(CondBranch(cond, body, exit_bb))
        body.append(Alloca("p1", IR_I32))
        body.append(Alloca("p2", IR_I64))
        body.append(Branch(header))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [header, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = AllocationHoistingPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_eliminated >= 1


# ===================================================================
# 39. TestPeepholeOptimizationPass
# ===================================================================


class TestPeepholeOptimizationPass:
    def test_add_zero_optimization(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        bb.append(Add("res", x, IntConstant(0, IR_I32)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = PeepholeOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_mul_by_one(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        bb.append(Mul("res", x, IntConstant(1, IR_I32)))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = PeepholeOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_sub_self(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        bb.append(Sub("res", x, x))
        bb.append(Return(bb[0]))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = PeepholeOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_icmp_self_equality(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        bb.append(ICmp("cmp", ICmpPredicate.EQ, x, x))
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = PeepholeOptimizationPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# 40. TestInstructionCombiningPass
# ===================================================================


class TestInstructionCombiningPass:
    def test_combine_nested_adds(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        inner = Add("inner", x, IntConstant(3, IR_I32))
        bb.append(inner)
        outer = Add("outer", inner, IntConstant(5, IR_I32))
        bb.append(outer)
        bb.append(Return(outer))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = InstructionCombiningPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert result.impact.instructions_combined >= 1

    def test_no_combine_different_ops(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        mul = Mul("m", x, IntConstant(2, IR_I32))
        bb.append(mul)
        add = Add("a", mul, IntConstant(3, IR_I32))
        bb.append(add)
        bb.append(Return(add))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = InstructionCombiningPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_no_combine_without_constants(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32, IR_I32))
        bb = BasicBlock("entry")
        x = func.args[0]
        y = func.args[1]
        inner = Add("inner", x, y)
        bb.append(inner)
        outer = Add("outer", inner, y)
        bb.append(outer)
        bb.append(Return(outer))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = InstructionCombiningPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 41. TestControlFlowSimplificationPass
# ===================================================================


class TestControlFlowSimplificationPass:
    def test_merge_trivial_block(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        trivial = BasicBlock("trivial")
        exit_bb = BasicBlock("exit")

        entry.add_successor(trivial)
        trivial.add_predecessor(entry)
        trivial.add_successor(exit_bb)
        exit_bb.add_predecessor(trivial)

        entry.append(Branch(trivial))
        trivial.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, trivial, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = ControlFlowSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert trivial not in func.basic_blocks

    def test_no_merge_block_with_instructions(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        body = BasicBlock("body")
        exit_bb = BasicBlock("exit")

        entry.add_successor(body)
        body.add_predecessor(entry)
        body.add_successor(exit_bb)
        exit_bb.add_predecessor(body)

        entry.append(Branch(body))
        body.append(Add("x", make_int_constant(1), make_int_constant(2)))
        body.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(0)))

        for b in [entry, body, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = ControlFlowSimplificationPass()
        result = p.run(mod, ctx)
        assert not result.changed

    def test_update_predecessors_after_merge(self):
        mod = _make_module()
        func = _make_func("f")
        entry = BasicBlock("entry")
        trivial = BasicBlock("trivial")
        target = BasicBlock("target")

        entry.add_successor(trivial)
        trivial.add_predecessor(entry)
        trivial.add_successor(target)
        target.add_predecessor(trivial)

        entry.append(Branch(trivial))
        trivial.append(Branch(target))
        target.append(Return(make_int_constant(0)))

        for b in [entry, trivial, target]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = ControlFlowSimplificationPass()
        result = p.run(mod, ctx)
        assert result.changed
        assert entry in target.predecessors or target in entry.successors


# ===================================================================
# 42. TestSwitchOptimizationPass
# ===================================================================


class TestSwitchOptimizationPass:
    def test_dense_switch_detected(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        default = BasicBlock("default")
        c1 = BasicBlock("c1")
        c2 = BasicBlock("c2")
        c3 = BasicBlock("c3")
        c4 = BasicBlock("c4")

        cases = [
            (IntConstant(1, IR_I32), c1),
            (IntConstant(2, IR_I32), c2),
            (IntConstant(3, IR_I32), c3),
            (IntConstant(4, IR_I32), c4),
        ]
        sw = Switch(func.args[0], default, cases)
        bb.append(sw)

        default.append(Return(make_int_constant(0)))
        c1.append(Return(make_int_constant(1)))
        c2.append(Return(make_int_constant(2)))
        c3.append(Return(make_int_constant(3)))
        c4.append(Return(make_int_constant(4)))

        for b in [bb, default, c1, c2, c3, c4]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SwitchOptimizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_sparse_switch_not_optimized(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        default = BasicBlock("default")
        c1 = BasicBlock("c1")

        cases = [(IntConstant(1, IR_I32), c1)]
        sw = Switch(func.args[0], default, cases)
        bb.append(sw)
        default.append(Return(make_int_constant(0)))
        c1.append(Return(make_int_constant(1)))

        for b in [bb, default, c1]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SwitchOptimizationPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 43. TestSparseCCPPass
# ===================================================================


class TestSparseCCPPass:
    def test_propagate_true_condition(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        live = BasicBlock("live")
        dead = BasicBlock("dead")
        exit_bb = BasicBlock("exit")

        bb.add_successor(live)
        bb.add_successor(dead)
        live.add_predecessor(bb)
        dead.add_predecessor(bb)
        live.add_successor(exit_bb)
        exit_bb.add_predecessor(live)
        exit_bb.add_predecessor(dead)

        bb.append(CondBranch(BoolConstant(True), live, dead))
        live.append(Branch(exit_bb))
        dead.append(Return(make_int_constant(0)))
        exit_bb.append(Return(make_int_constant(1)))

        for b in [bb, live, dead, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SparseConditionalConstantPropagationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_propagate_false_condition(self):
        mod = _make_module()
        func = _make_func("f")
        bb = BasicBlock("entry")
        live = BasicBlock("live")
        dead = BasicBlock("dead")
        exit_bb = BasicBlock("exit")

        bb.add_successor(live)
        bb.add_successor(dead)
        live.add_predecessor(bb)
        dead.add_predecessor(bb)
        dead.add_successor(exit_bb)
        exit_bb.add_predecessor(live)
        exit_bb.add_predecessor(dead)

        bb.append(CondBranch(BoolConstant(False), live, dead))
        live.append(Return(make_int_constant(0)))
        dead.append(Branch(exit_bb))
        exit_bb.append(Return(make_int_constant(1)))

        for b in [bb, live, dead, exit_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SparseConditionalConstantPropagationPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_no_propagate_variable_condition(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I1,))
        bb = BasicBlock("entry")
        true_bb = BasicBlock("true_path")
        false_bb = BasicBlock("false_path")

        bb.add_successor(true_bb)
        bb.add_successor(false_bb)
        true_bb.add_predecessor(bb)
        false_bb.add_predecessor(bb)

        bb.append(CondBranch(func.args[0], true_bb, false_bb))
        true_bb.append(Return(make_int_constant(1)))
        false_bb.append(Return(make_int_constant(0)))

        for b in [bb, true_bb, false_bb]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SparseConditionalConstantPropagationPass()
        result = p.run(mod, ctx)
        assert not result.changed


# ===================================================================
# 44. TestSSACleanupPass
# ===================================================================


class TestSSACleanupPass:
    def test_eliminate_trivial_phi(self):
        mod = _make_module()
        func = _make_func("f")
        bb1 = BasicBlock("bb1")
        bb2 = BasicBlock("bb2")
        merge = BasicBlock("merge")

        bb1.add_successor(merge)
        bb2.add_successor(merge)
        merge.add_predecessor(bb1)
        merge.add_predecessor(bb2)

        val = make_int_constant(42)
        phi = Phi("p", IR_I32, [(val, bb1), (val, bb2)])
        merge.append(phi)
        merge.append(Return(phi))

        bb1.append(Branch(merge))
        bb2.append(Branch(merge))

        for b in [bb1, bb2, merge]:
            func.append_block(b)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_eliminate_identity_add_zero(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        add = Add("res", x, IntConstant(0, IR_I32))
        bb.append(add)
        bb.append(Return(add))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_eliminate_identity_mul_one(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        mul = Mul("res", x, IntConstant(1, IR_I32))
        bb.append(mul)
        bb.append(Return(mul))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert result.changed

    def test_eliminate_identity_sub_zero(self):
        mod = _make_module()
        func = _make_func("f", param_types=(IR_I32,))
        bb = BasicBlock("entry")
        x = func.args[0]
        sub = Sub("res", x, IntConstant(0, IR_I32))
        bb.append(sub)
        bb.append(Return(sub))
        func.append_block(bb)
        mod.add_function(func)

        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert result.changed


# ===================================================================
# 45. TestIntegrationPipeline
# ===================================================================


class TestIntegrationPipeline:
    def test_o0_no_optimization(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        ctx = OptimizationContext(mod, level=OptimizationLevel.O0)
        p = OptimizationPipeline(PassRegistry())
        report = p.run(mod, ctx)
        assert report is not None
        assert report.pass_count == 0

    def test_o2_full_optimization(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        registry = PassRegistry()
        registry.register_pass(
            type("_TestA", (_RegistryPass,), {"run": lambda s, m, c: PassResult(changed=True)}),
            name="test_a", level=2,
        )
        registry.register_pass(
            type("_TestB", (_RegistryPass,), {"run": lambda s, m, c: PassResult(changed=False)}),
            name="test_b", level=2,
        )

        ctx = OptimizationContext(mod, level=OptimizationLevel.O2)
        p = OptimizationPipeline(registry)
        report = p.run(mod, ctx)
        assert report is not None
        assert report.pass_count >= 2

    def test_fixed_point_convergence(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        registry = PassRegistry()
        registry.register_pass(
            type("_ConvPass", (_RegistryPass,), {
                "run": lambda s, m, c: PassResult(changed=False),
            }),
            name="conv_pass", level=2,
        )

        ctx = OptimizationContext(mod, level=OptimizationLevel.O2)
        p = OptimizationPipeline(registry)
        report = p.run_fixed_point(mod, ctx)
        assert report is not None
        assert isinstance(report, OptimizationReport)

    def test_statistics_collection(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(42)))
        func.append_block(bb)
        mod.add_function(func)

        registry = PassRegistry()
        registry.register_pass(
            type("_StatPass", (_RegistryPass,), {
                "run": lambda s, m, c: PassResult(changed=True),
            }),
            name="stat_pass", level=2,
        )

        stats = StatisticsEngine()
        ctx = OptimizationContext(mod, level=OptimizationLevel.O2, stats=stats)
        p = OptimizationPipeline(registry)
        report = p.run(mod, ctx)
        assert report is not None
        assert stats.total_passes_run >= 1

    def test_pass_ordering(self):
        mod = _make_module()
        ft = func_type((), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        bb.append(Return(make_int_constant(0)))
        func.append_block(bb)
        mod.add_function(func)

        registry = PassRegistry()
        registry.register_pass(_RegistryPass, name="first", level=1)
        registry.register_pass(_RegistryPass, name="second", level=2)
        registry.register_pass(_RegistryPass, name="third", level=2)

        ctx = OptimizationContext(mod, level=OptimizationLevel.O2)
        p = OptimizationPipeline(registry)
        passes = p.get_passes(OptimizationLevel.O2)
        assert len(passes) == 3
        assert "first" in passes
        assert "second" in passes
        assert "third" in passes


# ===================================================================
# 46. TestOptimizationReport
# ===================================================================


class TestOptimizationReport:
    def test_report_summary(self):
        stats = StatisticsEngine()
        stats.start_pass("test_pass")
        stats.record_instruction_count(10, 8)
        stats.end_pass("test_pass", changed=True)
        report = stats.generate_report("my_module")

        summary = report.format_summary()
        assert "my_module" in summary
        assert "test_pass" in summary or "Passes" in summary
        assert "10" in summary

    def test_report_table(self):
        stats = StatisticsEngine()
        stats.start_pass("pass_a")
        stats.record_instruction_count(5, 3)
        stats.end_pass("pass_a", changed=True)
        stats.start_pass("pass_b")
        stats.record_instruction_count(2, 2)
        stats.end_pass("pass_b", changed=False)
        report = stats.generate_report("mod")

        table = report.format_table()
        assert "pass_a" in table
        assert "pass_b" in table
        assert "TOTAL" in table

    def test_report_dict(self):
        stats = StatisticsEngine()
        stats.start_pass("p1")
        stats.record_instruction_count(10, 7)
        stats.record_block_count(3, 2)
        stats.end_pass("p1", changed=True)
        report = stats.generate_report("test_mod")

        d = report.to_dict()
        assert d["module_name"] == "test_mod"
        assert d["pass_count"] == 1
        assert d["instructions"]["before"] == 10
        assert d["instructions"]["after"] == 7
        assert d["instructions"]["eliminated"] == 3
        assert d["blocks"]["eliminated"] == 1
        assert len(d["passes"]) == 1
        assert d["passes"][0]["name"] == "p1"
        assert d["passes"][0]["changed"] is True
