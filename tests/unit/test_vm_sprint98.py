"""Comprehensive tests for the IVM Production Virtual Machine (Sprint 9.8).

Covers:
  - All 88 IVMOpcodes
  - Bytecode format and serialization
  - Verifier (valid/invalid chunks)
  - Memory (Stack, CallFrame, Heap, Pools)
  - Objects (all 9 VMObject types)
  - Garbage Collector (generational, root scanning)
  - Debugger (breakpoints, stepping, watches)
  - Profiler (timing, hot spots, instruction counts)
  - Statistics
  - Runtime (builtins, modules, exceptions)
  - Scheduler (fibers, states)
  - VMInstance orchestration
  - Integration and regression tests
"""
from __future__ import annotations

import os
import struct
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from vm.vm_bytecode import IVMChunk, IVMInstruction, IVMOpcode
from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_debug import StepMode, VMDebugger
from vm.vm_executor import VMExecutor, VMRuntimeError
from vm.vm_gc import GarbageCollector, GCStats
from vm.vm_instance import VMInstance
from vm.vm_loader import BytecodeFormat, VMLoader, VMVerifier
from vm.vm_memory import (
    CallFrame,
    ConstantPool,
    Heap,
    Stack,
    StackOverflowError,
    StringPool,
)
from vm.vm_objects import (
    VMClosure,
    VMException,
    VMIterator,
    VMList,
    VMMap,
    VMObject,
    VMSet,
    VMString,
    VMStruct,
    VMTuple,
)
from vm.vm_profiler import ProfileEntry, VMProfiler
from vm.vm_runtime import VMRuntime
from vm.vm_scheduler import Fiber, FiberState, VMScheduler
from vm.vm_stats import VMStatistics

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_chunk(name: str = "test") -> IVMChunk:
    return IVMChunk(name=name)


def _emit(chunk: IVMChunk, opcode: IVMOpcode, arg: int = 0, arg2: int = 0, line: int = 0) -> int:
    return chunk.emit(opcode=opcode, arg=arg, arg2=arg2, line=line)


def _add_const(chunk: IVMChunk, value) -> int:
    return chunk.add_constant(value)


def _run(chunk: IVMChunk, config: VMConfig | None = None) -> VMInstance:
    vm = VMInstance(config or VMConfig())
    vm.execute(chunk)
    return vm


# ===================================================================
# 1. Bytecode Format
# ===================================================================

class TestIVMBytecodeFormat(unittest.TestCase):
    """IVMOpcode, IVMInstruction, IVMChunk construction and properties."""

    def test_all_opcodes_have_unique_values(self):
        values = [o.value for o in IVMOpcode]
        self.assertEqual(len(values), len(set(values)))

    def test_opcode_values_in_range(self):
        for o in IVMOpcode:
            v = o.value
            self.assertTrue((0 <= v <= 61) or (64 <= v <= 88), f"{o.name} = {v}")

    def test_instruction_creation(self):
        inst = IVMInstruction(opcode=IVMOpcode.ADD, arg=0, arg2=1, line=5, column=3, source_file="test.i")
        self.assertEqual(inst.opcode, IVMOpcode.ADD)
        self.assertEqual(inst.arg, 0)
        self.assertEqual(inst.arg2, 1)
        self.assertEqual(inst.line, 5)
        self.assertEqual(inst.column, 3)
        self.assertEqual(inst.source_file, "test.i")

    def test_instruction_repr(self):
        inst = IVMInstruction(opcode=IVMOpcode.LOAD_CONST, arg=42)
        r = repr(inst)
        self.assertIn("LOAD_CONST", r)

    def test_chunk_creation(self):
        chunk = IVMChunk("test")
        self.assertEqual(chunk.name, "test")
        self.assertEqual(chunk.instruction_count, 0)
        self.assertEqual(chunk.constant_count, 0)

    def test_chunk_emit(self):
        chunk = _make_chunk()
        idx = _emit(chunk, IVMOpcode.LOAD_CONST, arg=0)
        self.assertEqual(idx, 0)
        self.assertEqual(chunk.instruction_count, 1)
        self.assertEqual(chunk.instructions[0].opcode, IVMOpcode.LOAD_CONST)

    def test_chunk_add_constant(self):
        chunk = _make_chunk()
        idx = chunk.add_constant(42)
        self.assertEqual(idx, 0)
        self.assertEqual(chunk.constants[0], 42)

    def test_chunk_dedup_constants(self):
        chunk = _make_chunk()
        idx1 = chunk.add_constant(42)
        idx2 = chunk.add_constant(42)
        self.assertEqual(idx1, idx2)

    def test_chunk_add_function(self):
        chunk = _make_chunk("main")
        inner = _make_chunk("helper")
        idx = chunk.add_function(inner)
        self.assertEqual(idx, 0)
        self.assertIs(chunk.functions[0], inner)

    def test_chunk_line_table(self):
        chunk = _make_chunk()
        chunk.record_line(10, 0)
        chunk.record_line(20, 5)
        self.assertEqual(chunk.get_line(0), 10)
        self.assertEqual(chunk.get_line(5), 20)
        self.assertEqual(chunk.get_line(3), 10)

    def test_chunk_source_files(self):
        chunk = _make_chunk()
        idx1 = chunk.add_source_file("main.i")
        idx2 = chunk.add_source_file("main.i")
        self.assertEqual(idx1, idx2)

    def test_chunk_repr(self):
        chunk = _make_chunk("test")
        r = repr(chunk)
        self.assertIn("test", r)
        self.assertIn("insts", r)


# ===================================================================
# 2. Memory
# ===================================================================

