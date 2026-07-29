# Testing Guide

This document provides comprehensive guidelines for testing the I Programming Language.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Organization](#test-organization)
- [Unit Testing](#unit-testing)
- [Integration Testing](#integration-testing)
- [Regression Testing](#regression-testing)
- [Performance Testing](#performance-testing)
- [Fuzzing Testing](#fuzzing-testing)
- [Property-Based Testing](#property-based-testing)
- [Test Coverage](#test-coverage)
- [Test Infrastructure](#test-infrastructure)
- [Test Data Management](#test-data-management)
- [Continuous Integration](#continuous-integration)

## Testing Philosophy

### Core Principles

1. **Test Early**: Write tests alongside code
2. **Test Often**: Run tests frequently
3. **Test Everything**: Every feature must have tests
4. **Test Thoroughly**: Cover all code paths
5. **Test Automatically**: Automate all testing
6. **Test Continuously**: Integrate testing into CI/CD

### Quality Standards

- **Coverage**: Aim for 90%+ code coverage
- **Reliability**: Tests must be reliable and repeatable
- **Speed**: Tests must run quickly
- **Clarity**: Tests must be easy to understand
- **Maintainability**: Tests must be easy to maintain

## Test Organization

### Directory Structure

```
tests/
├── unit/              # Unit tests
│   ├── lexer/
│   ├── parser/
│   ├── semantic/
│   ├── codegen/
│   └── vm/
├── integration/       # Integration tests
│   ├── compiler/
│   ├── runtime/
│   └── stdlib/
├── regression/        # Regression tests
│   ├── known_bugs/
│   └── fixed_issues/
├── performance/       # Performance tests
│   ├── compilation/
│   ├── execution/
│   └── memory/
├── fuzzing/          # Fuzzing tests
│   ├── lexer/
│   ├── parser/
│   └── vm/
└── property/         # Property-based tests
    ├── types/
    └── algorithms/
```

### Test Naming

Use descriptive test names:

```python
# Good
def test_lexer_integer_literal_tokenization():
    """Test that integer literals are tokenized correctly."""
    pass

def test_parser_binary_expression_precedence():
    """Test that binary expressions respect operator precedence."""
    pass

# Bad
def test_lexer():
    pass

def test_parser():
    pass
```

## Unit Testing

### Purpose

Test individual components in isolation.

### Guidelines

- Test each function/method
- Test edge cases
- Test error conditions
- Keep tests independent
- Use mocks for dependencies

### Example

```python
class TestLexer:
    """Unit tests for the Lexer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lexer = Lexer("")
    
    def test_integer_literal(self):
        """Test integer literal tokenization."""
        source = "42"
        tokens = self.lexer.tokenize(source)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].literal, 42)
    
    def test_float_literal(self):
        """Test float literal tokenization."""
        source = "3.14"
        tokens = self.lexer.tokenize(source)
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
        self.assertEqual(tokens[0].literal, 3.14)
    
    def test_string_literal(self):
        """Test string literal tokenization."""
        source = '"Muraho"'
        tokens = self.lexer.tokenize(source)
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "Muraho")
    
    def test_unterminated_string(self):
        """Test error handling for unterminated string."""
        source = '"unterminated'
        with self.assertRaises(LexerError):
            self.lexer.tokenize(source)
```

## Integration Testing

### Purpose

Test component interactions.

### Guidelines

- Test real component interactions
- Test across module boundaries
- Test with real dependencies
- Focus on integration points
- Use test fixtures

### Example

```python
class TestCompilerIntegration:
    """Integration tests for the compiler pipeline."""
    
    def test_compile_and_run_simple_program(self):
        """Test compiling and running a simple program."""
        source = """
        shyira x = 10
        andika x
        """
        compiler = Compiler()
        chunk = compiler.compile_source(source)
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        self.assertEqual(result, 10)
    
    def test_function_definition_and_call(self):
        """Test function definition and call."""
        source = """
        umurimo add(a: int, b: int) -> int
            subira a + b
        iherezo
        andika add(5, 3)
        """
        compiler = Compiler()
        chunk = compiler.compile_source(source)
        vm = VirtualMachine()
        result = vm.interpret(chunk)
        self.assertEqual(result, 8)
```

## Regression Testing

### Purpose

Ensure bugs stay fixed.

### Guidelines

- Add test for every bug fix
- Document the original issue
- Test the specific bug scenario
- Test related scenarios
- Keep tests indefinitely

### Example

```python
class TestRegression:
    """Regression tests for known bugs."""
    
    def test_issue_123_division_by_zero(self):
        """Test that division by zero is properly handled.
        
        Issue: #123 - Division by zero was not caught at compile time.
        """
        source = """
        shyira x = 10 / 0
        """
        compiler = Compiler()
        with self.assertRaises(SemanticError):
            compiler.compile_source(source)
    
    def test_issue_456_uninitialized_variable(self):
        """Test that uninitialized variables are caught.
        
        Issue: #456 - Uninitialized variables were not detected.
        """
        source = """
        andika x
        """
        compiler = Compiler()
        with self.assertRaises(SemanticError):
            compiler.compile_source(source)
```

## Performance Testing

### Purpose

Ensure performance targets are met.

### Guidelines

- Establish baseline performance
- Test against performance targets
- Profile bottlenecks
- Test with realistic data
- Monitor performance over time

### Example

```python
class TestPerformance:
    """Performance tests for the compiler and runtime."""
    
    def test_compilation_speed(self):
        """Test that compilation is fast enough."""
        source = """
        buri i muri 0 kugeza 1000
            andika i
        iherezo
        """
        compiler = Compiler()
        start_time = time.time()
        chunk = compiler.compile_source(source)
        compilation_time = time.time() - start_time
        self.assertLess(compilation_time, 1.0)  # Should compile in < 1 second
    
    def test_execution_speed(self):
        """Test that execution is fast enough."""
        source = """
        umurimo fibonacci(n: int) -> int
            niba n munsi_ya 2
                subira n
            iherezo
            subira fibonacci(n - 1) + fibonacci(n - 2)
        iherezo
        andika fibonacci(20)
        """
        compiler = Compiler()
        chunk = compiler.compile_source(source)
        vm = VirtualMachine()
        start_time = time.time()
        vm.interpret(chunk)
        execution_time = time.time() - start_time
        self.assertLess(execution_time, 5.0)  # Should execute in < 5 seconds
```

## Fuzzing Testing

### Purpose

Find unexpected bugs through random input.

### Guidelines

- Use fuzzing frameworks
- Test with random inputs
- Monitor for crashes
- Analyze crash results
- Fix discovered bugs

### Example

```python
class TestFuzzing:
    """Fuzzing tests for robustness."""
    
    def test_lexer_fuzzing(self):
        """Test lexer with random input."""
        import random
        import string
        
        for _ in range(1000):
            # Generate random input
            length = random.randint(0, 1000)
            random_input = ''.join(random.choices(string.printable, k=length))
            
            # Test that lexer doesn't crash
            try:
                lexer = Lexer(random_input)
                tokens = lexer.tokenize()
                # Verify tokens are valid
                for token in tokens:
                    self.assertIsNotNone(token.type)
            except LexerError:
                # Expected for invalid input
                pass
```

## Property-Based Testing

### Purpose

Test properties that should always hold true.

### Guidelines

- Identify invariants
- Test with many inputs
- Use property testing frameworks
- Document properties
- Fix property violations

### Example

```python
class TestProperties:
    """Property-based tests."""
    
    def test_addition_commutativity(self):
        """Test that addition is commutative."""
        for a in range(-100, 100):
            for b in range(-100, 100):
                source = f"""
                shyira x = {a} + {b}
                shyira y = {b} + {a}
                """
                compiler = Compiler()
                chunk = compiler.compile_source(source)
                vm = VirtualMachine()
                vm.interpret(chunk)
                # x should equal y
                self.assertEqual(vm.stack[-2], vm.stack[-1])
    
    def test_multiplication_associativity(self):
        """Test that multiplication is associative."""
        for a in range(-10, 10):
            for b in range(-10, 10):
                for c in range(-10, 10):
                    source = f"""
                    shyira x = ({a} * {b}) * {c}
                    shyira y = {a} * ({b} * {c})
                    """
                    compiler = Compiler()
                    chunk = compiler.compile_source(source)
                    vm = VirtualMachine()
                    vm.interpret(chunk)
                    # x should equal y
                    self.assertEqual(vm.stack[-2], vm.stack[-1])
```

## Test Coverage

### Goals

- **Overall**: 90%+ coverage
- **Critical paths**: 100% coverage
- **Error handling**: 100% coverage

### Tools

- `pytest-cov`: Coverage measurement
- `coverage.py`: Detailed coverage reports

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=compiler --cov=vm --cov-report=html

# Generate coverage report
coverage report
coverage html
```

### Coverage Reports

Review coverage reports regularly:
- Identify uncovered code
- Add tests for uncovered areas
- Monitor coverage trends
- Set coverage targets

## Test Infrastructure

### Test Framework

We use `pytest` as our test framework:

```python
# conftest.py
import pytest

@pytest.fixture
def compiler():
    """Fixture providing a compiler instance."""
    return Compiler()

@pytest.fixture
def vm():
    """Fixture providing a VM instance."""
    return VirtualMachine()
```

### Test Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### Continuous Integration

Tests run automatically on:
- Every pull request
- Every commit to main
- Scheduled nightly runs

## Test Data Management

### Test Fixtures

Use fixtures for test data:

```python
@pytest.fixture
def sample_program():
    """Fixture providing sample program source."""
    return """
    umurimo main() -> int
        subira 0
    iherezo
    """
```

### Test Data Files

Store test data in files:

```
tests/
├── data/
│   ├── programs/
│   │   ├── simple.i
│   │   ├── complex.i
│   │   └── edge_cases.i
│   └── expected/
│       ├── simple.json
│       ├── complex.json
│       └── edge_cases.json
```

## Continuous Integration

### CI Pipeline

1. **Lint**: Check code style
2. **Type Check**: Verify type annotations
3. **Unit Tests**: Run unit tests
4. **Integration Tests**: Run integration tests
5. **Coverage**: Measure coverage
6. **Performance**: Run performance tests

### CI Configuration

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -e . -r requirements-dev.txt
      - name: Run tests
        run: pytest --cov=compiler --cov=vm
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Best Practices

### Test Independence

Each test should be independent:

```python
# Good - Independent test
def test_function_a():
    result = function_a()
    assert result == expected

def test_function_b():
    result = function_b()
    assert result == expected

# Bad - Dependent test
def test_function_a():
    global state = function_a()
    assert state == expected

def test_function_b():
    # Depends on test_function_a
    result = function_b(state)
    assert result == expected
```

### Test Isolation

Use fresh fixtures for each test:

```python
# Good - Fresh fixture
def test_with_fresh_fixture(compiler):
    source = "test code"
    chunk = compiler.compile_source(source)
    # Test with fresh compiler

# Bad - Shared state
compiler = Compiler()

def test_1():
    source = "test code"
    compiler.compile_source(source)

def test_2():
    # May have state from test_1
    source = "other code"
    compiler.compile_source(source)
```

### Test Speed

Keep tests fast:

```python
# Good - Fast test
def test_function():
    result = function()
    assert result == expected

# Bad - Slow test
def test_function():
    time.sleep(10)  # Unnecessary delay
    result = function()
    assert result == expected
```

## Review Checklist

Before committing tests, review:

- [ ] Test is independent
- [ ] Test is fast
- [ ] Test is clear
- [ ] Test covers the scenario
- [ ] Test has proper assertions
- [ ] Test has proper fixtures
- [ ] Test is documented
- [ ] Test follows naming conventions

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
