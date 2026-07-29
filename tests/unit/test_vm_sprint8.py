"""Comprehensive tests for the I Virtual Machine (Sprint 8)."""
from __future__ import annotations

import struct
import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from compiler.codegen.bytecode import Chunk, Instruction, OpCode
from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_executor import VMExecutor, VMRuntimeError
from vm.vm_memory import Stack, CallFrame, Heap, StringPool, ConstantPool, StackOverflowError
from vm.vm_objects import (
    VMObject, VMString, VMList, VMMap, VMSet, VMTuple,
    VMStruct, VMClosure, VMException, VMIterator,
)
from vm.vm_gc import GarbageCollector, GCStats
from vm.vm_debug import VMDebugger, StepMode, Breakpoint
from vm.vm_profiler import VMProfiler, ProfileEntry
from vm.vm_stats import VMStatistics
from vm.vm_loader import VMLoader, VMVerifier, BytecodeFormat
from vm.vm_runtime import VMRuntime
from vm.vm_scheduler import VMScheduler, Fiber, FiberState
from vm.vm_instance import VMInstance
from vm.vm_bytecode import IVMOpcode, IVMInstruction, IVMChunk


def _make_chunk(name: str = "test") -> Chunk:
    return Chunk(name=name)


def _emit(chunk: Chunk, opcode: OpCode, arg: int = None, line: int = 0) -> int:
    return chunk.emit(opcode, arg, line)


def _run(chunk: Chunk, config: VMConfig | None = None) -> VMInstance:
    vm = VMInstance(config or VMConfig())
    vm.execute(chunk)
    return vm