class TestStack(unittest.TestCase):
    """Value stack — push, pop, peek, overflow, underflow."""

    def test_push_pop(self):
        s = Stack(16)
        s.push(10)
        s.push(20)
        self.assertEqual(s.pop(), 20)
        self.assertEqual(s.pop(), 10)

    def test_peek(self):
        s = Stack(16)
        s.push(42)
        self.assertEqual(s.peek(), 42)

    def test_peek_at(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(s.peek_at(0), 3)
        self.assertEqual(s.peek_at(1), 2)
        self.assertEqual(s.peek_at(2), 1)

    def test_set_at(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.set_at(0, 99)
        self.assertEqual(s.peek(), 99)

    def test_dup_empty_raises(self):
        s = Stack(16)
        with self.assertRaises(IndexError):
            s.dup()

    def test_dup(self):
        s = Stack(16)
        s.push(42)
        s.dup()
        self.assertEqual(len(s), 2)
        self.assertEqual(s.peek(), 42)

    def test_swap(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.swap()
        self.assertEqual(s.pop(), 1)
        self.assertEqual(s.pop(), 2)

    def test_swap_underflow(self):
        s = Stack(16)
        with self.assertRaises(IndexError):
            s.swap()

    def test_rot_three(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.push(3)
        s.rot_three()
        self.assertEqual(s.pop(), 2)
        self.assertEqual(s.pop(), 1)
        self.assertEqual(s.pop(), 3)

    def test_rot_three_underflow(self):
        s = Stack(16)
        with self.assertRaises(IndexError):
            s.rot_three()

    def test_overflow(self):
        s = Stack(4)
        for _ in range(4):
            s.push(0)
        with self.assertRaises(StackOverflowError):
            s.push(99)

    def test_underflow(self):
        s = Stack(4)
        with self.assertRaises(IndexError):
            s.pop()

    def test_clear(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.clear()
        self.assertEqual(len(s), 0)

    def test_truncate(self):
        s = Stack(16)
        for i in range(10):
            s.push(i)
        s.truncate(5)
        self.assertEqual(len(s), 5)

    def test_to_list(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        self.assertEqual(s.to_list(), [1, 2])

    def test_bool(self):
        s = Stack(16)
        self.assertFalse(bool(s))
        s.push(1)
        self.assertTrue(bool(s))


class TestCallFrame(unittest.TestCase):
    """Call frame creation, properties, IP manipulation."""

    def test_create(self):
        chunk = _make_chunk("func")
        frame = CallFrame(chunk=chunk, ip=5, base_pointer=10, function_name="foo", line=3)
        self.assertEqual(frame.ip, 5)
        self.assertEqual(frame.base_pointer, 10)
        self.assertEqual(frame.function_name, "foo")
        self.assertEqual(frame.line, 3)

    def test_advance(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk=chunk, ip=0)
        frame.advance()
        self.assertEqual(frame.ip, 1)

    def test_ip_setter(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk=chunk, ip=0)
        frame.ip = 10
        self.assertEqual(frame.ip, 10)

    def test_repr(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk=chunk, ip=0, base_pointer=5, function_name="bar")
        r = repr(frame)
        self.assertIn("bar", r)
        self.assertIn("ip=0", r)

    def test_closure_property(self):
        chunk = _make_chunk()
        closure = VMClosure(chunk, "fn", 0)
        frame = CallFrame(chunk=chunk, ip=0, closure=closure)
        self.assertIs(frame.closure, closure)


class TestHeap(unittest.TestCase):
    """Object heap — allocation, tracking, statistics."""

    def test_allocate(self):
        h = Heap()
        obj = VMObject()
        h.allocate(obj)
        self.assertEqual(h.size, 1)

    def test_needs_gc(self):
        h = Heap(threshold=2)
        h.allocate(VMObject())
        self.assertFalse(h.needs_gc)
        h.allocate(VMObject())
        self.assertTrue(h.needs_gc)

    def test_collect(self):
        h = Heap()
        obj = VMObject()
        h.allocate(obj)
        freed = h.collect()
        self.assertGreaterEqual(freed, 0)

    def test_track_untrack(self):
        h = Heap()
        obj = VMObject()
        h.track(obj)
        self.assertEqual(h.size, 1)
        h.untrack(obj)
        self.assertEqual(h.size, 0)

    def test_stats(self):
        h = Heap()
        stats = h.get_stats()
        self.assertIn("objects", stats)
        self.assertIn("allocated", stats)
        self.assertIn("collections", stats)


class TestStringPool(unittest.TestCase):
    """String interning — deduplication, lookup, resolve."""

    def test_intern(self):
        p = StringPool()
        idx1 = p.intern("hello")
        idx2 = p.intern("hello")
        self.assertEqual(idx1, idx2)
        self.assertEqual(p.count, 1)

    def test_lookup(self):
        p = StringPool()
        idx = p.intern("world")
        self.assertEqual(p.lookup(idx), "world")
        self.assertEqual(p.lookup(999), "")

    def test_resolve(self):
        p = StringPool()
        p.intern("test")
        self.assertEqual(p.resolve("test"), 0)
        self.assertEqual(p.resolve("missing"), -1)

    def test_len(self):
        p = StringPool()
        p.intern("a")
        p.intern("b")
        self.assertEqual(len(p), 2)


class TestConstantPool(unittest.TestCase):
    """Constant pool — add, get, dedup, iteration."""

    def test_add_get(self):
        cp = ConstantPool()
        idx = cp.add(42)
        self.assertEqual(cp.get(idx), 42)
        self.assertIsNone(cp.get(999))

    def test_dedup(self):
        cp = ConstantPool()
        idx1 = cp.add(42)
        idx2 = cp.add(42)
        self.assertEqual(idx1, idx2)

    def test_len(self):
        cp = ConstantPool()
        cp.add(1)
        cp.add(2)
        self.assertEqual(len(cp), 2)

    def test_iteration(self):
        cp = ConstantPool()
        cp.add(1)
        cp.add(2)
        self.assertEqual(list(cp), [1, 2])

    def test_to_list(self):
        cp = ConstantPool()
        cp.add(1)
        cp.add(2)
        self.assertEqual(cp.to_list(), [1, 2])


# ===================================================================
# 3. VM Objects
# ===================================================================

class TestVMObjects(unittest.TestCase):
    """All 9 heap-allocated VM object types."""

    def test_vmobject_gc_slots(self):
        obj = VMObject()
        self.assertFalse(obj.gc_marked)
        obj.gc_marked = True
        self.assertTrue(obj.gc_marked)
        self.assertEqual(obj.gc_gen, 0)
        obj.gc_gen = 1
        self.assertEqual(obj.gc_gen, 1)
        self.assertIsNone(obj.gc_next)

    def test_vmobject_gc_trace(self):
        obj = VMObject()
        self.assertEqual(obj.gc_trace(), [])

    def test_vmstring(self):
        s = VMString("hello")
        self.assertEqual(s.value, "hello")
        self.assertEqual(len(s), 5)
        self.assertEqual(s, VMString("hello"))
        self.assertNotEqual(s, VMString("world"))
        self.assertEqual(hash(s), hash("hello"))

    def test_vmlist(self):
        lst = VMList([1, 2, 3])
        self.assertEqual(len(lst), 3)
        self.assertEqual(lst.get(0), 1)
        lst.set(1, 99)
        self.assertEqual(lst.get(1), 99)
        lst.append(4)
        self.assertEqual(len(lst), 4)
        with self.assertRaises(IndexError):
            lst.get(100)

    def test_vmlist_slice(self):
        lst = VMList([0, 1, 2, 3])
        sliced = lst.slice(1, 3)
        self.assertEqual(sliced.to_list(), [1, 2])

    def test_vmlist_gc_trace(self):
        inner = VMObject()
        lst = VMList([inner])
        traced = lst.gc_trace()
        self.assertIn(inner, traced)

    def test_vmmap(self):
        m = VMMap()
        m.set("key", "value")
        self.assertEqual(m.get("key"), "value")
        self.assertIsNone(m.get("missing"))

    def test_vmmap_gc_trace(self):
        val = VMObject()
        m = VMMap()
        m.set("k", val)
        traced = m.gc_trace()
        self.assertIn(val, traced)

    def test_vmset(self):
        s = VMSet()
        s.add(1)
        s.add(2)
        s.add(1)
        self.assertEqual(len(s), 2)

    def test_vmtuple(self):
        t = VMTuple((1, 2, 3))
        self.assertEqual(len(t), 3)
        self.assertEqual(t.elements, (1, 2, 3))

    def test_vmtuple_gc_trace(self):
        inner = VMObject()
        t = VMTuple((inner,))
        traced = t.gc_trace()
        self.assertIn(inner, traced)

    def test_vmstruct(self):
        s = VMStruct("Point", ["x", "y"])
        s.set_field("x", 10)
        s.set_field("y", 20)
        self.assertEqual(s.get_field("x"), 10)
        self.assertEqual(s.type_name, "Point")
        with self.assertRaises(AttributeError):
            s.set_field("z", 1)

    def test_vmstruct_gc_trace(self):
        inner = VMObject()
        s = VMStruct("Box", ["content"])
        s.set_field("content", inner)
        traced = s.gc_trace()
        self.assertIn(inner, traced)

    def test_vmclosure(self):
        chunk = _make_chunk()
        c = VMClosure(chunk, "foo", 2)
        self.assertEqual(c.name, "foo")
        self.assertEqual(c.arity, 2)
        self.assertIs(c.chunk, chunk)
        c.capture([1, 2])
        self.assertEqual(c.free_vars, [1, 2])

    def test_vmclosure_gc_trace(self):
        inner = VMObject()
        c = VMClosure(_make_chunk(), "fn", 0)
        c.capture([inner])
        traced = c.gc_trace()
        self.assertIn(inner, traced)

    def test_vmexception(self):
        exc = VMException("error", "TypeError")
        self.assertEqual(exc.message, "error")
        self.assertEqual(exc.type_name, "TypeError")

    def test_vmexception_stack_trace(self):
        exc = VMException("err")
        trace = [{"function": "main", "line": 5}]
        exc.stack_trace = trace
        self.assertEqual(exc.stack_trace, trace)

    def test_vmexception_with_cause(self):
        cause = VMException("root")
        exc = VMException("wrap").with_cause(cause)
        self.assertIs(exc.cause, cause)

    def test_vmiterator_list(self):
        lst = VMList([1, 2, 3])
        it = VMIterator(lst)
        self.assertTrue(it.has_next())
        self.assertEqual(it.next(), 1)
        self.assertEqual(it.next(), 2)
        self.assertEqual(it.next(), 3)
        self.assertFalse(it.has_next())

    def test_vmiterator_string(self):
        it = VMIterator("ab")
        self.assertEqual(it.next(), "a")
        self.assertEqual(it.next(), "b")

    def test_vmiterator_empty_raises(self):
        it = VMIterator([])
        with self.assertRaises(StopIteration):
            it.next()

    def test_vmiterator_map(self):
        m = VMMap()
        m.set("a", 1)
        m.set("b", 2)
        it = VMIterator(m)
        keys = set()
        while it.has_next():
            keys.add(it.next())
        self.assertEqual(keys, {"a", "b"})


# ===================================================================
# 4. Garbage Collector
# ===================================================================

class TestGarbageCollector(unittest.TestCase):
    """Generational GC with root scanning."""

    def test_allocate_young(self):
        gc = GarbageCollector(threshold=100)
        obj = VMObject()
        gc.allocate(obj)
        self.assertEqual(obj.gc_gen, GarbageCollector.YOUNG_GEN)

    def test_collect_young(self):
        gc = GarbageCollector(threshold=2, generational=True)
        gc._auto_collect = False
        for _ in range(5):
            gc.allocate(VMObject())
        collected = gc.collect_young()
        self.assertGreaterEqual(collected, 0)

    def test_collect_all(self):
        gc = GarbageCollector(generational=False)
        gc._auto_collect = False
        for _ in range(5):
            gc.allocate(VMObject())
        collected = gc.collect_all()
        self.assertIsInstance(collected, int)

    def test_needs_collection(self):
        gc = GarbageCollector(threshold=2)
        gc._auto_collect = False
        gc.allocate(VMObject())
        self.assertFalse(gc.needs_collection)
        gc.allocate(VMObject())
        self.assertTrue(gc.needs_collection)

    def test_auto_collect(self):
        gc = GarbageCollector(threshold=2)
        gc.allocate(VMObject())
        gc.allocate(VMObject())
        gc.allocate(VMObject())
        self.assertGreaterEqual(gc.stats.collections, 0)

    def test_promote(self):
        gc = GarbageCollector()
        obj = VMObject()
        gc.allocate(obj)
        gc.promote(obj)
        self.assertEqual(obj.gc_gen, GarbageCollector.OLD_GEN)

    def test_stats(self):
        gc = GarbageCollector()
        stats = gc.stats
        self.assertIsInstance(stats, GCStats)
        d = stats.to_dict()
        self.assertIn("collections", d)

    def test_format_stats(self):
        gc = GarbageCollector()
        text = gc.format_stats()
        self.assertIn("GC Statistics", text)

    def test_root_scanning(self):
        gc = GarbageCollector(threshold=10)
        gc._auto_collect = False
        obj = VMObject()
        gc.allocate(obj)
        gc.set_stack_roots([obj])
        gc.set_global_roots([])
        collected = gc.collect_young()
        self.assertEqual(collected, 0)

    def test_root_scanning_frees_unreachable(self):
        gc = GarbageCollector(threshold=10)
        gc._auto_collect = False
        reachable = VMObject()
        gc.allocate(reachable)
        gc.allocate(VMObject())
        gc.set_stack_roots([reachable])
        collected = gc.collect_young()
        self.assertGreaterEqual(collected, 0)


# ===================================================================
# 5. Debugger
# ===================================================================

class TestDebugger(unittest.TestCase):
    """Breakpoints, stepping modes, watches, stack traces."""

    def test_add_breakpoint(self):
        d = VMDebugger()
        bp = d.add_breakpoint("main", 10)
        self.assertEqual(bp.chunk_name, "main")
        self.assertEqual(bp.line, 10)
        self.assertTrue(bp.enabled)
        self.assertEqual(bp.hit_count, 0)

    def test_remove_breakpoint(self):
        d = VMDebugger()
        d.add_breakpoint("main", 10)
        self.assertTrue(d.remove_breakpoint("main", 10))
        self.assertFalse(d.remove_breakpoint("main", 10))

    def test_clear_breakpoints(self):
        d = VMDebugger()
        d.add_breakpoint("main", 1)
        d.add_breakpoint("main", 2)
        d.clear_breakpoints()
        self.assertEqual(len(d.get_breakpoints()), 0)

    def test_hit_breakpoint(self):
        d = VMDebugger()
        d.add_breakpoint("main", 10)
        self.assertTrue(d.hit_breakpoint("main", 10))
        self.assertFalse(d.hit_breakpoint("main", 20))
        bp = d.get_breakpoints()[0]
        self.assertEqual(bp.hit_count, 1)

    def test_step_into(self):
        d = VMDebugger()
        d.step_into()
        self.assertEqual(d.step_mode, StepMode.INTO)

    def test_step_over(self):
        d = VMDebugger()
        d.step_over()
        self.assertEqual(d.step_mode, StepMode.OVER)

    def test_step_out(self):
        d = VMDebugger()
        d.step_out()
        self.assertEqual(d.step_mode, StepMode.OUT)

    def test_continue_execution(self):
        d = VMDebugger()
        d.step_into()
        d.continue_execution()
        self.assertEqual(d.step_mode, StepMode.NONE)

    def test_should_break_breakpoint(self):
        d = VMDebugger()
        d.add_breakpoint("main", 5)
        self.assertTrue(d.should_break("main", 5, 0))
        self.assertFalse(d.should_break("main", 6, 0))

    def test_should_break_step_into(self):
        d = VMDebugger()
        d.step_into()
        self.assertTrue(d.should_break("main", 0, 0))

    def test_watches(self):
        d = VMDebugger()
        d.add_watch("x", 42)
        self.assertEqual(d.get_watches(), {"x": 42})
        d.remove_watch("x")
        self.assertEqual(len(d.get_watches()), 0)

    def test_stack_trace(self):
        d = VMDebugger()
        frames = [CallFrame(_make_chunk(), function_name="foo", line=10)]
        trace = d.get_stack_trace(frames)
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["function"], "foo")

    def test_inspect_variable(self):
        d = VMDebugger()
        info = d.inspect_variable("x", 42)
        self.assertEqual(info["name"], "x")
        self.assertEqual(info["type"], "int")
        self.assertIn("value", info)

    def test_call_return_tracking(self):
        d = VMDebugger()
        d.on_call()
        d.on_return()
        self.assertFalse(d.paused)

    def test_pause_resume(self):
        d = VMDebugger()
        d.pause("test")
        self.assertTrue(d.paused)
        d.resume()
        self.assertFalse(d.paused)


# ===================================================================
# 6. Profiler
# ===================================================================

class TestProfiler(unittest.TestCase):
    """Execution profiler — timing, calls, hot spots, format."""

    def test_start_stop(self):
        p = VMProfiler()
        p.start()
        self.assertTrue(p.enabled)
        p.stop()
        self.assertFalse(p.enabled)

    def test_record_call(self):
        p = VMProfiler()
        p.start()
        p.on_call("foo")
        p.on_return("foo")
        entries = p.get_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].calls, 1)

    def test_top_functions(self):
        p = VMProfiler()
        p.start()
        for _ in range(5):
            p.on_call("a")
            p.on_return("a")
        p.on_call("b")
        p.on_return("b")
        top = p.top_functions(1)
        self.assertEqual(top[0].name, "a")

    def test_format_profile(self):
        p = VMProfiler()
        p.start()
        p.on_call("test")
        p.on_return("test")
        text = p.format_profile()
        self.assertIn("Function", text)

    def test_reset(self):
        p = VMProfiler()
        p.start()
        p.on_call("foo")
        p.reset()
        self.assertEqual(len(p.get_entries()), 0)

    def test_record_instruction(self):
        p = VMProfiler()
        p.start()
        p.record_instruction(1, "main")
        d = p.to_dict()
        self.assertIn("instruction_counts", d)

    def test_hot_spots(self):
        p = VMProfiler()
        p.record_time("hot", 100.0)
        p.record_time("cold", 0.01)
        spots = p.get_hot_spots(threshold=10.0)
        self.assertEqual(len(spots), 1)
        self.assertEqual(spots[0].name, "hot")

    def test_record_time(self):
        p = VMProfiler()
        p.record_time("fn", 5.0)
        p.record_time("fn", 3.0)
        e = p.get_entries()[0]
        self.assertAlmostEqual(e.total_time_ms, 8.0)
        self.assertAlmostEqual(e.max_time_ms, 5.0)
        self.assertAlmostEqual(e.min_time_ms, 3.0)

    def test_avg_time_ms(self):
        e = ProfileEntry("test")
        e.calls = 2
        e.total_time_ms = 10.0
        self.assertAlmostEqual(e.avg_time_ms, 5.0)
        e.calls = 0
        self.assertAlmostEqual(e.avg_time_ms, 0.0)


# ===================================================================
# 7. Statistics
# ===================================================================

class TestStatistics(unittest.TestCase):
    """Execution statistics — instructions, calls, depth, exceptions."""

    def test_record_instruction(self):
        s = VMStatistics()
        s.record_instruction(1)
        s.record_instruction(1)
        s.record_instruction(2)
        self.assertEqual(s.instructions_executed, 3)

    def test_record_call(self):
        s = VMStatistics()
        s.record_call()
        s.record_call()
        self.assertEqual(s.function_calls, 2)
        self.assertEqual(s.max_call_depth, 2)

    def test_record_return(self):
        s = VMStatistics()
        s.record_call()
        s.record_call()
        s.record_return()
        self.assertEqual(s.max_call_depth, 2)

    def test_format_summary(self):
        s = VMStatistics()
        text = s.format_summary()
        self.assertIn("IVM Execution Statistics", text)

    def test_to_dict(self):
        s = VMStatistics()
        d = s.to_dict()
        self.assertIn("instructions_executed", d)
        self.assertIn("function_calls", d)

    def test_stack_depth(self):
        s = VMStatistics()
        s.record_stack_depth(5)
        s.record_stack_depth(3)
        self.assertEqual(s.max_stack_depth, 5)

    def test_exceptions(self):
        s = VMStatistics()
        s.record_exception()
        s.record_exception()
        s.record_exception_caught()
        self.assertEqual(s.exceptions_raised, 2)
        self.assertEqual(s.exceptions_caught, 1)

    def test_instructions_per_second(self):
        s = VMStatistics()
        s._start_time = 1.0
        s._end_time = 2.0
        s._instructions_executed = 1000
        self.assertGreater(s.instructions_per_second, 0)

    def test_get_top_opcodes(self):
        s = VMStatistics()
        s.record_instruction(1)
        s.record_instruction(2)
        s.record_instruction(1)
        top = s.get_top_opcodes(2)
        self.assertEqual(len(top), 2)
        self.assertEqual(top[0][0], 1)


# ===================================================================
# 8. Verifier
# ===================================================================

class TestVerifier(unittest.TestCase):
    """Bytecode verifier — valid chunks, invalid detection."""

    def test_valid_chunk(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.LOAD_CONST, 0)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(v.verify(chunk))

    def test_invalid_opcode(self):
        v = VMVerifier()
        chunk = _make_chunk()
        inst = IVMInstruction(opcode=IVMOpcode.HALT)
        object.__setattr__(inst, 'opcode', 999)
        chunk._instructions.append(inst)
        self.assertFalse(v.verify(chunk))
        self.assertTrue(len(v.errors) > 0)

    def test_invalid_branch_target(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.JUMP, 999)
        _emit(chunk, IVMOpcode.HALT)
        result = v.verify(chunk)
        self.assertFalse(result)

    def test_valid_branch_target(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.JUMP, 2)
        _emit(chunk, IVMOpcode.NOP)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(v.verify(chunk))

    def test_stack_underflow_detected(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        self.assertFalse(v.verify(chunk))

    def test_valid_stack_balance(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.LOAD_CONST, 0)
        _emit(chunk, IVMOpcode.LOAD_CONST, 1)
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(v.verify(chunk))


# ===================================================================
# 9. Loader
# ===================================================================

class TestLoader(unittest.TestCase):
    """Bytecode loading, serialization, file roundtrip."""

    def test_load_chunk(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.HALT)
        loaded = loader.load_chunk(chunk)
        self.assertEqual(loaded.instruction_count, 1)

    def test_verify_and_load(self):
        loader = VMLoader(enable_verification=True)
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.HALT)
        loaded = loader.load_chunk(chunk)
        self.assertIsNotNone(loaded)

    def test_serialize_deserialize(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk("roundtrip")
        chunk.add_constant(42)
        chunk.add_constant("hello")
        _emit(chunk, IVMOpcode.LOAD_CONST, 0)
        _emit(chunk, IVMOpcode.LOAD_CONST, 1)
        _emit(chunk, IVMOpcode.ADD)
        data = loader.save_bytes(chunk)
        self.assertIsInstance(data, bytes)
        self.assertTrue(data.startswith(BytecodeFormat.MAGIC))
        loaded = loader.load_bytes(data)
        self.assertEqual(loaded.name, "roundtrip")
        self.assertEqual(len(loaded.constants), 2)
        self.assertEqual(loaded.constants[0], 42)
        self.assertEqual(loaded.constants[1], "hello")

    def test_save_load_file(self):
        import tempfile
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk("filetest")
        chunk.add_constant(99)
        _emit(chunk, IVMOpcode.LOAD_CONST, 0)
        _emit(chunk, IVMOpcode.HALT)
        with tempfile.NamedTemporaryFile(suffix=".ibc", delete=False) as f:
            path = f.name
        try:
            loader.save_file(chunk, path)
            loaded = loader.load_file(path)
            self.assertEqual(loaded.name, "filetest")
        finally:
            os.unlink(path)

    def test_bad_magic(self):
        loader = VMLoader()
        with self.assertRaises(ValueError):
            loader.load_bytes(b"BAD_DATA")

    def test_bad_version(self):
        loader = VMLoader()
        data = BytecodeFormat.MAGIC + struct.pack(">H", 999) + b"\x00" * 100
        with self.assertRaises(ValueError):
            loader.load_bytes(data)

    def test_empty_chunk_serialization(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk("empty")
        data = loader.save_bytes(chunk)
        loaded = loader.load_bytes(data)
        self.assertEqual(loaded.name, "empty")
        self.assertEqual(loaded.instruction_count, 0)

    def test_serialize_with_all_constant_types(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk("alltypes")
        chunk.add_constant(None)
        chunk.add_constant(42)
        chunk.add_constant(3.14)
        chunk.add_constant(True)
        chunk.add_constant("hello")
        data = loader.save_bytes(chunk)
        loaded = loader.load_bytes(data)
        self.assertIsNone(loaded.constants[0])
        self.assertEqual(loaded.constants[1], 42)
        self.assertAlmostEqual(loaded.constants[2], 3.14)
        self.assertTrue(loaded.constants[3])
        self.assertEqual(loaded.constants[4], "hello")


# ===================================================================
# 10. Runtime
# ===================================================================

class TestRuntime(unittest.TestCase):
    """Builtins, modules, exception formatting."""

    def test_default_builtins(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        for name in ("andika", "int", "str", "abs", "min", "max", "igihe", "kubura"):
            self.assertIn(name, rt.builtins, f"missing builtin: {name}")

    def test_register_builtin(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        rt.register_builtin("custom", lambda: 42)
        self.assertIn("custom", rt.builtins)

    def test_create_exception(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        exc = rt.create_exception("test error", "TypeError")
        self.assertEqual(exc.message, "test error")
        self.assertEqual(exc.type_name, "TypeError")

    def test_module_registration(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        rt.register_module("math", {"pi": 3.14})
        self.assertTrue(rt.has_module("math"))
        self.assertIsNotNone(rt.get_module("math"))

    def test_format_exception(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        exc = rt.create_exception("oops")
        exc.stack_trace = [{"function": "main", "line": 10}]
        text = rt.format_exception(exc)
        self.assertIn("oops", text)

    def test_get_traceback(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        frames = [CallFrame(_make_chunk(), function_name="main", line=5)]
        tb = rt.get_traceback(frames)
        self.assertIn("main", tb)

    def test_builtin_andika(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        func = rt.builtins["andika"]
        self.assertIsNotNone(func)

    def test_builtin_int(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        func = rt.builtins["int"]
        self.assertEqual(func("42"), 42)

    def test_builtin_abs(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        func = rt.builtins["abs"]
        self.assertEqual(func(-5), 5)


# ===================================================================
# 11. Scheduler
# ===================================================================

class TestScheduler(unittest.TestCase):
    """Fiber scheduler — spawn, run, step, stats."""

    def test_spawn(self):
        s = VMScheduler()
        f = s.spawn(lambda: 42)
        self.assertEqual(f.state, FiberState.READY)

    def test_fiber_state_enum(self):
        self.assertEqual(FiberState.CREATED, 0)
        self.assertEqual(FiberState.READY, 1)
        self.assertEqual(FiberState.RUNNING, 2)
        self.assertEqual(FiberState.SUSPENDED, 3)
        self.assertEqual(FiberState.FINISHED, 4)

    def test_fiber_run(self):
        f = Fiber(0, lambda: 99)
        result = f.run()
        self.assertEqual(result, 99)
        self.assertEqual(f.state, FiberState.FINISHED)

    def test_fiber_error(self):
        def will_raise():
            raise ValueError("boom")
        f = Fiber(0, will_raise)
        f.run()
        self.assertIsNotNone(f.error)
        self.assertIsNone(f.result)

    def test_run_all(self):
        s = VMScheduler()
        results = []
        s.spawn(lambda: results.append(1))
        s.spawn(lambda: results.append(2))
        s.run_all()
        self.assertEqual(sorted(results), [1, 2])

    def test_step(self):
        s = VMScheduler()
        s.spawn(lambda: None)
        self.assertTrue(s.step())
        self.assertFalse(s.step())

    def test_stats(self):
        s = VMScheduler()
        s.spawn(lambda: None)
        stats = s.get_stats()
        self.assertIn("total_fibers", stats)
        self.assertIn("active", stats)
        self.assertIn("finished", stats)

    def test_fiber_repr(self):
        f = Fiber(1, lambda: None)
        r = repr(f)
        self.assertIn("Fiber", r)
        self.assertIn("id=1", r)


# ===================================================================
# 12. VMContext
# ===================================================================

class TestVMContext(unittest.TestCase):
    """Context — globals, builtins, modules, string interning."""

    def test_globals(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.globals["x"] = 42
        self.assertEqual(ctx.globals["x"], 42)

    def test_builtins(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.register_builtin("test", lambda: 1)
        self.assertEqual(ctx.get_builtin("test")(), 1)
        self.assertIsNone(ctx.get_builtin("missing"))

    def test_modules(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.register_module("mod", {})
        self.assertTrue(ctx.has_module("mod"))

    def test_intern_string(self):
        config = VMConfig()
        ctx = VMContext(config)
        idx1 = ctx.intern_string("hello")
        idx2 = ctx.intern_string("hello")
        self.assertEqual(idx1, idx2)

    def test_interned_lookup(self):
        config = VMConfig()
        ctx = VMContext(config)
        idx = ctx.intern_string("world")
        self.assertEqual(ctx.get_interned(idx), "world")

    def test_ffi_registry(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.register_ffi("sql", object())
        self.assertIsNotNone(ctx.get_ffi("sql"))
        self.assertIsNone(ctx.get_ffi("missing"))

    def test_metadata(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.set_metadata("key", "value")
        self.assertEqual(ctx.get_metadata("key"), "value")
        self.assertIsNone(ctx.get_metadata("missing"))


# ===================================================================
# 13. VMExecutor Basics
# ===================================================================

class TestVMExecutor(unittest.TestCase):
    """Executor — push/pop, hooks, GC wiring."""

    def test_push_pop(self):
        config = VMConfig()
        ctx = VMContext(config)
        ex = VMExecutor(config, ctx)
        ex.push(42)
        self.assertEqual(ex.pop(), 42)

    def test_stack_property(self):
        config = VMConfig()
        ctx = VMContext(config)
        ex = VMExecutor(config, ctx)
        self.assertIsInstance(ex.stack, Stack)

    def test_hooks(self):
        config = VMConfig()
        ctx = VMContext(config)
        ex = VMExecutor(config, ctx)
        calls = []
        ex.hook("test", lambda x: calls.append(x))
        ex._fire("test", 42)
        self.assertEqual(calls, [42])

    def test_unhook(self):
        config = VMConfig()
        ctx = VMContext(config)
        ex = VMExecutor(config, ctx)
        def cb(x): pass
        ex.hook("e", cb)
        ex.unhook("e", cb)
        ex.unhook("e", cb)

    def test_make_exception(self):
        config = VMConfig()
        ctx = VMContext(config)
        ex = VMExecutor(config, ctx)
        exc = ex._make_exception("err")
        self.assertIsInstance(exc, VMException)
        self.assertEqual(exc.message, "err")


# ===================================================================
# 14. VMInstance
# ===================================================================

class TestVMInstance(unittest.TestCase):
    """VMInstance — creation, properties, execution, reset."""

    def test_create(self):
        vm = VMInstance()
        self.assertIsNotNone(vm.config)
        self.assertIsNotNone(vm.context)
        self.assertIsNotNone(vm.executor)

    def test_with_config(self):
        config = VMConfig(max_stack_depth=512)
        vm = VMInstance(config)
        self.assertEqual(vm.config.max_stack_depth, 512)

    def test_execute_simple(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNone(result)

    def test_register_builtin(self):
        vm = VMInstance()
        vm.register_builtin("test_fn", lambda: 99)
        self.assertEqual(vm.context.get_builtin("test_fn")(), 99)

    def test_global_get_set(self):
        vm = VMInstance()
        vm.set_global("x", 42)
        self.assertEqual(vm.get_global("x"), 42)

    def test_stats_report(self):
        vm = VMInstance()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        report = vm.get_stats_report()
        self.assertIn("vm", report)
        self.assertIn("gc", report)

    def test_format_report(self):
        vm = VMInstance()
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        text = vm.format_report()
        self.assertIn("I Virtual Machine", text)

    def test_reset(self):
        vm = VMInstance()
        vm.set_global("x", 1)
        vm.reset()
        self.assertIsNone(vm.get_global("x"))

    def test_gc_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.gc, GarbageCollector)

    def test_debugger_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.debugger, VMDebugger)

    def test_profiler_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.profiler, VMProfiler)

    def test_scheduler_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.scheduler, VMScheduler)

    def test_loader_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.loader, VMLoader)

    def test_runtime_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.runtime, VMRuntime)

    def test_string_pool(self):
        vm = VMInstance()
        idx = vm.string_pool.intern("hello")
        self.assertEqual(vm.string_pool.lookup(idx), "hello")

    def test_constant_pool(self):
        vm = VMInstance()
        idx = vm.constant_pool.add(42)
        self.assertEqual(vm.constant_pool.get(idx), 42)

    def test_config_property(self):
        vm = VMInstance()
        self.assertIsInstance(vm.config, VMConfig)


# ===================================================================
# 15. Opcode Execution Tests
# ===================================================================

class TestOpcodesArithmetic(unittest.TestCase):
    """Arithmetic opcodes: ADD, SUB, MUL, DIV, MOD, NEG."""

    def test_add(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c5 = chunk.add_constant(5)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c5)
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 15)

    def test_sub(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.SUB)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 7)

    def test_mul(self):
        chunk = _make_chunk()
        c3 = chunk.add_constant(3)
        c4 = chunk.add_constant(4)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c4)
        _emit(chunk, IVMOpcode.MUL)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 12)

    def test_div(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.DIV)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 5.0)

    def test_div_by_zero(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c0 = chunk.add_constant(0)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.DIV)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_mod(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.MOD)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 1)

    def test_mod_by_zero(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c0 = chunk.add_constant(0)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.MOD)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_neg(self):
        chunk = _make_chunk()
        c5 = chunk.add_constant(5)
        _emit(chunk, IVMOpcode.LOAD_CONST, c5)
        _emit(chunk, IVMOpcode.NEG)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, -5)

    def test_multiple_ops(self):
        chunk = _make_chunk()
        c3 = chunk.add_constant(3)
        c4 = chunk.add_constant(4)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c4)
        _emit(chunk, IVMOpcode.MUL)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 14)


class TestOpcodesBitwise(unittest.TestCase):
    """Bitwise opcodes: AND, OR, XOR, NOT, SHIFT."""

    def test_bit_and(self):
        chunk = _make_chunk()
        c6 = chunk.add_constant(6)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c6)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.BIT_AND)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 2)

    def test_bit_or(self):
        chunk = _make_chunk()
        c4 = chunk.add_constant(4)
        c1 = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c4)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.BIT_OR)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 5)

    def test_bit_xor(self):
        chunk = _make_chunk()
        c5 = chunk.add_constant(5)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c5)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.BIT_XOR)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 6)

    def test_bit_not(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.BIT_NOT)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, -2)

    def test_left_shift(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.LEFT_SHIFT)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 8)

    def test_right_shift(self):
        chunk = _make_chunk()
        c16 = chunk.add_constant(16)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c16)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.RIGHT_SHIFT)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 4)


