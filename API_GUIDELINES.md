# API Guidelines

This document provides guidelines for designing and implementing APIs in the I Programming Language.

## Table of Contents

- [API Design Principles](#api-design-principles)
- [Naming Conventions](#naming-conventions)
- [Function Design](#function-design)
- [Type Design](#type-design)
- [Error Handling](#error-handling)
- [Documentation](#documentation)
- [Versioning](#versioning)
- [Deprecation](#deprecation)
- [Security](#security)
- [Performance](#performance)

## API Design Principles

### Core Principles

1. **Clarity**: APIs should be self-documenting and intuitive
2. **Consistency**: Follow consistent patterns across all APIs
3. **Simplicity**: Keep APIs simple and focused
4. **Extensibility**: Design for future extension
5. **Stability**: Maintain backward compatibility
6. **Safety**: Default to safe behavior

### User-Centric Design

- Design for the common use case
- Make common operations easy
- Make uncommon operations possible
- Provide sensible defaults
- Minimize required configuration

## Naming Conventions

### Function Names

Use descriptive, action-oriented names:

```i
# Good
umurimo calculate_fibonacci(n: int) -> int
umurimo read_file(path: string) -> string
umurimo connect_to_database(url: string) -> Connection

# Bad
umurimo calc(n: int) -> int
umurimo read(path: string) -> string
umurimo connect(url: string) -> Connection
```

### Type Names

Use descriptive, noun-based names:

```i
# Good
igiceri UserAccount
igiceri DatabaseConnection
ikindi HttpError

# Bad
igiceri UA
igiceri DBConn
ikindi Err
```

### Parameter Names

Use descriptive parameter names:

```i
# Good
umurimo connect_to_database(host: string, port: int, timeout: int) -> Connection

# Bad
umurimo connect(h: string, p: int, t: int) -> Connection
```

## Function Design

### Function Signature

Keep function signatures focused:

```i
# Good
umurimo calculate_fibonacci(n: int) -> int
    """Calculate the nth Fibonacci number."""
    # implementation
iherezo

# Bad
umurimo calculate(n: int, verbose: bool, debug: bool, cache: bool) -> int
    """Calculate with many options."""
    # implementation
iherezo
```

### Parameter Order

Follow consistent parameter ordering:

1. Required parameters
2. Optional parameters
3. Keyword parameters

```i
# Good
umurimo process_data(data: list, options: ProcessOptions = nil) -> Result

# Bad
umurimo process_data(options: ProcessOptions = nil, data: list) -> Result
```

### Return Values

Return meaningful values:

```i
# Good
umurimo divide(a: int, b: int) -> int
    niba b == 0
        gushyingura ValueError("Division by zero")
    iherezo
    subira a / b
iherezo

# Bad
umurimo divide(a: int, b: int) -> int
    subira a / b  # May throw division by zero
iherezo
```

## Type Design

### Struct Design

Keep structs focused:

```i
# Good
igiceri User
    izina: string
    email: string
    imyaka: int
iherezo

# Bad
igiceri User
    izina: string
    email: string
    imyaka: int
    address: string
    phone: string
    preferences: Preferences
    history: History
    # ... too many fields
iherezo
```

### Interface Design

Define clear contracts:

```i
# Good
akabuto Drawable
    umurimo draw() -> void
    umurimo get_bounds() -> Rectangle
iherezo

# Bad
akabuto Drawable
    umurimo draw()
    umurimo get_bounds()
    umurimo set_color()
    umurimo get_color()
    # ... too many methods
iherezo
```

### Enum Design

Use enums for fixed sets of values:

```i
# Good
ikindi Color
    Umutuku
    Ubururu
    Ibara
    Umutuku
iherezo

# Bad
shyira RED = 1
shyira BLUE = 2
shyira GREEN = 3
```

## Error Handling

### Error Types

Define specific error types:

```i
# Good
ikindi FileNotFoundError kugira Error
ikindi PermissionError kugira Error
ikindi ParseError kugira Error

# Bad
gushyingura Error("File not found")
gushyingura Error("Permission denied")
gushyingura Error("Parse error")
```

### Error Messages

Provide clear error messages:

```i
# Good
gushyingura FileNotFoundError(f"File not found: {path}")

# Bad
gushyingura Error("Error")
```

### Error Recovery

Provide ways to recover from errors:

```i
# Good
umurimo read_file(path: string) -> string
    kora
        subira file_contents
    kubika FileNotFoundError
        gushyingura FileNotFoundError(f"File not found: {path}")
    iherezo
iherezo

# Bad
umurimo read_file(path: string) -> string
    subira file_contents  # May throw without context
iherezo
```

## Documentation

### Function Documentation

Document all public APIs:

```i
umurimo calculate_fibonacci(n: int) -> int
    """Calculate the nth Fibonacci number.
    
    This function uses an iterative algorithm for efficiency.
    For large values of n, consider using the memoized version.
    
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
    # implementation
iherezo
```

### Type Documentation

Document all public types:

```i
igiceri UserAccount
    """Represents a user account in the system.
    
    Attributes:
        username: The unique username for the account
        email: The email address associated with the account
        created_at: The timestamp when the account was created
    """
    username: string
    email: string
    created_at: int
iherezo
```

### Module Documentation

Document all public modules:

```i
"""
Math utilities for the I programming language.

This module provides common mathematical operations and functions.
All functions are optimized for performance and accuracy.
"""
```

## Versioning

### Semantic Versioning

Follow semantic versioning for APIs:

- **MAJOR**: Breaking changes
- **MINOR**: Backward-compatible additions
- **PATCH**: Backward-compatible bug fixes

### Backward Compatibility

Maintain backward compatibility:

```i
# Good - Add new parameter with default
umurimo process_data(data: list, options: ProcessOptions = nil) -> Result

# Bad - Change parameter order
umurimo process_data(options: ProcessOptions, data: list) -> Result
```

### Deprecation Process

Mark deprecated APIs:

```i
# Deprecated
@deprecated("Use new_function instead")
umurimo old_function(data: list) -> Result
    """Deprecated: Use new_function instead."""
    subira new_function(data)
iherezo
```

## Deprecation

### Deprecation Timeline

- **Announce**: Announce deprecation in release notes
- **Document**: Document deprecation in API docs
- **Warn**: Emit warnings when deprecated API is used
- **Remove**: Remove after 2 major versions

### Deprecation Warning

```i
@deprecated("Use new_function instead (will be removed in v2.0)")
umurimo old_function(data: list) -> Result
    """Deprecated: Use new_function instead."""
    # Emit warning
    andika "Warning: old_function is deprecated, use new_function instead"
    subira new_function(data)
iherezo
```

## Security

### Input Validation

Validate all inputs:

```i
# Good
umurimo process_user_input(input: string) -> string
    niba len(input) > MAX_INPUT_LENGTH
        gushyingura ValueError("Input too long")
    niba not is_valid_input(input)
        gushyingura ValueError("Invalid input")
    subira sanitize(input)
iherezo

# Bad
umurimo process_user_input(input: string) -> string
    subira input  # No validation
iherezo
```

### Output Sanitization

Sanitize all outputs:

```i
# Good
umurimo render_template(template: string, data: map) -> string
    shyira sanitized_data = sanitize_data(data)
    subira render(template, sanitized_data)
iherezo

# Bad
umurimo render_template(template: string, data: map) -> string
    subira render(template, data)  # No sanitization
iherezo
```

### Secure Defaults

Use secure defaults:

```i
# Good
umurimo connect_to_server(url: string, secure: bool = yego) -> Connection

# Bad
umurimo connect_to_server(url: string, secure: bool = oya) -> Connection
```

## Performance

### Efficiency

Design efficient APIs:

```i
# Good - Use generator for large data
umurimo process_large_file(path: string) -> Generator<string>
    kora
        with open(path) kugira file
            buri line muri file
                kuhindura process_line(line)
    iherezo
iherezo

# Bad - Load entire file into memory
umurimo process_large_file(path: string) -> list<string>
    with open(path) kugira file
        subira file.readlines()
iherezo
```

### Caching

Cache expensive operations:

```i
# Good
umurimo calculate_expensive_result(input: string) -> int
    niba input muri cache
        subira cache[input]
    iherezo
    shyira result = perform_calculation(input)
    cache[input] = result
    subira result
iherezo
```

### Lazy Evaluation

Use lazy evaluation where appropriate:

```i
# Good
igiceri LazyValue
    value: int
    calculated: bool = oya
    
    umurimo get() -> int
        niba not self.calculated
            self.value = calculate_value()
            self.calculated = yego
        iherezo
        subira self.value
    iherezo
iherezo
```

## Best Practices

### API Consistency

Maintain consistency across APIs:

```i
# Good - Consistent naming
umurimo open_file(path: string) -> File
umurimo open_connection(url: string) -> Connection
umurimo open_stream(source: string) -> Stream

# Bad - Inconsistent naming
umurimo open_file(path: string) -> File
umurimo create_connection(url: string) -> Connection
umurimo get_stream(source: string) -> Stream
```

### API Composition

Design APIs that compose well:

```i
# Good - Composable APIs
umurimo map(data: list, func: Function) -> list
umurimo filter(data: list, predicate: Function) -> list
umurimo reduce(data: list, func: Function, initial: int) -> int

# Usage
result = reduce(filter(map(data, square), is_even), add, 0)
```

### API Testing

Test all public APIs:

```python
def test_api_function():
    """Test the API function."""
    # Test normal case
    result = api_function(valid_input)
    assert result == expected_result
    
    # Test edge cases
    result = api_function(edge_case_input)
    assert result == expected_edge_result
    
    # Test error cases
    with pytest.raises(ValueError):
        api_function(invalid_input)
```

## Review Checklist

Before releasing an API, review:

- [ ] Naming is clear and consistent
- [ ] Parameters are well-ordered
- [ ] Return values are meaningful
- [ ] Error handling is comprehensive
- [ ] Documentation is complete
- [ ] Examples are provided
- [ ] Security is considered
- [ ] Performance is acceptable
- [ ] Tests are comprehensive
- [ ] Backward compatibility is maintained

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
