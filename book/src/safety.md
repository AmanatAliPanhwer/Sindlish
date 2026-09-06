# Safety: What Sindlish Promises You

<div class="youarehere">📍 <strong>You are here:</strong> Part Four · Safety</div>

## 🌱 The hook

"Safety" in language design sounds abstract. It isn't. It answers one question:

> *When something goes wrong, how early do you find out — and how loud is it?*

Sindlish's answer is a ladder. Every rung is a moment where a bug can die, ordered from cheapest to most expensive. This chapter walks the whole ladder in plain terms, then gives you the enforcement map you'll use when hacking on the interpreter.

## 🧠 Mental model: the smoke-alarm principle

A good house has smoke alarms in every room — not one giant siren at the end of the night. Sindlish's pipeline *is* that alarm system: each stage checks what it can cheaply, and hands survivors to the next, stricter stage. A typo never reaches runtime; a missing list element can't be caught any earlier than the moment it happens.

```mermaid
flowchart TD
    A["🔥 Bug enters the program"] --> B{"Syntax problem?"}
    B -->|yes| C["💀 Dies at lexer/parser<br>cheapest, before anything runs"]
    B -->|no| D{"Name/scope/annotation lie?"}
    D -->|yes| E["💀 Dies at resolver<br>still before anything runs"]
    D -->|no| F{"Wrong kind of value<br>at a checked edge?"}
    F -->|yes| G["💀 Dies at VM check<br>exact line & column"]
    F -->|no| H["💥 Genuine failure<br>(index, zero-div)<br>= a VALUE, not a crash<br>until you consume it"]
```

Now each promise in detail.

## Promise 1 · Nothing crashes quietly

Every failure path ends in a `SindhiBaseError` with **file position and source text attached** — rendered as the caret display you've seen throughout this book. Python exceptions leaking to users are treated as interpreter bugs: `call_method` (`objects/base.py:249`) maps `TypeError → QisamJeGhalti`, `IndexError → IndexJeGhalti`, `ZeroDivisionError → ZeroVindJeGhalti`, everything else → `HalndeVaktGhalti`. Verified example of the worst ordinary accident — an out-of-bounds index:

```text
IndexJeGhalti: Fehrist jo index 10 hadd khaan bahar aahe.
Call Stack (most recent call last):
  --> Line 2, in main
    likh(l[10])
At Location:
   1 | fehrist[adad] l = [1,2,3]
   2 | likh(l[10])
           ^
```

No stack dumps, no hex addresses. Same for missing dict keys: `Key 'z' Lughat mein na mili.`

## Promise 2 · Recoverable errors are values, not surprises

The division you *expected* to fail shouldn't nuke your program. So all six arithmetic operators (`+ - * ^ / %`) are fallible: success returns the **raw value**, and any failure returns a **Result** — `Ok(value)` or `Ghalti(message)` — and Results are inert until consumed ([full chapter](results.md)). Ordering comparisons (`< <= > >=`) don't have that luxury — a kind mismatch raises `QisamJeGhalti` on the spot; `==`/`!=` are total booleans.

```sd
likh(10 / 0)              # verified: prints the error MESSAGE, program lives
r = 9 / 3?                # soft unwrap: value flows, errors keep flowing past
x = (9 / 0)!!             # panic unwrap: raise HERE, with captured traceback
fallback = (9 / 0).bachao(0)   # ✓ verified: fallback wins, program lives
```

Two verified subtleties worth tattooing somewhere visible:

1. **Postfix binds tight.** `a / b?` means `a / (b?)`, exactly like Rust's `a / b?`. Wrap the whole expression when you mean it: `(a / b)?`. Even `.method()` binds to the literal: un-parenthesized `9 / 0.bachao(0)` dies with `Nalo 'bachao' na milyo` because it calls a method on the *number 0*.
2. **Errors must be acknowledged.** A bare statement whose value is a Ghalti (e.g. `bhag(9, 0)`) raises it at the discard — errors demand acknowledgment. Storing, printing, or inspecting one keeps it a value.
3. **A Ghalti survives every boundary.** It passes through annotated parameters and typed slots untouched — only `Ok` unwraps on return. The error class raised on strict consumption is the class the failure was *born with* (`ZeroVindJeGhalti` for `% 0`, `QisamJeGhalti` for kind mismatches), with the creation-site traceback intact.

