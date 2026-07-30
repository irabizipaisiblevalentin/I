from __future__ import annotations

import unittest

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import (
    Return,
)
from compiler.ir.types import IR_F64, IR_I64, IR_PTR, IR_VOID, IRFunctionType
from compiler.ir.values import Value
from compiler.native.register.allocator import (
    X86_64_GPRS,
    AllocationResult,
    GraphColoringAllocator,
    InterferenceGraph,
    PhysicalRegister,
    RegisterClass,
    register_class_for,
)
from compiler.native.register.coalescing import Move, coalesce
from compiler.native.register.liveness import LiveInterval, LiveRangeAnalysis
from compiler.native.register.spill import SpillManager, StackSlot
from compiler.native.target.desc import TargetDescription
from compiler.native.target.kind import TargetKind


class _TestValue(Value):
    def __init__(self, name: str, typ=IR_I64) -> None:
        super().__init__(name, typ)

    def _value_kind(self):
        from compiler.ir.values import ValueKind
        return ValueKind.INSTRUCTION


class TestLiveInterval(unittest.TestCase):
    def test_basic(self) -> None:
        v = _TestValue("v1")
        li = LiveInterval(0, 10, v)
        self.assertEqual(li.start, 0)
        self.assertEqual(li.end, 10)
        self.assertIs(li.value, v)

    def test_overlaps(self) -> None:
        v1 = _TestValue("a")
        v2 = _TestValue("b")
        a = LiveInterval(0, 10, v1)
        b = LiveInterval(5, 15, v2)
        self.assertTrue(a.overlaps(b))

        c = LiveInterval(10, 20, v2)
        self.assertFalse(a.overlaps(c))

    def test_contains(self) -> None:
        v = _TestValue("x")
        li = LiveInterval(2, 8, v)
        self.assertTrue(li.contains(3))
        self.assertTrue(li.contains(2))
        self.assertFalse(li.contains(8))

    def test_range(self) -> None:
        v = _TestValue("r")
        li = LiveInterval(3, 7, v)
        self.assertEqual(list(li.range), [3, 4, 5, 6])


class TestInterferenceGraph(unittest.TestCase):
    def setUp(self) -> None:
        self.a = _TestValue("a")
        self.b = _TestValue("b")
        self.c = _TestValue("c")
        self.graph = InterferenceGraph()

    def test_add_node(self) -> None:
        self.graph.add_node(self.a)
        self.assertTrue(self.graph.has_node(self.a))
        self.assertEqual(len(self.graph), 1)

    def test_add_edge(self) -> None:
        self.graph.add_edge(self.a, self.b)
        self.assertTrue(self.graph.interferes(self.a, self.b))
        self.assertTrue(self.graph.interferes(self.b, self.a))

    def test_degree(self) -> None:
        self.graph.add_edge(self.a, self.b)
        self.graph.add_edge(self.a, self.c)
        self.assertEqual(self.graph.degree(self.a), 2)
        self.assertEqual(self.graph.degree(self.b), 1)

    def test_remove_node(self) -> None:
        self.graph.add_edge(self.a, self.b)
        self.graph.add_edge(self.a, self.c)
        self.graph.remove_node(self.a)
        self.assertFalse(self.graph.has_node(self.a))
        self.assertEqual(self.graph.degree(self.b), 0)

    def test_no_self_edge(self) -> None:
        self.graph.add_edge(self.a, self.a)
        self.assertFalse(self.graph.interferes(self.a, self.a))
        self.assertEqual(self.graph.degree(self.a), 0)


