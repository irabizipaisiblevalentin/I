"""
Unit tests for the I programming language virtual machine.
"""

import unittest
from vm.virtual_machine import VirtualMachine, RuntimeError
from compiler.codegen.bytecode import OpCode, Chunk


class TestVirtualMachine(unittest.TestCase):
    """Test cases for the virtual machine."""
    
    def setUp(self):
        """Set up a fresh VM for each test."""
        self.vm = VirtualMachine()
    
    def test_load_const(self):
        """Test loading constants."""
        chunk = Chunk("test")
        const_index = chunk.add_constant(42)
        chunk.emit(OpCode.LOAD_CONST, const_index)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 42)
    
    def test_arithmetic_add(self):
        """Test addition."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(20))
        chunk.emit(OpCode.ADD)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 30)
    
    def test_arithmetic_subtract(self):
        """Test subtraction."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(20))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.SUB)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 10)
    
    def test_arithmetic_multiply(self):
        """Test multiplication."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(5))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(6))
        chunk.emit(OpCode.MUL)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 30)
    
    def test_arithmetic_divide(self):
        """Test division."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(20))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(4))
        chunk.emit(OpCode.DIV)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 5)
    
    def test_comparison_equal(self):
        """Test equality comparison."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.EQ)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertTrue(result)
    
    def test_comparison_less_than(self):
        """Test less than comparison."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(5))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.LT)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertTrue(result)
    
    def test_logical_and(self):
        """Test logical AND."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(True))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(True))
        chunk.emit(OpCode.AND)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertTrue(result)
    
    def test_logical_or(self):
        """Test logical OR."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(True))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(False))
        chunk.emit(OpCode.OR)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertTrue(result)
    
    def test_logical_not(self):
        """Test logical NOT."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(True))
        chunk.emit(OpCode.NOT)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertFalse(result)
    
    def test_unary_negation(self):
        """Test unary negation."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))
        chunk.emit(OpCode.NEG)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, -10)
    
    def test_jump_if_false(self):
        """Test conditional jump."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(False))
        jump_pos = chunk.emit(OpCode.JUMP_IF_FALSE)
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(10))  # Should be skipped
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(20))  # Should be returned
        chunk.code[jump_pos].arg = len(chunk.code)  # Patch jump
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 20)
    
    def test_build_list(self):
        """Test building a list."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(1))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(2))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(3))
        chunk.emit(OpCode.BUILD_LIST, 3)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, [1, 2, 3])
    
    def test_get_item(self):
        """Test getting an item from a list."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant([1, 2, 3]))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant(1))
        chunk.emit(OpCode.GET_ITEM)
        chunk.emit(OpCode.HALT)
        
        result = self.vm.interpret(chunk)
        self.assertEqual(result, 2)
    
    def test_builtin_print(self):
        """Test built-in print function."""
        chunk = Chunk("test")
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant("Hello"))
        chunk.emit(OpCode.LOAD_CONST, chunk.add_constant("andika"))
        chunk.emit(OpCode.CALL, 1)
        chunk.emit(OpCode.HALT)
        
        # This should print "Hello" without error
        result = self.vm.interpret(chunk)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