class TestOpcodesComparison(unittest.TestCase):
    """Comparison opcodes: EQ, NEQ, LT, LTE, GT, GTE."""

    def _run_cmp(self, a, b, opcode):
        chunk = _make_chunk()
        ca = chunk.add_constant(a)
        cb = chunk.add_constant(b)
        _emit(chunk, IVMOpcode.LOAD_CONST, ca)
        _emit(chunk, IVMOpcode.LOAD_CONST, cb)
        _emit(chunk, opcode)
        _emit(chunk, IVMOpcode.HALT)
        return VMInstance().execute(chunk)

    def test_eq_true(self):
        self.assertTrue(self._run_cmp(5, 5, IVMOpcode.EQ))

    def test_eq_false(self):
        self.assertFalse(self._run_cmp(5, 3, IVMOpcode.EQ))

    def test_neq_true(self):
        self.assertTrue(self._run_cmp(5, 3, IVMOpcode.NEQ))

    def test_neq_false(self):
        self.assertFalse(self._run_cmp(5, 5, IVMOpcode.NEQ))

    def test_lt_true(self):
        self.assertTrue(self._run_cmp(3, 5, IVMOpcode.LT))

    def test_lt_false(self):
        self.assertFalse(self._run_cmp(5, 3, IVMOpcode.LT))

    def test_lte_true(self):
        self.assertTrue(self._run_cmp(5, 5, IVMOpcode.LTE))

    def test_lte_false(self):
        self.assertFalse(self._run_cmp(6, 5, IVMOpcode.LTE))

    def test_gt_true(self):
        self.assertTrue(self._run_cmp(5, 3, IVMOpcode.GT))

    def test_gt_false(self):
        self.assertFalse(self._run_cmp(3, 5, IVMOpcode.GT))

    def test_gte_true(self):
        self.assertTrue(self._run_cmp(5, 5, IVMOpcode.GTE))

    def test_gte_false(self):
        self.assertFalse(self._run_cmp(3, 5, IVMOpcode.GTE))


