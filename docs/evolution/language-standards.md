# Language Standards

This document defines the official standards for the I Programming Language ecosystem.

## Table of Contents

- [Overview](#overview)
- [Coding Conventions](#coding-conventions)
- [Documentation Conventions](#documentation-conventions)
- [Framework Conventions](#framework-conventions)
- [Testing Standards](#testing-standards)
- [Performance Standards](#performance-standards)
- [Security Standards](#security-standards)
- [Accessibility Standards](#accessibility-standards)

---

## Overview

### Purpose

These standards ensure:
1. Consistency across the ecosystem
2. Quality and reliability
3. Accessibility and usability
4. Security and safety
5. Professional appearance

### Standard Categories

| Category | Scope | Enforced By |
|----------|-------|-------------|
| Coding | Source code | Formatter, linter |
| Documentation | Docs, comments | Documentation tool |
| Framework | Official frameworks | Framework teams |
| Testing | Test code | Test runner |
| Performance | All code | Benchmarking tools |
| Security | All code | Security tools |
| Accessibility | UI, docs | Accessibility tools |

---

## Coding Conventions

### File Structure

```
# Standard file structure
1. Module declaration
2. Imports
3. Constants
4. Types
5. Functions
6. Main entry point
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Variables | snake_case | `user_name` |
| Functions | snake_case | `get_user_name` |
| Types | PascalCase | `UserName` |
| Constants | UPPER_SNAKE_CASE | `MAX_LENGTH` |
| Keywords | Kinyarwanda lowercase | `niba`, `cyangwa` |
| English aliases | English lowercase | `if`, `else` |

### Code Style

```
# Indentation
- 4 spaces
- No tabs

# Line length
- Maximum 100 characters

# Braces
- Opening brace on same line
- Closing brace on new line

# Blank lines
- 2 blank lines between functions
- 1 blank line between logical sections

# Comments
- Use sparingly
- Explain why, not what
- Use doc comments for public APIs
```

### Example Code

```
shyiramo urubuga

# Module documentation
## User management module
##
## This module provides functions for managing users.

# Constants
gusangiza MAX_USERS = 10000
gusangiza DEFAULT_ROLE = "user"

# Types
igiceri User:
    id: int
    name: string
    email: string
    role: string = DEFAULT_ROLE
iherezo

# Functions
umurimo create_user(name: string, email: string) -> Result<User, Error>:
    niba name.is_empty():
        subira Err(Error("Name is required"))
    
    niba email.is_empty():
        subira Err(Error("Email is required"))
    
    shyira user = User(
        id = generate_id(),
        name = name,
        email = email
    )
    
    subira Ok(user)
iherezo

# Main function
umurimo main() -> void:
    shyira result = create_user("John", "john@example.com")
    
    niba result.is_ok():
        print("User created: " + result.unwrap().name)
    cyangwa:
        print("Error: " + result.unwrap_err().message)
    iherezo
iherezo
```

### Import Conventions

```
# Import order
1. Standard library
2. Third-party packages
3. Local modules

# Example
shyiramo core
shyiramo io
shyiramo math

shyiramo urubuga
shyiramo ilang_database

shyiramo ./models
shyiramo ./utils
```

---

## Documentation Conventions

### Documentation Types

| Type | Location | Purpose |
|------|----------|---------|
| Module docs | Top of file | Module overview |
| Function docs | Above function | API documentation |
| Type docs | Above type | Type documentation |
| Inline comments | In code | Explain complex logic |
| README | Project root | Project overview |

### Documentation Format

```
# Module documentation
## Module Name
##
## Brief description of the module.
##
## ## Features
## - Feature 1
## - Feature 2
##
## ## Usage
## ```
## shyiramo module_name
## ```
```

### Function Documentation

```
# Function documentation
## Function name
##
## Brief description of the function.
##
## ## Parameters
## - `param1`: Description of param1
## - `param2`: Description of param2
##
## ## Returns
## Description of return value
##
## ## Errors
## Description of possible errors
##
## ## Examples
## ```
## result = function_name(arg1, arg2)
## ```
```

### Type Documentation

```
# Type documentation
## Type name
##
## Brief description of the type.
##
## ## Fields
## - `field1`: Description of field1
## - `field2`: Description of field2
##
## ## Methods
## - `method1()`: Description of method1
##
## ## Examples
## ```
## instance = TypeName(field1 = value1, field2 = value2)
## ```
```

### Documentation Standards

| Requirement | Description |
|-------------|-------------|
| Language | English + Kinyarwanda |
| Completeness | All public APIs documented |
| Accuracy | Documentation matches code |
| Examples | Real, runnable examples |
| Updates | Documentation updated with code |

---

## Framework Conventions

### Framework Structure

```
framework/
├── src/
│   ├── core/
│   ├── features/
│   └── utils/
├── tests/
├── docs/
├── examples/
├── ilang.toml
└── README.md
```

### API Design

1. **Consistent Naming**
   - Use Kinyarwanda for main APIs
   - Provide English aliases
   - Follow naming conventions

2. **Builder Pattern**
   ```i
   igiceri App
       __init__(name: string)
       
       option(self, key: string, value: Any) -> Self
       
       build(self) -> Result<App, Error>
   iherezo
   ```

3. **Error Handling**
   ```i
   # Return Result types
   umurimo function() -> Result<T, Error>:
       niba error_condition:
           subira Err(Error("message"))
       subira Ok(value)
   iherezo
   ```

4. **Async Operations**
   ```i
   # Async by default for I/O
   async umurimo fetch_data() -> Result<Data>:
       shyira response = await http.get(url)
       subira json.decode(response.body)
   iherezo
   ```

### Framework Testing

1. **Unit Tests**
   - 100% coverage for core functions
   - Test all edge cases
   - Test error conditions

2. **Integration Tests**
   - Test framework interactions
   - Test real-world scenarios
   - Test performance

3. **Example Tests**
   - Test all examples
   - Ensure examples work
   - Update examples with changes

---

## Testing Standards

### Test Organization

```
tests/
├── unit/           # Unit tests
│   ├── test_core.i
│   └── test_utils.i
├── integration/    # Integration tests
│   ├── test_api.i
│   └── test_database.i
├── performance/    # Performance tests
│   ├── bench_core.i
│   └── bench_api.i
└── fixtures/       # Test data
    └── ...
```

### Test Naming

```
# Test file naming
test_<module>.i

# Test function naming
test_<function_name>_<scenario>

# Example
test_create_user_valid_input
test_create_user_empty_name
test_create_user_invalid_email
```

### Test Structure

```
igiceri UserTest(itest.TestSuite)
    setup(self) -> void
        self.db = create_test_database()
    iherezo
    
    teardown(self) -> void
        self.db.cleanup()
    iherezo
    
    test_create_user_valid(self) -> void
        shyira user = create_user("John", "john@example.com")
        itest.assert_true(user.is_ok())
        itest.assert_equal(user.unwrap().name, "John")
    iherezo
    
    test_create_user_empty_name(self) -> void
        shyira user = create_user("", "john@example.com")
        itest.assert_true(user.is_err())
    iherezo
iherezo
```

### Test Coverage

| Component | Minimum Coverage |
|-----------|------------------|
| Core functions | 100% |
| Public APIs | 100% |
| Framework features | 90% |
| Standard library | 95% |
| Total | 90% |

### Test Requirements

| Requirement | Description |
|-------------|-------------|
| Isolation | Tests must be isolated |
| Reproducibility | Tests must be reproducible |
| Speed | Tests must be fast |
| Clarity | Tests must be readable |
| Coverage | Tests must meet coverage targets |

---

## Performance Standards

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Compile speed | > 10,000 LOC/s | Developer experience |
| Runtime speed | Within 20% of C | Competitive performance |
| Memory usage | Within 2x of C | Resource efficiency |
| Binary size | Within 3x of C | Distribution size |
| Startup time | < 100ms | User experience |

### Benchmarking

```
# Benchmark file structure
benchmarks/
├── bench_core.i
├── bench_algorithm.i
├── bench_io.i
└── bench_memory.i
```

### Benchmark Requirements

| Requirement | Description |
|-------------|-------------|
| Consistency | Run on same hardware |
| Isolation | No interference |
| Warmup | Allow JIT warmup |
| Multiple runs | Average multiple runs |
| Comparison | Compare with baseline |

### Performance Guidelines

1. **Algorithm Choice**
   - Use appropriate data structures
   - Consider time/space trade-offs
   - Profile before optimizing

2. **Memory Management**
   - Minimize allocations
   - Use appropriate data types
   - Avoid memory leaks

3. **Concurrency**
   - Use appropriate concurrency model
   - Minimize synchronization
   - Avoid race conditions

4. **Optimization**
   - Profile first
   - Optimize hot paths
   - Don't premature optimize

---

## Security Standards

### Security Requirements

| Requirement | Description |
|-------------|-------------|
| Input validation | Validate all inputs |
| Output encoding | Encode all outputs |
| Authentication | Secure authentication |
| Authorization | Proper authorization |
| Cryptography | Use approved algorithms |
| Secrets | Never hardcode secrets |
| Dependencies | Audit dependencies |

### Security Guidelines

1. **Input Validation**
   ```
   # Validate all inputs
   umurimo process_input(input: string) -> Result<Data, Error>:
       niba !is_valid(input):
           subira Err(Error("Invalid input"))
       # Process valid input
   iherezo
   ```

2. **Output Encoding**
   ```
   # Encode all outputs
   umurimo display_data(data: string) -> string:
       subira html.encode(data)
   iherezo
   ```

3. **Secret Management**
   ```
   # Never hardcode secrets
   shyira api_key = env.get("API_KEY")
   niba api_key.is_null():
       subira Err(Error("API_KEY not set"))
   iherezo
   ```

### Security Testing

| Test Type | Description | Frequency |
|-----------|-------------|-----------|
| Static analysis | Code analysis | Every commit |
| Dependency audit | Check dependencies | Weekly |
| Penetration testing | External testing | Quarterly |
| Security review | Manual review | Before release |

---

## Accessibility Standards

### Accessibility Requirements

| Requirement | Description |
|-------------|-------------|
| Keyboard navigation | Full keyboard support |
| Screen reader | ARIA labels, semantic HTML |
| Color contrast | WCAG AA contrast ratios |
| Text scaling | Responsive to text size |
| Focus indicators | Visible focus states |
| Alt text | Images have alt text |
| Captions | Videos have captions |
| Transcripts | Audio has transcripts |

### Accessibility Testing

| Tool | Purpose | Frequency |
|------|---------|-----------|
| axe-core | Automated testing | Every build |
| Lighthouse | Performance audit | Weekly |
| WAVE | Evaluation | Monthly |
| Manual testing | Manual audit | Quarterly |

### Accessibility Guidelines

1. **Keyboard Navigation**
   - All interactive elements focusable
   - Logical tab order
   - Skip links provided
   - Keyboard shortcuts documented

2. **Screen Reader Support**
   - Semantic HTML used
   - ARIA labels provided
   - Dynamic content announced
   - Forms properly labeled

3. **Visual Design**
   - Sufficient color contrast
   - Text scalable to 200%
   - Focus indicators visible
   - No information by color alone

4. **Content**
   - Headings properly structured
   - Lists properly marked up
   - Tables properly structured
   - Language specified

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
