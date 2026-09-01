# The Built-in Type Zoo

<div class="youarehere">📍 <strong>You are here:</strong> Part Six · The Object Zoo — 3 of 3</div>

A quick tour of every concrete value type, its singleton, and where it lives. Method tables are complete — this doubles as the native-methods reference.

## The residents

| Type singleton | Sindlish name | Class | Home |
|---|---|---|---|
| `ADAD_TYPE` / `DAHAI_TYPE` | `adad` / `dahai` | `SdNumber` (int *and* float) | `objects/numbers.py` |
| `FAISLO_TYPE` | `faislo` | `SdBool` | `objects/numbers.py` |
| `LAFZ_TYPE` | `lafz` | `SdString` | `objects/strings.py` |
| `FEHRIST_TYPE` | `fehrist` | `SdList` | `objects/collections.py` |
| `LUGHAT_TYPE` | `lughat` | `SdDict` | `objects/collections.py` |
| `MAJMUO_TYPE` | `majmuo` | `SdSet` | `objects/collections.py` |
| `SILSILO_TYPE` | *(range results)* | `SdRange` — lazy! | `objects/collections.py:116` |
| `KHALI_TYPE` | `khali` | `SdNull` | `objects/core.py` |
| `KAAM_TYPE` | `kaam` | `SdFunction` (+ closure `Cell`) | `objects/core.py` |
| `RESULT_TYPE` | — | `SdResult` | `objects/core.py` |

Note the one-class-two-types trick: `SdNumber` picks `ADAD_TYPE` or `DAHAI_TYPE` at construction based on Python type of `.value` — ints and floats are siblings, not subclasses.

## Operator personalities (dunder side)

| Op | adad/dahai | lafz | fehrist | majmuo |
|---|---|---|---|---|
| `+` | add | concat | concat | union |
| `-` | sub | ✗ QisamJeGhalti | ✗ | difference |
| `*` | mul | repeat by adad | repeat by adad | intersection |
| `/` `%` | **→ Result** (Ok/Ghalti) | ✗ | ✗ | ✗ |
| `^` | pow | ✗ | ✗ | ✗ |
| `< <= > >=` | compare | lexicographic | ✗ | subset/superset checks |

Division/modulo returning Results instead of raising is the flagship design decision — see [results.md](results.md). Indexing (`[]`) is bounds-checked everywhere with clean errors; negative indexes work on lists, strings, and ranges.

## Native method registry (the `_methods` books)

Registered once at import time, bottom half of `collections.py`. Signature for each entry: plain function `(obj, args) → SdShey`.

**fehrist** — `wadha` append · `wadhayo` extend · `wajh` insert · `hata` remove · `kadh` pop · `saf` clear · `index` · `garn` count · `tarteeb` sort · `ulto` reverse · `nakal` copy

**lughat** — `hasil(key, dflt)` get · `syon` items · `cabeyon` keys · `raqamon` values · `syonkadh` popitem · `defaultrakh` setdefault · `update` · `kadh` pop · `saf` · `nakal`

**majmuo** — `addkar` add · `chad` discard · `hata` remove(strict) · `kadh` pop · `bade` union · `mushtarak` intersection · `farq` difference · `symmetric_farq` · `nandohisoahe` ⊆ · `wadohisoahe` ⊇ · `alaghahe` disjoint · `saf` · `nakal` · `update`

> 📝 Naming footnote: SLA dictionaries list both `bade` (ٻڌي) and `milap` (ميلاپ) as words for *union*, so mapping `milap → intersection` contradicted the source. **Decided in #32:** union keeps `bade`; intersection was renamed to `mushtarak` (مشترک, "shared/common") — matching the SLA's view of *milap* as a union word.

Mutating methods return the object itself (`return obj`) so chains like `nums.wadha(4).wadha(5)` read left-to-right; a few return `SdNull` instead (e.g. `SdList.append` the dunder-side helper). Consistency here is an easy first contribution.

## Adding your own method in 3 lines

```python
# objects/collections.py — bottom, next to the others
def fehrist_dojor(obj, args):  # our imaginary "double-join"
    obj.elements.extend(obj.elements)
    return obj


FEHRIST_TYPE.register_method("dojor", fehrist_dojor)
```

That's genuinely all — dispatch finds it via MRO lookup automatically. Add tests in `tests/test_list_methods.py` following existing style.

<div class="recap">
<p>10 types, 10 singletons; <code>SdNumber</code> covers int+float via construction-time choice.</p>
<p><code>/ %</code> are Result-returning; comparisons differ per family.</p>
<p>~35 registered natives; mutating ones conventionally return <code>obj</code>.</p>
<p>New method = one function + one <code>register_method</code> call.</p>
</div>