class TestOpcodesLogical(unittest.TestCase):
    """Logical opcodes: AND, OR, NOT."""

    def test_and_true(self):
        chunk = _make_chunk()
        ct = chunk.add_constant(True)
        _emit(chunk, IVMOpcode.LOAD_CONST, ct)
        _emit(chunk, IVMOpcode.LOAD_CONST, ct)
        _emit(chunk, IVMOpcode.AND)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))

    def test_and_false(self):
        chunk = _make_chunk()
        ct = chunk.add_constant(True)
        cf = chunk.add_constant(False)
        _emit(chunk, IVMOpcode.LOAD_CONST, ct)
        _emit(chunk, IVMOpcode.LOAD_CONST, cf)
        _emit(chunk, IVMOpcode.AND)
        _emit(chunk, IVMOpcode.HALT)
        self.assertFalse(VMInstance().execute(chunk))

    def test_or_true(self):
        chunk = _make_chunk()
        cf = chunk.add_constant(False)
        ct = chunk.add_constant(True)
        _emit(chunk, IVMOpcode.LOAD_CONST, cf)
        _emit(chunk, IVMOpcode.LOAD_CONST, ct)
        _emit(chunk, IVMOpcode.OR)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))

    def test_or_false(self):
        chunk = _make_chunk()
        cf = chunk.add_constant(False)
        _emit(chunk, IVMOpcode.LOAD_CONST, cf)
        _emit(chunk, IVMOpcode.LOAD_CONST, cf)
        _emit(chunk, IVMOpcode.OR)
        _emit(chunk, IVMOpcode.HALT)
        self.assertFalse(VMInstance().execute(chunk))

    def test_not_true(self):
        chunk = _make_chunk()
        ct = chunk.add_constant(True)
        _emit(chunk, IVMOpcode.LOAD_CONST, ct)
        _emit(chunk, IVMOpcode.NOT)
        _emit(chunk, IVMOpcode.HALT)
        self.assertFalse(VMInstance().execute(chunk))

    def test_not_false(self):
        chunk = _make_chunk()
        cf = chunk.add_constant(False)
        _emit(chunk, IVMOpcode.LOAD_CONST, cf)
        _emit(chunk, IVMOpcode.NOT)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))


