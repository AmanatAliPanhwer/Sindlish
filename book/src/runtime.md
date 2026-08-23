# Environment, Builtins & the REPL

<div class="youarehere">📍 <strong>You are here:</strong> Part Eight · Living Here — 1 of 3</div>

## 🧠 The globals environment

One dict with discipline: `runtime/env.py` maps names → `VariableRecord(value, type, element_type, is_const)`. That record struct is *why* global const/type enforcement is cheap — checks read the slot next to the value. `define/lookup_record/assign` are the whole API; `assign` refuses on `is_const`.

Builtins are seeded into this environment at startup (`tests/conftest.py` shows the exact recipe): each of the five builtins registered as a const `KAAM`-typed record.

| Builtin | Behavior notes |
|---|---|
| `likh(...)` | space-separated print; does **not** consume Results |
| `puch(prompt)` | returns `SdString` |
| `lambi(x)` | works on strings, lists/dicts/sets, ranges |
| `range(a[,b[,c]])` | returns **lazy** `SdRange` (O(1) length, indexable) |
| `majmuo([iterable])` | 0 or 1 args |

## 🖥️ The REPL (`interpreter/repl.py`)

The REPL reuses the whole pipeline per line with two twists:

1. **Persistence**: resolver runs with `is_repl = True`, forcing top-level definitions into globals so they survive across lines.
2. **Prompt tooling**: syntax highlighting via a regex pass, plus completion fed by the resolver's `symbols` list — the same data the VS Code extension uses. One producer, two consumers.

Errors in REPL mode don't kill the session: the interpreter reports and keeps the loop alive (file mode exits non-zero instead).

<div class="recap">
<p>Globals = records with enforcement metadata attached.</p>
<p>Builtins seed as const KAAM records; <code>range</code> is lazy.</p>
<p>REPL = pipeline + is_repl flag + symbols-driven completion.</p>
</div>
