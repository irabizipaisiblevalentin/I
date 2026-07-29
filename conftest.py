"""Pytest configuration and fixtures."""

import pytest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic import SemanticAnalyzer
from compiler.codegen import CodeGenerator
from vm.virtual_machine import VirtualMachine


@pytest.fixture
def lexer():
    """Fixture providing a Lexer instance."""
    return Lexer("")


@pytest.fixture
def parser():
    """Fixture providing a Parser instance."""
    return Parser()


@pytest.fixture
def semantic_analyzer():
    """Fixture providing a SemanticAnalyzer instance."""
    return SemanticAnalyzer()


@pytest.fixture
def code_generator():
    """Fixture providing a CodeGenerator instance."""
    return CodeGenerator()


@pytest.fixture
def vm():
    """Fixture providing a VirtualMachine instance."""
    return VirtualMachine()


@pytest.fixture
def sample_program():
    """Fixture providing a sample I program."""
    return """
    shyira x = 10
    andika x
    """


@pytest.fixture
def fibonacci_program():
    """Fixture providing a Fibonacci program."""
    return """
    umurimo fibonacci(n: int) -> int
        niba n munsi_ya 2
            subira n
        iherezo
        subira fibonacci(n - 1) + fibonacci(n - 2)
    iherezo
    andika fibonacci(10)
    """