## Promise 3 · Bindings say what they mean

Three mechanisms, three different guarantees:

- **`pakko` constants** — once assigned, rebinding raises `'PI' pakko (const) aahe, eho badli natho saghjay.` Enforced for globals *and* function locals (via per-function slot metadata).
- **Type annotations** — checked twice (resolve-time + every store), per [Part Three](typing-model.md). They're opt-in: dynamic code stays dynamic.
- **Closure write discipline** — assigning into an enclosing function's variable without `bahari` is rejected at resolve time with instructions, killing the classic "why did my counter reset?" bug class before it exists.

## Promise 4 · Collections defend their borders

| Accident | Result |
|---|---|
| `l[99]` / `s[99]` | clean bounds error naming the bad index |
| `l[-1]` | allowed — negative indexing from the end |
| `d["missing"]` | `Key … na mili.` (use `.hasil(key, default)` for the gentle version) |
| `{[1,2]}` — unhashable set member | `QisamJeghalti` at build time, mapped from raw TypeError |
| `nums.wadha("str")` into `fehrist[adad]` | ⚠️ passes today — element pushes aren't re-checked yet |

That last row is the honest hole in the fence, logged and waiting for a contributor.

## Promise 5 · Truthiness can't blow up the VM

Conditions used to crash when fed dicts or sets. Now every condition, loop guard, and logical operator routes through one helper, `sd_truthy()` (`objects/base.py:163`): containers are true when non-empty; an `Ok` unwraps to its value, and a Ghalti parcel raises itself there — conditions strictly consume errors instead of guessing. One definition, zero special cases in the VM. (The pre-#33 "errors are truthy" behavior is gone.)

## The enforcement map

Where each promise physically lives — your cheat sheet for future work:

| Guarantee | Checked at | Source anchor |
|---|---|---|
| syntax sanity | lexer/parser | `frontend/lexer.py`, `frontend/parser.py` |
| names exist, annotations honest, closure writes declared | resolver walk | `analysis/resolver.py:104,136,294,415` |
| const/type on globals | every store | `backend/vm.py:_op_store_global` |
| const/type on locals | every store | `backend/vm.py:_op_store_fast` |
| param/return types | call boundaries | `backend/vm.py:_call_sd_function`, `_op_return_value` |
| errors-as-values | arithmetic wrapped at the VM | `backend/vm.py:_binary_op_result` (506), `objects/numbers.py:50` (`__truediv__`) |
| discarded Ghalti raises | top-level & block `POP_TOP` | `backend/vm.py:_op_pop_top`, `compiler.py:compile_ProgramNode` |
| Ghalti survives boundaries | typed params/slots | `backend/vm.py:_call_sd_function`, `_call_simple_function`, `_check_type` |
| exception laundering | dispatch boundary | `objects/base.py:call_method`, `backend/vm.py:_invoke`, `_op_call_method` |
| pretty reports | final render | `errors.py:ErrorReporter.report` |
| safe truthiness | all jumps/logic | `objects/base.py:sd_truthy` |

<div class="recap">
<p>Safety = alarms on a ladder: syntax → resolution → runtime edges → values.</p>
<p>Recoverable failures arrive as Ok/Ghalti VALUES; postfix binds tight, so parenthesize <code>(a/b)?</code>.</p>
<p><code>pakko</code>, annotations, and <code>bahari</code> give bindings meaning; collections check borders.</p>
<p>Known hole (element-push checks) is logged in roadmap/TODO.md.</p>
</div>
