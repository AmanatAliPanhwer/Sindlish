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
- [x] Set method naming: Sindhi Language Authority dictionaries list **both** `ٻڌي` ("bade") and `ميلاپ` ("milap") as words for **union**; official intersection terms are cutting/crossing words (ڪٽڻ، منقطع ٿيڻ). So `bade` = union is defensible, but `milap` for intersection contradicts SLA. **Decided 2026-08 (#32): option 2 — intersection renamed to `mushtarak` (مشترک, "shared/common", familiar from Urdu math education); `bade` keeps union; `milap` retired (no alias).**
- [x] `main.py tokens/ast` commands skip the file-existence check other commands perform → raw `FileNotFoundError` traceback
- [x] `silsilo(step=0)` leaks raw Python `ValueError` — guarded with a clean error; `silsilo()` now returns a lazy `SdRange` (O(1) `lambi`, indexing, truthiness, no list materialization)
- [x] `-2 ^ 2 == 4` kept **deliberately**: unary minus binds tighter than `^`, so it reads as `(-2) ^ 2`. Documented language convention; do not "fix" toward Python's `-4`
- [x] Dead code removed: conftest no longer builds the `slot_names` hack; `VM.variables` reads only globals-environment records; `get_variable_value` prefers `vm.globals.records`
- [x] **`main.py ast` crashes on any program containing a function** — `FunctionNode.__repr__` iterates every name in `__slots__`, but `slot_metadata` is declared there yet never initialized in `FunctionNode.__init__` (the resolver assigns it later). Printing a pre-resolution AST raises `AttributeError: ... has no attribute 'slot_metadata'`. Found 2026-08 while verifying docs snippets (`python main.py ast journey.sd`). **Fixed 2026-08 by the #29 frontend refactor:** `FunctionNode` (and all AST nodes) became a `@dataclass(slots=True)` with `slot_metadata: dict = field(default_factory=dict)`, so it is initialized at construction time
- [x] **Typed redeclaration in a nested block corrupts the enclosing variable's slot metadata** — inside a function, `adad x = 1` followed by `lafz x = "hi"` in an inner block reuses the *same* slot (resolver's `_find` returns the outer binding, so no true shadowing is created) and overwrites `slot_metadata[slot]` with the new explicit type. The overwritten metadata applies to the whole function, so the *earlier* line now fails at runtime: `QisamJeGhalti: 'lafz' qisam laai lafz khapyo paye, par 'ADAD' milyo` pointing at `adad x = 1`. Found 2026-08 while writing the resolver chapter. Repro: `kaam test() { adad x = 1  agar sach { lafz x = "hi" } }` then call it. Fix direction: when `found[0] == "slot"` but `found[2] != len(self.scopes)-1`, either define a fresh slot (real shadowing) or refuse to re-type the existing binding. **Fixed 2026-08 by the #30 Phase 2 resolver refactor:** the first explicit type on a function-local slot is retained; a conflicting typed redeclaration raises `QisamJeGhalti` at the redeclaration line (`resolver.py:_verify_assignment_types` metadata conflict check)
- [x] **Dead print pipeline: `TokenType.LIKH`, `parse_print()`, `PrintNode`, `PRINT_ITEM` are all unreachable** — `"likh"` is missing from `KEYWORDS` (`interpreter/frontend/keywords.py`), so the lexer always emits `IDENTIFIER('likh')`; printing actually works as a builtin call (`CallNode` → `CALL_FUNCTION` → `SimpleBuiltins.likh`). The whole dedicated statement path is dead weight kept in sync by hand. Found 2026-08 while writing the lexer chapter (`python main.py tokens` shows `IDENTIFIER('likh')`). **Fixed 2026-08 by the #29 frontend refactor:** deleted the whole dead chain — `TokenType.LIKH`, `parse_print()`, `PrintNode`, `PRINT_ITEM`, and `resolve_PrintNode` now have zero references in `interpreter/` (printing remains a builtin call)
- [x] **Dict/set element-type violations say "Fehrist"** — `VM._check_element_type` (`interpreter/backend/vm.py:183`) hardcodes "Fehrist je elements jo qisam …" in every message branch. When a typed `lughat[lafz, adad] = {"ali": "x"}` fails its value check, or a `majmuo[lafz]` gets a bad member, the user is told about *fehrist* regardless of container. Verified 2026-08: `lughat[lafz, adad] ages = {"ali": "x"}` → `QisamJeGhalti: Fehrist je elements jo qisam 'adad' hujjhan lazmi aahe`. **Fixed 2026-08 by the #29 frontend refactor:** `_check_element_type` takes a `container_name` parameter and callers pass "Majmuo"/"Lughat" so messages name the right container
- [x] **Storing a propagated Ghalti Result into an annotated variable raises instead of propagating** — `VM._check_type` (`interpreter/backend/vm.py:146`) unwraps only *Ok* results; an *Err* flowing through `expr?` into an explicitly-typed slot hits the type comparison and raises `QisamJeGhalti: 'dahai' qisam laai dahai khapyo paye, par 'RESULT' milyo.` Verified 2026-08: `kaam bhag(adad a, adad b) { dahai r = a / b?  wapas r }` with `bhag(9, 0)` reports RESULT-milyo at the store instead of surfacing ZeroVindJeGhalti (untyped slots propagate correctly). Fix direction: in `_check_type`, early-return true when `isinstance(value, SdResult) and value.is_error()` so errors stay values across typed boundaries. **Fixed 2026-08 by the #30 Phase 2 resolver refactor:** `_check_type` early-returns on error `SdResult`, keeping errors as values across typed boundaries (covered by `TestResultTyping::test_error_result_propagates_through_typed_slot`)
- [x] **MRO/C3 was inverted and silently truncated** (fixed in #32) — two verified defects in `SdType` (`interpreter/objects/base.py:67-124`), found 2026-08 while writing the book's MRO chapter:
  1. `_compute_mro` appended `self` at the **end** (`result + (self,)`) instead of merging it as the *first* C3 sequence like Python does. Consequence: ancestor methods overrode descendants — `B(A)` that registers its own `hello` still resolved A's version via `lookup_method`. Overriding was structurally broken for any type using inheritance.
  2. `_c3_merge` had no failure path: when no valid head existed it just `break`s and returned a partial order. Repro: F/G unrelated; `FA(F,G)`, `GA(G,F)`, `HA(FA,GA)` → `HA.mro == (HA,)` — both parents vanished from the MRO with no error. Python raises `TypeError: Cannot create a consistent method resolution order`.
  **Fixed 2026-08 by #32:** `_compute_mro` now prepends `self` and includes `self._bases` in the merge so direct bases precede shared ancestors; `_c3_merge` raises `TypeError` on stuck-merge (message in Romanized Sindhi). Covered by `tests/test_mro.py`. Load-bearing for the planned `jamaat` classes feature.
- [ ] **`tests/conftest.py` hardcodes a machine-specific sys.path** — line 12 does `sys.path.insert(0, "d:/Code/Sindlish")`, which breaks on any other checkout location/OS. Fix: derive from `pathlib.Path(__file__).resolve().parents[1]`. Found 2026-08 while writing the testing chapter

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
- [x] Runtime type-check builtin `qisam(x)` — shipped with #32; returns the type name of its argument as a `lafz`
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
- [ ] Pretty print in ast                                                    {P1}
- [ ] Execution trace / debug mode
- [ ] AST pretty-printer (current `ast` command dumps repr)
- [ ] LSP: hover info using resolver's symbol table
- [ ] Transpiler mode (Sindlish → Python)

---

## 4. Quality

- [x] Unify error philosophy across operators — **shipped with #33** (2026-09): all six arithmetic ops (`+ - * ^ / %`) return Ghalti parcels on failure; ordering comparisons (`< <= > >=`) raise `QisamJeGhalti`; `== !=` stay total. **#57** (top-level surfacing of a discarded Ghalti — the original "silent error bug") also fixed here via discard-aware `POP_TOP`.
- [x] Tighten the error-class taxonomy (follow-up audit of #33, 2026-09): out-of-bounds reaches `IndexJeGhalti` everywhere (`SdList`/`SdRange`/string OOB + native `kadh`/`pop`); method/name misses are `NaleJeGhalti`; runtime argument-count errors became `MatalabJeGhalti` (parse-time typecast arity stays `LikhaiJeGhalti`); `bahari` misuse is `TarteebJeGhalti` vs unknown-outer-name `NaleJeGhalti`; `call_method` + VM native-call edges both launder raw `IndexError`/`ZeroDivisionError` so no dispatch boundary leaks Python exceptions.
- [x] Close the five remaining safety gaps found in that audit (2026-09, `tests/test_safety_gaps.py`): (1) runaway recursion now stops with `HalndeVaktGhalti` at a 10,000-frame cap (`vm.py:_push_frame`) instead of hanging; (2) top-level `wapas` is a `TarteebJeGhalti` structure error (`compiler.compile_ReturnNode`); (3) duplicate keyword args raise `MatalabJeGhalti` instead of silently last-wins (`vm.py:_expand_call_args`); (4) `silsilo()` rejects non-`adad` args with a clean `QisamJeGhalti` instead of leaking Python's `int()` message (`builtins.py`); (5) `fehrist[adad]` stamps its element type onto the list so `wadha`/`wajh`/`wadhayo` and `x[i] = v` re-check at mutation time (`objects/collections.py:_check_list_element`). The safety.md Promise-4 "element pushes aren't re-checked" hole is now closed.
- [x] Tests for every fix above (currently 501 passing)
- [ ] VM performance pass guided by `bench/run_benchmarks.py`
- [ ] Sync docs website (`docs/` submodule) with language changes
- [x] Remove vestigial code: `SdShey._ref_count`, unused `Environment.global_names/nonlocal_names` — shipped with #32

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
