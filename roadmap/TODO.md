# Sindlish — Working TODO

Companion to [ROADMAP.md](ROADMAP.md) and [FEATURE_ROADMAP.md](FEATURE_ROADMAP.md).
Original audit against v0.1.1 (236 tests). Bug sweep fixed 2026-08: 286 tests passing.

---

## 0. Known Bugs (fix first)

All items below were verified against v0.1.1 by executing the interpreter.
Items marked [x] are fixed with regression coverage in `tests/test_bugfixes.py`.

### Critical
- [x] **Functions cannot read top-level variables** — `x = 42; kaam foo() { wapas x }; likh(foo())` crashes with `IndexError`. Fixed by unifying storage: program-level variables live in the globals environment (`STORE_GLOBAL`/`LOAD_GLOBAL`); block/function scopes keep frame slots. Function names are registered without allocating slots, so references compile to `LOAD_GLOBAL`
- [x] **Non-ASCII string literals are mangled** — `"سلام"` was mojibake via `codecs.decode(..., "unicode_escape")`. Replaced with a manual escape decoder (`_unescape`) that preserves all non-ASCII bytes
- [x] **Default parameter values are stored as AST nodes** — defaults are now compiled at definition site (Python semantics) and bound via the new `MAKE_FUNCTION` opcode onto `SdFunction.defaults`; VM consumes evaluated values and type-checks them
- [x] **Dict/set used directly as a condition crashes the VM** — shared truthiness helper `sd_truthy()` handles every object kind; `SdDict`/`SdSet` gained `__bool__`; `JUMP_IF_FALSE` no longer reads `.value` blindly
- [x] **Typed assignment from Result-returning ops always fails** — type checks unwrap `Ok(...)` wrappers before comparing, so `dahai d = 10 / 2` works while `adad x = 10 / 2` cleanly reports `'DAHAI' milyo`. Error Results still propagate as values
- [x] **`aalmi` crashes the compiler** — added `compile_GlobalNode` (declaration hint recorded by resolver) and fixed the `type(node).name` → `__name__` typo

### Silent wrong behavior
- [x] **Call-site `*args` / `**kwargs` are silently dropped** — compiler now emits marker-prefixed operands (`StarArgsMarker`/`KwargsDictMarker`); VM expands them into positionals/kwargs and fills `*param`/`**kw` params. `examples/star_args.sd` prints correct output
- [x] **Keyword detection sniffs string arguments** — kwarg names travel as `KwargMarker(SdString)` consts, a distinct type, so runtime string args can never collide with param names
- [x] **No short-circuit evaluation** — `aen`/`ya` compile to `JUMP_IF_FALSE_OR_POP` / `JUMP_IF_TRUE_OR_POP`; right operand is skipped when decided
- [x] **`nah` / `aen` / `ya` on numbers do bitwise ops** — logical ops are now truthiness-based for every type (`nah 5` → `koorh`); bitwise behavior removed from the logical path
- [x] **`lambi(lughat)` raises** — builtin handles `SdDict.pairs`
- [x] **Redeclared variable fails runtime check against stale metadata** — explicit redeclaration overwrites slot metadata (last-wins)
- [x] **Functions-as-values bind None** — function names resolve through globals, so `g = foo` binds the real `SdFunction`
- [x] **`jistain x / y { }` never terminates naturally** — conditions evaluate through `sd_truthy`, which unwraps `Ok(...)` Results

### Correctness / UX
- [x] **`likh(sach)` prints "such"**, keyword is spelled `sach`
- [x] **Chained comparisons crash cryptically** — parser now rejects them with "Chained comparisons supported natho; likho (a < b) aen (b < c)."
- [x] **Unclosed block accepted at EOF** — parser raises "Block band natho thayo"; unterminated string/block-comment literals raise clean `LikhaiJeGhalti`
- [x] **Unhashable element in set/dict literal leaks raw TypeError** — BUILD_SET/BUILD_DICT map it to a clean `QisamJeGhalti`
- [x] **REPL consts/types unenforced** — `STORE_GLOBAL` carries `(const_idx, is_const, type, element_type)`; VM enforces const + type on program-level assignments (also fixes typed-global reassignment like `lafz s = "ok"` then `s = 5`)
- [x] **Traceback lines are off-by-one** — both `_build_traceback` and `SdResult.capture_traceback` read `frame.ip - 1`