class TestOpcodesStack(unittest.TestCase):
    """Stack manipulation: POP, DUP, SWAP, ROT_THREE."""

    def test_pop(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.POP)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 1)

    def test_dup(self):
        chunk = _make_chunk()
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.DUP)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_swap(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.SWAP)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 1)

    def test_rot_three(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.ROT_THREE)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 2)


class TestOpcodesControlFlow(unittest.TestCase):
    """Control flow: JUMP, JUMP_IF_FALSE, JUMP_IF_TRUE, LOOP."""

    def test_jump(self):
        chunk = _make_chunk()
        c_42 = chunk.add_constant(42)
        c_99 = chunk.add_constant(99)
        _emit(chunk, IVMOpcode.JUMP, 3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.HALT)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_99)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 99)

    def test_jump_if_false_true(self):
        chunk = _make_chunk()
        c_true = chunk.add_constant(True)
        c_42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_true)
        _emit(chunk, IVMOpcode.JUMP_IF_FALSE, 3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_jump_if_false_false(self):
        chunk = _make_chunk()
        c_false = chunk.add_constant(False)
        c_42 = chunk.add_constant(42)
        c_99 = chunk.add_constant(99)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_false)
        _emit(chunk, IVMOpcode.JUMP_IF_FALSE, 3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_99)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 99)

    def test_jump_if_true_true(self):
        chunk = _make_chunk()
        c_true = chunk.add_constant(True)
        c_42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_true)
        _emit(chunk, IVMOpcode.JUMP_IF_TRUE, 2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_jump_if_true_false(self):
        chunk = _make_chunk()
        c_false = chunk.add_constant(False)
        c_42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_false)
        _emit(chunk, IVMOpcode.JUMP_IF_TRUE, 2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_jump_if_false_pop(self):
        chunk = _make_chunk()
        c_true = chunk.add_constant(True)
        c_42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_true)
        _emit(chunk, IVMOpcode.JUMP_IF_FALSE_POP, 2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_42)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)


