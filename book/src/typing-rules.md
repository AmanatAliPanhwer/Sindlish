# Type Checks In Depth

<div class="youarehere">📍 <strong>You are here:</strong> Part Three · Hybrid Typing — 2 of 2</div>

This is the reference chapter: every rule, every matrix, every edge case — with the exact source anchor for each. Nothing here is speculative; everything below was executed against the interpreter while writing this book.

## The inference engine (such as it is)

`Resolver.infer_type(node)` (`resolver.py:44`) returns a `TokenType` or `None`:

| Node kind | Returns | Notes |
|---|---|---|
| `NumberNode` | `ADAD` if int, `DAHAI` if float | the int/float split happens here |
| `StringNode` | `LAFZ` | |
| `BoolNode` | `FAISLO` | |
| `NullNode` | `KHALI` | |
| `ListNode` / `DictNode` / `SetNode` | container type | *not* recursive into elements |
| annotated `VariableNode` | its slot's recorded type | only if slot metadata exists |
| anything else (`BinaryOpNode`, calls, casts…) | **`None`** | = "can't prove → defer" |

That last row is the load-bearing wall of hybrid typing. `_verify_assignment_types` treats `None` as *"unknown, let runtime decide"* — which is why `adad x = some_fn()` never trips Layer 1.

## Matrix 1 · scalar annotation vs literal

Declared type must equal inferred type exactly. There is no numeric widening: `ADAD ≠ DAHAI`, period.

| Declaration | Right side | Verdict |
|---|---|---|
| `adad x = 5` | int literal | ✓ |
| `adad x = 5.0` | float literal | ✗ resolve-time |
| `dahai x = 5.0` | ✓ | |
| `faislo f = sach` | ✓ | |
| `khali k = khali` | ✓ | |
| `lafz s = 42` | ✗ — verified message below | |

```text
QisamJeGhalti: Qisam natho mile: lafz khapyo paye, par adad milyo.
```

Source: `resolver.py:_verify_assignment_types`; the error carries no traceback because resolution precedes execution.

## Matrix 2 · collections & dicts, element-wise

For `fehrist[T]` / `majmuo[T]`, every element literal is inferred and compared to `T`. For `lughat[K, V]`, keys and values are checked separately (`resolver.py:114-134`).

```sd
fehrist[adad] nums = [1, 2, 3]        # ✓
lughat[lafz, adad] ages = {"ali": 30} # ✓
```

```sd
fehrist[adad] nums = [1, "oops"]      # ✗ points at the ELEMENT's position
```

```text
QisamJeGhalti: Fehrist je elements jo qisam adad hujjhan lazmi aahe,
par lafz milyo.
```

> ⚠️ Two honest footnotes:
> 1. The *runtime* twin of this check (`vm.py:_check_element_type`) hardcodes "Fehrist…" in its message even for dict/set violations — a known cosmetic bug, logged in `roadmap/TODO.md`.
> 2. Runtime element checks fire when an annotated collection is stored, so `fehrist[adad] l = fehrist("abc")` correctly dies at runtime with `…'LAFZ' milyo` (verified).

## Matrix 3 · casts — the explicit escape hatch

When types don't line up, you convert on purpose. Casts are parsed as datatype-token calls (`parser.py:390`) and become one opcode, `TYPECAST` (`vm.py:737`). Full verified behavior:

| Cast | From → Result | Notes |
|---|---|---|
| `adad("12.9")` | string → `12` | goes through float first, truncates toward zero |
| `adad(5.7)` | → `5` | truncation, not rounding |
| `adad(sach)` | bool → `1` / `koorh` → `0` | |
| `dahai(3)` | → `3.0` | |
| `dahai("2.5")` | → `2.5` | invalid strings raise clean `HalndeVaktGhalti`, never raw Python |
| `lafz(anything)` | → its printed form | `lafz(sach)` → `"sach"` |
| `faislo(0)` | → `koorh` (verified) | any non-empty value → `sach` |
| `fehrist("abc")` | → `["a","b","c"]` | strings explode per character |
| `majmuo([1,1,2])` | → `{1, 2}` | dedupe via hashing |

Casts auto-unwrap successful Results first; casting a *Ghalti* re-raises it (you can't cast an error into a value).

## Function edges in detail

Parameter annotations ride along inside `ParamNode.type`; binding checks happen in `VM._call_sd_function` (`vm.py:562`), return annotations in `_op_return_value` (`vm.py:857`). Three rules make these checks Result-friendly:

1. Success Results are unwrapped before comparing (so returning `ok(5)` from a `-> adad` function is fine).
2. Ghalti Results pass through untouched — errors are always allowed to travel.
3. Mismatch messages name the function: `Wapas khe 'adad' khapyo paye, par jor mein 'lafz' milyo.`

Defaults are evaluated **once at definition time** (Python semantics) and carried on the `SdFunction` object — see [compiler.md](compiler.md).

## Constants (`pakko`) at both levels

- **Globals:** the record stores `is_const`; any later `STORE_GLOBAL` for that name raises `'PI' pakko (const) aahe, eho badli natho saghjay.` — verified above in [the model chapter](typing-model.md)'s sibling tests.
- **Locals:** per-function `slot_metadata` snapshots enforce the same rule via `STORE_FAST`.

One nuance from the source (`vm.py:_op_store_global`): a const record whose value is still `None` may be initialized once; after that, it locks.

## Edge cases worth knowing by heart

1. **Rebinding an annotated variable keeps its belt forever.** Metadata lives on the slot/global record, not the assignment site.
2. **The nested-block redeclaration bug** — typed shadowing across blocks corrupts metadata and can make *earlier* lines fail. See [resolver.md](resolver.md) Walkthrough 2 and `roadmap/TODO.md` before relying on it.
3. **REPL parity:** global consts/types are enforced identically in REPL sessions because top-level assignments always compile through `STORE_GLOBAL`'s checked path.
4. **`khali` as annotation** is accepted syntactically but there's no cast target named `khali` — casting to it raises `Na-maloom typecast target`.
5. **Truthiness ignores belts:** conditions use `sd_truthy()` on whatever value shows up; typing never changes control flow semantics.

## Where to change what

| Task | File : focus |
|---|---|
| add a new scalar type check | `vm.py` `_check_type` + resolver matrices |
| widen inference (e.g. fold constants) | `resolver.py` `infer_type` |
| fix misleading collection messages | `vm.py` `_check_element_type` (bug logged) |
| allow `.wadha()` element enforcement | would live in method registration + slot metadata lookup |

<div class="recap">
<p>Inference proves literals & known slots only; <code>None</code> means "defer to runtime".</p>
<p>No widening: ADAD ≠ DAHAI ever.</p>
<p>Casts cover all conversions; they unwrap Ok, re-raise Ghalti, and never leak Python exceptions.</p>
<p>Function edges check at call/return; bodies stay dynamic.</p>
<p><code>pakko</code> enforced for globals and locals alike.</p>
</div>