### Cosmetic
- [x] **Keyword arguments at call sites misparse** — `f(x = 1)` emits a KwargMarker pair; builtins/methods cleanly reject kwargs they don't support (`likh(1, 2, sep="-")` errors instead of printing junk)
- [x] **`bahari` (nonlocal) crashes the compiler** — fully implemented since closures landed: declaration routes writes to the enclosing function's cell; unknown targets and program-level use raise clean errors
- [x] Function-local `pakko` const checks are silently disabled — resolver snapshots slot metadata per function (`FunctionNode.slot_metadata`), compiler passes it into `SdFunction`; VM `STORE_FAST` enforces const + type inside function bodies. Also fixed the flat-dict collision where a function's typed local overwrote same-index main-frame metadata
- [x] `majmuo()` arity error message says "`lambi()` khe 0 ya 1 argument khapay" (copy-paste)
- [x] Inconsistent division semantics resolved — **all arithmetic operators (`+ - * ^ / %`) now always return `Result`**: success wraps as `Ok`, any failure (type mismatch, divide-by-zero) becomes `Err` instead of raising. Strict consumption: using an `Err` in a further operation or condition raises immediately. **Boundaries unwrap success values**: function returns, parameter binding, and conditions all strip `Ok`, so `Err` is the only Result that survives to callers — which makes every Result-inspection path (`.ghalti`/`.ok`/`.bachao()`/`.lazmi()`/`|?`) treat raw values as the success case automatically. Comparisons auto-unwrap `Ok` operands and stay boolean; `likh` prints Results without consuming them. Dead bitwise `_op_logical_and/or` VM handlers removed
- [x] `match` keyword accepted by lexer but parser has no handler — reserved with a clear message until implemented
- [x] Duplicate `JUMP_IF_FALSE` entry in VM dispatch table; unused `DUP_TOP` opcode
- [x] `SdString.__add__` type-mismatch message mentions comparison ("bhet") instead of concatenation
- [ ] Set method naming: Sindhi Language Authority dictionaries list **both** `ٻڌي` ("bade") and `ميلاپ` ("milap") as words for **union**; official intersection terms are cutting/crossing words (ڪٽڻ، منقطع ٿيڻ). So `bade` = union is defensible, but `milap` for intersection contradicts SLA. Suggest renaming intersection to something like `mushtarak` (مشترک، "shared/common", familiar from Urdu math education) or keeping `milap` as an alias — decision needed
- [x] `main.py tokens/ast` commands skip the file-existence check other commands perform → raw `FileNotFoundError` traceback
- [x] `range(step=0)` leaks raw Python `ValueError` — guarded with a clean error; `range()` now returns a lazy `SdRange` (O(1) `lambi`, indexing, truthiness, no list materialization)
- [x] `-2 ^ 2 == 4` kept **deliberately**: unary minus binds tighter than `^`, so it reads as `(-2) ^ 2`. Documented language convention; do not "fix" toward Python's `-4`
- [x] Dead code removed: conftest no longer builds the `slot_names` hack; `VM.variables` reads only globals-environment records; `get_variable_value` prefers `vm.globals.records`

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
- [x] Call-site unpacking `f(*list)`, `f(**dict)` — shipped with the v0.1.2 bug sweep (marker-based arg encoding); `*param`/`**kw` params also work
- [x] Closures — Python-style shared cells: locals captured by inner functions become `Cell` boxes; `LOAD_DEREF`/`STORE_DEREF` opcodes read/write them by reference. Cells link at definition time via the defining frame's cell table (intermediate functions forward the owner's cell), so closures stay valid after their defining call returns. Chained calls `f()()` work via the new `CALL_VALUE` opcode
- [x] `bahari` semantics — declares a name as belonging to the nearest enclosing function's scope; writes go through the captured cell. Reads capture automatically without declaration; assigning to an outer local *without* `bahari` raises a helpful error. Unknown/program-level `bahari` targets raise clean errors
- [ ] Anonymous functions (`lambai`)
- [x] Const/type enforcement inside function bodies — shipped with the function-local metadata sweep (per-function `slot_metadata` snapshots)

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
