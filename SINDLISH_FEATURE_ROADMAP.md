# Sindlish Feature Roadmap

> A comprehensive guide to all current and future features of the Sindlish programming language.

---

## Table of Contents

1. [Legend & Conventions](#legend--conventions)
2. [Data Types & Variables](#1-data-types--variables)
3. [Collection Types](#2-collection-types)
4. [Operators](#3-operators)
5. [Comparison & Logical](#4-comparison--logical)
6. [Control Flow](#5-control-flow)
7. [Functions & Methods](#6-functions--methods)
8. [String Operations](#7-string-operations)
9. [Collection Operations](#8-collection-operations)
10. [Collection Methods](#9-collection-methods)
11. [Input/Output](#10-inputoutput)
12. [Error Handling](#11-error-handling)
13. [Object-Oriented Programming](#12-object-oriented-programming)
14. [Type System](#13-type-system)
15. [Modules & Namespaces](#14-modules--namespaces)
16. [Memory & Concurrency](#15-memory--concurrency)
17. [Advanced Features (Nice-to-Have)](#17-advanced-features-nice-to-have)
18. [Priority Matrix](#18-priority-matrix)

---

## Legend & Conventions

### Status Icons
- ✅ **Supported** - Fully implemented and tested
- ⚠️ **Partial** - Partially implemented, may have limitations
- ❌ **Not Supported** - Not yet implemented
- 🔄 **In Progress** - Currently being developed

### Priority Levels
- **P0 (Critical)** - Must have for basic functionality
- **P1 (High)** - Important for practical use
- **P2 (Medium)** - Nice to have for better developer experience
- **P3 (Low)** - Future enhancement / Nice-to-have

### Dependencies
Some features depend on others. Format: `Depends on: [Feature Name]`

---

## 1. Data Types & Variables

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Integer (adad) | ✅ | `adad x = 10` | P0 | - |
| Float (dahai) | ✅ | `dahai x = 3.14` | P0 | - |
| String (lafz) | ✅ | `lafz s = "hello"` | P0 | - |
| Boolean (faislo) | ✅ | `faislo b = sach` | P0 | - |
| Null (khali) | ✅ | `khali n` | P0 | - |
| Dynamic typing | ✅ | `x = 10; x = "text"` | P0 | - |
| Type keywords | ✅ | `adad`, `lafz`, `dahai`, etc. | P0 | - |
| Type inference | ✅ | `x = 10` | P0 | - |
| Constants (pakko) | ✅ | `pakko lafz X = "hi"` | P0 | - |
| Type annotations | ✅ | `x : adad = 10` | P0 | - |
| BigInt | ❌ | - | P2 | - |
| Decimal | ❌ | - | P2 | - |
| Complex numbers | ❌ | - | P3 | - |
| Currency/Fixed-point | ❌ | - | P3 | - |
| UUID | ❌ | - | P3 | - |
| DateTime | ❌ | - | P2 | - |
| Regex/Pattern | ❌ | - | P2 | - |
| Void type | ❌ | - | P2 | Functions |

### Default Values for Type Keywords
```sindlish
adad a        # defaults to 0
dahai b       # defaults to 0.0  
lafz c        # defaults to ""
faislo e      # defaults to koorh (False)
khali d       # defaults to khali (None)
```

---

## 2. Collection Types

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| List (fehrist) | ✅ | `[1, 2, 3]` | P0 | - |
| Dict (lughat) | ✅ | `{"a": 1}` | P0 | - |
| Set (majmuo) | ✅ | `{1, 2, 3}` | P0 | - |
| Typed List | ✅ | `fehrist[adad]` | P1 | - |
| Typed Dict | ✅ | `lughat[lafz, adad]` | P1 | - |
| Typed Set | ✅ | `majmuo[lafz]` | P1 | - |
| Tuple | ❌ | - | P2 | - |
| Frozen Set | ❌ | - | P3 | - |
| Byte Array | ❌ | - | P3 | - |
| Range | ✅ | `range(5)` | P2 | - |
| Deque | ❌ | - | P3 | - |
| Nested Collections | ✅ | `fehrist[lughat]` | P1 | Typed collections |

### Typed Collection Examples
```sindlish
fehrist[adad] nums = [1, 2, 3]           # List of integers
lughat[lafz, adad] scores = {"Ali": 90}  # Dict: string keys, int values
majmuo[lafz] names = {"Ali", "Sara"}     # Set of strings

# Nested typed collections
fehrist[fehrist] matrix = [[1, 2], [3, 4]]
fehrist[lughat] users = [{"naam": "Ali"}]
lughat[adad, fehrist] groups = {1: [1, 2, 3]}
```

---

## 3. Operators

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Addition (+) | ✅ | `x + y` | P0 | - |
| Subtraction (-) | ✅ | `x - y` | P0 | - |
| Multiplication (*) | ✅ | `x * y` | P0 | - |
| Division (/) | ✅ | `x / y` | P0 | - |
| Modulo (%) | ✅ | `x % y` | P0 | - |
| Exponentiation (^) | ✅ | `x ^ y` | P0 | - |
| Unary Minus | ✅ | `-x` | P0 | - |
| Unary Plus | ✅ | `+x` | P0 | - |
| Floor Division | ❌ | - | P2 | - |
| Augmented Assignment | ❌ | `x += 1` | P1 | - |
| Bitwise AND | ❌ | `x & y` | P2 | - |
| Bitwise OR | ❌ | `x \| y` | P2 | - |
| Bitwise XOR | ❌ | `x ^ y` | P2 | - |
| Bitwise NOT | ❌ | `~x` | P2 | - |
| Left Shift | ❌ | `x << y` | P3 | - |
| Right Shift | ❌ | `x >> y` | P3 | - |
| Ternary/Conditional | ❌ | `x if cond else y` | P1 | - |

### Operator Precedence
```sindlish
# Highest to lowest:
# 1. Parentheses: ( )
# 2. Unary: - + (negate/positive)
# 3. Power: ^
# 4. Mul/Div/Mod: * / %
# 5. Add/Sub: + -
# 6. Comparison: < > <= >=
# 7. Equality: == !=
# 8. Logical NOT: nah/!
# 9. Logical AND: aen
# 10. Logical OR: ya
```

---

## 4. Comparison & Logical

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Equal (==) | ✅ | `x == y` | P0 | - |
| Not Equal (!=) | ✅ | `x != y` | P0 | - |
| Less Than (<) | ✅ | `x < y` | P0 | - |
| Greater Than (>) | ✅ | `x > y` | P0 | - |
| Less or Equal (<=) | ✅ | `x <= y` | P0 | - |
| Greater or Equal (>=) | ✅ | `x >= y` | P0 | - |
| AND (aen) | ✅ | `x aen y` | P0 | - |
| OR (ya) | ✅ | `x ya y` | P0 | - |
| NOT (nah, !) | ✅ | `nah x` or `!x` | P0 | - |
| Identity Check (is) | ❌ | `x is y` | P2 | - |
| Chained Comparisons | ❌ | `1 < x < 10` | P2 | - |

---

## 5. Control Flow

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| If (agar) | ✅ | `agar condition { }` | P0 | - |
| Else (warna) | ✅ | `warna { }` | P0 | - |
| Else-if (yawari) | ✅ | `yawari condition { }` | P0 | - |
| While (jistain) | ✅ | `jistain condition { }` | P0 | - |
| For Loop (har) | ✅ | `har i mein range(5) { }` | P1 | - |
| Break (tor) | ✅ | `tor` | P1 | Loops |
| Continue (jari) | ✅ | `jari` | P1 | Loops |
| Do-While | ❌ | `kar { } jistain condition` | P2 | - |
| Switch/Match | ⚠️ Partial | `match x { ... }` | P2 | AST only |
| Goto | ❌ | - | P3 | (controversial) |

### Current Control Flow Syntax
```sindlish
agar x > 5 {
    likh("Big")
} yawari x > 2 {
    likh("Medium")
} warna {
    likh("Small")
}

jistain x < 10 {
    likh(x)
    x = x + 1
}

har i mein range(5) {
    likh(i)
}
```

---

## 6. Functions & Methods

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Built-in Functions | ✅ | `likh()`, `lambi()`, `puch()` | P0 | - |
| Method Calls | ✅ | `list.wadha(item)` | P0 | - |
| User-defined Functions | ✅ | `kaam add(a, b) { }` | P0 | - |
| Anonymous Functions | ❌ | `lambai x => x + 1` | P1 | User-defined functions |
| Recursion | ✅ | Function calling itself | P1 | User-defined functions |
| Closures | ✅ | - | P2 | User-defined functions |
| Default Arguments | ✅ | `kaam foo(x=10) { }` | P1 | User-defined functions |
| Variadic Args | ✅ | `kaam foo(*args) { }` | P1 | User-defined functions |
| Keyword Arguments | ✅ | `kaam foo(**kwargs) { }` | P1 | User-defined functions |
| Decorators | ❌ | `@decorator` | P2 | User-defined functions |
| Generators (yield) | ❌ | `yield x` | P2 | User-defined functions |
| Async/Await | ❌ | `async def` / `await` | P2 | - |

### Built-in Functions
```sindlish
likh("Hello")          # Print output
lambi(list)            # Get length
majmuo(items)          # Create set
```

---

## 7. String Operations

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| String Literals | ✅ | `"hello"` or `'hello'` | P0 | - |
| Multiline Strings | ✅ | `"""multi line"""` | P0 | - |
| Escape Sequences | ✅ | `"\n\t\"` | P0 | - |
| Concatenation | ✅ | `s1 + s2` | P0 | - |
| Replication | ✅ | `s * 3` | P0 | - |
| String Indexing | ✅ | `s[0]`, `s[-1]` | P0 | - |
| String Slicing | ❌ | `s[1:3]` | P1 | - |
| String Methods | ❌ | `s.upper()` | P1 | - |
| String Formatting | ❌ | `f"value: {x}"` | P1 | - |
| F-strings | ❌ | `f"text {var}"` | P1 | - |
| Regex | ❌ | - | P2 | - |
| Unicode Full Support | ⚠️ Limited | - | P1 | - |

### String Examples
```sindlish
lafz s = "Sindlish"
likh(s[0])           # First char: S
likh(s[-1])          # Last char: h

lafz multi = """Multi
line
string"""
```

---

## 8. Collection Operations

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Length (lambi) | ✅ | `lambi(list)` | P0 | - |
| Indexing | ✅ | `l[0]`, `l[-1]` | P0 | - |
| Iteration | ⚠️ Limited | - | P0 | - |
| List Slicing | ❌ | `l[1:3]` | P1 | - |
| List Comprehension | ❌ | `[x for x in l]` | P1 | - |
| Dict Comprehension | ❌ | `{k:v for k,v in d}` | P1 | - |
| Set Comprehension | ❌ | `{x for x in s}` | P1 | - |
| Unpacking | ❌ | `a, b = [1, 2]` | P1 | - |
| Spread Operator | ❌ | `[...l1, ...l2]` | P2 | - |
| Dictionary Merge | ❌ | `d1 \| d2` | P2 | - |

---

## 9. Collection Methods

### List Methods
| Method | Sindlish | Status | Priority |
|--------|----------|--------|----------|
| append | wadha | ✅ | P0 |
| extend | wadhayo | ✅ | P0 |
| insert | wajh | ✅ | P0 |
| remove | hata | ✅ | P0 |
| pop | kadh | ✅ | P0 |
| clear | saf | ✅ | P0 |
| index | index | ✅ | P0 |
| count | garn | ✅ | P0 |
| sort | tarteeb | ✅ | P0 |
| reverse | ulto | ✅ | P0 |
| copy | nakal | ✅ | P0 |
| find | - | ❌ | P2 |
| filter | - | ❌ | P2 |
| map | - | ❌ | P2 |

### Dict Methods
| Method | Sindlish | Status | Priority |
|--------|----------|--------|----------|
| get | hasil | ✅ | P0 |
| keys | cabeyon | ✅ | P0 |
| values | raqamon | ✅ | P0 |
| items | syon | ✅ | P0 |
| pop | kadh | ✅ | P0 |
| popitem | syonkadh | ✅ | P0 |
| clear | saf | ✅ | P0 |
| update | update | ✅ | P0 |
| copy | nakal | ✅ | P0 |
| setdefault | defaultrakh | ✅ | P0 |
| fromkeys | - | ❌ | P2 |

### Set Methods
| Method | Sindlish | Status | Priority |
|--------|----------|--------|----------|
| add | addkar | ✅ | P0 |
| remove | hata | ✅ | P0 |
| discard | chad | ✅ | P0 |
| clear | saf | ✅ | P0 |
| union | bade | ✅ | P0 |
| intersection | milap | ✅ | P0 |
| difference | farq | ✅ | P0 |
| symmetric_difference | symmetric_farq | ✅ | P0 |
| issubset | nandohisoahe | ✅ | P0 |
| issuperset | wadohisoahe | ✅ | P0 |
| isdisjoint | alaghahe | ✅ | P0 |
| copy | nakal | ✅ | P0 |
| pop | kadh | ✅ | P0 |
| update | update | ✅ | P0 |

---

## 10. Input/Output

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Print Output | ✅ | `likh("text")` | P0 | - |
| File I/O | ❌ | - | P1 | - |
| Standard Input | ✅ | `puch("?")` | P1 | - |
| Formatted Output | ❌ | - | P1 | - |
| JSON | ❌ | - | P1 | - |
| CSV | ❌ | - | P2 | - |
| Binary I/O | ❌ | - | P2 | - |

---

## 11. Error Handling

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Syntax Errors | ✅ | Lexer/Parser | P0 | - |
| Runtime Errors | ✅ | Via exceptions | P0 | - |
| Try-Except | ❌ | `try { } hatana (e) { }` | P0 | - |
| Try-Except-Finally | ❌ | `finally { }` | P0 | - |
| Custom Exceptions | ❌ | - | P1 | OOP |
| Result System | ✅ | `ok()`, `ghalti()`, `?`, `!!` | P0 | - |
| Raise | ✅ | `ghalti("msg")` | P0 | - |
| Assert | ❌ | `yaqeen condition` | P1 | - |

---

## 12. Object-Oriented Programming

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Internal Objects | ✅ | SdObject classes | P0 | - |
| Classes | ❌ | `class Nama { }` | P1 | - |
| Objects | ❌ | `obj = Class()` | P1 | Classes |
| Inheritance | ❌ | `class B : A` | P1 | Classes |
| Polymorphism | ❌ | - | P1 | Classes |
| Encapsulation | ❌ | - | P1 | Classes |
| Properties | ❌ | `property x` | P2 | Classes |
| Static Methods | ❌ | `staticmethod` | P2 | Classes |
| Class Methods | ❌ | `classmethod` | P2 | Classes |
| Magic Methods | ⚠️ | Internal only | P2 | - |

---

## 13. Type System

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Static Typing Keywords | ✅ | `adad x = 10` | P0 | - |
| Type Inference | ✅ | `x = 10` | P0 | - |
| Type Annotations | ✅ | `x : adad` | P0 | - |
| Type Aliases | ❌ | `type IntList = fehrist[adad]` | P2 | - |
| Generics | ❌ | `fehrist[T]` | P2 | - |
| Union Types | ❌ | `adad \| lafz` | P2 | - |
| Optional Types | ❌ | `x?` or `khali x` | P1 | - |
| Type Guards | ❌ | - | P2 | - |
| Runtime Type Check | ❌ | `kya(x, adad)` | P1 | - |

---

## 14. Modules & Namespaces

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Built-in Modules | ⚠️ Limited | Internal only | P0 | - |
| Import | ❌ | `shamil kar "module"` | P1 | - |
| Export | ❌ | `kharj kar` | P1 | - |
| Alias Import | ❌ | `shamil kar m san module` | P1 | Import |
| Relative Import | ❌ | `shamil kar .sub` | P2 | Import |
| Module Alias | ❌ | `shamil kar m san module` | P1 | Import |

---

## 15. Memory & Concurrency

| Feature | Status | Syntax | Priority | Dependencies |
|---------|--------|--------|----------|--------------|
| Reference Counting | ⚠️ | Internal | P0 | - |
| Garbage Collection | ⚠️ | Auto | P0 | - |
| Threads | ❌ | - | P2 | - |
| Async/Await | ❌ | - | P2 | - |
| Processes | ❌ | - | P3 | - |
| Locks/Mutex | ❌ | - | P2 | Threads |
| Channels | ❌ | - | P3 | Threads |

---

## 17. Advanced Features (Nice-to-Have)

### External Libraries
| Feature | Priority | Description |
|---------|----------|-------------|
| Graphics/UI | P3 | Window, buttons, canvas |
| Audio/Video | P3 | Playback, recording |
| Networking/HTTP | P2 | Web requests, sockets |
| Database | P2 | SQL, NoSQL connectors |
| Cryptography | P2 | Encryption, hashing |
| Math Libraries | P2 | Statistics, matrices |
| JSON/YAML | P1 | Data serialization |
| Date/Time | P1 | DateTime utilities |
| Logging | P2 | Application logging |
| Testing | P2 | Unit test framework |
| CLI Args | P2 | Command-line parsing |
| Templating | P2 | HTML, text templates |
| Emoji Support | P3 | Full Unicode emoji |

### Advanced Language Features
| Feature | Priority | Description |
|---------|----------|-------------|
| Macros | P3 | Code generation |
| Metaprogramming | P3 | Dynamic code |
| Reflection | P3 | Introspection |
| Serialization | P2 | Pickle, marshal |
| Hot Reloading | P3 | Live reload |
| Plugins/Extensions | P3 | Dynamic loading |
| FFI | P3 | Foreign function interface |
| JIT Compilation | P3 | Just-in-time compiler |

---

## 18. Priority Matrix

### P0 - Critical (Must Have)
- [x] Basic data types (int, float, string, bool, null)
- [x] Collections (list, dict, set)
- [x] Arithmetic operators
- [x] Comparison operators  
- [x] Logical operators
- [x] If/else control flow
- [x] While loops
- [x] Print output
- [x] User-defined functions (kaam)
- [x] Error handling (Result system)
- [x] Try/except (Replaced by Result system)

### P1 - High Priority
- [x] For loops
- [x] Break/continue
- [ ] Ternary operator
- [ ] Augmented assignment
- [ ] String slicing
- [ ] String methods
- [ ] List comprehension
- [ ] File I/O
- [ ] JSON support
- [x] User input
- [ ] Type guards
- [ ] Runtime type checking

### P2 - Medium Priority  
- [ ] BigInt / Decimal
- [ ] DateTime
- [ ] Regex
- [ ] Bitwise operators
- [ ] Chained comparisons
- [ ] Identity checks
- [ ] Closures
- [ ] Default arguments
- [ ] Variadic args
- [ ] Decorators
- [ ] OOP classes
- [ ] Inheritance
- [ ] Module system
- [ ] HTTP/Networking

### P3 - Low Priority (Nice-to-Have)
- [ ] Graphics/UI
- [ ] Audio/Video
- [ ] Database connectivity
- [ ] Cryptography
- [ ] Threads
- [ ] Async/await
- [ ] Generators
- [ ] Macros
- [ ] Metaprogramming
- [ ] JIT compilation

---

## Contributing to Sindlish

### How to Add a New Feature

1. **Lexer** (`interpreter/lexer.py`): Add token recognition
2. **Tokens** (`interpreter/tokens.py`): Add TokenType enum
3. **Parser** (`interpreter/parser.py`): Add parsing logic
4. **AST** (`interpreter/ast_nodes.py`): Add AST node class
5. **Compiler** (`interpreter/compiler.py`): Add bytecode compilation
6. **VM** (`interpreter/vm.py`): Add VM execution
7. **Tests** (`tests/`): Add test cases
8. **Documentation**: Update this roadmap

### Code Style
- Follow existing patterns in the codebase
- Use Sindlish names for new features (e.g., `wadha` for `append`)
- Add error handling with proper error messages

---

## License

This roadmap is part of the Sindlish programming language project.

---

*Last updated: April 29, 2026 - Phase 1-4 Complete*
*All 236 tests passing*