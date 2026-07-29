"""
IR Benchmark Suite

Performance benchmarks for the I language Intermediate Representation.
"""

import sys
import os
import time
import statistics
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.ir.types import (
    IR_I1, IR_I8, IR_I16, IR_I32, IR_I64, IR_F32, IR_F64,
    int_type, float_type, ptr_type, array_type, struct_type, func_type,
    is_numeric_type, is_integer_type,
)
from compiler.ir.values import (
    IntConstant, FloatConstant, BoolConstant, StringConstant,
    Argument, GlobalVariable, make_int_constant,
)
from compiler.ir.instructions import (
    Add, Sub, Mul, ICmp, ICmpPredicate, Return, Branch, CondBranch,
    Load, Store, Alloca, Call, Phi,
    Trunc, ZExt, SExt, BitCast,
)
from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.module import IRModule
from compiler.ir.context import IRContext
from compiler.ir.builder import IRBuilder
from compiler.ir.validator import IRValidator, validate
from compiler.ir.printer import IRPrinter, print_ir
from compiler.ir.serialization import serialize_json, deserialize_json, serialize_text
from compiler.ir.cfg import CFG
from compiler.ir.ssa import LivenessAnalysis, SSABuilder
from compiler.ir.lir import (
    LIRInstKind, LIRInstruction, LIRBlock, LIRFunction,
    LIRModule, LIRPrinter, LIRBuilder, lower_ir_to_lir,
)


class BenchmarkResult:
    """Result of a single benchmark."""

    def __init__(self, name: str, times: List[float], ops: int = 1) -> None:
        self.name = name
        self.times = times
        self.ops = ops

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.times) * 1000

    @property
    def median_ms(self) -> float:
        return statistics.median(self.times) * 1000

    @property
    def min_ms(self) -> float:
        return min(self.times) * 1000

    @property
    def max_ms(self) -> float:
        return max(self.times) * 1000

    @property
    def stdev_ms(self) -> float:
        return statistics.stdev(self.times) * 1000 if len(self.times) > 1 else 0

    @property
    def ops_per_sec(self) -> float:
        return self.ops / (self.mean_ms / 1000) if self.mean_ms > 0 else 0

    def format(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Mean: {self.mean_ms:.3f}ms | "
            f"Median: {self.median_ms:.3f}ms | "
            f"Stdev: {self.stdev_ms:.3f}ms\n"
            f"  Min: {self.min_ms:.3f}ms | "
            f"Max: {self.max_ms:.3f}ms\n"
            f"  Throughput: {self.ops_per_sec:,.0f} ops/s"
        )


# ── Benchmarks ────────────────────────────────────────────────────