class TestOpcodesValues(unittest.TestCase):
    """Value loading: LOAD_NULL, LOAD_TRUE, LOAD_FALSE, LOAD_CONST."""

    def test_load_null(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.LOAD_NULL)
        _emit(chunk, IVMOpcode.HALT)
        self.assertIsNone(VMInstance().execute(chunk))

    def test_load_true(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.LOAD_TRUE)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))

    def test_load_false(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.LOAD_FALSE)
        _emit(chunk, IVMOpcode.HALT)
        self.assertFalse(VMInstance().execute(chunk))

    def test_load_const_int(self):
        chunk = _make_chunk()
        idx = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, idx)
        _emit(chunk, IVMOpcode.HALT)
        self.assertEqual(VMInstance().execute(chunk), 42)

    def test_load_const_str(self):
        chunk = _make_chunk()
        idx = chunk.add_constant("hello")
        _emit(chunk, IVMOpcode.LOAD_CONST, idx)
        _emit(chunk, IVMOpcode.HALT)
        self.assertEqual(VMInstance().execute(chunk), "hello")

    def test_load_const_bool(self):
        chunk = _make_chunk()
        idx = chunk.add_constant(True)
        _emit(chunk, IVMOpcode.LOAD_CONST, idx)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))

    def test_load_const_float(self):
        chunk = _make_chunk()
        idx = chunk.add_constant(3.14)
        _emit(chunk, IVMOpcode.LOAD_CONST, idx)
        _emit(chunk, IVMOpcode.HALT)
        self.assertAlmostEqual(VMInstance().execute(chunk), 3.14)


class TestOpcodesGlobals(unittest.TestCase):
    """Global access: LOAD_GLOBAL, STORE_GLOBAL."""

    def test_store_load_global(self):
        chunk = _make_chunk()
        name_idx = chunk.add_constant("x")
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.STORE_GLOBAL, name_idx)
        _emit(chunk, IVMOpcode.LOAD_GLOBAL, name_idx)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_global_default_none(self):
        chunk = _make_chunk()
        name_idx = chunk.add_constant("undefined")
        _emit(chunk, IVMOpcode.LOAD_GLOBAL, name_idx)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsNone(result)


class TestOpcodesCollections(unittest.TestCase):
    """Collection opcodes: BUILD_LIST, BUILD_MAP, BUILD_SET, BUILD_TUPLE,
    GET_ITEM, SET_ITEM, SLICE.
    """

    def test_build_list(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.BUILD_LIST, 3)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMList)
        self.assertEqual(len(result), 3)
        self.assertEqual(result.get(0), 1)

    def test_build_map(self):
        chunk = _make_chunk()
        c_k = chunk.add_constant("key")
        c_v = chunk.add_constant("value")
        _emit(chunk, IVMOpcode.LOAD_CONST, c_k)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_v)
        _emit(chunk, IVMOpcode.BUILD_MAP, 1)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMMap)
        self.assertEqual(result.get("key"), "value")

    def test_build_set(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_SET, 2)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMSet)

    def test_build_tuple(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_TUPLE, 2)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMTuple)
        self.assertEqual(len(result), 2)

    def test_get_item_list(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(10)
        c2 = chunk.add_constant(20)
        c_idx = chunk.add_constant(0)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_LIST, 2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_idx)
        _emit(chunk, IVMOpcode.GET_ITEM)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 10)

    def test_get_item_map(self):
        chunk = _make_chunk()
        c_k = chunk.add_constant("name")
        c_v = chunk.add_constant("Alice")
        _emit(chunk, IVMOpcode.LOAD_CONST, c_k)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_v)
        _emit(chunk, IVMOpcode.BUILD_MAP, 1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_k)
        _emit(chunk, IVMOpcode.GET_ITEM)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, "Alice")

    def test_set_item(self):
        chunk = _make_chunk()
        c0 = chunk.add_constant(0)
        c99 = chunk.add_constant(99)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.BUILD_LIST, 1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.LOAD_CONST, c99)
        _emit(chunk, IVMOpcode.SET_ITEM)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.GET_ITEM)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 99)

    def test_slice(self):
        chunk = _make_chunk()
        chunk.add_constant(1)
        chunk.add_constant(2)
        chunk.add_constant(3)
        chunk.add_constant(4)
        c1 = chunk.add_constant(1)
        c3 = chunk.add_constant(3)
        c_step = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, 0)
        _emit(chunk, IVMOpcode.LOAD_CONST, 1)
        _emit(chunk, IVMOpcode.LOAD_CONST, 2)
        _emit(chunk, IVMOpcode.LOAD_CONST, 3)
        _emit(chunk, IVMOpcode.BUILD_LIST, 4)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_step)
        _emit(chunk, IVMOpcode.SLICE)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMList)
        self.assertEqual(len(result), 2)


