# Style Guide

This document provides coding style guidelines for the I Programming Language project.

## Table of Contents

- [General Principles](#general-principles)
- [Python Style Guide](#python-style-guide)
- [I Language Style Guide](#i-language-style-guide)
- [Documentation Style](#documentation-style)
- [Naming Conventions](#naming-conventions)
- [Code Organization](#code-organization)
- [Error Handling](#error-handling)
- [Testing Style](#testing-style)
- [Git Style](#git-style)

## General Principles

### Core Values

- **Readability**: Code should be easy to read and understand
- **Consistency**: Use consistent style throughout the codebase
- **Simplicity**: Keep code simple and straightforward
- **Clarity**: Make intent clear through naming and structure
- **Maintainability**: Write code that is easy to maintain and modify

### Golden Rules

1. **Never rush implementation** - Take time to do it right
2. **Never create hacks** - Solve problems properly
3. **Never duplicate code** - Extract common functionality
4. **Never create technical debt** - Build for the long term
5. **Design for millions of developers** - Think at scale

## Python Style Guide

### PEP 8 Compliance

We follow PEP 8 with some modifications:

```python
# Good
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n < 2:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)

# Bad
def calcFib(n):
    if n<2:return n
    return calcFib(n-1)+calcFib(n-2)
```

### Type Annotations

All functions must have type annotations:

```python
# Good
def process_data(data: List[str]) -> Dict[str, int]:
    """Process data and return statistics."""
    result = {}
    for item in data:
        result[item] = len(item)
    return result

# Bad
def process_data(data):
    result = {}
    for item in data:
        result[item] = len(item)
    return result
```

### Docstrings

All functions, classes, and modules must have docstrings:

```python
# Good
class Lexer:
    """Lexical analyzer for the I programming language.
    
    This class converts source code into a stream of tokens.
    """
    
    def __init__(self, source: str):
        """Initialize the lexer with source code.
        
        Args:
            source: The source code to tokenize
            
        Raises:
            LexerError: If the source contains invalid characters
        """
        self.source = source
        self.position = 0

# Bad
class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
```

### Import Style

Organize imports in this order:

1. Standard library imports
2. Third-party imports
3. Local imports

```python
# Good
import os
import sys
from typing import List, Dict, Optional

import pytest
from requests import get

from compiler.lexer import Lexer
from compiler.parser import Parser

# Bad
from compiler.lexer import Lexer
import os
from typing import List
import pytest
```

### Line Length

Maximum line length: 100 characters

```python
# Good
def process_very_long_function_name(
    parameter_one: str,
    parameter_two: int,
    parameter_three: bool
) -> Optional[str]:
    """Process parameters."""
    pass

# Bad
def process_very_long_function_name(parameter_one: str, parameter_two: int, parameter_three: bool) -> Optional[str]:
    pass
```

### Class Organization

```python
# Good
class MyClass:
    """Class description."""
    
    # Class variables
    CLASS_VAR: str = "value"
    
    def __init__(self, value: str):
        """Initialize instance."""
        self.instance_var = value
    
    # Public methods
    def public_method(self) -> None:
        """Public method."""
        pass
    
    # Protected methods
    def _protected_method(self) -> None:
        """Protected method."""
        pass
    
    # Private methods
    def __private_method(self) -> None:
        """Private method."""
        pass
    
    # Special methods
    def __str__(self) -> str:
        """String representation."""
        return self.instance_var
```

## I Language Style Guide

### Naming Conventions

Use Kinyarwanda words for I language code:

```i
# Good
shyira umuntu = "Jean"
shyira imyaka = 25
umurimo sagura(a: int, b: int) -> int
    subira a + b
iherezo

# Bad
let person = "Jean"
let age = 25
function add(a: int, b: int) -> int
    return a + b
end
```

### Block Structure

Every block ends with `iherezo`:

```i
# Good
niba a irenze 5
    andika a
iherezo

# Bad
if a > 5
    print a
```

### Indentation

Use 4 spaces for indentation:

```i
# Good
umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo

# Bad
umurimo fibonacci(n: int) -> int
niba n munsi_ya 2
subira n
iherezo
subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo
```

### Comments

Use `#` for comments:

```i
# Calculate Fibonacci number
umurimo fibonacci(n: int) -> int
    niba n munsi_ya 2  # Base case
        subira n
    iherezo
    subira fibonacci(n - 1) + fibonacci(n - 2)
iherezo
```

### Function Definitions

```i
# Good
umurimo function_name(param1: type, param2: type) -> return_type
    # Implementation
    subira result
iherezo

# Bad
function function_name(param1, param2) {
    return result
}
```

## Documentation Style

### Docstring Format

Use Google-style docstrings:

```python
def calculate_fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    This function uses a recursive algorithm to calculate
    the Fibonacci number at position n.
    
    Args:
        n: The position in the Fibonacci sequence (must be >= 0)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
        
    Examples:
        >>> calculate_fibonacci(10)
        55
        >>> calculate_fibonacci(0)
        0
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
```

### Documentation Comments

```python
# Good
# Calculate the Fibonacci number using memoization
# to improve performance for large values of n.
def calculate_fibonacci_memoized(n: int, memo: Dict[int, int] = None) -> int:
    """Calculate Fibonacci with memoization."""
    if memo is None:
        memo = {}
    if n in memo:
        return memo[n]
    if n < 2:
        result = n
    else:
        result = calculate_fibonacci_memoized(n - 1, memo) + calculate_fibonacci_memoized(n - 2, memo)
    memo[n] = result
    return result

# Bad
# calc fib
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)
```

## Naming Conventions

### Python Naming

```python
# Variables and functions: snake_case
my_variable = 10
my_function()

# Classes: PascalCase
class MyClass:
    pass

# Constants: UPPER_SNAKE_CASE
MY_CONSTANT = 3.14159

# Private members: prefix with underscore
_private_variable = 10
class MyClass:
    def _private_method(self):
        pass
```

### I Language Naming

```i
# Variables: lowercase with underscores
shyira my_variable = 10

# Functions: lowercase with underscores
umurimo my_function()
    subira result
iherezo

# Constants: uppercase with underscores
shyira_ko MY_CONSTANT = 3.14159

# Types: PascalCase
igiceri MyStruct
    field: int
iherezo
```

## Code Organization

### File Organization

```python
# 1. Imports
import os
import sys
from typing import List, Dict

# 2. Constants
MAX_SIZE = 1000
DEFAULT_TIMEOUT = 30

# 3. Classes
class MyClass:
    pass

# 4. Functions
def my_function():
    pass

# 5. Main execution
if __name__ == "__main__":
    my_function()
```

### Module Organization

```
package/
├── __init__.py
├── module1.py
├── module2.py
└── submodule/
    ├── __init__.py
    └── module3.py
```

## Error Handling

### Exception Handling

```python
# Good
def process_file(filename: str) -> str:
    """Process a file and return its contents."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {filename}")
    except Exception as e:
        raise RuntimeError(f"Error processing file: {e}")

# Bad
def process_file(filename):
    try:
        f = open(filename)
        return f.read()
    except:
        return None
```

### Custom Exceptions

```python
# Good
class LexerError(Exception):
    """Exception raised for lexical errors."""
    
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")

# Bad
class LexerError(Exception):
    pass
```

## Testing Style

### Test Organization

```python
# Good
class TestLexer:
    """Test cases for the Lexer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.lexer = Lexer("")
    
    def test_integer_literals(self):
        """Test integer literal tokenization."""
        tokens = self.lexer.tokenize("42")
        self.assertEqual(tokens[0].type, TokenType.INTEGER)
        self.assertEqual(tokens[0].literal, 42)
    
    def test_float_literals(self):
        """Test float literal tokenization."""
        tokens = self.lexer.tokenize("3.14")
        self.assertEqual(tokens[0].type, TokenType.FLOAT)
        self.assertEqual(tokens[0].literal, 3.14)
```

### Test Naming

```python
# Good
def test_function_name_scenario():
    """Test function_name with specific scenario."""
    pass

# Bad
def test1():
    pass
```

## Git Style

### Commit Messages

Follow conventional commits:

```
type(scope): subject

body

footer
```

Examples:
```
feat(lexer): add support for Unicode identifiers

Add support for Unicode characters in identifiers to better
support Kinyarwanda and other African languages.

Closes #123

fix(parser): handle empty input gracefully

The parser now handles empty input without raising an exception.
Instead, it returns an empty AST.

Fixes #456
```

### Branch Naming

```
feature/feature-name
bugfix/bug-description
hotfix/critical-fix
release/version-number
```

## Security Considerations

### Input Validation

```python
# Good
def process_input(user_input: str) -> str:
    """Process user input safely."""
    if not isinstance(user_input, str):
        raise TypeError("Input must be a string")
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValueError("Input too long")
    # Process input
    return user_input.upper()

# Bad
def process_input(user_input):
    return user_input.upper()
```

### Sensitive Data

```python
# Good
# Never commit sensitive data
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable not set")

# Bad
API_KEY = "secret-key-123"  # Never commit this!
```

## Performance Considerations

### Algorithm Choice

```python
# Good - O(n)
def find_item(items: List[str], target: str) -> bool:
    """Find item using binary search."""
    return target in items

# Bad - O(n²) for repeated lookups
def find_item_slow(items: List[str], target: str) -> bool:
    """Find item using linear search."""
    for item in items:
        if item == target:
            return True
    return False
```

### Memory Efficiency

```python
# Good - Generator
def process_large_file(filename: str):
    """Process large file line by line."""
    with open(filename) as f:
        for line in f:
            yield process_line(line)

# Bad - Loads entire file into memory
def process_large_file_bad(filename: str):
    """Process large file by loading all at once."""
    with open(filename) as f:
        lines = f.readlines()
    for line in lines:
        yield process_line(line)
```

## Accessibility

### Code Comments

```python
# Good - Clear and descriptive
# Calculate the greatest common divisor using Euclid's algorithm
def gcd(a: int, b: int) -> int:
    """Calculate GCD of two numbers."""
    while b:
        a, b = b, a % b
    return a

# Bad - Unclear
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

### Variable Names

```python
# Good - Descriptive names
user_authentication_token = "abc123"
maximum_allowed_connections = 100

# Bad - Cryptic names
uat = "abc123"
mac = 100
```

## Tools and Automation

### Linting

We use the following tools:
- `flake8` - Style guide enforcement
- `pylint` - Code analysis
- `mypy` - Type checking
- `black` - Code formatting

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