class TestGraphColoringAllocator(unittest.TestCase):
    def test_allocate_trivial(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        ret = Return()
        block.append(ret)

        allocator = GraphColoringAllocator()
        result = allocator.allocate(func, TargetDescription(kind=TargetKind.X86_64))
        self.assertIsInstance(result, AllocationResult)

    def test_allocate_with_values(self) -> None:
        v1 = _TestValue("v1")
        v2 = _TestValue("v2")

        allocator = GraphColoringAllocator()

        intervals = {
            v1: LiveInterval(0, 10, v1),
            v2: LiveInterval(5, 15, v2),
        }
        g = allocator._build_interference_graph(intervals)
        self.assertTrue(g.interferes(v1, v2))

    def test_color_simple(self) -> None:
        v1 = _TestValue("a")
        v2 = _TestValue("b")
        graph = InterferenceGraph()
        graph.add_edge(v1, v2)

        allocator = GraphColoringAllocator()
        allocation, spilled = allocator._color(graph, X86_64_GPRS[:4], RegisterClass.GPR)

        self.assertEqual(len(spilled), 0)
        self.assertIn(v1, allocation)
        self.assertIn(v2, allocation)
        self.assertNotEqual(allocation[v1], allocation[v2])

    def test_spill_when_out_of_registers(self) -> None:
        vals = [_TestValue(f"v{i}") for i in range(20)]
        graph = InterferenceGraph()
        for i, a in enumerate(vals):
            for b in vals[i + 1:]:
                graph.add_edge(a, b)

        allocator = GraphColoringAllocator()
        allocation, spilled = allocator._color(graph, X86_64_GPRS[:4], RegisterClass.GPR)

        self.assertTrue(len(spilled) > 0)


class TestPhysicalRegister(unittest.TestCase):
    def test_basic(self) -> None:
        r = PhysicalRegister("rax", RegisterClass.GPR, True)
        self.assertEqual(r.name, "rax")
        self.assertEqual(r.reg_class, RegisterClass.GPR)
        self.assertTrue(r.is_caller_save)

    def test_equality(self) -> None:
        a = PhysicalRegister("rax", RegisterClass.GPR)
        b = PhysicalRegister("rax", RegisterClass.GPR)
        c = PhysicalRegister("rbx", RegisterClass.GPR)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hashing(self) -> None:
        s = {PhysicalRegister("rax", RegisterClass.GPR)}
        s.add(PhysicalRegister("rax", RegisterClass.GPR))
        self.assertEqual(len(s), 1)


class TestRegisterClass(unittest.TestCase):
    def test_classify_int(self) -> None:
        v = _TestValue("x", IR_I64)
        self.assertEqual(register_class_for(v), RegisterClass.GPR)

    def test_classify_float(self) -> None:
        v = _TestValue("f", IR_F64)
        self.assertEqual(register_class_for(v), RegisterClass.XMM)

    def test_classify_ptr(self) -> None:
        v = _TestValue("p", IR_PTR)
        self.assertEqual(register_class_for(v), RegisterClass.GPR)


class TestSpillManager(unittest.TestCase):
    def test_allocate_slot(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)

        mgr = SpillManager()
        v = _TestValue("spillme")
        slot = mgr.allocate_spill_slot(v, func)
        self.assertEqual(slot, 0)
        self.assertIsNotNone(mgr.get_slot(v))
        self.assertEqual(mgr.get_slot(v).index, 0)

    def test_multiple_slots(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)

        mgr = SpillManager()
        v1 = _TestValue("a")
        v2 = _TestValue("b")
        s1 = mgr.allocate_spill_slot(v1, func)
        s2 = mgr.allocate_spill_slot(v2, func)
        self.assertEqual(s1, 0)
        self.assertEqual(s2, 1)

    def test_slot_reuse(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("test", func_type)
        block = BasicBlock("entry")
        func.append_block(block)

        mgr = SpillManager()
        v = _TestValue("v")
        mgr.allocate_spill_slot(v, func)
        self.assertEqual(mgr.allocate_spill_slot(v, func), 0)


class TestStackSlot(unittest.TestCase):
    def test_defaults(self) -> None:
        s = StackSlot(0)
        self.assertEqual(s.index, 0)
        self.assertEqual(s.size, 8)
        self.assertEqual(s.alignment, 8)

    def test_custom(self) -> None:
        s = StackSlot(3, size=16, alignment=16)
        self.assertEqual(s.index, 3)
        self.assertEqual(s.size, 16)


class TestCoalescing(unittest.TestCase):
    def test_coalesce_no_moves(self) -> None:
        graph = InterferenceGraph()
        result = coalesce(graph, [])
        self.assertIsInstance(result, InterferenceGraph)

    def test_coalesce_simple(self) -> None:
        v1 = _TestValue("a")
        v2 = _TestValue("b")
        graph = InterferenceGraph()
        graph.add_node(v1)
        graph.add_node(v2)
        moves = [Move(v1, v2)]
        result = coalesce(graph, moves)
        self.assertIsNotNone(result)


class TestLiveRangeAnalysis(unittest.TestCase):
    def test_analyze_empty_function(self) -> None:
        func_type = IRFunctionType((), IR_VOID)
        func = IRFunction("empty", func_type)
        block = BasicBlock("entry")
        func.append_block(block)
        block.append(Return())

        lra = LiveRangeAnalysis()
        intervals = lra.analyze(func)
        self.assertIsInstance(intervals, dict)