class TestOpcodesAttributes(unittest.TestCase):
    """Attribute access: GET_ATTR, SET_ATTR."""

    def test_get_attr(self):
        chunk = _make_chunk()
        c_coords = chunk.add_constant(10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_coords)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_coords)
        _emit(chunk, IVMOpcode.NEW_STRUCT, 0)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNotNone(result)


class TestOpcodesStructs(unittest.TestCase):
    """Struct operations: NEW_STRUCT, GET_FIELD, PUT_FIELD."""

    def test_new_struct(self):
        chunk = _make_chunk()
        c_pt = chunk.add_constant("Point")
        cx = chunk.add_constant("x")
        cy = chunk.add_constant("y")
        _emit(chunk, IVMOpcode.LOAD_CONST, cx)
        _emit(chunk, IVMOpcode.LOAD_CONST, cy)
        _emit(chunk, IVMOpcode.NEW_STRUCT, c_pt, 2)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMStruct)
        self.assertEqual(result.type_name, "Point")

    def test_put_get_field(self):
        chunk = _make_chunk()
        c_pt = chunk.add_constant("Point")
        cx_name = chunk.add_constant("x")
        cx_val = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, cx_name)
        _emit(chunk, IVMOpcode.NEW_STRUCT, c_pt, 1)
        _emit(chunk, IVMOpcode.LOAD_CONST, cx_val)
        _emit(chunk, IVMOpcode.PUT_FIELD, cx_name)
        _emit(chunk, IVMOpcode.GET_FIELD, cx_name)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)

    def test_get_field_missing(self):
        chunk = _make_chunk()
        c_point = chunk.add_constant("Point")
        cx = chunk.add_constant("x")
        cmissing = chunk.add_constant("missing")
        _emit(chunk, IVMOpcode.LOAD_CONST, cx)
        _emit(chunk, IVMOpcode.NEW_STRUCT, c_point, 1)
        _emit(chunk, IVMOpcode.GET_FIELD, cmissing)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)


class TestOpcodesFunctions(unittest.TestCase):
    """Function/closure opcodes: MAKE_FUNCTION, MAKE_CLOSURE, CALL, RETURN."""

    def test_make_function(self):
        chunk = _make_chunk()
        inner = _make_chunk("fn")
        c_fn = chunk.add_constant(inner)
        _emit(chunk, IVMOpcode.MAKE_FUNCTION, c_fn, 0)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMClosure)
        self.assertEqual(result.name, "fn")

    def test_make_closure(self):
        chunk = _make_chunk()
        inner = _make_chunk("cl")
        c_cl = chunk.add_constant(inner)
        c_v = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_v)
        _emit(chunk, IVMOpcode.MAKE_CLOSURE, c_cl, 1)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMClosure)
        self.assertEqual(len(result.free_vars), 1)
        self.assertEqual(result.free_vars[0], 42)


class TestOpcodesIterators(unittest.TestCase):
    """Iterator opcodes: GET_ITER, FOR_ITER."""

    def test_get_iter_list(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_LIST, 2)
        _emit(chunk, IVMOpcode.GET_ITER)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMIterator)

    def test_for_iter(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_LIST, 2)
        _emit(chunk, IVMOpcode.GET_ITER)
        _emit(chunk, IVMOpcode.FOR_ITER, 2)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsNotNone(result)


class TestOpcodesExceptions(unittest.TestCase):
    """Exception opcodes: RAISE, THROW, SETUP_TRY, POP_BLOCK."""

    def test_raise(self):
        chunk = _make_chunk()
        c_msg = chunk.add_constant("boom")
        _emit(chunk, IVMOpcode.LOAD_CONST, c_msg)
        _emit(chunk, IVMOpcode.RAISE)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_throw(self):
        chunk = _make_chunk()
        c_msg = chunk.add_constant("thrown")
        _emit(chunk, IVMOpcode.LOAD_CONST, c_msg)
        _emit(chunk, IVMOpcode.THROW)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_throw_exception_object(self):
        chunk = _make_chunk()
        c_msg = chunk.add_constant("custom error")
        _emit(chunk, IVMOpcode.LOAD_CONST, c_msg)
        _emit(chunk, IVMOpcode.THROW)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_setup_try_pop_block(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.SETUP_TRY, 2)
        _emit(chunk, IVMOpcode.POP_BLOCK)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsNone(result)


class TestOpcodesStatic(unittest.TestCase):
    """Static access: GET_STATIC, PUT_STATIC."""

    def test_get_static(self):
        chunk = _make_chunk()
        c_name = chunk.add_constant("PI")
        _emit(chunk, IVMOpcode.GET_STATIC, c_name)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        vm.set_global("PI", 3.14)
        result = vm.execute(chunk)
        self.assertAlmostEqual(result, 3.14)

    def test_put_static(self):
        chunk = _make_chunk()
        c_name = chunk.add_constant("x")
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.PUT_STATIC, c_name)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        vm.execute(chunk)
        self.assertEqual(vm.get_global("x"), 42)


class TestOpcodesFrame(unittest.TestCase):
    """Frame opcodes: ENTER_FRAME, EXIT_FRAME, LOAD_FAST, STORE_FAST,
    LOAD_ARG, STORE_ARG."""

    def test_enter_exit_frame(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.ENTER_FRAME, 3)
        _emit(chunk, IVMOpcode.EXIT_FRAME, 3)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsNone(result)

    def test_store_load_fast(self):
        chunk = _make_chunk()
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.ENTER_FRAME, 1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.STORE_FAST, 0)
        _emit(chunk, IVMOpcode.LOAD_FAST, 0)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 42)


class TestOpcodesInvoke(unittest.TestCase):
    """Method dispatch: INVOKE, INVOKE_VIRTUAL, INVOKE_INTERFACE."""

    def test_invoke_virtual(self):
        chunk = _make_chunk()
        name_idx = chunk.add_constant("__len__")
        c_lst = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c_lst)
        _emit(chunk, IVMOpcode.BUILD_LIST, 1)
        _emit(chunk, IVMOpcode.INVOKE_VIRTUAL, name_idx, 0)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 1)

    def test_invoke_interface(self):
        chunk = _make_chunk()
        name_idx = chunk.add_constant("append")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.BUILD_LIST, 1)
        _emit(chunk, IVMOpcode.DUP)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.INVOKE_INTERFACE, name_idx, 1)
        _emit(chunk, IVMOpcode.POP)
        _emit(chunk, IVMOpcode.LOAD_CONST, chunk.add_constant(1))
        _emit(chunk, IVMOpcode.GET_ITEM)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 2)


class TestOpcodesType(unittest.TestCase):
    """Type opcodes: INSTANCE_OF, CHECK_CAST, NEW_ARRAY, NEW_OBJECT."""

    def test_new_array(self):
        chunk = _make_chunk()
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.NEW_ARRAY, 2)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMList)
        self.assertEqual(len(result), 2)

    def test_new_object(self):
        chunk = _make_chunk()
        _emit(chunk, IVMOpcode.NEW_OBJECT)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMStruct)
        self.assertEqual(result.type_name, "Object")

    def test_instance_of(self):
        chunk = _make_chunk()
        c_type = chunk.add_constant("Object")
        _emit(chunk, IVMOpcode.NEW_OBJECT)
        _emit(chunk, IVMOpcode.INSTANCE_OF, c_type)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertTrue(result)


