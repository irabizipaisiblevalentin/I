"""IVM Executor — instruction dispatcher and execution engine."""
from __future__ import annotations

import operator
import time
from typing import Any, Callable

from vm.vm_config import VMConfig
from vm.vm_context import VMContext
from vm.vm_memory import CallFrame, Heap, Stack, StackOverflowError
from vm.vm_objects import (
    VMClosure, VMException, VMIterator, VMList, VMMap, VMObject,
    VMSet, VMString, VMStruct, VMTuple,
)
from compiler.codegen.bytecode import OpCode


class VMRuntimeError(RuntimeError):
    """Error raised during VM execution."""
    __slots__ = ("_frame_stack", "_line")

    def __init__(self, message: str, frame_stack: list[CallFrame] | None = None, line: int = 0) -> None:
        super().__init__(message)
        self._frame_stack = frame_stack or []
        self._line = line

    @property
    def frame_stack(self) -> list[CallFrame]:
        return self._frame_stack

    @property
    def line(self) -> int:
        return self._line

    def format_trace(self) -> str:
        lines = [f"RuntimeError: {self}"]
        for frame in reversed(self._frame_stack):
            lines.append(f"  in {frame.function_name} (line {frame.line})")
        return "\n".join(lines)


class VMExecutor:
    """Core execution engine — dispatches and executes bytecode instructions."""

    __slots__ = (
        "_config", "_context", "_stack", "_call_stack",
        "_heap", "_gc", "_ip", "_chunk",
        "_running", "_interrupted", "_single_step",
        "_hooks", "_exception_handlers",
    )

    def __init__(self, config: VMConfig, context: VMContext) -> None:
        self._config = config
        self._context = context
        self._stack = Stack(config.max_stack_depth)
        self._call_stack: list[CallFrame] = []
        self._heap = Heap(config.heap_initial_size, config.gc_threshold)
        self._running = False
        self._interrupted = False
        self._single_step = False
        self._hooks: dict[str, list[Callable]] = {}
        self._exception_handlers: list[int] = []
        self._ip = 0
        self._chunk = None
        self._gc = None

    @property
    def stack(self) -> Stack:
        return self._stack

    @property
    def call_stack(self) -> list[CallFrame]:
        return self._call_stack

    @property
    def heap(self) -> Heap:
        return self._heap

    @property
    def running(self) -> bool:
        return self._running

    @property
    def config(self) -> VMConfig:
        return self._config

    @property
    def context(self) -> VMContext:
        return self._context

    def set_gc(self, gc: Any) -> None:
        self._gc = gc

    def hook(self, event: str, callback: Callable) -> None:
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    def unhook(self, event: str, callback: Callable) -> None:
        if event in self._hooks:
            try:
                self._hooks[event].remove(callback)
            except ValueError:
                pass

    def _fire(self, event: str, *args: Any) -> None:
        for cb in self._hooks.get(event, []):
            cb(*args)

    def push(self, value: Any) -> None:
        self._stack.push(value)

    def pop(self) -> Any:
        return self._stack.pop()

    def peek(self) -> Any:
        return self._stack.peek()

    def peek_at(self, offset: int) -> Any:
        return self._stack.peek_at(offset)

    def set_at(self, offset: int, value: Any) -> None:
        self._stack.set_at(offset, value)

    def _make_exception(self, message: str, type_name: str = "RuntimeError") -> VMException:
        exc = VMException(message, type_name)
        frames = []
        for frame in self._call_stack:
            frames.append({
                "function": frame.function_name,
                "line": frame.line,
            })
        exc.stack_trace = frames
        return exc

    def _current_line(self) -> int:
        if self._call_stack:
            return self._call_stack[-1].line
        return 0

    def run(self, chunk: Any) -> Any:
        """Execute a chunk of bytecode. Returns the top of stack."""
        self._chunk = chunk
        self._ip = 0
        self._running = True
        self._interrupted = False

        self._push_frame(chunk, "<module>")

        try:
            self._dispatch_loop()
        except VMRuntimeError:
            raise
        except Exception as e:
            raise VMRuntimeError(str(e), list(self._call_stack), self._current_line()) from e

        self._running = False

        if self._stack.top > 0:
            return self._stack.pop()
        return None

    def _push_frame(self, chunk: Any, name: str, closure: Any = None) -> None:
        if len(self._call_stack) >= self._config.max_call_depth:
            raise VMRuntimeError(
                f"maximum call depth exceeded ({self._config.max_call_depth})",
                list(self._call_stack),
            )
        bp = self._stack.top
        frame = CallFrame(chunk, ip=0, base_pointer=bp, function_name=name, closure=closure)
        self._call_stack.append(frame)
        self._fire("call", name, bp)

    def _pop_frame(self) -> CallFrame:
        if not self._call_stack:
            raise VMRuntimeError("call stack underflow")
        frame = self._call_stack.pop()
        self._stack.truncate(frame.base_pointer)
        self._fire("return", frame.function_name)
        return frame

    def call_function(self, closure: VMClosure, arg_count: int) -> None:
        """Call a closure with the given number of arguments on the stack."""
        if arg_count != closure.arity:
            raise VMRuntimeError(
                f"{closure.name}() takes {closure.arity} arguments but {arg_count} were given"
            )
        chunk = closure.chunk
        self._push_frame(chunk, closure.name, closure)

    def call_native(self, func: Callable, arg_count: int) -> None:
        """Call a native/builtin function."""
        args = []
        for _ in range(arg_count):
            args.append(self._stack.pop())
        args.reverse()
        result = func(*args)
        self._stack.push(result)

    def _get_local(self, index: int) -> Any:
        bp = self._call_stack[-1].base_pointer
        return self._stack.peek_at(self._stack.top - bp - 1 - index)

    def _set_local(self, index: int, value: Any) -> None:
        bp = self._call_stack[-1].base_pointer
        self._stack.set_at(self._stack.top - bp - 1 - index, value)

    def _dispatch_loop(self) -> None:
        """Main instruction dispatch loop."""
        frame = self._call_stack[-1] if self._call_stack else None
        if frame is None:
            return

        code = frame.chunk.code
        constants = frame.chunk.constants

        while self._running and not self._interrupted:
            if frame.ip >= len(code):
                break

            instruction = code[frame.ip]
            opcode = instruction.opcode
            arg = instruction.arg
            frame.ip += 1

            self._fire("instruction", opcode.value, frame.ip - 1, frame.function_name)

            if opcode == OpCode.HALT:
                break

            elif opcode == OpCode.LOAD_CONST:
                self._stack.push(constants[arg] if arg is not None else None)

            elif opcode == OpCode.LOAD_NULL:
                self._stack.push(None)

            elif opcode == OpCode.LOAD_TRUE:
                self._stack.push(True)

            elif opcode == OpCode.LOAD_FALSE:
                self._stack.push(False)

            elif opcode == OpCode.LOAD_LOCAL:
                self._stack.push(self._get_local(arg))

            elif opcode == OpCode.STORE_LOCAL:
                val = self._stack.pop()
                self._set_local(arg, val)

            elif opcode == OpCode.LOAD_GLOBAL:
                name = constants[arg] if arg is not None else None
                val = self._context.globals.get(name)
                self._stack.push(val)

            elif opcode == OpCode.STORE_GLOBAL:
                val = self._stack.pop()
                name = constants[arg] if arg is not None else None
                self._context.globals[name] = val

            elif opcode == OpCode.POP:
                self._stack.pop()

            elif opcode == OpCode.DUP:
                self._stack.dup()

            elif opcode == OpCode.SWAP:
                self._stack.swap()

            elif opcode == OpCode.ROT_THREE:
                self._stack.rot_three()

            elif opcode == OpCode.ADD:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a + b)

            elif opcode == OpCode.SUB:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a - b)

            elif opcode == OpCode.MUL:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a * b)

            elif opcode == OpCode.DIV:
                b = self._stack.pop()
                a = self._stack.pop()
                if b == 0:
                    raise VMRuntimeError("division by zero", list(self._call_stack), self._current_line())
                self._stack.push(a / b)

            elif opcode == OpCode.MOD:
                b = self._stack.pop()
                a = self._stack.pop()
                if b == 0:
                    raise VMRuntimeError("modulo by zero", list(self._call_stack), self._current_line())
                self._stack.push(a % b)

            elif opcode == OpCode.NEG:
                val = self._stack.pop()
                self._stack.push(-val)

            elif opcode == OpCode.BIT_AND:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a & b)

            elif opcode == OpCode.BIT_OR:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a | b)

            elif opcode == OpCode.BIT_XOR:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a ^ b)

            elif opcode == OpCode.BIT_NOT:
                val = self._stack.pop()
                self._stack.push(~val)

            elif opcode == OpCode.LEFT_SHIFT:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a << b)

            elif opcode == OpCode.RIGHT_SHIFT:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a >> b)

            elif opcode == OpCode.EQ:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a == b)

            elif opcode == OpCode.NEQ:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a != b)

            elif opcode == OpCode.LT:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a < b)

            elif opcode == OpCode.LTE:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a <= b)

            elif opcode == OpCode.GT:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a > b)

            elif opcode == OpCode.GTE:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(a >= b)

            elif opcode == OpCode.AND:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(bool(a) and bool(b))

            elif opcode == OpCode.OR:
                b = self._stack.pop()
                a = self._stack.pop()
                self._stack.push(bool(a) or bool(b))

            elif opcode == OpCode.NOT:
                val = self._stack.pop()
                self._stack.push(not bool(val))

            elif opcode == OpCode.JUMP:
                frame.ip = arg

            elif opcode == OpCode.JUMP_IF_FALSE:
                cond = self._stack.pop()
                if not cond:
                    frame.ip = arg

            elif opcode == OpCode.JUMP_IF_TRUE:
                cond = self._stack.pop()
                if cond:
                    frame.ip = arg

            elif opcode == OpCode.JUMP_IF_FALSE_POP:
                cond = self._stack.pop()
                if not cond:
                    frame.ip = arg

            elif opcode == OpCode.LOOP:
                frame.ip = arg

            elif opcode == OpCode.CALL:
                arg_count = arg
                callee = self._stack.peek_at(arg_count)
                if isinstance(callee, VMClosure):
                    self._stack.pop()
                    self.call_function(callee, arg_count)
                    frame = self._call_stack[-1]
                    code = frame.chunk.code
                    constants = frame.chunk.constants
                elif callable(callee):
                    self._stack.pop()
                    args = []
                    for _ in range(arg_count):
                        args.append(self._stack.pop())
                    args.reverse()
                    result = callee(*args)
                    self._stack.push(result)
                elif callee in self._context.builtins:
                    self._stack.pop()
                    args = []
                    for _ in range(arg_count):
                        args.append(self._stack.pop())
                    args.reverse()
                    result = self._context.builtins[callee](*args)
                    self._stack.push(result)
                else:
                    raise VMRuntimeError(
                        f"cannot call {type(callee).__name__}: {callee!r}",
                        list(self._call_stack),
                    )

            elif opcode == OpCode.RETURN:
                self._pop_frame()
                if not self._call_stack:
                    self._running = False
                    return
                frame = self._call_stack[-1]
                code = frame.chunk.code
                constants = frame.chunk.constants

            elif opcode == OpCode.BUILD_LIST:
                count = arg
                elements = []
                for _ in range(count):
                    elements.append(self._stack.pop())
                elements.reverse()
                self._stack.push(VMList(elements))

            elif opcode == OpCode.BUILD_MAP:
                count = arg
                entries = {}
                for _ in range(count):
                    val = self._stack.pop()
                    key = self._stack.pop()
                    entries[id(key) if isinstance(key, VMObject) else key] = val
                m = VMMap()
                m._entries = entries
                self._stack.push(m)

            elif opcode == OpCode.BUILD_SET:
                count = arg
                elements = []
                for _ in range(count):
                    elements.append(self._stack.pop())
                elements.reverse()
                s = VMSet()
                for e in elements:
                    s.add(e)
                self._stack.push(s)

            elif opcode == OpCode.BUILD_TUPLE:
                count = arg
                elements = []
                for _ in range(count):
                    elements.append(self._stack.pop())
                elements.reverse()
                self._stack.push(VMTuple(tuple(elements)))

            elif opcode == OpCode.GET_ITEM:
                index = self._stack.pop()
                collection = self._stack.pop()
                if isinstance(collection, VMList):
                    self._stack.push(collection.get(index))
                elif isinstance(collection, (list, tuple)):
                    self._stack.push(collection[index])
                elif isinstance(collection, VMMap):
                    self._stack.push(collection.get(index))
                elif isinstance(collection, str):
                    self._stack.push(collection[index])
                else:
                    raise VMRuntimeError(
                        f"cannot index {type(collection).__name__}",
                        list(self._call_stack),
                    )

            elif opcode == OpCode.SET_ITEM:
                value = self._stack.pop()
                index = self._stack.pop()
                collection = self._stack.pop()
                if isinstance(collection, VMList):
                    collection.set(index, value)
                elif isinstance(collection, VMMap):
                    collection.set(index, value)
                else:
                    raise VMRuntimeError(
                        f"cannot set item on {type(collection).__name__}",
                        list(self._call_stack),
                    )

            elif opcode == OpCode.SLICE:
                step = self._stack.pop()
                end = self._stack.pop()
                start = self._stack.pop()
                collection = self._stack.pop()
                if isinstance(collection, VMList):
                    self._stack.push(collection.slice(start, end, step))
                elif isinstance(collection, str):
                    self._stack.push(collection[start:end:step])
                else:
                    raise VMRuntimeError(
                        f"cannot slice {type(collection).__name__}",
                        list(self._call_stack),
                    )

            elif opcode == OpCode.GET_ATTR:
                name = constants[arg] if arg is not None else None
                obj = self._stack.peek()
                if isinstance(obj, VMObject):
                    val = obj.get_field(name) if hasattr(obj, 'get_field') else getattr(obj, name, None)
                else:
                    val = getattr(obj, name, None)
                if val is None:
                    raise VMRuntimeError(
                        f"attribute '{name}' not found on {type(obj).__name__}",
                        list(self._call_stack),
                    )
                self._stack.push(val)

            elif opcode == OpCode.SET_ATTR:
                name = constants[arg] if arg is not None else None
                value = self._stack.pop()
                obj = self._stack.pop()
                if isinstance(obj, VMObject) and hasattr(obj, 'set_field'):
                    obj.set_field(name, value)
                else:
                    setattr(obj, name, value)

            elif opcode == OpCode.NEW_STRUCT:
                pass

            elif opcode == OpCode.NEW_INSTANCE:
                pass

            elif opcode == OpCode.MAKE_FUNCTION:
                chunk_idx = arg if arg is not None else 0
                name = constants[chunk_idx] if chunk_idx < len(constants) else "<lambda>"
                arity = 0
                func_chunk = constants[chunk_idx] if chunk_idx < len(constants) else None
                closure = VMClosure(func_chunk, name, arity)
                self._stack.push(closure)

            elif opcode == OpCode.MAKE_CLOSURE:
                pass

            elif opcode == OpCode.GET_ITER:
                collection = self._stack.pop()
                iterator = VMIterator(collection)
                self._stack.push(iterator)

            elif opcode == OpCode.FOR_ITER:
                iterator = self._stack.peek()
                if isinstance(iterator, VMIterator) and iterator.has_next():
                    val = iterator.next()
                    self._stack.push(val)
                else:
                    frame.ip += arg

            elif opcode == OpCode.RAISE:
                if len(self._exception_handlers) > 0:
                    pass
                else:
                    message = self._stack.pop()
                    exc = self._make_exception(str(message))
                    raise VMRuntimeError(str(message), list(self._call_stack), self._current_line())

            elif opcode == OpCode.SETUP_TRY:
                self._exception_handlers.append(len(self._call_stack))

            elif opcode == OpCode.POP_BLOCK:
                if self._exception_handlers:
                    self._exception_handlers.pop()

            elif opcode == OpCode.NOP:
                pass

            else:
                raise VMRuntimeError(
                    f"unknown opcode: {opcode}",
                    list(self._call_stack),
                )

    def execute_single(self, opcode: int, arg: int = 0) -> Any:
        """Execute a single instruction (for debugger)."""
        frame = self._call_stack[-1] if self._call_stack else None
        if frame is None:
            return None
        frame.ip -= 1
        self._dispatch_loop()
        if self._stack.top > 0:
            return self._stack.peek()
        return None