def bench_ir_type_creation(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: creating IR type objects."""
    for _ in range(warmup):
        int_type(32)
        float_type(64)
        ptr_type(IR_I32)
        array_type(10, IR_I8)
        struct_type((IR_I32, IR_I64))
        func_type((IR_I32, IR_I64), IR_I32)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            int_type(32)
            float_type(64)
            ptr_type(IR_I32)
            array_type(10, IR_I8)
            struct_type((IR_I32, IR_I64))
            func_type((IR_I32, IR_I64), IR_I32)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Type Creation", times, iterations * 1000 * 6)


def bench_ir_type_equality(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IR type equality checks."""
    types_a = [IR_I32, IR_I64, IR_F32, IR_F64,
               ptr_type(IR_I32), array_type(5, IR_I8)]
    types_b = [IR_I32, IR_I64, IR_F32, IR_F64,
               ptr_type(IR_I32), array_type(5, IR_I8)]

    for _ in range(warmup):
        for a in types_a:
            for b in types_b:
                _ = a == b

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            for a in types_a:
                for b in types_b:
                    _ = a == b
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Type Equality", times, iterations * 1000 * 36)


def bench_ir_constant_creation(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: creating IR constants."""
    for _ in range(warmup):
        IntConstant(42, IR_I32)
        FloatConstant(3.14, IR_F64)
        BoolConstant(True)
        StringConstant("hello")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            IntConstant(42, IR_I32)
            FloatConstant(3.14, IR_F64)
            BoolConstant(True)
            StringConstant("hello")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Constant Creation", times, iterations * 1000 * 4)


def bench_ir_instruction_creation(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: creating IR instructions."""
    a = IntConstant(1, IR_I32)
    b = IntConstant(2, IR_I32)
    bb = BasicBlock("bench")

    for _ in range(warmup):
        Add("t", a, b)
        Sub("t", a, b)
        Mul("t", a, b)
        ICmp("t", ICmpPredicate.SLT, a, b)
        Return(a)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            Add("t", a, b)
            Sub("t", a, b)
            Mul("t", a, b)
            ICmp("t", ICmpPredicate.SLT, a, b)
            Return(a)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Instruction Creation", times, iterations * 1000 * 5)


def bench_ir_block_operations(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: basic block append and iterate."""
    for _ in range(warmup):
        bb = BasicBlock("bench")
        for i in range(50):
            a = make_int_constant(i)
            b = make_int_constant(i + 1)
            bb.append(Add(f"t{i}", a, b))
        for inst in bb:
            pass

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(500):
            bb = BasicBlock("bench")
            for i in range(50):
                a = make_int_constant(i)
                b = make_int_constant(i + 1)
                bb.append(Add(f"t{i}", a, b))
            for inst in bb:
                pass
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Block Operations (50 insts)", times, iterations * 500)


def bench_ir_builder(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IRBuilder instruction construction."""
    ctx = IRContext()
    builder = IRBuilder(ctx)
    mod = ctx.module

    for _ in range(warmup):
        ft = func_type((IR_I32, IR_I32), IR_I32)
        func = IRFunction("bench", ft)
        mod.add_function(func)
        entry = builder.append_to(func, "entry")
        val = builder.add(func.args[0], func.args[1], "v")
        for _ in range(20):
            val = builder.add(val, func.args[0], "v")
        builder.ret(val)
        mod.remove_function(func)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(200):
            ft = func_type((IR_I32, IR_I32), IR_I32)
            func = IRFunction("bench", ft)
            mod.add_function(func)
            entry = builder.append_to(func, "entry")
            val = builder.add(func.args[0], func.args[1], "v")
            for _ in range(20):
                val = builder.add(val, func.args[0], "v")
            builder.ret(val)
            mod.remove_function(func)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IRBuilder Construction", times, iterations * 200)


def bench_ir_validation(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IR module validation."""
    mod = IRModule("bench")
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("validate_me", ft)
    bb = BasicBlock("entry")
    a = make_int_constant(1)
    b = make_int_constant(2)
    bb.append(Add("sum", a, b))
    bb.append(Return(bb[0]))
    func.append_block(bb)
    mod.add_function(func)

    validator = IRValidator()

    for _ in range(warmup):
        validator.validate_module(mod)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(5000):
            validator.validate_module(mod)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Validation", times, iterations * 5000)


def bench_ir_serialization(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IR JSON serialization roundtrip."""
    mod = IRModule("bench")
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("serialize_me", ft)
    bb = BasicBlock("entry")
    a = make_int_constant(1)
    b = make_int_constant(2)
    bb.append(Add("sum", a, b))
    bb.append(Return(bb[0]))
    func.append_block(bb)
    mod.add_function(func)

    for _ in range(warmup):
        json_str = serialize_json(mod)
        deserialize_json(json_str)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(500):
            json_str = serialize_json(mod)
            deserialize_json(json_str)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Serialization Roundtrip", times, iterations * 500)


def bench_ir_text_output(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IR text output."""
    mod = IRModule("bench")
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("print_me", ft)
    bb = BasicBlock("entry")
    a = make_int_constant(1)
    b = make_int_constant(2)
    bb.append(Add("sum", a, b))
    bb.append(Return(bb[0]))
    func.append_block(bb)
    mod.add_function(func)

    for _ in range(warmup):
        print_ir(mod)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(2000):
            print_ir(mod)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR Text Output", times, iterations * 2000)


def bench_cfg_analysis(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: CFG dominator and loop analysis."""
    ft = func_type((), IR_I32)
    func = IRFunction("cfg_bench", ft)
    entry = BasicBlock("entry")
    bb1 = BasicBlock("bb1")
    bb2 = BasicBlock("bb2")
    exit_bb = BasicBlock("exit")

    entry.add_successor(bb1)
    entry.add_successor(bb2)
    bb1.add_predecessor(entry)
    bb2.add_predecessor(entry)
    entry.append(CondBranch(BoolConstant(True), bb1, bb2))

    bb1.add_successor(exit_bb)
    bb2.add_successor(exit_bb)
    exit_bb.add_predecessor(bb1)
    exit_bb.add_predecessor(bb2)
    bb1.append(Branch(exit_bb))
    bb2.append(Branch(exit_bb))

    exit_bb.append(Return(make_int_constant(0)))

    for b in [entry, bb1, bb2, exit_bb]:
        func.append_block(b)

    for _ in range(warmup):
        cfg = CFG(func)
        cfg.dominates(entry, exit_bb)
        cfg.immediate_dominator(bb1)
        cfg.loops

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(2000):
            cfg = CFG(func)
            cfg.dominates(entry, exit_bb)
            cfg.immediate_dominator(bb1)
            _ = cfg.loops
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("CFG Analysis", times, iterations * 2000)


def bench_lir_lowering(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: IR to LIR lowering."""
    mod = IRModule("bench")
    ft = func_type((IR_I32, IR_I32), IR_I32)
    func = IRFunction("lower_me", ft)
    bb = BasicBlock("entry")
    a = make_int_constant(1)
    b = make_int_constant(2)
    bb.append(Add("sum", a, b))
    bb.append(Return(bb[0]))
    func.append_block(bb)
    mod.add_function(func)

    for _ in range(warmup):
        lower_ir_to_lir(mod)

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(1000):
            lower_ir_to_lir(mod)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("IR to LIR Lowering", times, iterations * 1000)


def bench_lir_operations(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: LIR instruction and block construction."""
    for _ in range(warmup):
        func = LIRFunction("bench")
        block = LIRBlock("entry")
        builder = LIRBuilder()
        builder.set_function(func)
        builder.create_block("entry")
        builder.position_at(block)
        for i in range(20):
            builder.emit_iadd(f"r{i}", f"r{i}", f"r{i+1}")
        builder.emit_ret("r0")

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(500):
            func = LIRFunction("bench")
            block = LIRBlock("entry")
            builder = LIRBuilder()
            builder.set_function(func)
            builder.create_block("entry")
            builder.position_at(block)
            for i in range(20):
                builder.emit_iadd(f"r{i}", f"r{i}", f"r{i+1}")
            builder.emit_ret("r0")
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("LIR Operations", times, iterations * 500)


def bench_use_tracking(iterations: int = 1000, warmup: int = 100) -> BenchmarkResult:
    """Benchmark: value use chain tracking."""
    c = make_int_constant(42)
    bb = BasicBlock("bench")

    for _ in range(warmup):
        for i in range(50):
            a = make_int_constant(i)
            inst = Add(f"t{i}", c, a)
            bb.append(inst)
        for inst in c.uses:
            pass
        _ = c.use_count
        bb.clear()

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        for _ in range(200):
            for i in range(50):
                a = make_int_constant(i)
                inst = Add(f"t{i}", c, a)
                bb.append(inst)
            for inst in c.uses:
                pass
            _ = c.use_count
            bb.clear()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("Use Tracking", times, iterations * 200)


# ── Run All ────────────────────────────────────────────────────────


def run_all_benchmarks() -> List[BenchmarkResult]:
    """Run all IR benchmarks."""
    benchmarks = [
        bench_ir_type_creation,
        bench_ir_type_equality,
        bench_ir_constant_creation,
        bench_ir_instruction_creation,
        bench_ir_block_operations,
        bench_ir_builder,
        bench_ir_validation,
        bench_ir_serialization,
        bench_ir_text_output,
        bench_cfg_analysis,
        bench_lir_lowering,
        bench_lir_operations,
        bench_use_tracking,
    ]

    results = []
    for bench_fn in benchmarks:
        print(f"  Running {bench_fn.__doc__.strip().split(':')[0]}...")
        result = bench_fn()
        results.append(result)

    return results


def print_results(results: List[BenchmarkResult]) -> None:
    """Print benchmark results."""
    print("\n" + "=" * 70)
    print("I LANGUAGE IR BENCHMARK RESULTS")
    print("=" * 70)

    for result in results:
        print()
        print(result.format())

    print("\n" + "=" * 70)


if __name__ == "__main__":
    results = run_all_benchmarks()
    print_results(results)
