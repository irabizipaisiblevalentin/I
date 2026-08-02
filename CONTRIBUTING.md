# Contributing to I Programming Language

Thank you for your interest in contributing to the I Programming Language. This document provides comprehensive guidelines for contributing to the project.

## Table of Contents

- [Our Philosophy](#our-philosophy)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Engineering Standards](#engineering-standards)
- [Code Quality](#code-quality)
- [Testing Requirements](#testing-requirements)
- [Documentation Requirements](#documentation-requirements)
- [Contribution Workflow](#contribution-workflow)
- [Language Design Considerations](#language-design-considerations)
- [Areas of Contribution](#areas-of-contribution)
- [Communication Guidelines](#communication-guidelines)
- [Recognition](#recognition)

## Our Philosophy

The I Programming Language is being built to last for decades. Every contribution must prioritize:

- **Maintainability** - Code should be easy to understand and modify
- **Performance** - Efficient execution and resource usage
- **Correctness** - Bug-free and reliable behavior
- **Testing** - Comprehensive test coverage
- **Documentation** - Clear and complete documentation
- **Scalability** - Design for growth and evolution
- **Long-term evolution** - Future-proof architecture

## Getting Started

### Development Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/irabizipaisiblevalentin/I.git
   cd I
   ```

2. **Install dependencies**
   ```bash
   python -m pip install -e .
   python -m pip install -r requirements-dev.txt
   ```

3. **Run the test suite**
   ```bash
   python -m pytest tests/
   ```

4. **Set up pre-commit hooks**
   ```bash
   python -m pre-commit install
   ```

5. **Read the documentation**
   - [Language Specification](docs/specification/LANGUAGE_SPECIFICATION.md)
   - [Architecture](ARCHITECTURE.md)
   - [Style Guide](STYLE_GUIDE.md)

### First Contribution

Look for issues labeled "good first issue" or start with:
- Documentation improvements
- Test enhancements
- Small bug fixes
- Example programs

## Development Process

We follow a strict development process. Never skip steps:

1. **Design** - Think through the solution before coding
2. **Review** - Discuss the design with the team
3. **Document** - Write documentation before implementation
4. **Implement** - Write the code
5. **Test** - Create comprehensive tests
6. **Refactor** - Improve the code quality
7. **Optimize** - Optimize performance only after correctness is ensured

## Engineering Standards

Every feature must include:

- **Implementation** - Clean, well-structured code
- **Tests** - Automated tests with high coverage
- **Documentation** - API documentation and user guides
- **Examples** - Working examples demonstrating usage
- **Benchmarks** - Performance measurements when relevant
- **Git Commit Message** - Clear, descriptive commit messages
- **Release Notes** - Documentation of changes for users

## Code Quality

### General Principles

- Follow existing code style in the project (see [STYLE_GUIDE.md](STYLE_GUIDE.md))
- Use descriptive variable and function names
- Write self-documenting code
- Keep functions focused and small
- Add comments only when necessary to explain complex logic
- Avoid code duplication
- Prefer composition over inheritance
- Follow SOLID principles

### Error Handling

- Compiler errors must be friendly and helpful
- Never expose internal exceptions to end users
- Error messages should support both Kinyarwanda and English
- Provide clear guidance on how to fix errors
- Include source location in error messages
- Suggest fixes when possible

### Performance Considerations

- Profile before optimizing
- Optimize hot paths first
- Consider memory vs. speed trade-offs
- Document performance characteristics
- Add benchmarks for performance-critical code

## Testing Requirements

### Mandatory Testing

- Every module must have automated tests
- Regression tests are mandatory for bug fixes
- Unit tests for individual components
- Integration tests for component interactions
- End-to-end tests for complete workflows

### Test Coverage

- Aim for high test coverage (90%+)
- Test edge cases and error conditions
- Test both success and failure paths
- Include performance tests for critical paths
- Use property-based testing where appropriate

### Test Organization

```
tests/
â”œâ”€â”€ unit/              # Unit tests for individual components
â”œâ”€â”€ integration/       # Integration tests for component interactions
â”œâ”€â”€ regression/        # Regression tests for known bugs
â”œâ”€â”€ performance/       # Performance benchmarks
â”œâ”€â”€ fuzzing/          # Fuzzing tests for robustness
â””â”€â”€ property/         # Property-based tests
```

## Documentation Requirements

### Every Public API Requires

- Clear description of purpose
- Parameter documentation
- Return value documentation
- Error conditions
- Usage examples
- Performance characteristics
- Thread safety notes (if applicable)

### Language Features

Every language feature must have:
- Syntax documentation
- Semantics explanation
- Type system implications
- Example programs
- Common use cases
- Edge case behavior

### Documentation Standards

- Use clear, concise language
- Provide code examples for all APIs
- Include both Kinyarwanda and English where appropriate
- Keep documentation up to date with code changes
- Use consistent formatting

## Contribution Workflow

### For New Contributors

1. Read this document thoroughly
2. Read the language specification
3. Set up the development environment
4. Start with small, well-defined tasks
5. Ask questions when uncertain

### For Experienced Contributors

1. Check existing issues and pull requests
2. Discuss major changes before implementation
3. Follow the development process strictly
4. Ensure all requirements are met
5. Request code review before merging

### Pull Request Process

1. **Create a branch** for your work
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the feature** with all requirements
   - Write clean, well-documented code
   - Add comprehensive tests
   - Update documentation
   - Add examples if applicable

3. **Ensure all tests pass**
   ```bash
   python -m pytest tests/
   python -m pre-commit run --all-files
   ```

4. **Submit a pull request** with clear description
   - Describe the change
   - Explain the motivation
   - Link to related issues
   - Add screenshots if applicable

5. **Address review feedback**
   - Respond to all comments
   - Make requested changes
   - Update tests and documentation

6. **Obtain approval** before merging

### Commit Message Guidelines

Follow conventional commits format:

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Example:
```
feat(lexer): add support for Unicode identifiers

Add support for Unicode characters in identifiers to better
support Kinyarwanda and other African languages.

Closes #123
```

## Language Design Considerations

When proposing language changes, consider:

- **Readability** - Does it make code more readable?
- **Naturalness** - Does it feel natural in Kinyarwanda?
- **Simplicity** - Is it simple to understand and use?
- **Consistency** - Is it consistent with existing features?
- **Power** - Does it add meaningful capability?
- **Performance** - What are the performance implications?
- **Safety** - Does it maintain or improve safety?
- **Modernity** - Is it aligned with modern best practices?
- **Professionalism** - Is it suitable for professional development?
- **Self-hosting** - Can it be implemented in I itself?

## Areas of Contribution

We welcome contributions in many areas:

### Compiler
- Lexer improvements
- Parser enhancements
- AST optimizations
- Semantic analysis
- Code generation
- Native compilation

### Runtime
- Virtual Machine
- Garbage collection
- Memory management
- Concurrency primitives

### Standard Library
- Core data structures
- I/O operations
- Networking
- File system
- Math and science

### Frameworks
- urubuga (web)
- ibiro (desktop)
- mobile (Android/iOS)
- ububiko (database)
- ubwenge (AI)
- imikino (games)
- sisitemu (systems)
- igicu (cloud)
- robot (robotics)
- amakuru (networking)

### Tools
- isoko (package manager)
- iformat (formatter)
- idebug (debugger)
- itest (testing)
- idoc (documentation)
- I Studio (IDE)

### Documentation
- Language reference
- Tutorials
- Examples
- Best practices
- Migration guides

## Communication Guidelines

- Be respectful and professional
- Assume good intentions
- Provide constructive feedback
- Listen to different perspectives
- Focus on what is best for the project
- Use inclusive language
- Be patient with new contributors

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Annual contributor reports

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

For questions about contributing:
- Open an issue with the "question" label
- Join our community discussions
- Read existing documentation

---

Thank you for contributing to the I Programming Language. Together, we're building a language that will serve millions of developers for decades to come.
