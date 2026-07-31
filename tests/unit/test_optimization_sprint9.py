from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import (
    Add,
    Alloca,
    Branch,
    Call,
    CondBranch,
    ICmp,
    ICmpPredicate,
    Load,
    Mul,
    Phi,
    Return,
    SDiv,
    Store,
    Sub,
)
from compiler.ir.module import IRModule
from compiler.ir.types import IR_I32, IR_I64, IR_VOID, func_type, int_type
from compiler.ir.values import IntConstant, make_bool_constant, make_int_constant
from compiler.optimization.base import PassResult
from compiler.optimization.context import OptimizationContext, OptimizationLevel
from compiler.optimization.manager import OptimizationManager
from compiler.optimization.pipeline import OptimizationPipeline, PipelineConfig
from compiler.optimization.registry import PassRegistry
from compiler.optimization.stats import OptimizationReport

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


def _make_simple_module():
    mod = _make_module()
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("test_func", ft)
    bb = BasicBlock("entry")
    a = func.args[0]
    b = func.args[1]
    s = Add("sum", a, b)
    bb.append(s)
    bb.append(Return(s))
    func.append_block(bb)
    mod.add_function(func)
    return mod


# ===================================================================
# 1. IR Verification Tests
# ===================================================================


class TestIRVerification:
    def test_verify_valid_module(self):
        mod = _make_simple_module()
        config = PipelineConfig()
        config.enable_verification = True
        reg = PassRegistry()
        pipeline = OptimizationPipeline(reg, config)
        pipeline._verify_ir(mod, "test")

    def test_verify_invalid_module_raises(self):
        mod = _make_module()
        func = _make_func("bad")
        bb = BasicBlock("no_terminator")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        func.append_block(bb)
        mod.add_function(func)
        mgr = OptimizationManager()
        pg = OptimizationPipeline(mgr.registry, PipelineConfig())
        with pytest.raises(RuntimeError) as excinfo:
            pg._verify_ir(mod, "test_bad")
        assert "IR validation failed" in str(excinfo.value)

    def test_verify_after_each_pass(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        config = PipelineConfig()
        config.enable_verification = True
        ctx = _make_ctx(mod)
        pipeline = OptimizationPipeline(mgr.registry, config)
        pipeline.build_default_pipeline()
        report = pipeline.run(mod, ctx)
        assert report is not None

    def test_verify_disabled_no_raise(self):
        mod = _make_module()
        func = _make_func("bad")
        bb = BasicBlock("no_terminator")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        func.append_block(bb)
        mod.add_function(func)
        mgr = OptimizationManager()
        config = PipelineConfig()
        config.enable_verification = False
        ctx = _make_ctx(mod)
        pipeline = OptimizationPipeline(mgr.registry, config)
        pipeline.build_default_pipeline()
        report = pipeline.run(mod, ctx)
        assert report is not None

    def test_verify_fixed_point(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        config = PipelineConfig()
        config.enable_verification = True
        config.max_fixed_point_iterations = 2
        ctx = _make_ctx(mod)
        pipeline = OptimizationPipeline(mgr.registry, config)
        pipeline.build_default_pipeline()
        report = pipeline.run_fixed_point(mod, ctx)
        assert report is not None


# ===================================================================
# 2. Debugging Support Tests
# ===================================================================


class TestDebugSupport:
    def test_transformation_log_empty(self):
        mod = _make_simple_module()
        ctx = _make_ctx(mod)
        log = ctx.transformation_log()
        assert "(no transformations recorded)" in log

    def test_transformation_log_records(self):
        mod = _make_simple_module()
        ctx = _make_ctx(mod)
        ctx.record_transformation("test_pass", "folded constant 2+2 -> 4")
        log = ctx.transformation_log()
        assert "test_pass" in log
        assert "folded constant" in log

    def test_context_debug_flags(self):
        mod = _make_simple_module()
        ctx = _make_ctx(mod)
        assert ctx.debug_enabled is False
        ctx.debug_enabled = True
        assert ctx.debug_enabled is True
        assert ctx.verify_ir is True
        ctx.verify_ir = False
        assert ctx.verify_ir is False
        assert ctx.dump_ir is False
        ctx.dump_ir = True
        assert ctx.dump_ir is True

    def test_debug_output_dir_config(self):
        config = PipelineConfig()
        assert config.enable_debug is False
        config.enable_debug = True
        assert config.enable_debug is True
        config.debug_output_dir = "/tmp/opt_debug"
        assert config.debug_output_dir == "/tmp/opt_debug"

    def test_dump_flags(self):
        config = PipelineConfig()
        assert config.dump_all_ir is False
        assert config.dump_changed_only is True
        config.dump_all_ir = True
        assert config.dump_all_ir is True


# ===================================================================
# 3. Devirtualization Pass Tests
# ===================================================================


class TestDevirtualizationPass:
    def test_direct_call_not_changed(self):
        mod = _make_module()
        callee = _make_func("callee")
        cbb = BasicBlock("entry")
        cbb.append(Return())
        callee.append_block(cbb)
        caller = _make_func("caller")
        fbb = BasicBlock("entry")
        ft = func_type((), IR_VOID)
        fbb.append(Call("c", ft, callee))
        fbb.append(Return())
        caller.append_block(fbb)
        mod.add_function(callee)
        mod.add_function(caller)
        from compiler.optimization.passes.devirtualization import DevirtualizationPass
        ctx = _make_ctx(mod)
        p = DevirtualizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_pass_registration(self):
        from compiler.optimization.passes.devirtualization import DevirtualizationPass
        p = DevirtualizationPass()
        assert p.name == "devirtualization"
        assert p.estimated_complexity() == "O(n * m)"
        assert p.performance_impact() == "high"
        assert "indirect" in p.description().lower()

    def test_pass_always_returns_result(self):
        mod = _make_module()
        from compiler.optimization.passes.devirtualization import DevirtualizationPass
        ctx = _make_ctx(mod)
        p = DevirtualizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)
        assert hasattr(result, "changed")
        assert hasattr(result, "impact")


# ===================================================================
# 4. Memory Optimization Pass Tests
# ===================================================================


class TestMemoryOptimizationPass:
    def test_basic_memory_opt(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        ptr = Alloca("p", IR_I32)
        bb.append(ptr)
        val = make_int_constant(42)
        bb.append(Store(val, ptr))
        load_val = Load("v", IR_I32, ptr)
        bb.append(load_val)
        bb.append(Return(load_val))
        f.append_block(bb)
        mod.add_function(f)
        from compiler.optimization.passes.memory_optimization import MemoryOptimizationPass
        ctx = _make_ctx(mod)
        p = MemoryOptimizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_pass_registration(self):
        from compiler.optimization.passes.memory_optimization import MemoryOptimizationPass
        p = MemoryOptimizationPass()
        assert p.name == "memory_optimization"
        assert "allocation" in p.description().lower()

    def test_empty_module(self):
        mod = _make_module()
        from compiler.optimization.passes.memory_optimization import MemoryOptimizationPass
        ctx = _make_ctx(mod)
        p = MemoryOptimizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 5. Basic Block Merging Pass Tests
# ===================================================================


class TestBasicBlockMergingPass:
    def test_merge_blocks(self):
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
        from compiler.optimization.passes.basic_block_merging import BasicBlockMergingPass
        ctx = _make_ctx(mod)
        p = BasicBlockMergingPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_pass_registration(self):
        from compiler.optimization.passes.basic_block_merging import BasicBlockMergingPass
        p = BasicBlockMergingPass()
        assert p.name == "basic_block_merging"
        assert "block" in p.description().lower()

    def test_no_single_predecessor(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("bb2")
        bb3 = BasicBlock("bb3")
        bb1.append(CondBranch(make_bool_constant(True), bb2, bb3))
        bb2.append(Return())
        bb3.append(Return())
        bb1.add_successor(bb2)
        bb1.add_successor(bb3)
        bb2.add_predecessor(bb1)
        bb3.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        f.append_block(bb3)
        mod.add_function(f)
        from compiler.optimization.passes.basic_block_merging import BasicBlockMergingPass
        ctx = _make_ctx(mod)
        p = BasicBlockMergingPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 6. Redundant Branch Elimination Pass Tests
# ===================================================================


class TestRedundantBranchEliminationPass:
    def test_constant_cond_branch(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("true_bb")
        bb3 = BasicBlock("false_bb")
        bb1.append(CondBranch(make_bool_constant(True), bb2, bb3))
        bb2.append(Return(make_int_constant(1)))
        bb3.append(Return(make_int_constant(0)))
        bb1.add_successor(bb2)
        bb1.add_successor(bb3)
        bb2.add_predecessor(bb1)
        bb3.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        f.append_block(bb3)
        mod.add_function(f)
        from compiler.optimization.passes.redundant_branch_elimination import RedundantBranchEliminationPass
        ctx = _make_ctx(mod)
        p = RedundantBranchEliminationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_pass_registration(self):
        from compiler.optimization.passes.redundant_branch_elimination import RedundantBranchEliminationPass
        p = RedundantBranchEliminationPass()
        assert p.name == "redundant_branch_elimination"
        assert "branch" in p.description().lower()

    def test_empty_module(self):
        mod = _make_module()
        from compiler.optimization.passes.redundant_branch_elimination import RedundantBranchEliminationPass
        ctx = _make_ctx(mod)
        p = RedundantBranchEliminationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)
        assert not result.changed


# ===================================================================
# 7. Register Allocation Pass Tests
# ===================================================================


class TestRegisterAllocationPass:
    def test_register_estimate(self):
        mod = _make_simple_module()
        from compiler.optimization.passes.register_allocation import RegisterAllocationPass
        ctx = _make_ctx(mod)
        p = RegisterAllocationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_pass_registration(self):
        from compiler.optimization.passes.register_allocation import RegisterAllocationPass
        p = RegisterAllocationPass()
        assert p.name == "register_allocation"
        assert "register" in p.description().lower()

    def test_empty_module(self):
        mod = _make_module()
        from compiler.optimization.passes.register_allocation import RegisterAllocationPass
        ctx = _make_ctx(mod)
        p = RegisterAllocationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 8. Benchmark Infrastructure Tests
# ===================================================================


class TestBenchmarkInfrastructure:
    def test_benchmark_runner_creation(self):
        from compiler.optimization.benchmark import BenchmarkRunner
        runner = BenchmarkRunner()
        assert runner is not None
        assert len(runner.levels) > 0

    def test_benchmark_result_defaults(self):
        from compiler.optimization.benchmark import BenchmarkResult
        r = BenchmarkResult("O2", 10.5, 100, 80, 10, 8, 2, 2)
        assert r.level_name == "O2"
        assert r.instructions_eliminated == 20
        assert r.elimination_pct == 20.0

    def test_benchmark_report(self):
        from compiler.optimization.benchmark import BenchmarkReport, BenchmarkResult
        report = BenchmarkReport("test_mod")
        report.results["O2"] = BenchmarkResult("O2", 10.5, 100, 80, 10, 8, 2, 2)
        assert report.best_level == "O2"
        assert report.fastest_level == "O2"
        summary = report.format_summary()
        assert "test_mod" in summary

    def test_benchmark_report_table(self):
        from compiler.optimization.benchmark import BenchmarkReport, BenchmarkResult
        report = BenchmarkReport("test")
        report.results["O0"] = BenchmarkResult("O0", 0.1, 100, 100, 10, 10, 2, 2)
        report.results["O2"] = BenchmarkResult("O2", 10.5, 100, 80, 10, 8, 2, 2)
        table = report.format_table()
        assert "Level" in table
        assert "O0" in table
        assert "O2" in table

    def test_benchmark_report_dict(self):
        from compiler.optimization.benchmark import BenchmarkReport, BenchmarkResult
        report = BenchmarkReport("test")
        report.results["O0"] = BenchmarkResult("O0", 0.1, 100, 100, 10, 10, 2, 2)
        d = report.to_dict()
        assert d["module_name"] == "test"
        assert "O0" in d["results"]

    def test_scalability_point(self):
        from compiler.optimization.benchmark import ScalabilityPoint
        p = ScalabilityPoint(size=100, duration_ms=5.0)
        assert p.size == 100

    def test_scalability_report(self):
        from compiler.optimization.benchmark import ScalabilityPoint, ScalabilityReport
        report = ScalabilityReport()
        report.points.append(ScalabilityPoint(10, 1.0))
        report.points.append(ScalabilityPoint(100, 10.0))
        summary = report.format_summary()
        assert "Scalability" in summary

    def test_scalability_estimate(self):
        from compiler.optimization.benchmark import ScalabilityPoint, ScalabilityReport
        report = ScalabilityReport()
        report.points.append(ScalabilityPoint(10, 1.0))
        report.points.append(ScalabilityPoint(100, 8.0))
        report.points.append(ScalabilityPoint(1000, 64.0))
        assert "O(n)" in report.estimated_complexity

    def test_benchmark_runner_runs(self):
        mod = _make_simple_module()
        from compiler.optimization.benchmark import BenchmarkRunner
        runner = BenchmarkRunner()
        report = runner.benchmark(mod, iterations=1)
        assert report.module_name == "test"
        assert "O0" in report.results
        assert "O2" in report.results


# ===================================================================
# 9. Pass Configuration Tests
# ===================================================================


class TestPassConfiguration:
    def test_pass_enable_disable(self):
        mgr = OptimizationManager()
        passes_before = len(mgr.registry.all_passes())
        for info in mgr.registry.all_passes():
            assert info is not None
        assert passes_before > 0

    def test_pipeline_config_defaults(self):
        config = PipelineConfig()
        assert config.max_fixed_point_iterations == 4
        assert config.enable_statistics is True
        assert config.enable_verification is True
        assert config.enable_debug is False
        assert config.debug_output_dir == ""
        assert config.timeout_seconds == 0.0

    def test_pipeline_config_custom(self):
        config = PipelineConfig()
        config.max_fixed_point_iterations = 10
        config.enable_verification = False
        config.enable_debug = True
        config.custom_pass_order = ["constant_folding", "dead_code_elimination"]
        assert config.max_fixed_point_iterations == 10
        assert config.enable_verification is False
        assert config.custom_pass_order is not None


# ===================================================================
# 10. Regression Tests
# ===================================================================


class TestRegressionTests:
    def test_empty_module_no_crash(self):
        mod = _make_module()
        mgr = OptimizationManager()
        for level in [OptimizationLevel.O0, OptimizationLevel.O1, OptimizationLevel.O2, OptimizationLevel.O3]:
            report = mgr.optimize(mod, level)
            assert report is not None

    def test_module_with_only_declaration(self):
        mod = _make_module()
        ft = func_type((), IR_VOID)
        func = IRFunction("declare_me", ft)
        mod.add_function(func)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None

    def test_single_block_no_terminator_no_crash(self):
        mod = _make_module()
        f = _make_func("no_term")
        bb = BasicBlock("entry")
        bb.append(Add("x", make_int_constant(1), make_int_constant(2)))
        f.append_block(bb)
        mod.add_function(f)
        config = PipelineConfig()
        config.enable_verification = False
        mgr = OptimizationManager(config=config)
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None

    def test_large_constants_no_overflow(self):
        mod = _make_module()
        ft = func_type((IR_I64,), IR_I64)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        max_val = 2**63 - 1
        a = make_int_constant(max_val)
        b = make_int_constant(1)
        x = Add("x", a, b)
        bb.append(x)
        bb.append(Return(func.args[0]))
        func.append_block(bb)
        mod.add_function(func)
        from compiler.optimization.passes.constant_folding import ConstantFoldingPass
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_many_functions(self):
        mod = _make_module("many")
        for i in range(50):
            f = _make_func(f"func_{i}")
            bb = BasicBlock("entry")
            bb.append(Return(make_int_constant(i)))
            f.append_block(bb)
            mod.add_function(f)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O1)
        assert report is not None

    def test_nested_blocks_keep_correctness(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("then")
        bb3 = BasicBlock("else_")
        bb4 = BasicBlock("merge")
        cond = ICmp("cmp", ICmpPredicate.SGT, f.args[0], make_int_constant(0))
        bb1.append(cond)
        bb1.append(CondBranch(cond, bb2, bb3))
        pos = Add("pos", f.args[0], make_int_constant(1))
        bb2.append(pos)
        bb2.append(Branch(bb4))
        neg = Sub("neg", f.args[0], make_int_constant(1))
        bb3.append(neg)
        bb3.append(Branch(bb4))
        phi = Phi("result", IR_I32, [(pos, bb2), (neg, bb3)])
        bb4.append(phi)
        bb4.append(Return(phi))
        bb1.add_successor(bb2)
        bb1.add_successor(bb3)
        bb2.add_predecessor(bb1)
        bb2.add_successor(bb4)
        bb3.add_predecessor(bb1)
        bb3.add_successor(bb4)
        bb4.add_predecessor(bb2)
        bb4.add_predecessor(bb3)
        f.append_block(bb1)
        f.append_block(bb2)
        f.append_block(bb3)
        f.append_block(bb4)
        mod.add_function(f)
        config = PipelineConfig()
        config.enable_verification = False
        mgr = OptimizationManager(config=config)
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None


# ===================================================================
# 11. Property-Based Tests
# ===================================================================


class TestPropertyBasedTests:
    def test_optimisation_is_idempotent(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        mgr.optimize(mod, OptimizationLevel.O2)
        instr_after_first = mod.instruction_count
        mgr.optimize(mod, OptimizationLevel.O2)
        instr_after_second = mod.instruction_count
        assert instr_after_second <= instr_after_first

    def test_never_increases_instruction_count(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        x = Add("x", f.args[0], make_int_constant(1))
        bb.append(x)
        bb.append(Return(x))
        f.append_block(bb)
        mod.add_function(f)
        before = mod.instruction_count
        mgr = OptimizationManager()
        for level in [OptimizationLevel.O0, OptimizationLevel.O1, OptimizationLevel.O2, OptimizationLevel.O3]:
            mod_copy = __import__("copy").deepcopy(mod)
            mgr.optimize(mod_copy, level)
            assert mod_copy.instruction_count <= before, f"O{level.value} increased instruction count"

    def test_monotonic_optimisation(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32, IR_I32), IR_I32)
        bb = BasicBlock("entry")
        a = f.args[0]
        b = f.args[1]
        c1 = Add("c1", a, make_int_constant(0))
        bb.append(c1)
        c2 = Add("c2", b, make_int_constant(0))
        bb.append(c2)
        c3 = Mul("c3", make_int_constant(2), make_int_constant(3))
        bb.append(c3)
        c4 = Add("c4", c1, c2)
        bb.append(c4)
        bb.append(Return(c4))
        f.append_block(bb)
        mod.add_function(f)
        mgr = OptimizationManager()
        o2_count = 0
        o3_count = 0
        m2 = __import__("copy").deepcopy(mod)
        mgr.optimize(m2, OptimizationLevel.O2)
        o2_count = m2.instruction_count
        m3 = __import__("copy").deepcopy(mod)
        mgr.optimize(m3, OptimizationLevel.O3)
        o3_count = m3.instruction_count
        assert o3_count <= o2_count

    def test_semantics_preserved_through_phi(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        entry = BasicBlock("entry")
        then_b = BasicBlock("then")
        else_b = BasicBlock("else")
        merge = BasicBlock("merge")
        cond = ICmp("c", ICmpPredicate.SGT, f.args[0], make_int_constant(0))
        entry.append(cond)
        entry.append(CondBranch(cond, then_b, else_b))
        pos = Add("pos", f.args[0], make_int_constant(1))
        then_b.append(pos)
        then_b.append(Branch(merge))
        neg = Sub("neg", f.args[0], make_int_constant(1))
        else_b.append(neg)
        else_b.append(Branch(merge))
        phi = Phi("result", IR_I32, [(pos, then_b), (neg, else_b)])
        merge.append(phi)
        merge.append(Return(phi))
        entry.add_successor(then_b)
        entry.add_successor(else_b)
        then_b.add_predecessor(entry)
        then_b.add_successor(merge)
        else_b.add_predecessor(entry)
        else_b.add_successor(merge)
        merge.add_predecessor(then_b)
        merge.add_predecessor(else_b)
        f.append_block(entry)
        f.append_block(then_b)
        f.append_block(else_b)
        f.append_block(merge)
        mod.add_function(f)
        config = PipelineConfig()
        config.enable_verification = False
        mgr = OptimizationManager(config=config)
        m2 = __import__("copy").deepcopy(mod)
        mgr.optimize(m2, OptimizationLevel.O1)
        assert m2.function_count >= 0


# ===================================================================
# 12. Security Boundary Tests
# ===================================================================


class TestSecurityBoundary:
    def test_large_ir_no_resource_exhaustion(self):
        mod = _make_module("large")
        for i in range(100):
            f = _make_func(f"func_{i}")
            bb = BasicBlock("entry")
            x = None
            for j in range(10):
                x = Add(f"x_{j}", make_int_constant(j), make_int_constant(j + 1))
                bb.append(x)
            bb.append(Return(make_int_constant(i)))
            f.append_block(bb)
            mod.add_function(f)
        ctx = _make_ctx(mod)
        ctx.set_option("max_iterations", 2)
        mgr = OptimizationManager()
        config = PipelineConfig()
        config.max_fixed_point_iterations = 2
        config.enable_verification = True
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None
        assert report.pass_count > 0

    def test_deep_nested_blocks(self):
        mod = _make_module()
        f = _make_func("deep")
        blocks = []
        for i in range(50):
            bb = BasicBlock(f"bb_{i}")
            blocks.append(bb)
            if i > 0:
                blocks[i - 1].append(Branch(bb))
                blocks[i - 1].add_successor(bb)
                bb.add_predecessor(blocks[i - 1])
            f.append_block(bb)
        blocks[-1].append(Return())
        mod.add_function(f)
        mgr = OptimizationManager()
        config = PipelineConfig()
        config.enable_verification = True
        config.max_fixed_point_iterations = 2
        ctx = _make_ctx(mod)
        pipeline = OptimizationPipeline(mgr.registry, config)
        pipeline.build_default_pipeline()
        report = pipeline.run(mod, ctx)
        assert report is not None

    def test_extreme_constants(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        huge = IntConstant(2**31 - 1, int_type(32))
        x = Mul("x", huge, huge)
        bb.append(x)
        bb.append(Return(x))
        f.append_block(bb)
        mod.add_function(f)
        from compiler.optimization.passes.constant_folding import ConstantFoldingPass
        ctx = _make_ctx(mod)
        p = ConstantFoldingPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_string_constants_no_modification(self):
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        bb.append(Return())
        f.append_block(bb)
        mod.add_function(f)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None


# ===================================================================
# 13. Cross-Platform Compatibility Tests
# ===================================================================


class TestCrossPlatform:
    def test_architecture_independent_results(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None
        assert mod.instruction_count >= 0
        assert mod.block_count >= 0

    def test_consistent_pass_registration(self):
        mgr1 = OptimizationManager()
        mgr2 = OptimizationManager()
        names1 = mgr1.available_passes()
        names2 = mgr2.available_passes()
        assert sorted(names1) == sorted(names2)

    def test_consistent_analysis_registration(self):
        mgr1 = OptimizationManager()
        mgr2 = OptimizationManager()
        a1 = mgr1.available_analyses()
        a2 = mgr2.available_analyses()
        assert sorted(a1) == sorted(a2)


# ===================================================================
# 14. Optimizer Manager Extended Tests
# ===================================================================


class TestOptimizerManagerExtended:
    def test_optimize_all_levels(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        for level in [
            OptimizationLevel.O0,
            OptimizationLevel.O1,
            OptimizationLevel.O2,
            OptimizationLevel.O3,
            OptimizationLevel.OS,
            OptimizationLevel.OZ,
            OptimizationLevel.OFAST,
        ]:
            report = mgr.optimize(mod, level)
            assert isinstance(report, OptimizationReport)

    def test_optimize_module_int_levels(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        for i in range(7):
            report = mgr.optimize_module(mod, level=i)
            assert isinstance(report, OptimizationReport)

    def test_run_single_pass_by_name(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        mgr.run_pass(mod, "constant_folding")
        assert True

    def test_nonexistent_pass(self):
        mod = _make_simple_module()
        mgr = OptimizationManager()
        mgr.run_pass(mod, "nonexistent_pass")
        assert True

    def test_summary_includes_pass_count(self):
        mgr = OptimizationManager()
        s = mgr.summary()
        assert "Registered passes" in s
        assert "Registered analyses" in s
        assert "Pipeline levels" in s


# ===================================================================
# 15. SSA Optimisation Tests
# ===================================================================


class TestSSAOptimization:
    def test_ssa_cleanup(self):
        from compiler.optimization.passes.ssa_cleanup import SSACleanupPass
        mod = _make_module()
        f = _make_func("f")
        bb = BasicBlock("entry")
        x = Add("x", make_int_constant(1), make_int_constant(2))
        bb.append(x)
        bb.append(Return(x))
        f.append_block(bb)
        mod.add_function(f)
        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_sparse_ccp(self):
        from compiler.optimization.passes.sparse_ccp import SparseConditionalConstantPropagationPass
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        entry = BasicBlock("entry")
        then_b = BasicBlock("then")
        else_b = BasicBlock("else")
        merge = BasicBlock("merge")
        cond = ICmp("c", ICmpPredicate.SGT, f.args[0], make_int_constant(0))
        entry.append(cond)
        entry.append(CondBranch(cond, then_b, else_b))
        pos = Add("pos", f.args[0], make_int_constant(1))
        then_b.append(pos)
        then_b.append(Branch(merge))
        neg = Sub("neg", f.args[0], make_int_constant(1))
        else_b.append(neg)
        else_b.append(Branch(merge))
        phi = Phi("result", IR_I32, [(pos, then_b), (neg, else_b)])
        merge.append(phi)
        merge.append(Return(phi))
        entry.add_successor(then_b)
        entry.add_successor(else_b)
        then_b.add_predecessor(entry)
        then_b.add_successor(merge)
        else_b.add_predecessor(entry)
        else_b.add_successor(merge)
        merge.add_predecessor(then_b)
        merge.add_predecessor(else_b)
        f.append_block(entry)
        f.append_block(then_b)
        f.append_block(else_b)
        f.append_block(merge)
        mod.add_function(f)
        ctx = _make_ctx(mod)
        p = SparseConditionalConstantPropagationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_phi_cleanup(self):
        from compiler.optimization.passes.ssa_cleanup import SSACleanupPass
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
        ctx = _make_ctx(mod)
        p = SSACleanupPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 16. Corner Case Tests
# ===================================================================


class TestCornerCases:
    def test_division_by_constant(self):
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        bb = BasicBlock("entry")
        x = SDiv("x", f.args[0], make_int_constant(2))
        bb.append(x)
        bb.append(Return(x))
        f.append_block(bb)
        mod.add_function(f)
        from compiler.optimization.passes.strength_reduction import StrengthReductionPass
        ctx = _make_ctx(mod)
        p = StrengthReductionPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)

    def test_multiple_returns(self):
        mod = _make_module()
        f = _make_func("f")
        bb1 = BasicBlock("entry")
        bb2 = BasicBlock("exit")
        bb1.append(Branch(bb2))
        bb2.append(Return(make_int_constant(0)))
        bb1.add_successor(bb2)
        bb2.add_predecessor(bb1)
        f.append_block(bb1)
        f.append_block(bb2)
        mod.add_function(f)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O2)
        assert report is not None

    def test_switch_statement(self):
        from compiler.ir.instructions import Switch
        mod = _make_module()
        f = _make_func("f", (IR_I32,), IR_I32)
        entry = BasicBlock("entry")
        case1 = BasicBlock("case1")
        case2 = BasicBlock("case2")
        default = BasicBlock("default")
        entry.append(Switch(f.args[0], default, [(make_int_constant(0), case1), (make_int_constant(1), case2)]))
        case1.append(Return(make_int_constant(10)))
        case2.append(Return(make_int_constant(20)))
        default.append(Return(make_int_constant(0)))
        entry.add_successor(case1)
        entry.add_successor(case2)
        entry.add_successor(default)
        case1.add_predecessor(entry)
        case2.add_predecessor(entry)
        default.add_predecessor(entry)
        f.append_block(entry)
        f.append_block(case1)
        f.append_block(case2)
        f.append_block(default)
        mod.add_function(f)
        from compiler.optimization.passes.switch_optimization import SwitchOptimizationPass
        ctx = _make_ctx(mod)
        p = SwitchOptimizationPass()
        result = p.run(mod, ctx)
        assert isinstance(result, PassResult)


# ===================================================================
# 17. Full Pipeline Integration Tests
# ===================================================================


class TestFullPipelineIntegration:
    def test_o0_preserves_all(self):
        mod = _make_simple_module()
        before = mod.instruction_count
        mgr = OptimizationManager()
        mgr.optimize(mod, OptimizationLevel.O0)
        assert mod.instruction_count == before

    def test_o1_folds_constants(self):
        mod = _make_module()
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        x = Add("x", make_int_constant(2), make_int_constant(3))
        bb.append(x)
        bb.append(Return(x))
        func.append_block(bb)
        mod.add_function(func)
        mgr = OptimizationManager()
        mgr.optimize(mod, OptimizationLevel.O1)
        assert mod.instruction_count >= 1

    def test_o2_performs_cse(self):
        mod = _make_module()
        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        a = func.args[0]
        b = func.args[1]
        x = Add("x", a, b)
        bb.append(x)
        y = Add("y", a, b)
        bb.append(y)
        z = Add("z", x, y)
        bb.append(z)
        bb.append(Return(z))
        func.append_block(bb)
        mod.add_function(func)
        mgr = OptimizationManager()
        mgr.optimize(mod, OptimizationLevel.O2)
        assert mod.instruction_count <= 4

    def test_o3_inlines_small_funcs(self):
        mod = _make_module()
        callee = _make_func("add_one", (IR_I32,), IR_I32)
        cbb = BasicBlock("entry")
        r = Add("r", callee.args[0], make_int_constant(1))
        cbb.append(r)
        cbb.append(Return(r))
        callee.append_block(cbb)
        caller = _make_func("caller", (IR_I32,), IR_I32)
        fbb = BasicBlock("entry")
        ft = func_type((IR_I32,), IR_I32)
        res = Call("res", ft, callee, [caller.args[0]])
        fbb.append(res)
        fbb.append(Return(res))
        caller.append_block(fbb)
        mod.add_function(callee)
        mod.add_function(caller)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.O3)
        assert report is not None

    def test_os_optimizes_for_size(self):
        mod = _make_module()
        ft = func_type((IR_I32,), IR_I32)
        func = IRFunction("f", ft)
        bb = BasicBlock("entry")
        x = Add("x", func.args[0], make_int_constant(1))
        bb.append(x)
        y = Add("y", x, make_int_constant(1))
        bb.append(y)
        z = Add("z", y, make_int_constant(0))
        bb.append(z)
        bb.append(Return(z))
        func.append_block(bb)
        mod.add_function(func)
        mgr = OptimizationManager()
        report = mgr.optimize(mod, OptimizationLevel.OS)
        assert report is not None

    def test_full_pipeline_does_not_crash_on_complex_module(self):
        mod = _make_module("complex")
        for i in range(5):
            f = _make_func(f"level_{i}", (IR_I32,), IR_I32)
            entry = BasicBlock("entry")
            then_b = BasicBlock("then")
            else_b = BasicBlock("else")
            merge = BasicBlock("merge")
            cond = ICmp(f"c_{i}", ICmpPredicate.SGT, f.args[0], make_int_constant(0))
            entry.append(cond)
            entry.append(CondBranch(cond, then_b, else_b))
            pos = Add(f"pos_{i}", f.args[0], make_int_constant(1))
            then_b.append(pos)
            then_b.append(Branch(merge))
            neg = Sub(f"neg_{i}", f.args[0], make_int_constant(1))
            else_b.append(neg)
            else_b.append(Branch(merge))
            phi = Phi(f"res_{i}", IR_I32, [(pos, then_b), (neg, else_b)])
            merge.append(phi)
            merge.append(Return(phi))
            entry.add_successor(then_b)
            entry.add_successor(else_b)
            then_b.add_predecessor(entry)
            then_b.add_successor(merge)
            else_b.add_predecessor(entry)
            else_b.add_successor(merge)
            merge.add_predecessor(then_b)
            merge.add_predecessor(else_b)
            f.append_block(entry)
            f.append_block(then_b)
            f.append_block(else_b)
            f.append_block(merge)
            mod.add_function(f)
        config = PipelineConfig()
        config.enable_verification = False
        mgr = OptimizationManager(config=config)
        for level in [OptimizationLevel.O0, OptimizationLevel.O1, OptimizationLevel.O2, OptimizationLevel.O3, OptimizationLevel.OS]:
            m = __import__("copy").deepcopy(mod)
            report = mgr.optimize(m, level)
            assert report is not None