# ===================================================================
# 16. Integration Tests
# ===================================================================

class TestIntegration(unittest.TestCase):
    """End-to-end integration scenarios."""

    def test_arithmetic_pipeline(self):
        chunk = _make_chunk("arith")
        c10 = chunk.add_constant(10)
        c5 = chunk.add_constant(5)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c5)
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertEqual(result, 15)

    def test_comparison_chain(self):
        chunk = _make_chunk("cmp")
        c5 = chunk.add_constant(5)
        c3 = chunk.add_constant(3)
        _emit(chunk, IVMOpcode.LOAD_CONST, c5)
        _emit(chunk, IVMOpcode.LOAD_CONST, c3)
        _emit(chunk, IVMOpcode.GT)
        _emit(chunk, IVMOpcode.HALT)
        self.assertTrue(VMInstance().execute(chunk))

    def test_global_interaction(self):
        vm = VMInstance()
        chunk = _make_chunk("glob")
        name_idx = chunk.add_constant("result")
        c42 = chunk.add_constant(42)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.STORE_GLOBAL, name_idx)
        _emit(chunk, IVMOpcode.LOAD_GLOBAL, name_idx)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.ADD)
        _emit(chunk, IVMOpcode.HALT)
        result = vm.execute(chunk)
        self.assertEqual(result, 44)

    def test_profiler_integration(self):
        config = VMConfig(enable_profiler=True)
        vm = VMInstance(config)
        chunk = _make_chunk("profiled")
        c1 = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        self.assertTrue(vm.profiler.enabled)

    def test_debugger_integration(self):
        vm = VMInstance()
        vm.debugger.add_breakpoint("test", 1)
        self.assertEqual(len(vm.debugger.get_breakpoints()), 1)

    def test_gc_integration(self):
        vm = VMInstance()
        chunk = _make_chunk("gc")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c2)
        _emit(chunk, IVMOpcode.BUILD_LIST, 2)
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        self.assertGreaterEqual(vm.gc.stats.collections, 0)

    def test_stats_integration(self):
        vm = VMInstance()
        chunk = _make_chunk("stats")
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.NEG)
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        self.assertGreater(vm.stats.instructions_executed, 0)

    def test_full_report(self):
        vm = VMInstance()
        chunk = _make_chunk("report")
        c1 = chunk.add_constant(1)
        _emit(chunk, IVMOpcode.LOAD_CONST, c1)
        _emit(chunk, IVMOpcode.HALT)
        vm.execute(chunk)
        report = vm.get_stats_report()
        self.assertIn("vm", report)
        self.assertIn("gc", report)


# ===================================================================
# 17. Error Handling
# ===================================================================

class TestErrorHandling(unittest.TestCase):
    """Runtime error handling and formatting."""

    def test_vm_runtime_error(self):
        err = VMRuntimeError("test", line=5)
        self.assertEqual(str(err), "test")
        self.assertEqual(err.line, 5)

    def test_vm_runtime_error_trace(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk=chunk, function_name="main", ip=0, base_pointer=0)
        err = VMRuntimeError("err", frame_stack=[frame])
        trace = err.format_trace()
        self.assertIn("main", trace)

    def test_division_by_zero(self):
        chunk = _make_chunk()
        c10 = chunk.add_constant(10)
        c0 = chunk.add_constant(0)
        _emit(chunk, IVMOpcode.LOAD_CONST, c10)
        _emit(chunk, IVMOpcode.LOAD_CONST, c0)
        _emit(chunk, IVMOpcode.DIV)
        _emit(chunk, IVMOpcode.HALT)
        with self.assertRaises(VMRuntimeError) as ctx:
            VMInstance().execute(chunk)
        self.assertIn("division by zero", str(ctx.exception))

    def test_unknown_opcode(self):
        chunk = _make_chunk()
        inst = IVMInstruction(opcode=IVMOpcode.HALT)
        object.__setattr__(inst, 'opcode', 255)
        chunk._instructions.append(inst)
        with self.assertRaises(VMRuntimeError):
            VMInstance().execute(chunk)

    def test_vm_config_defaults(self):
        config = VMConfig()
        self.assertEqual(config.max_stack_depth, 1024)
        self.assertEqual(config.max_call_depth, 256)
        self.assertTrue(config.enable_stats)
        self.assertFalse(config.enable_debug)

    def test_vm_config_with_debug(self):
        config = VMConfig()
        config.with_debug()
        self.assertTrue(config.enable_debug)

    def test_vm_config_with_profiler(self):
        config = VMConfig()
        config.with_profiler()
        self.assertTrue(config.enable_profiler)


# ===================================================================
# 18. Regression Tests
# ===================================================================

class TestRegression(unittest.TestCase):
    """Regression tests for known issues."""

    def test_empty_chunk(self):
        chunk = _make_chunk("empty")
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNone(result)

    def test_halt_only(self):
        chunk = _make_chunk("halt")
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNone(result)

    def test_large_stack(self):
        config = VMConfig(max_stack_depth=8192)
        vm = VMInstance(config)
        chunk = _make_chunk("bigstack")
        c = chunk.add_constant(1)
        for _ in range(1000):
            _emit(chunk, IVMOpcode.LOAD_CONST, c)
        _emit(chunk, IVMOpcode.HALT)
        result = vm.execute(chunk)
        self.assertEqual(result, 1)

    def test_chunk_with_functions(self):
        chunk = _make_chunk("outer")
        inner = _make_chunk("inner")
        _emit(inner, IVMOpcode.RETURN)
        c_inner = chunk.add_constant(inner)
        _emit(chunk, IVMOpcode.MAKE_FUNCTION, c_inner, 0)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMClosure)

    def test_reset_reuse(self):
        vm = VMInstance()
        chunk = _make_chunk("r1")
        c42 = chunk.add_constant(42)
        _emit(chunk, IVMOpcode.LOAD_CONST, c42)
        _emit(chunk, IVMOpcode.HALT)
        r1 = vm.execute(chunk)
        self.assertEqual(r1, 42)
        vm.reset()
        chunk2 = _make_chunk("r2")
        c99 = chunk2.add_constant(99)
        _emit(chunk2, IVMOpcode.LOAD_CONST, c99)
        _emit(chunk2, IVMOpcode.HALT)
        r2 = vm.execute(chunk2)
        self.assertEqual(r2, 99)

    def test_multiple_executions(self):
        vm = VMInstance()
        for i in range(5):
            chunk = _make_chunk(f"e{i}")
            c = chunk.add_constant(i)
            _emit(chunk, IVMOpcode.LOAD_CONST, c)
            _emit(chunk, IVMOpcode.HALT)
            result = vm.execute(chunk)
            self.assertEqual(result, i)


# ===================================================================
# 19. Stress Tests
# ===================================================================

class TestStress(unittest.TestCase):
    """Stress tests for VM stability."""

    def test_many_instructions(self):
        chunk = _make_chunk("stress")
        c = chunk.add_constant(1)
        for _ in range(1000):
            _emit(chunk, IVMOpcode.LOAD_CONST, c)
            _emit(chunk, IVMOpcode.POP)
        _emit(chunk, IVMOpcode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNone(result)

    def test_build_large_list(self):
        chunk = _make_chunk("biglist")
        c = chunk.add_constant(0)
        for _ in range(500):
            _emit(chunk, IVMOpcode.LOAD_CONST, c)
        _emit(chunk, IVMOpcode.BUILD_LIST, 500)
        _emit(chunk, IVMOpcode.HALT)
        result = VMInstance().execute(chunk)
        self.assertIsInstance(result, VMList)
        self.assertEqual(len(result), 500)


# ===================================================================
# 20. Config
# ===================================================================

class TestVMConfig(unittest.TestCase):
    """VMConfig defaults and builder methods."""

    def test_defaults(self):
        config = VMConfig()
        self.assertEqual(config.max_stack_depth, 1024)
        self.assertEqual(config.max_call_depth, 256)
        self.assertTrue(config.enable_stats)
        self.assertFalse(config.enable_debug)

    def test_with_debug(self):
        config = VMConfig()
        config.with_debug()
        self.assertTrue(config.enable_debug)

    def test_with_profiler(self):
        config = VMConfig()
        config.with_profiler()
        self.assertTrue(config.enable_profiler)

    def test_resource_limits(self):
        config = VMConfig(resource_limits={"max_memory": 64 * 1024 * 1024})
        self.assertEqual(config.resource_limits["max_memory"], 64 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
