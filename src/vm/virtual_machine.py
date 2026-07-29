"""
Virtual Machine for the I programming language.

This module implements a stack-based virtual machine that executes bytecode.
"""

from typing import List, Any, Callable, Dict
from compiler.codegen.bytecode import OpCode, Chunk, Instruction


class RuntimeError(Exception):
    """Runtime error raised by the VM."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Runtime error: {message}")


class VirtualMachine:
    """Stack-based virtual machine for executing I bytecode."""
    
    def __init__(self):
        self.chunk: Optional[Chunk] = None
        self.ip: int = 0  # Instruction pointer
        self.stack: List[Any] = []
        self.globals: Dict[str, Any] = {}
        self.builtins: Dict[str, Callable] = {}
        
        self._init_builtins()
    
    def _init_builtins(self):
        """Initialize built-in functions."""
        self.builtins['andika'] = self._builtin_print
    
    def _builtin_print(self, *args):
        """Built-in print function."""
        print(*args)
        return None
    
    def interpret(self, chunk: Chunk) -> Any:
        """
        Interpret and execute a chunk of bytecode.
        
        Args:
            chunk: The bytecode chunk to execute
            
        Returns:
            The result of the execution (if any)
            
        Raises:
            RuntimeError: If a runtime error occurs
        """
        self.chunk = chunk
        self.ip = 0
        self.stack = []
        
        while True:
            instruction = self._read_instruction()
            
            if instruction.opcode == OpCode.HALT:
                break
            
            self._execute_instruction(instruction)
        
        return self._pop() if self.stack else None
    
    def _read_instruction(self) -> Instruction:
        """Read the current instruction and advance the IP."""
        if self.chunk is None or self.ip >= len(self.chunk.code):
            raise RuntimeError("Unexpected end of bytecode")
        
        instruction = self.chunk.code[self.ip]
        self.ip += 1
        return instruction
    
    def _execute_instruction(self, instruction: Instruction):
        """Execute a single instruction."""
        opcode = instruction.opcode
        arg = instruction.arg
        
        # Constants and Literals
        if opcode == OpCode.LOAD_CONST:
            if arg is None or self.chunk is None:
                raise RuntimeError("LOAD_CONST requires an argument")
            self._push(self.chunk.constants[arg])
        
        elif opcode == OpCode.LOAD_NULL:
            self._push(None)
        
        elif opcode == OpCode.LOAD_TRUE:
            self._push(True)
        
        elif opcode == OpCode.LOAD_FALSE:
            self._push(False)
        
        # Variable Operations
        elif opcode == OpCode.LOAD_LOCAL:
            if arg is None:
                raise RuntimeError("LOAD_LOCAL requires an argument")
            self._push(self.stack[arg])
        
        elif opcode == OpCode.STORE_LOCAL:
            if arg is None:
                raise RuntimeError("STORE_LOCAL requires an argument")
            value = self._pop()
            if arg >= len(self.stack):
                self.stack.append(value)
            else:
                self.stack[arg] = value
        
        elif opcode == OpCode.LOAD_GLOBAL:
            if arg is None or self.chunk is None:
                raise RuntimeError("LOAD_GLOBAL requires an argument")
            name = self.chunk.constants[arg]
            if name not in self.globals:
                raise RuntimeError(f"Undefined global variable: {name}")
            self._push(self.globals[name])
        
        elif opcode == OpCode.STORE_GLOBAL:
            if arg is None or self.chunk is None:
                raise RuntimeError("STORE_GLOBAL requires an argument")
            name = self.chunk.constants[arg]
            value = self._pop()
            self.globals[name] = value
        
        # Stack Operations
        elif opcode == OpCode.POP:
            self._pop()
        
        elif opcode == OpCode.DUP:
            self._push(self._peek())
        
        elif opcode == OpCode.SWAP:
            if len(self.stack) < 2:
                raise RuntimeError("SWAP requires at least 2 values on the stack")
            a = self._pop()
            b = self._pop()
            self._push(a)
            self._push(b)
        
        elif opcode == OpCode.ROT_THREE:
            if len(self.stack) < 3:
                raise RuntimeError("ROT_THREE requires at least 3 values on the stack")
            c = self._pop()
            b = self._pop()
            a = self._pop()
            self._push(c)
            self._push(a)
            self._push(b)
        
        # Arithmetic Operations
        elif opcode == OpCode.ADD:
            b = self._pop()
            a = self._pop()
            self._push(a + b)
        
        elif opcode == OpCode.SUB:
            b = self._pop()
            a = self._pop()
            self._push(a - b)
        
        elif opcode == OpCode.MUL:
            b = self._pop()
            a = self._pop()
            self._push(a * b)
        
        elif opcode == OpCode.DIV:
            b = self._pop()
            a = self._pop()
            if b == 0:
                raise RuntimeError("Division by zero")
            self._push(a / b)
        
        elif opcode == OpCode.MOD:
            b = self._pop()
            a = self._pop()
            if b == 0:
                raise RuntimeError("Modulo by zero")
            self._push(a % b)
        
        elif opcode == OpCode.NEG:
            a = self._pop()
            self._push(-a)
        
        # Bitwise Operations
        elif opcode == OpCode.BIT_AND:
            b = self._pop()
            a = self._pop()
            self._push(a & b)
        
        elif opcode == OpCode.BIT_OR:
            b = self._pop()
            a = self._pop()
            self._push(a | b)
        
        elif opcode == OpCode.BIT_XOR:
            b = self._pop()
            a = self._pop()
            self._push(a ^ b)
        
        elif opcode == OpCode.BIT_NOT:
            a = self._pop()
            self._push(~a)
        
        elif opcode == OpCode.LEFT_SHIFT:
            b = self._pop()
            a = self._pop()
            self._push(a << b)
        
        elif opcode == OpCode.RIGHT_SHIFT:
            b = self._pop()
            a = self._pop()
            self._push(a >> b)
        
        # Comparison Operations
        elif opcode == OpCode.EQ:
            b = self._pop()
            a = self._pop()
            self._push(a == b)
        
        elif opcode == OpCode.NEQ:
            b = self._pop()
            a = self._pop()
            self._push(a != b)
        
        elif opcode == OpCode.LT:
            b = self._pop()
            a = self._pop()
            self._push(a < b)
        
        elif opcode == OpCode.LTE:
            b = self._pop()
            a = self._pop()
            self._push(a <= b)
        
        elif opcode == OpCode.GT:
            b = self._pop()
            a = self._pop()
            self._push(a > b)
        
        elif opcode == OpCode.GTE:
            b = self._pop()
            a = self._pop()
            self._push(a >= b)
        
        # Logical Operations
        elif opcode == OpCode.AND:
            b = self._pop()
            a = self._pop()
            self._push(a and b)
        
        elif opcode == OpCode.OR:
            b = self._pop()
            a = self._pop()
            self._push(a or b)
        
        elif opcode == OpCode.NOT:
            a = self._pop()
            self._push(not a)
        
        # Control Flow
        elif opcode == OpCode.JUMP:
            if arg is None:
                raise RuntimeError("JUMP requires an argument")
            self.ip = arg
        
        elif opcode == OpCode.JUMP_IF_FALSE:
            if arg is None:
                raise RuntimeError("JUMP_IF_FALSE requires an argument")
            condition = self._pop()
            if not condition:
                self.ip = arg
        
        elif opcode == OpCode.JUMP_IF_TRUE:
            if arg is None:
                raise RuntimeError("JUMP_IF_TRUE requires an argument")
            condition = self._pop()
            if condition:
                self.ip = arg
        
        elif opcode == OpCode.JUMP_IF_FALSE_POP:
            if arg is None:
                raise RuntimeError("JUMP_IF_FALSE_POP requires an argument")
            condition = self._pop()
            if not condition:
                self.ip = arg
        
        elif opcode == OpCode.LOOP:
            if arg is None:
                raise RuntimeError("LOOP requires an argument")
            self.ip -= arg
        
        elif opcode == OpCode.CALL:
            if arg is None:
                raise RuntimeError("CALL requires an argument")
            self._call(arg)
        
        elif opcode == OpCode.RETURN:
            return self._pop() if self.stack else None
        
        # Collections
        elif opcode == OpCode.BUILD_LIST:
            if arg is None:
                raise RuntimeError("BUILD_LIST requires an argument")
            items = [self._pop() for _ in range(arg)]
            items.reverse()
            self._push(items)
        
        elif opcode == OpCode.BUILD_MAP:
            if arg is None:
                raise RuntimeError("BUILD_MAP requires an argument")
            map_dict = {}
            for _ in range(arg):
                value = self._pop()
                key = self._pop()
                map_dict[key] = value
            self._push(map_dict)
        
        elif opcode == OpCode.BUILD_SET:
            if arg is None:
                raise RuntimeError("BUILD_SET requires an argument")
            items = {self._pop() for _ in range(arg)}
            self._push(items)
        
        elif opcode == OpCode.BUILD_TUPLE:
            if arg is None:
                raise RuntimeError("BUILD_TUPLE requires an argument")
            items = tuple(self._pop() for _ in range(arg))
            self._push(items)
        
        elif opcode == OpCode.GET_ITEM:
            index = self._pop()
            collection = self._pop()
            if isinstance(collection, (list, str)):
                self._push(collection[index])
            elif isinstance(collection, dict):
                self._push(collection.get(index))
            else:
                raise RuntimeError("Cannot index non-collection type")
        
        elif opcode == OpCode.SET_ITEM:
            value = self._pop()
            index = self._pop()
            collection = self._pop()
            if isinstance(collection, list):
                collection[index] = value
            elif isinstance(collection, dict):
                collection[index] = value
            else:
                raise RuntimeError("Cannot set item on non-collection type")
            self._push(collection)
        
        elif opcode == OpCode.SLICE:
            end = self._pop()
            start = self._pop()
            collection = self._pop()
            if isinstance(collection, (list, str)):
                if end == -1:
                    self._push(collection[start:])
                else:
                    self._push(collection[start:end])
            else:
                raise RuntimeError("Cannot slice non-sequence type")
        
        # Objects
        elif opcode == OpCode.FOR_ITER:
            iterator = self._peek()
            if hasattr(iterator, '__iter__'):
                try:
                    value = next(iter(iterator))
                    self._push(value)
                    self._push(True)
                except StopIteration:
                    self._pop()
                    self._push(False)
            else:
                raise RuntimeError("Cannot iterate over non-iterable")
        
        # Exceptions
        elif opcode == OpCode.RAISE:
            exception = self._pop()
            raise RuntimeError(str(exception))
        
        elif opcode == OpCode.SETUP_TRY:
            # Simplified - just continue for now
            pass
        
        elif opcode == OpCode.POP_BLOCK:
            # Simplified - just continue for now
            pass
        
        elif opcode == OpCode.NOP:
            pass
        
        else:
            raise RuntimeError(f"Unknown opcode: {opcode}")
    
    def _call(self, arg_count: int):
        """Call a function."""
        if not self.stack:
            raise RuntimeError("Cannot call: stack is empty")
        
        callee = self._pop()
        
        if callable(callee):
            args = [self._pop() for _ in range(arg_count)]
            args.reverse()
            result = callee(*args)
            self._push(result)
        elif isinstance(callee, str) and callee in self.builtins:
            args = [self._pop() for _ in range(arg_count)]
            args.reverse()
            result = self.builtins[callee](*args)
            self._push(result)
        else:
            raise RuntimeError(f"Cannot call non-callable: {type(callee)}")
    
    def _push(self, value: Any):
        """Push a value onto the stack."""
        self.stack.append(value)
    
    def _pop(self) -> Any:
        """Pop a value from the stack."""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()
    
    def _peek(self) -> Any:
        """Peek at the top value on the stack."""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack[-1]
    
    def reset(self):
        """Reset the VM state."""
        self.chunk = None
        self.ip = 0
        self.stack = []
        self.globals = {}
