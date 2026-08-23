# The Repository Map

<div class="youarehere">📍 <strong>You are here:</strong> Part One · The Big Picture</div>

Before we open drawers, learn the floor plan. The repo has exactly one room that matters daily (`interpreter/`) and a hallway of supporting rooms.

```mermaid
flowchart TD
    subgraph CORE["interpreter/ — the whole language"]
        direction TB
        F["frontend/<br>lexer.py · parser.py<br>ast_nodes.py · tokens.py · keywords.py"]
        A["analysis/<br>resolver.py"]
        B["backend/<br>compiler.py · opcodes.py<br>vm.py · frame.py · markers.py"]
        O["objects/<br>base.py · core.py · numbers.py<br>strings.py · collections.py"]
        R["runtime/<br>env.py · builtins.py"]
        E["errors.py · repl.py · __init__.py"]
    end
    MAIN["main.py — CLI entry"] --> CORE
    T["tests/ — 25 pytest files"] --> CORE
    VSC["vscode-extension/ — grammar + LSP"] -. reads .-> RES2["resolver symbols"]
```

## `interpreter/` — room by room

| Path | Lines | One-breath summary |
|---|---|---|
| `frontend/lexer.py` | ~350 | Characters → tokens. Dispatch table for simple chars, methods for strings/numbers/operators. |
| `frontend/tokens.py` | ~105 | `TokenType` enum (~60 members) + frozen `Token` dataclass. |
| `frontend/keywords.py` | ~54 | The Sindhi→TokenType dictionary. **Adding a keyword starts here.** |
| `frontend/ast_nodes.py` | ~455 | 36 node classes; each carries `(line, column)`. |
| `frontend/parser.py` | ~880 | Recursive-descent parser; precedence via method-call nesting. |
| `analysis/resolver.py` | ~460 | Scope stack, slot allocation, closure capture analysis, static type checks. |
| `backend/opcodes.py` | ~80 | The 52-opcode `IntEnum`. |
| `backend/compiler.py` | ~500 | AST → bytecode; two-phase jump patching; per-function code blocks. |
| `backend/vm.py` | ~880 | Stack machine: dispatch table, frames, all runtime checks & Result ops. |
| `backend/frame.py` | ~56 | `BytecodeFrame`: instructions, slots array, closure cells, `ip`. |
| `objects/base.py` | ~306 | `SdType` (types + MRO/C3) and `SdShey` (base value + dispatch). |
| `objects/core.py` | ~130 | `SdResult`, `SdFunction`, `SdNull`, closure `Cell`. |
| `objects/numbers.py` | ~195 | `SdNumber` (int *and* float), `SdBool`. Division returns Results! |
| `objects/strings.py` | ~90 | `SdString`. |
| `objects/collections.py` | ~570 | List/dict/set/range + all registered native methods. |
| `runtime/env.py` | ~72 | Globals `Environment`: name → `VariableRecord(value, type, is_const)`. |
| `runtime/builtins.py` | ~80 | `likh`, `puch`, `lambi`, `range`, `majmuo`. |
| `errors.py` | ~119 | Error hierarchy + ANSI-pretty `ErrorReporter`. |
| `repl.py` | — | Interactive shell with highlighting/completion. |

> 🧭 **Orientation trick:** when reading an unfamiliar part of the code, ask *"which stop of the journey is this?"* Everything in `frontend/` happens before execution; everything in `backend/` happens during it; `objects/` is the vocabulary both halves share.

## Outside the core

- **`main.py`** — CLI: `run / repl / eval / tokens / ast / check / docs`. Great for poking at intermediate stages.
- **`tests/`** — one file per feature area (`test_typed_variables.py`, `test_closures.py`, …). Run with `uv run pytest`.
- **`examples/`** — tiny `.sd` programs (`hello.sd`, `factorial.sd`, `star_args.sd`).
- **`vscode-extension/`** — TextMate grammar plus a small LSP that consumes the resolver's `symbols` list for completions.
- **`bench/`** — cross-language timing harness.
- **`developer-docs/`** — the older contributor docs (this book supersedes them).

## Where do I change…?

A preview of the map you'll use constantly:

| "I want to…" | Touch first | Full walkthrough |
|---|---|---|
| add a keyword | `frontend/keywords.py` → `tokens.py` → parser → compiler | [contributing.md](contributing.md) |
| add a builtin | `runtime/builtins.py` | [runtime.md](runtime.md) |
| add a collection method | `objects/collections.py` bottom section | [type-zoo.md](type-zoo.md) |
| add an opcode | `opcodes.py` → compiler → VM dispatch table | [compiler.md](compiler.md) |
| tweak type checking | `resolver.py` (+ `vm._check_type`) | [typing-rules.md](typing-rules.md) |
| change error messages | `errors.py` or raiser site | [errors-reporting.md](errors-reporting.md) |

<div class="recap">
<p><code>interpreter/</code> = frontend (before run), backend (during run), objects (shared vocabulary).</p>
<p><code>main.py</code>'s <code>tokens</code>/<code>ast</code>/<code>check</code> commands are your X-ray glasses.</p>
<p>The "Where do I change…?" table is the fastest route into any task.</p>
</div>