class TestStack(unittest.TestCase):
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
        self.assertEqual(len(s), 1)

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

    def test_dup(self):
        s = Stack(16)
        s.push(42)
        s.dup()
        self.assertEqual(s.peek(), 42)
        self.assertEqual(len(s), 2)

    def test_swap(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.swap()
        self.assertEqual(s.peek(), 1)

    def test_rot_three(self):
        s = Stack(16)
        s.push(1)
        s.push(2)
        s.push(3)
        s.rot_three()
        self.assertEqual(s.peek(), 2)

    def test_overflow(self):
        s = Stack(4)
        for i in range(4):
            s.push(i)
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

    def test_empty_bool(self):
        s = Stack(16)
        self.assertFalse(bool(s))
        s.push(1)
        self.assertTrue(bool(s))


class TestCallFrame(unittest.TestCase):
    def test_basic(self):
        chunk = _make_chunk("func")
        frame = CallFrame(chunk, ip=5, base_pointer=10, function_name="foo")
        self.assertEqual(frame.ip, 5)
        self.assertEqual(frame.base_pointer, 10)
        self.assertEqual(frame.function_name, "foo")

    def test_advance(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk, ip=0)
        frame.advance()
        self.assertEqual(frame.ip, 1)

    def test_read_byte(self):
        chunk = _make_chunk()
        chunk.emit(OpCode.LOAD_CONST, 0)
        chunk.emit(OpCode.ADD)
        frame = CallFrame(chunk, ip=0)
        self.assertEqual(frame.read_byte(), OpCode.LOAD_CONST.value)
        self.assertEqual(frame.read_byte(), OpCode.ADD.value)

    def test_repr(self):
        chunk = _make_chunk()
        frame = CallFrame(chunk, ip=0, function_name="bar")
        self.assertIn("bar", repr(frame))


class TestHeap(unittest.TestCase):
    def test_allocate(self):
        h = Heap()
        obj = VMObject()
        h.allocate(obj)
        self.assertEqual(h.size, 1)

    def test_collect(self):
        h = Heap()
        obj = VMObject()
        h.allocate(obj)
        obj.gc_marked = True
        freed = h.collect()
        self.assertEqual(h.size, 1)

    def test_stats(self):
        h = Heap()
        stats = h.get_stats()
        self.assertIn("objects", stats)
        self.assertIn("allocated", stats)


class TestStringPool(unittest.TestCase):
    def test_intern(self):
        pool = StringPool()
        idx1 = pool.intern("hello")
        idx2 = pool.intern("hello")
        self.assertEqual(idx1, idx2)
        self.assertEqual(pool.count, 1)

    def test_lookup(self):
        pool = StringPool()
        idx = pool.intern("world")
        self.assertEqual(pool.lookup(idx), "world")

    def test_resolve(self):
        pool = StringPool()
        pool.intern("test")
        self.assertEqual(pool.resolve("test"), 0)
        self.assertEqual(pool.resolve("missing"), -1)


class TestConstantPool(unittest.TestCase):
    def test_add_get(self):
        cp = ConstantPool()
        idx = cp.add(42)
        self.assertEqual(cp.get(idx), 42)

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


class TestVMObjects(unittest.TestCase):
    def test_string(self):
        s = VMString("hello")
        self.assertEqual(s.value, "hello")
        self.assertEqual(len(s), 5)

    def test_string_eq(self):
        self.assertEqual(VMString("a"), VMString("a"))
        self.assertNotEqual(VMString("a"), VMString("b"))

    def test_list(self):
        lst = VMList([1, 2, 3])
        self.assertEqual(lst.get(0), 1)
        self.assertEqual(len(lst), 3)

    def test_list_set(self):
        lst = VMList([1, 2, 3])
        lst.set(1, 99)
        self.assertEqual(lst.get(1), 99)

    def test_list_append(self):
        lst = VMList()
        lst.append(42)
        self.assertEqual(len(lst), 1)

    def test_list_slice(self):
        lst = VMList([0, 1, 2, 3, 4])
        sliced = lst.slice(1, 4)
        self.assertEqual(sliced.to_list(), [1, 2, 3])

    def test_list_index_error(self):
        lst = VMList([1])
        with self.assertRaises(IndexError):
            lst.get(5)

    def test_map(self):
        m = VMMap()
        m.set("key", "value")
        self.assertEqual(m.get("key"), "value")

    def test_set(self):
        s = VMSet()
        s.add(1)
        s.add(2)
        self.assertEqual(len(s), 2)

    def test_tuple(self):
        t = VMTuple((1, 2, 3))
        self.assertEqual(len(t), 3)

    def test_struct(self):
        s = VMStruct("Point", ["x", "y"])
        s.set_field("x", 10)
        s.set_field("y", 20)
        self.assertEqual(s.get_field("x"), 10)

    def test_struct_missing_field(self):
        s = VMStruct("Point", ["x"])
        with self.assertRaises(AttributeError):
            s.set_field("z", 1)

    def test_closure(self):
        chunk = _make_chunk()
        c = VMClosure(chunk, "foo", 2)
        self.assertEqual(c.name, "foo")
        self.assertEqual(c.arity, 2)

    def test_exception(self):
        exc = VMException("error message")
        self.assertEqual(exc.message, "error message")
        self.assertEqual(exc.type_name, "RuntimeError")

    def test_exception_with_cause(self):
        cause = VMException("root cause")
        exc = VMException("wrapper").with_cause(cause)
        self.assertIs(exc.cause, cause)

    def test_iterator_list(self):
        lst = VMList([1, 2, 3])
        it = VMIterator(lst)
        self.assertTrue(it.has_next())
        self.assertEqual(it.next(), 1)
        self.assertEqual(it.next(), 2)
        self.assertEqual(it.next(), 3)
        self.assertFalse(it.has_next())

    def test_iterator_string(self):
        it = VMIterator("abc")
        self.assertEqual(it.next(), "a")
        self.assertEqual(it.next(), "b")
        self.assertEqual(it.next(), "c")

    def test_iterator_stop(self):
        it = VMIterator([])
        with self.assertRaises(StopIteration):
            it.next()

    def test_gc_marking(self):
        obj = VMObject()
        self.assertFalse(obj.gc_marked)
        obj.gc_marked = True
        self.assertTrue(obj.gc_marked)


class TestGarbageCollector(unittest.TestCase):
    def test_collect_young(self):
        gc = GarbageCollector(threshold=5, generational=True)
        for i in range(10):
            gc.allocate(VMObject())
        collected = gc.collect_young()
        self.assertGreaterEqual(collected, 0)

    def test_collect_all(self):
        gc = GarbageCollector(generational=False)
        for i in range(5):
            gc.allocate(VMObject())
        collected = gc.collect_all()
        self.assertIsInstance(collected, int)

    def test_stats(self):
        gc = GarbageCollector()
        stats = gc.stats
        self.assertIsInstance(stats, GCStats)
        d = stats.to_dict()
        self.assertIn("collections", d)

    def test_needs_collection(self):
        gc = GarbageCollector(threshold=2)
        gc._auto_collect = False
        gc.allocate(VMObject())
        self.assertFalse(gc.needs_collection)
        gc.allocate(VMObject())
        self.assertTrue(gc.needs_collection)

    def test_format_stats(self):
        gc = GarbageCollector()
        text = gc.format_stats()
        self.assertIn("GC Statistics", text)

    def test_promote(self):
        gc = GarbageCollector()
        obj = VMObject()
        gc.allocate(obj)
        gc.promote(obj)
        self.assertEqual(obj.gc_gen, GarbageCollector.OLD_GEN)


class TestVMDebugger(unittest.TestCase):
    def test_add_breakpoint(self):
        dbg = VMDebugger()
        bp = dbg.add_breakpoint("main", 10)
        self.assertEqual(bp.chunk_name, "main")
        self.assertEqual(bp.line, 10)
        self.assertTrue(bp.enabled)

    def test_remove_breakpoint(self):
        dbg = VMDebugger()
        dbg.add_breakpoint("main", 10)
        self.assertTrue(dbg.remove_breakpoint("main", 10))
        self.assertEqual(len(dbg.get_breakpoints()), 0)

    def test_clear_breakpoints(self):
        dbg = VMDebugger()
        dbg.add_breakpoint("main", 1)
        dbg.add_breakpoint("main", 2)
        dbg.clear_breakpoints()
        self.assertEqual(len(dbg.get_breakpoints()), 0)

    def test_hit_breakpoint(self):
        dbg = VMDebugger()
        dbg.add_breakpoint("main", 10)
        self.assertTrue(dbg.hit_breakpoint("main", 10))
        self.assertFalse(dbg.hit_breakpoint("main", 20))

    def test_step_into(self):
        dbg = VMDebugger()
        dbg.step_into()
        self.assertEqual(dbg.step_mode, StepMode.INTO)
        self.assertFalse(dbg.paused)

    def test_step_over(self):
        dbg = VMDebugger()
        dbg.step_over()
        self.assertEqual(dbg.step_mode, StepMode.OVER)

    def test_step_out(self):
        dbg = VMDebugger()
        dbg.step_out()
        self.assertEqual(dbg.step_mode, StepMode.OUT)

    def test_continue(self):
        dbg = VMDebugger()
        dbg.step_into()
        dbg.continue_execution()
        self.assertEqual(dbg.step_mode, StepMode.NONE)

    def test_should_break_breakpoint(self):
        dbg = VMDebugger()
        dbg.add_breakpoint("main", 5)
        self.assertTrue(dbg.should_break("main", 5, 0))
        self.assertFalse(dbg.should_break("main", 6, 0))

    def test_should_break_step_into(self):
        dbg = VMDebugger()
        dbg.step_into()
        self.assertTrue(dbg.should_break("main", 0, 0))

    def test_watch_expressions(self):
        dbg = VMDebugger()
        dbg.add_watch("x", 42)
        self.assertEqual(dbg.get_watches()["x"], 42)
        dbg.remove_watch("x")
        self.assertEqual(len(dbg.get_watches()), 0)

    def test_stack_trace(self):
        from vm.vm_memory import CallFrame
        from compiler.codegen.bytecode import Chunk
        chunk = Chunk("test")
        frame = CallFrame(chunk, function_name="foo", line=10)
        dbg = VMDebugger()
        trace = dbg.get_stack_trace([frame])
        self.assertEqual(len(trace), 1)
        self.assertEqual(trace[0]["function"], "foo")

    def test_inspect_variable(self):
        dbg = VMDebugger()
        info = dbg.inspect_variable("x", 42)
        self.assertEqual(info["name"], "x")
        self.assertEqual(info["type"], "int")

    def test_call_return_tracking(self):
        dbg = VMDebugger()
        dbg.on_call()
        dbg.on_call()
        dbg.on_return()
        dbg.on_return()


class TestVMProfiler(unittest.TestCase):
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
        self.assertEqual(entries[0].name, "foo")
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


class TestVMStatistics(unittest.TestCase):
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
        ips = s.instructions_per_second
        self.assertGreater(ips, 0)


class TestVMVerifier(unittest.TestCase):
    def test_valid_chunk(self):
        v = VMVerifier()
        chunk = _make_chunk()
        _emit(chunk, OpCode.LOAD_CONST, 0)
        _emit(chunk, OpCode.RETURN)
        self.assertTrue(v.verify(chunk))

    def test_invalid_opcode(self):
        v = VMVerifier()
        chunk = _make_chunk()
        bad_inst = Instruction(opcode=OpCode.NOP, arg=None, line=0)
        bad_inst.opcode = 999
        chunk.code.append(bad_inst)
        result = v.verify(chunk)
        self.assertFalse(result)
        self.assertTrue(len(v.errors) > 0)


class TestVMLoader(unittest.TestCase):
    def test_load_chunk(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk()
        _emit(chunk, OpCode.LOAD_CONST, 0)
        _emit(chunk, OpCode.RETURN)
        loaded = loader.load_chunk(chunk)
        self.assertEqual(len(loaded.code), 2)

    def test_verify_and_load(self):
        loader = VMLoader(enable_verification=True)
        chunk = _make_chunk()
        _emit(chunk, OpCode.LOAD_CONST, 0)
        _emit(chunk, OpCode.RETURN)
        loaded = loader.load_chunk(chunk)
        self.assertIsNotNone(loaded)

    def test_serialize_deserialize(self):
        loader = VMLoader(enable_verification=False)
        chunk = _make_chunk("roundtrip")
        chunk.add_constant(42)
        chunk.add_constant("hello")
        _emit(chunk, OpCode.LOAD_CONST, 0)
        _emit(chunk, OpCode.LOAD_CONST, 1)
        _emit(chunk, OpCode.ADD)
        _emit(chunk, OpCode.RETURN)

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
        _emit(chunk, OpCode.LOAD_CONST, 0)
        _emit(chunk, OpCode.RETURN)

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
            loader.load_bytes(b"BAD_DATA_HERE!")

    def test_bad_version(self):
        loader = VMLoader()
        data = BytecodeFormat.MAGIC + struct.pack(">H", 999) + b"\x00" * 100
        with self.assertRaises(ValueError):
            loader.load_bytes(data)


class TestVMRuntime(unittest.TestCase):
    def test_builtins(self):
        config = VMConfig()
        ctx = VMContext(config)
        rt = VMRuntime(ctx, config)
        self.assertIn("andika", rt.builtins)
        self.assertIn("int", rt.builtins)
        self.assertIn("str", rt.builtins)
        self.assertIn("abs", rt.builtins)

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
        exc = rt.create_exception("test error")
        self.assertEqual(exc.message, "test error")

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


class TestVMScheduler(unittest.TestCase):
    def test_spawn(self):
        sched = VMScheduler()
        f = sched.spawn(lambda: 42)
        self.assertEqual(f.state, FiberState.READY)

    def test_run_all(self):
        results = []
        sched = VMScheduler()
        sched.spawn(lambda: results.append(1))
        sched.spawn(lambda: results.append(2))
        sched.run_all()
        self.assertEqual(sorted(results), [1, 2])

    def test_step(self):
        sched = VMScheduler()
        sched.spawn(lambda: None)
        self.assertTrue(sched.step())

    def test_stats(self):
        sched = VMScheduler()
        sched.spawn(lambda: None)
        stats = sched.get_stats()
        self.assertIn("total_fibers", stats)


class TestVMContext(unittest.TestCase):
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

    def test_metadata(self):
        config = VMConfig()
        ctx = VMContext(config)
        ctx.set_metadata("key", "value")
        self.assertEqual(ctx.get_metadata("key"), "value")


class TestVMExecutor(unittest.TestCase):
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
        ex.hook("test_event", lambda x: calls.append(x))
        ex._fire("test_event", 42)
        self.assertEqual(calls, [42])


class TestVMInstance(unittest.TestCase):
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
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, None)

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
        _emit(chunk, OpCode.HALT)
        vm.execute(chunk)
        report = vm.get_stats_report()
        self.assertIn("vm", report)
        self.assertIn("gc", report)

    def test_format_report(self):
        vm = VMInstance()
        chunk = _make_chunk()
        _emit(chunk, OpCode.HALT)
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


class TestIVMBytecode(unittest.TestCase):
    def test_opcodes(self):
        self.assertEqual(IVMOpcode.HALT, 0)
        self.assertEqual(IVMOpcode.LOAD_CONST, 1)
        self.assertEqual(IVMOpcode.ADD, 14)

    def test_instruction(self):
        inst = IVMInstruction(opcode=IVMOpcode.ADD, arg=0, line=5)
        self.assertEqual(inst.opcode, IVMOpcode.ADD)
        self.assertEqual(inst.line, 5)

    def test_chunk_emit(self):
        chunk = IVMChunk("test")
        idx = chunk.emit(IVMOpcode.LOAD_CONST, arg=0)
        self.assertEqual(idx, 0)
        self.assertEqual(chunk.instruction_count, 1)

    def test_chunk_add_constant(self):
        chunk = IVMChunk("test")
        idx = chunk.add_constant(42)
        self.assertEqual(idx, 0)
        self.assertEqual(chunk.constants[0], 42)

    def test_chunk_dedup_constants(self):
        chunk = IVMChunk("test")
        idx1 = chunk.add_constant(42)
        idx2 = chunk.add_constant(42)
        self.assertEqual(idx1, idx2)

    def test_chunk_line_table(self):
        chunk = IVMChunk("test")
        chunk.record_line(10, 0)
        chunk.record_line(20, 5)
        self.assertEqual(chunk.get_line(0), 10)
        self.assertEqual(chunk.get_line(5), 20)
        self.assertEqual(chunk.get_line(3), 10)

    def test_chunk_source_files(self):
        chunk = IVMChunk("test")
        idx1 = chunk.add_source_file("main.i")
        idx2 = chunk.add_source_file("main.i")
        self.assertEqual(idx1, idx2)

    def test_chunk_repr(self):
        chunk = IVMChunk("test")
        r = repr(chunk)
        self.assertIn("test", r)


class TestVMConfig(unittest.TestCase):
    def test_defaults(self):
        config = VMConfig()
        self.assertEqual(config.max_stack_depth, 1024)
        self.assertEqual(config.max_call_depth, 256)
        self.assertTrue(config.enable_stats)
        self.assertFalse(config.enable_debug)

    def test_with_debug(self):
        config = VMConfig()
        result = config.with_debug()
        self.assertTrue(config.enable_debug)
        self.assertIs(result, config)

    def test_with_profiler(self):
        config = VMConfig()
        result = config.with_profiler()
        self.assertTrue(config.enable_profiler)
        self.assertIs(result, config)


class TestVMIntegration(unittest.TestCase):
    def test_arithmetic_pipeline(self):
        chunk = _make_chunk("arith")
        const_10 = chunk.add_constant(10)
        const_5 = chunk.add_constant(5)
        _emit(chunk, OpCode.LOAD_CONST, const_10)
        _emit(chunk, OpCode.LOAD_CONST, const_5)
        _emit(chunk, OpCode.ADD)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 15)

    def test_multiple_ops(self):
        chunk = _make_chunk("multi")
        c3 = chunk.add_constant(3)
        c4 = chunk.add_constant(4)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.LOAD_CONST, c4)
        _emit(chunk, OpCode.MUL)
        const_2 = chunk.add_constant(2)
        _emit(chunk, OpCode.LOAD_CONST, const_2)
        _emit(chunk, OpCode.ADD)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 14)

    def test_comparison(self):
        chunk = _make_chunk("cmp")
        c5 = chunk.add_constant(5)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c5)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.GT)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_jump(self):
        chunk = _make_chunk("jump")
        c_true = chunk.add_constant(True)
        c_42 = chunk.add_constant(42)
        _emit(chunk, OpCode.LOAD_CONST, c_true)
        _emit(chunk, OpCode.JUMP_IF_FALSE, 2)
        _emit(chunk, OpCode.LOAD_CONST, c_42)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 42)

    def test_jump_skip(self):
        chunk = _make_chunk("skip")
        c_false = chunk.add_constant(False)
        c_42 = chunk.add_constant(42)
        c_99 = chunk.add_constant(99)
        _emit(chunk, OpCode.LOAD_CONST, c_false)
        _emit(chunk, OpCode.JUMP_IF_FALSE, 3)
        _emit(chunk, OpCode.LOAD_CONST, c_42)
        _emit(chunk, OpCode.LOAD_CONST, c_99)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 99)

    def test_negation(self):
        chunk = _make_chunk("neg")
        c5 = chunk.add_constant(5)
        _emit(chunk, OpCode.LOAD_CONST, c5)
        _emit(chunk, OpCode.NEG)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, -5)

    def test_not(self):
        chunk = _make_chunk("not")
        c_true = chunk.add_constant(True)
        _emit(chunk, OpCode.LOAD_CONST, c_true)
        _emit(chunk, OpCode.NOT)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertFalse(result)

    def test_division(self):
        chunk = _make_chunk("div")
        c10 = chunk.add_constant(10)
        c2 = chunk.add_constant(2)
        _emit(chunk, OpCode.LOAD_CONST, c10)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.DIV)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 5.0)

    def test_build_list(self):
        chunk = _make_chunk("list")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.BUILD_LIST, 3)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsInstance(result, VMList)
        self.assertEqual(len(result), 3)

    def test_build_tuple(self):
        chunk = _make_chunk("tuple")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.BUILD_TUPLE, 2)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsInstance(result, VMTuple)
        self.assertEqual(len(result), 2)

    def test_pop(self):
        chunk = _make_chunk("pop")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.POP)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 1)

    def test_dup(self):
        chunk = _make_chunk("dup")
        c42 = chunk.add_constant(42)
        _emit(chunk, OpCode.LOAD_CONST, c42)
        _emit(chunk, OpCode.DUP)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 42)

    def test_swap(self):
        chunk = _make_chunk("swap")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.SWAP)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 1)

    def test_bitwise(self):
        chunk = _make_chunk("bit")
        c6 = chunk.add_constant(6)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c6)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.BIT_AND)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 2)

    def test_null_load(self):
        chunk = _make_chunk("null")
        _emit(chunk, OpCode.LOAD_NULL)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertIsNone(result)

    def test_true_load(self):
        chunk = _make_chunk("true")
        _emit(chunk, OpCode.LOAD_TRUE)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_false_load(self):
        chunk = _make_chunk("false")
        _emit(chunk, OpCode.LOAD_FALSE)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertFalse(result)

    def test_eq(self):
        chunk = _make_chunk("eq")
        c5a = chunk.add_constant(5)
        c5b = chunk.add_constant(5)
        _emit(chunk, OpCode.LOAD_CONST, c5a)
        _emit(chunk, OpCode.LOAD_CONST, c5b)
        _emit(chunk, OpCode.EQ)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_neq(self):
        chunk = _make_chunk("neq")
        c5 = chunk.add_constant(5)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c5)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.NEQ)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_lte(self):
        chunk = _make_chunk("lte")
        c3 = chunk.add_constant(3)
        c5 = chunk.add_constant(5)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.LOAD_CONST, c5)
        _emit(chunk, OpCode.LTE)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_mod(self):
        chunk = _make_chunk("mod")
        c10 = chunk.add_constant(10)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c10)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.MOD)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 1)

    def test_or(self):
        chunk = _make_chunk("or")
        c_false = chunk.add_constant(False)
        c_true = chunk.add_constant(True)
        _emit(chunk, OpCode.LOAD_CONST, c_false)
        _emit(chunk, OpCode.LOAD_CONST, c_true)
        _emit(chunk, OpCode.OR)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertTrue(result)

    def test_and(self):
        chunk = _make_chunk("and")
        c_true = chunk.add_constant(True)
        c_false = chunk.add_constant(False)
        _emit(chunk, OpCode.LOAD_CONST, c_true)
        _emit(chunk, OpCode.LOAD_CONST, c_false)
        _emit(chunk, OpCode.AND)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertFalse(result)

    def test_rotation(self):
        chunk = _make_chunk("rot")
        c1 = chunk.add_constant(1)
        c2 = chunk.add_constant(2)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.LOAD_CONST, c2)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.ROT_THREE)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 2)

    def test_global_store_load(self):
        chunk = _make_chunk("global")
        name_idx = chunk.add_constant("myvar")
        c42 = chunk.add_constant(42)
        _emit(chunk, OpCode.LOAD_CONST, c42)
        _emit(chunk, OpCode.STORE_GLOBAL, name_idx)
        _emit(chunk, OpCode.LOAD_GLOBAL, name_idx)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 42)

    def test_sub(self):
        chunk = _make_chunk("sub")
        c10 = chunk.add_constant(10)
        c3 = chunk.add_constant(3)
        _emit(chunk, OpCode.LOAD_CONST, c10)
        _emit(chunk, OpCode.LOAD_CONST, c3)
        _emit(chunk, OpCode.SUB)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        result = vm.execute(chunk)
        self.assertEqual(result, 7)

    def test_div_by_zero(self):
        chunk = _make_chunk("div0")
        c10 = chunk.add_constant(10)
        c0 = chunk.add_constant(0)
        _emit(chunk, OpCode.LOAD_CONST, c10)
        _emit(chunk, OpCode.LOAD_CONST, c0)
        _emit(chunk, OpCode.DIV)
        _emit(chunk, OpCode.HALT)
        vm = VMInstance()
        with self.assertRaises(VMRuntimeError):
            vm.execute(chunk)

    def test_profiler_integration(self):
        config = VMConfig(enable_profiler=True)
        vm = VMInstance(config)
        chunk = _make_chunk("profiled")
        c1 = chunk.add_constant(1)
        _emit(chunk, OpCode.LOAD_CONST, c1)
        _emit(chunk, OpCode.HALT)
        vm.execute(chunk)
        self.assertTrue(vm.profiler.enabled)

    def test_debugger_integration(self):
        vm = VMInstance()
        vm.debugger.add_breakpoint("test", 1)
        self.assertEqual(len(vm.debugger.get_breakpoints()), 1)


if __name__ == "__main__":
    unittest.main()
