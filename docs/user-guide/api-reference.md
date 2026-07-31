# I API Reference

This reference documents the public APIs of the I toolchain for host (Python)
integration. Version **1.0.0**.

## Packages

| Package | Purpose |
| --- | --- |
| `compiler` | lexer, parser, semantic analysis, code generation, CLI logic |
| `vm` | virtual machine (IVM classes) |
| `stdlib` | 44 standard-library modules for host integrations |
| `isoko` | package manager: manifest, registry, semver |
| `istudio`, `uam`, `ufa` | editor engine, build config, source utilities |

## `compiler` — Compiler API

Exports: `Lexer`, `LexerError`, `tokenize`, `Token`, `TokenType`, `Parser`,
`ParseError`, `parse`, `SemanticAnalyzer`, `SemanticErrorCollection`, `analyze`,
`CodeGenerator`, `generate`, `OpCode`, `Chunk`, `Compiler`, `__version__`.

### High-level compiler

```python
from compiler.compiler import Compiler

compiler = Compiler(verbose=False)

chunk = compiler.compile_file("hello.i")      # CompilerError on failure
chunk = compiler.compile_source('andika "hi"')
result = compiler.run_file("hello.i")          # compile + run
result = compiler.run_source('andika "hi"')    # compile + run from source
result = compiler.run_chunk(chunk)             # run compiled bytecode
asm = compiler.disassemble(chunk)              # disassembly string
```

`CompilerError` is raised for parse, semantic, and codegen failures. `vm.virtual_machine.RuntimeError`
is raised for runtime failures.

### Pipeline stages

Each stage can be used independently:

```python
from compiler.lexer import tokenize, LexerError
from compiler.parser import parse, ParseError
from compiler.semantic import analyze, SemanticErrorCollection
from compiler.codegen import generate, Chunk

tokens = tokenize('andika "Muraho"')      # list[Token]
ast = parse(tokens)                        # Program; ParseError on failure
analyze(ast)                               # SemanticErrorCollection if errors
chunk: Chunk = generate(ast)               # bytecode chunk
```

### Token types

```python
from compiler.lexer import TokenType, Token

tok: Token          # .lexeme, .type, .line, .column
types = list(TokenType)
```

Keywords include `niba`, `cyangwa`, `cyangwa_niba`, `wihuse`, `kugeza`, `kuri`,
`muri`, `buri`, `shyira`, `shyira_ko`, `umurimo`, `subira`, `gukoma`, `kugenda`,
`andika`, `iherezo`, `igiceri`, `ikindi`, `urwego`, `akabuto`, `urubingo`,
`shyiramo`, `kandi`, `si`, `gushyingura`, `kubika`, `ikinyoma`, plus English literals
`true`, `false`, `null`.

### Bytecode

```python
from compiler.codegen import OpCode, Chunk

chunk.code       # list[Instruction]
Instruction.opcode  # OpCode
Instruction.arg     # argument (or None)
```

## `vm` — Virtual Machine API

Exports: `VMConfig`, `VMContext`, `VMInstance`.

```python
from vm import VMConfig, VMContext, VMInstance

config = VMConfig()
context = VMContext(config)
vm = VMInstance(context)
```

The convenience helpers in `stdlib.vm` wrap this for common use:

```python
import stdlib.vm as v

v.run_source('andika "Muraho"')   # compile and run source text
v.run_bytecode(chunk)             # run an existing compiled chunk
vm = v.create_vm()                # return a VM instance
v.format_report(stats)            # format profiling/statistics
v.version                         # "1.0.0"
```

## `stdlib` — Standard Library

The 44 modules and their functions are documented in the
[Standard Library Reference](stdlib-reference.md). Highlights:

```python
import stdlib.json as j, stdlib.text as t, stdlib.crypto as c

j.dumps({"ok": True})
t.to_upper("muraho")
c.hash_sha256(b"data")
```

## `isoko` — Package Manager API

```python
from isoko.manifest import Manifest

m = Manifest()
m.name = "my-project"
m.version = "0.1.0"
m.save("ilang.toml")
```

```python
from isoko.semver import version_satisfies  # compare semver ranges
from isoko.registry import ...              # registry client
```

## Errors and Exit Codes

| Layer | Error type | Notes |
| --- | --- | --- |
| Lexer | `LexerError` | invalid characters, unterminated strings |
| Parser | `ParseError` | raises `PARS###` diagnostics |
| Semantic | `SemanticErrorCollection` | `SEM###` diagnostics |
| Compiler | `CompilerError` | aggregates the above; CLI exit code 1 |
| VM | `vm.virtual_machine.RuntimeError` | runtime failures; CLI prints `Runtime Error:` |

See the [Error Reference](error-reference.md) for code tables.
