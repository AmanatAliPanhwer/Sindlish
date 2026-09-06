# Sindlish — Development Roadmap

**Version:** 0.1.1
**Status:** Core language usable · 236 tests passing · bytecode VM architecture

Sindlish runs a classic five-stage pipeline: **Lexer → Parser → Resolver → Compiler → VM**.
This roadmap tracks what is done and what comes next. Feature-level detail lives in
[FEATURE_ROADMAP.md](FEATURE_ROADMAP.md); the working checklist lives in [TODO.md](TODO.md).

---

## Where Sindlish stands (v0.1.1)

| Area | Status |
|---|---|
| Lexer / Parser / AST | Done — comments (`#`, `/* */`), strings incl. triple-quote, full precedence chain, `{ }` blocks |
| Types & variables | Done — `adad`, `dahai`, `lafz`, `faislo`, `khali`; 6 declaration styles; `pakko` consts; typed collections |
| Operators | Done — arithmetic, comparison, logical (`aen`/`ya`/`nah`) |
| Control flow | Done — `agar`/`yawari`/`warna`, `jistain`, `har … mein`, `tor`, `jari` |
| Collections | Done — `fehrist`, `lughat`, `majmuo` with ~35 native methods |
| Functions | Mostly done — `kaam`, typed/default params, `*args`/`**kwargs` in definitions, recursion, implicit return |
| Result error system | Done — `ok()`/`ghalti()`, postfix `?` / `!!`, `.bachao()`, `.lazmi()`, panic + call-stack tracebacks |
| Bytecode backend | Done — slot-based locals, static type checks on annotated declarations, shared constant pool |
| CLI & REPL | Done — `run`/`repl`/`eval`/`tokens`/`ast`/`check`/`docs`/`--version`; highlighted REPL with completions |
| Tooling & distribution | Done — VS Code extension (grammar, snippets, LSP), Windows/macOS/Linux installers, benchmarks |

---

## Phase A — Correctness & gaps in shipped features (NEXT)

Small, high-value items that complete features users already touch:

| Priority | Task | Notes |
|---|---|---|
| P0 | Fix keyword arguments at call sites | `f(x = 1)` currently misparses as positional — silently wrong |
| P0 | Support or reject `bahari` (nonlocal) cleanly | Compiler currently crashes on `NonLocalNode` |
| P0 | Implement the `match` statement | Keyword/token/AST nodes exist; parsing missing |
| P1 | Call-site unpacking `f(*list)`, `f(**dict)` | Parsed today, rejected by compiler |
| P1 | Compound assignment `+= -= *= /=` | Not in lexer yet |
| P1 | String methods (`ulato`/reverse, `badlo`/replace, …) | `SdString` has dunders but no registered natives |
| P1 | Slicing `s[1:3]`, `l[1:3]` for strings and lists | |
| P2 | `likh()` options: `sep=`, `end=` | |
| P2 | Runtime type check builtin `qisam(x)` | |
| P2 | Ternary expression | e.g. `(x agar cond warna y)` — syntax TBD |
| P2 | Enable const/type enforcement inside function bodies | Resolver collects metadata; VM receives `{}` for locals |

---

## Phase B — Closures & scoping

- Upvalue/cell variables so nested `kaam` capture enclosing locals
- Working `bahari` (nonlocal) semantics
- Decide `aalmi` (global) interaction with function frames

## Phase C — Object-oriented programming

The internal object model already has `SdType`/`SdShey` with C3-linearized MRO lookup;
user-facing classes build on it:

1. Class declaration (`jamaat`) parser + AST + compiler support
2. Constructors, `haso`/self handling, attribute access beyond `Result.ok/.ghalti`
3. Inheritance + method overriding (MRO infra exists)
4. Encapsulation conventions, properties

## Phase D — Modules & standard library

- `shamil` (import) for multi-file programs
- Standard library modules: math, string utilities, JSON, file I/O
- Package layout / search paths

## Phase E — Quality & performance

- Grow test suite alongside every feature above
- VM throughput work (benchmarks vs Python/Rust live in `bench/`)
- Consistent error philosophy — **decided 2026-09 (RFC in #33):** all six arithmetic ops return `Result` (parcels) on failure; ordering comparisons raise; equality is total. TODO.md item shipped with #33.
- Docs website sync (`docs/` submodule)

---

*Last updated: August 2026*
