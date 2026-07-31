"""
Comprehensive tests for the AST-to-IR lowering pass.
Tests use correct I language syntax (Kinyarwanda keywords).
"""
from __future__ import annotations

import sys

import pytest

sys.path.insert(0, 'src')

from compiler.ir.basic_block import BasicBlock
from compiler.ir.function import IRFunction
from compiler.ir.instructions import (
    Instruction,
    Opcode,
)
from compiler.ir.lower import ASTLowering
from compiler.ir.module import IRModule
from compiler.ir.types import (
    IR_F64,
    IR_I1,
    IR_I64,
    IR_VOID,
)
from compiler.ir.values import (
    BoolConstant,
    IntConstant,
)
from compiler.lexer.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.typesystem.checker import check_types

# ────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────


def compile_and_lower(source: str) -> IRModule:
    """Compile source code all the way through type checking and IR lowering."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    sema = SemanticAnalyzer()
    sema.analyze(ast)
    diag = check_types(ast)
    if diag.has_errors:
        raise RuntimeError(f"Type errors:\n{diag.format_all()}")
    lowerer = ASTLowering("main")
    return lowerer.lower(ast)


def get_func(mod: IRModule, name: str) -> IRFunction:
    """Get a function from the module by name."""
    for func in mod.functions:
        if func.name == name:
            return func
    raise KeyError(f"Function '{name}' not found in module")


def find_inst(block: BasicBlock, opcode: Opcode) -> Instruction:
    """Find the first instruction in a block with the given opcode."""
    for inst in block:
        if inst.opcode == opcode:
            return inst
    raise ValueError(f"No {opcode} in block {block.name}")


def has_inst(block: BasicBlock, opcode: Opcode) -> bool:
    """Check if a block has an instruction with the given opcode."""
    return any(inst.opcode == opcode for inst in block)


def count_inst(block: BasicBlock, opcode: Opcode) -> int:
    """Count instructions with the given opcode in a block."""
    return sum(1 for inst in block if inst.opcode == opcode)


# ────────────────────────────────────────────────────────────────
# Module & Function Structure
# ────────────────────────────────────────────────────────────────


class TestModuleStructure:
    def test_empty_program(self):
        mod = compile_and_lower("")
        assert isinstance(mod, IRModule)
        assert mod.name == "main"

    def test_single_function(self):
        src = """
        umurimo main() -> int kora
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert isinstance(func, IRFunction)
        assert func.name == "main"
        assert not func.is_declaration

    def test_multiple_functions(self):
        src = """
        umurimo foo() -> int kora
            subira 1
        iherezo
        umurimo bar() -> int kora
            subira 2
        iherezo
        """
        mod = compile_and_lower(src)
        assert get_func(mod, "foo")
        assert get_func(mod, "bar")
        assert len([f for f in mod.functions]) == 2

    def test_function_arguments(self):
        src = """
        umurimo add(a: int, b: int) -> int kora
            subira a + b
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "add")
        assert len(func.args) == 2
        assert func.args[0].type == IR_I64
        assert func.args[1].type == IR_I64


# ────────────────────────────────────────────────────────────────
# Control Flow
# ────────────────────────────────────────────────────────────────


class TestControlFlow:
    def test_return_literal(self):
        src = """
        umurimo main() -> int kora
            subira 42
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.block_count >= 1
        entry = func.entry_block
        assert entry is not None
        assert has_inst(entry, Opcode.RETURN), "Expected RETURN in entry block"

    def test_return_void(self):
        src = """
        umurimo main() kora
            subira
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        ret = find_inst(entry, Opcode.RETURN)
        assert ret is not None

    def test_if_statement(self):
        src = """
        umurimo main(x: int) -> int kora
            niba x > 0 kora
                subira 1
            cyangwa
                subira 0
            iherezo
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.block_count >= 3, f"Expected >=3 blocks, got {func.block_count}"

    def test_while_loop(self):
        src = """
        umurimo main(n: int) -> int kora
            shyira x = n
            wihuse x > 0 kora
                x = x - 1
            iherezo
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.block_count >= 3, f"Expected >=3 blocks, got {func.block_count}"
        ret_count = sum(1 for b in func for i in b if i.opcode == Opcode.RETURN)
        assert ret_count >= 1, "Expected at least one RETURN"

    def test_var_decl_no_init(self):
        src = """
        umurimo main() -> int kora
            shyira x: int
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        assert has_inst(entry, Opcode.ALLOCA), "Expected ALLOCA for variable"

    def test_var_decl_with_init(self):
        src = """
        umurimo main() -> int kora
            shyira x = 42
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        assert has_inst(entry, Opcode.ALLOCA), "Expected ALLOCA for variable"

    def test_assignment(self):
        src = """
        umurimo main() -> int kora
            shyira x: int
            x = 42
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        store_count = count_inst(entry, Opcode.STORE)
        assert store_count >= 1, "Expected STORE for assignment"


