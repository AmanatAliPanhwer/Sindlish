# Sindlish Developer Documentation

Comprehensive internal documentation for the Sindlish programming language interpreter. This documentation covers the full architecture, every subsystem, and is intended for contributors and developers working on the Sindlish codebase.

## Overview

Sindlish is a high-level, bytecode-compiled programming language written in Romanized Sindhi. The interpreter is implemented in Python and follows a classic 5-stage pipeline:

```
Source Code --> Lexer --> Parser --> Resolver --> Compiler --> VM
               (tokens)  (AST)    (slots)     (bytecode)  (execute)
```

## Documentation Index

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Master architecture overview, pipeline diagrams, module structure |
| [FRONTEND.md](FRONTEND.md) | Lexer, token types, parser, AST node reference |
| [ANALYSIS.md](ANALYSIS.md) | Resolver: name resolution, slot allocation, type checking |
| [BACKEND.md](BACKEND.md) | Compiler, opcodes, virtual machine, execution model |
| [OBJECT_MODEL.md](OBJECT_MODEL.md) | SdType/SdShey base classes, MRO, protocol dispatch |
| [OBJECTS.md](OBJECTS.md) | All concrete types: SdNumber, SdString, SdList, etc. |
| [RUNTIME.md](RUNTIME.md) | Environment, builtins, REPL implementation |
| [ERRORS.md](ERRORS.md) | Error hierarchy, Result system, error reporting |
| [TESTING.md](TESTING.md) | Test suite structure, helpers, patterns |
| [EXTENSION.md](EXTENSION.md) | VS Code extension, LSP server, syntax highlighting |
| [DISTRIBUTION.md](DISTRIBUTION.md) | Build system, CI/CD, platform installers |
| [LANGUAGE_REFERENCE.md](LANGUAGE_REFERENCE.md) | Sindlish keyword mapping, syntax reference |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to add features, code conventions |

## Quick Start

### Run the interpreter

```bash
# Interactive REPL
python main.py

# Execute a file
python main.py run script.sd

# View tokens
python main.py tokens script.sd

# View AST
python main.py ast script.sd

# Check syntax
python main.py check script.sd

# Offline docs
python main.py docs
```

### Run tests

```bash
uv run pytest
```

### Run benchmarks

```bash
python bench/run_benchmarks.py
```

## Project Statistics

| Metric | Value |
|--------|-------|
| Total source files | 17 Python files |
| Total lines (interpreter) | ~3,500 |
| AST node classes | 36 |
| Opcodes | 37 |
| Sindlish keywords | 28 |
| Token types | 60 |
| Object types | 10 |
| Built-in functions | 5 |
| Collection methods | 35 |
| Test files | 23 |
| Test cases | 236+ |

## Directory Structure

```
Sindlish/
├── main.py                    # CLI entry point
├── pyproject.toml             # Project config
├── interpreter/               # Core interpreter package
│   ├── __init__.py            # Interpreter facade
│   ├── errors.py              # Error types & reporting
│   ├── repl.py                # Interactive REPL
│   ├── frontend/              # Lexer + Parser + AST
│   │   ├── tokens.py          # TokenType enum (60 members)
│   │   ├── keywords.py        # Sindhi keyword mappings
│   │   ├── lexer.py           # Character-by-character scanner
│   │   ├── ast_nodes.py       # 36 AST node classes
│   │   └── parser.py          # Recursive descent parser
│   ├── analysis/              # Semantic analysis
│   │   └── resolver.py        # Name resolution & type checking
│   ├── backend/               # Compilation & execution
│   │   ├── opcodes.py         # Bytecode opcodes + OPERAND_SHAPES encoding
│   │   ├── compiler.py        # AST to bytecode compiler
│   │   ├── frame.py           # Execution frame
│   │   └── vm.py              # Stack-based virtual machine
│   ├── objects/               # Object model
│   │   ├── base.py            # SdType & SdShey base classes
│   │   ├── numbers.py         # SdNumber, SdBool
│   │   ├── strings.py         # SdString
│   │   ├── collections.py     # SdList, SdDict, SdSet
│   │   └── core.py            # SdResult, SdFunction, SdNull
│   └── runtime/               # Runtime support
│       ├── env.py             # Environment (symbol table)
│       └── builtins.py        # 5 built-in functions
├── tests/                     # Test suite (23 files)
├── tools/                     # Developer tools
├── bench/                     # Cross-language benchmarks
├── vscode-extension/          # VS Code extension + LSP
└── developer-docs/            # This documentation
```
