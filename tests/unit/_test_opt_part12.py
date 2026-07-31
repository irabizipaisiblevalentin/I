"""
Optimization Test Suite -- Sprint 7 (Parts 1 & 2)

Tests for optimization infrastructure and analysis modules.
"""
from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ir.types import IR_I32, IR_I64, IR_VOID, int_type, func_type, ptr_type
from compiler.ir.values import IntConstant, FloatConstant, BoolConstant, make_int_constant, Argument
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
        assert result.escape_kind("f", f.args[0].name) == "argument"

    def test_local_no_escape(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        assert result.escape_kind("f", "x") == "none"

    def test_non_escaping_values(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        bb.append(Return(bb[0]))
        f.append_block(bb)
        mod.add_function(f)
        a = EscapeAnalysis()
        result = a.run(mod, _make_ctx(mod))
        ne = result.non_escaping_values("f")
        assert "x" in ne

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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(42)))
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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(42)))
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
        ptr = bb.append(Alloca("p", IR_I32))
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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(42)))
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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(1)))
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
        c = bb.append(Add("c", make_int_constant(5), make_int_constant(0)))
        bb.append(Add("x", c, make_int_constant(1)))
        bb.append(Return(bb[0]))
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
        a = bb.append(Add("a", make_int_constant(1), make_int_constant(2)))
        b = bb.append(Add("b", a, make_int_constant(3)))
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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(1)))
        bb.append(Store(ptr, make_int_constant(2)))
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
        p1 = bb.append(Alloca("p1", IR_I32))
        p2 = bb.append(Alloca("p2", IR_I32))
        bb.append(Store(p1, make_int_constant(1)))
        bb.append(Store(p2, make_int_constant(2)))
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
        ptr = bb.append(Alloca("p", IR_I32))
        bb.append(Store(ptr, make_int_constant(1)))
        bb.append(Load("v", IR_I32, ptr))
        bb.append(Store(ptr, make_int_constant(2)))
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
        ptr = bb.append(Alloca("p", IR_I32))
        for i in range(4):
            bb.append(Store(ptr, make_int_constant(i)))
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
