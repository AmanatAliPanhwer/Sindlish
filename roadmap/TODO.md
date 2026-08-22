# Sindlish — Working TODO

Companion to [ROADMAP.md](ROADMAP.md) and [FEATURE_ROADMAP.md](FEATURE_ROADMAP.md).
Statuses verified against v0.1.1 (236 tests passing).

---

## 0. Known Bugs (fix first)

- [ ] **Keyword arguments at call sites misparse** — `f(x = 1)` is treated as positional; `likh(1, 2, sep="-")` prints `1 2 sep -` instead of erroring or honoring `sep`
- [ ] **`bahari` (nonlocal) crashes the compiler** — `NonLocalNode` reaches the compiler unhandled ("Compiler node qisam NonLocalNode…")
- [ ] Function-local `pakko` const checks are silently disabled — resolver collects slot metadata but VM receives `{}` for function frames
- [ ] `majmuo()` arity error message says "`lambi()` khe 0 ya 1 argument khapay" (copy-paste)
- [ ] Inconsistent division semantics: `/`, `%` return `Result` while `+ - * ^` raise on bad types
- [ ] `match` keyword accepted by lexer but parser has no handler — produces a generic syntax error; either implement or reserve with a clear message
- [ ] Duplicate `JUMP_IF_FALSE` entry in VM dispatch table; unused `DUP_TOP` opcode
- [ ] `SdString.__add__` type-mismatch message mentions comparison ("bhet") instead of concatenation
- [ ] Set method naming: `bade` = union vs `milap` = intersection — verify against intended Sindhi meanings

---

## 1. Complete Shipped Features

### Strings
- [ ] String methods: reverse (`ulato`), replace (`badlo`), split (`wand`), join, upper/lower, starts/ends-with
- [ ] Slicing `s[1:3]`
- [ ] F-strings / interpolation

### Collections
- [ ] Slicing `l[1:3]`
- [ ] Comprehensions (list/dict/set)
- [ ] Unpacking assignment `a, b = [1, 2]`
- [ ] Value equality for containers (currently identity-based)

### Functions & Scope
- [ ] Call-site unpacking `f(*list)`, `f(**dict)`
- [ ] Closures with captured variables (cell/upvalue slots in frames)
- [ ] Working `bahari` semantics once closures land
- [ ] Anonymous functions (`lambai`)
- [ ] Const/type enforcement inside function bodies (wire resolver metadata into VM frames)

### Output & Builtins
- [ ] `likh(sep=, end=)` parameters
- [ ] Runtime type-check builtin `qisam(x)`
- [ ] More casts: `lafz()` for numbers, `lughat()`

---

## 2. New Language Features

- [ ] `match` statement (keyword + AST nodes already exist)
- [ ] Compound assignment operators (`+= -= *= /= %= ^=`)
- [ ] Ternary conditional expression
- [ ] Classes (`jamaat`) — build on existing SdType/MRO object model:
  - [ ] Class declaration parsing + compilation
  - [ ] Constructor + self handling
  - [ ] Attribute access (extend GET_ATTR beyond `Result.ok/.ghalti`)
  - [ ] Inheritance + overriding
- [ ] Modules: `shamil` import, multi-file programs, search paths

---

## 3. Tooling & Ecosystem

- [x] CLI: run / repl / eval / tokens / ast / check / docs / --version
- [x] REPL with highlighting + completion
- [x] VS Code extension (grammar, snippets, LSP diagnostics + completion)
- [x] Installers for Windows/macOS/Linux (--onedir packaging)
- [ ] Execution trace / debug mode
- [ ] AST pretty-printer (current `ast` command dumps repr)
- [ ] LSP: hover info using resolver's symbol table
- [ ] Transpiler mode (Sindlish → Python)

---

## 4. Quality

- [ ] Unify error philosophy across operators
- [ ] Tests for every fix above (currently 236 passing)
- [ ] VM performance pass guided by `bench/run_benchmarks.py`
- [ ] Sync docs website (`docs/` submodule) with language changes
- [ ] Remove vestigial code: `SdShey._ref_count`, unused `Environment.global_names/nonlocal_names`

---

## Done (highlights)

- [x] Full pipeline: Lexer → Parser → Resolver → Compiler → bytecode VM
- [x] Types + 6 declaration styles + `pakko` consts + typed collections
- [x] Control flow: agar/yawari/warna, jistain, har…mein, tor, jari
- [x] ~35 collection methods across fehrist/lughat/majmuo
- [x] Result system: ok/ghalti, `?`, `!!`, `.bachao()`, `.lazmi()`, panics + tracebacks
- [x] Static type checking on annotated declarations (top level)
- [x] Multiline expressions, collections literals, parameter lists
- [x] Typecasting builtins: `adad()`, `dahai()`, `lafz()`, `faislo()`, `fehrist()`
