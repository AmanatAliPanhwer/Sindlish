# Opcode Field Guide

<div class="youarehere">📍 <strong>You are here:</strong> Part Seven · The Engine Room — 3 of 4</div>

All 50 opcodes from `backend/opcodes.py`, grouped by duty. Stack effect notation: `[before] → [after]` with the top on the right. Every handler lives as `_op_<name>` in `vm.py`; anchors give its first line.

## Loads & stores

| Opcode | arg | Stack | What happens |
|---|---|---|---|
| `LOAD_CONST` | pool idx | `[] → [v]` | push pooled value (`vm.py:259`) |
| `LOAD_FAST` / `STORE_FAST` | slot# | `[v]→[]` store | frame slots; **STORE enforces pakko + types** (`vm.py:265`) |
| `LOAD_GLOBAL` / `STORE_GLOBAL` | name-idx / tuple | checked | dict env; tuple carries `(idx, is_const, type, elem)` for enforcement (`vm.py:280`) |
| `LOAD_DEREF` / `STORE_DEREF` | cell idx | cells | closure boxes (`vm.py:314`) |
| `PUSH_NULL/TRUE/FALSE` | – | push singleton-ish | cheap literals without pool hits |

## Arithmetic & comparison (all binary: pop right, pop left)

`BINARY_ADD SUB MUL DIV POW MOD` — delegate to left operand's dunder via `_binary_op_result`; failures become Ghalti parcels, exceptions get line info. Comparisons `COMPARE_EQ NE LT LE GT GE` call dunders directly. `LOGICAL_NOT` uses `sd_truthy`.

## Control flow

| Opcode | Consumes? | Use |
|---|---|---|
| `JUMP_ABSOLUTE` | no | loops, end-chains |
| `JUMP_IF_FALSE` | yes | conditions (`agar/jistain`) |
| `JUMP_IF_FALSE_OR_POP` | peeks; pops if true | short-circuit `aen` |
| `JUMP_IF_TRUE_OR_POP` | peeks; pops if false | short-circuit `ya` |

## Iteration & output

`GET_ITER` (wraps iterable; non-iterable → clean QisamJeGhalti) · `FOR_ITER` (peeks iterator; pushes next item or pops+jumps on exhaustion).

> Output is not a dedicated opcode: `likh(...)` is a builtin call (`CallNode` → `CALL_FUNCTION` → `SimpleBuiltins.likh`). The retired statement-style print path (`PRINT_ITEM`) was removed in the frontend refactor (issue #29).

## Collections

`BUILD_LIST n` / `BUILD_DICT n` / `BUILD_SET n` — pop 2n or n values (reverse order), auto-unwrapping Ok parcels; unhashable members raise clean errors. `BINARY_SUBSCRIPT` / `STORE_SUBSCRIPT` route through dunder dispatch.

## Calls

| Opcode | arg | Mechanism |
|---|---|---|
| `CALL_FUNCTION` | `(name_idx, nargs, has_kwargs)` | lookup global by name, bind, new frame |
| `CALL_VALUE` | `(nargs, has_kwargs)` | callee already on stack (`f()()`, local callees) |
| `CALL_METHOD` | `(name_idx, nargs, has_kwargs)` | MRO lookup on popped receiver; `.ok/.ghalti` special-cased |
| `GET_ATTR` | name_idx | only `ok`/`ghalti` exist today |
| `MAKE_FUNCTION` | ndefaults | binds defaults, links closure cells to defining frame |

> `has_kwargs` is `True` when the call carries keyword arguments (marker pairs); the VM uses it to decide whether to scan for marker-encoded kwargs.

Argument markers: kwargs travel as constant-pool `KwargMarker(name)` pairs, `*args`/`**kwargs` as marker+payload — so runtime strings can never impersonate parameter names.

## Results & panics

`MAKE_OK` / `MAKE_ERROR` (idempotent wrap) · `POSTFIX_QMARK` / `POSTFIX_BANGBANG` (the `?`/`!!` pair) · `CALL_BACHAO` / `CALL_LAZMI` · `PANIC` (bare `ghalti(msg)` statement) · `TYPECAST` (target name via const; unwraps Ok, re-raises Ghalti). Full semantics: [results.md](results.md).

## Completion

`RETURN_VALUE` pops, drops frame, unwraps Ok at the boundary, checks declared return type (errors pass free) · `POP_TOP` · `HALT` pins ip at end.

> 🔍 Reading tip: when a test fails weirdly, dump bytecode with a 10-line script (compile → print instructions) and compare against this table. The [VM chapter](vm-stack-machine.md) shows the technique.

## Operand encoding

Every opcode declares one operand shape, enforced at emit time (`Compiler.emit` / `_patch`) and pinned by `OPERAND_SHAPES` in `backend/opcodes.py`. A mismatched operand is a compiler bug caught the moment it's emitted — never a runtime surprise.

| Shape | Opcodes | Operand |
|---|---|---|
| `none` | `PUSH_*`, `BINARY_*`, `COMPARE_*`, `LOGICAL_NOT`, `POP_TOP`, `GET_ITER`, `BINARY/STORE_SUBSCRIPT`, `MAKE_OK`, `MAKE_ERROR`, `CALL_BACHAO`, `CALL_LAZMI`, `POSTFIX_*`, `PANIC`, `RETURN_VALUE`, `HALT` | no operand (`None`) |
| `int` | `LOAD_CONST`, `LOAD/STORE_FAST`, `LOAD/STORE_DEREF`, `LOAD_GLOBAL`, `GET_ATTR`, `MAKE_FUNCTION`, `BUILD_*`, `JUMP_ABSOLUTE`, `JUMP_IF_*`, `FOR_ITER` | pool / slot / cell / name index, jump target, build count, default count |
| `token` | `TYPECAST` | the `TokenType` cast target |
| `call` | `CALL_FUNCTION`, `CALL_METHOD` | `(name_idx, nargs, has_kwargs)` |
| `callvalue` | `CALL_VALUE` | `(nargs, has_kwargs)` |
| `store` | `STORE_GLOBAL` | bare `name_idx` (function def) **or** `(idx, is_const, type, elem)` enforcement tuple |

<div class="recap">
<p>50 opcodes, 8 families; every handler ≤ ~40 lines in vm.py.</p>
<p>Checked stores live in FAST/GLOBAL handlers — safety is baked into loads/stores.</p>
<p>Kwargs are marker constants, never raw strings.</p>
</div>