# ────────────────────────────────────────────────────────────────
# Arithmetic & Expressions
# ────────────────────────────────────────────────────────────────


class TestExpressions:
    def test_literal_int(self):
        src = """
        umurimo main() -> int kora
            subira 42
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        ret = find_inst(entry, Opcode.RETURN)
        assert ret is not None
        val = ret.operands[0] if ret.operands else None
        if isinstance(val, IntConstant):
            assert val.value == 42

    def test_literal_bool(self):
        src = """
        umurimo main() -> bool kora
            subira yego
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        ret = find_inst(entry, Opcode.RETURN)
        val = ret.operands[0] if ret.operands else None
        if isinstance(val, BoolConstant):
            assert val.value is True

    def test_binary_add(self):
        src = """
        umurimo main(a: int, b: int) -> int kora
            subira a + b
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        assert has_inst(entry, Opcode.ADD), "Expected ADD instruction"

    def test_binary_sub(self):
        src = """
        umurimo main(a: int, b: int) -> int kora
            subira a - b
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert has_inst(entry, Opcode.SUB), "Expected SUB instruction"

    def test_binary_mul(self):
        src = """
        umurimo main(a: int, b: int) -> int kora
            subira a * b
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert has_inst(entry, Opcode.MUL), "Expected MUL instruction"

    def test_binary_comparison(self):
        src = """
        umurimo main(a: int, b: int) -> bool kora
            subira a == b
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert has_inst(entry, Opcode.ICMP), "Expected ICMP instruction"

    def test_unary_neg(self):
        src = """
        umurimo main(x: int) -> int kora
            subira -x
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert has_inst(entry, Opcode.NEG), "Expected NEG instruction"


# ────────────────────────────────────────────────────────────────
# Type Mapping
# ────────────────────────────────────────────────────────────────


class TestTypeMapping:
    def test_int_type(self):
        src = """
        umurimo main() -> int kora
            subira 0
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.return_type == IR_I64

    def test_bool_type(self):
        src = """
        umurimo main() -> bool kora
            subira yego
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.return_type == IR_I1

    def test_void_type(self):
        src = """
        umurimo main() kora
            subira
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.return_type == IR_VOID

    def test_float_arg(self):
        src = """
        umurimo main(x: float) -> float kora
            subira x
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert len(func.args) == 1
        assert func.args[0].type == IR_F64


# ────────────────────────────────────────────────────────────────
# Blocks and Control Flow Detail
# ────────────────────────────────────────────────────────────────


class TestBlockDetail:
    def test_if_else_blocks(self):
        src = """
        umurimo main(x: int) -> int kora
            niba x > 0 kora
                subira 1
            cyangwa
                subira 0
            iherezo
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.block_count >= 3
        has_branch = any(
            has_inst(b, Opcode.BRANCH) or has_inst(b, Opcode.COND_BRANCH)
            for b in func
        )
        assert has_branch, "Expected branch instructions in if/else"

    def test_block_termination(self):
        src = """
        umurimo main(x: int) -> int kora
            subira x
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        assert len(entry.instructions) > 0
        assert entry.instructions[-1].is_terminator


# ────────────────────────────────────────────────────────────────
# Edge Cases
# ────────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_empty_function(self):
        src = """
        umurimo main() kora
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        entry = func.entry_block
        assert entry is not None
        assert has_inst(entry, Opcode.RETURN)

    def test_multiple_returns(self):
        src = """
        umurimo main(x: int) -> int kora
            niba x > 0 kora
                subira 1
            cyangwa
                subira 0
            iherezo
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        ret_count = sum(1 for b in func for i in b if i.opcode == Opcode.RETURN)
        assert ret_count >= 2, f"Expected >=2 RETURNs, got {ret_count}"

    def test_nested_blocks(self):
        src = """
        umurimo main(x: int, y: int) -> int kora
            niba x > 0 kora
                niba y > 0 kora
                    subira 1
                iherezo
                subira 2
            cyangwa
                subira 0
            iherezo
        iherezo
        """
        mod = compile_and_lower(src)
        func = get_func(mod, "main")
        assert func.block_count >= 4, f"Expected >=4 blocks, got {func.block_count}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
