# Opcode Field Guide

<div class="youarehere">📍 <strong>You are here:</strong> Part Seven · The Engine Room — 3 of 4</div>

All 52 opcodes from `backend/opcodes.py`, grouped by duty. Stack effect notation: `[before] → [after]` with the top on the right. Every handler lives as `_op_<name>` in `vm.py`; anchors give its first line.

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

`GET_ITER` (wraps iterable; non-iterable → clean QisamJeGhalti) · `FOR_ITER` (peeks iterator; pushes next item or pops+jumps on exhaustion) · `PRINT_ITEM` (pop & print).

## Collections

`BUILD_LIST n` / `BUILD_DICT n` / `BUILD_SET n` — pop 2n or n values (reverse order), auto-unwrapping Ok parcels; unhashable members raise clean errors. `BINARY_SUBSCRIPT` / `STORE_SUBSCRIPT` route through dunder dispatch.

## Calls

| Opcode | arg | Mechanism |
|---|---|---|
| `CALL_FUNCTION` | `(name_idx, nargs)` | lookup global by name, bind, new frame |
| `CALL_VALUE` | nargs | callee already on stack (`f()()`) |
| `CALL_METHOD` | `(name_idx, nargs)` | MRO lookup on popped receiver; `.ok/.ghalti` special-cased |
| `GET_ATTR` | name_idx | only `ok`/`ghalti` exist today |
| `MAKE_FUNCTION` | ndefaults | binds defaults, links closure cells to defining frame |

Argument markers: kwargs travel as constant-pool `KwargMarker(name)` pairs, `*args`/`**kwargs` as marker+payload — so runtime strings can never impersonate parameter names.

## Results & panics

`MAKE_OK` / `MAKE_ERROR` (idempotent wrap) · `POSTFIX_QMARK` / `POSTFIX_BANGBANG` (the `?`/`!!` pair) · `CALL_BACHAO` / `CALL_LAZMI` · `PANIC` (kharabi) · `TYPECAST` (target name via const; unwraps Ok, re-raises Ghalti). Full semantics: [results.md](results.md).

## Completion

`RETURN_VALUE` pops, drops frame, unwraps Ok at the boundary, checks declared return type (errors pass free) · `POP_TOP` · `DUP_TOP` (currently unused — logged) · `HALT` pins ip at end.

> 🔍 Reading tip: when a test fails weirdly, dump bytecode with a 10-line script (compile → print instructions) and compare against this table. The [VM chapter](vm-stack-machine.md) shows the technique.

<div class="recap">
<p>52 opcodes, 8 families; every handler ≤ ~40 lines in vm.py.</p>
<p>Checked stores live in FAST/GLOBAL handlers — safety is baked into loads/stores.</p>
<p>Kwargs are marker constants, never raw strings.</p>
</div>
