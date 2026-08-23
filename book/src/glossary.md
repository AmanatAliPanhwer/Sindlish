# The Sindhi Dictionary

<div class="youarehere">📍 <strong>You are here:</strong> Part Zero · Settle In</div>

Sindlish reads keywords from **Romanized Sindhi**. You never need to learn the language to hack on the interpreter — but knowing that `wapas` means *"back"* makes `RETURN_VALUE` feel inevitable instead of arbitrary. Bookmark this chapter; everything else links back here.

## Keywords

| Sindlish | Means… | Role | Python cousin |
|---|---|---|---|
| `agar` | *if* | conditional | `if` |
| `yawari` | *otherwise* | else-if branch | `elif` |
| `warna` | *or else* | fallback branch | `else` |
| `jistain` | *as long as* | while loop | `while` |
| `har … mein` | *every … in* | for-each loop | `for x in y` |
| `tor` | *break* | exit loop early | `break` |
| `jari` | *carry on* | skip to next iteration | `continue` |
| `kaam` | *work* | function definition | `def` |
| `wapas` | *give back* | return value | `return` |
| `aalmi` | *worldly* | global declaration | `global` |
| `bahari` | *outer* | nonlocal declaration | `nonlocal` |
| `pakko` | *firm / fixed* | constant binding | `final` |
| `mein` | *in* | membership / iteration | `in` |
| `likh` | *write!* | print to stdout | `print` |
| `puch` | *ask* | read from stdin | `input` |

## Type names

| Sindlish | Means… | Is… |
|---|---|---|
| `adad` | *number* | integer (`int`) |
| `dahai` | *decimal* | float (`float`) |
| `lafz` | *word* | string (`str`) |
| `faislo` | *decision* | boolean (`bool`) |
| `sach` | *truth* | `true` |
| `koorh` | *falsehood* | `false` |
| `khali` | *empty* | null (`None`) |
| `fehrist` | *catalogue* | list |
| `lughat` | *dictionary* | dict |
| `majmuo` | *collection* | set |
| `ok(value)` | — | wrap a success Result |
| `ghalti(msg)` | *mistake* | wrap an error Result |
| `kharabi(msg)` | *brokenness* | panic immediately |

## The Result toolbox

| Form | Reads as | Does |
|---|---|---|
| `r?` | *"if it went well, give me the value"* | soft unwrap; error passes through |
| `r!!` | *"it better have gone well"* | unwrap or crash |
| `r.bachao(fb)` | *rescue* | error → use fallback `fb` |
| `r.lazmi(msg)` | *necessarily* | error → crash with your message |

## Error names — they're sentences

Every error class is a tiny Sindhi sentence ending in **Ghalti** (*mistake*):

| Class | Literal reading | Fires when |
|---|---|---|
| `LikhaiJeGhalti` | *writing-mistake* | lexer/parser rejects syntax |
| `NaleJeGhalti` | *name-mistake* | unknown variable/function |
| `QisamJeGhalti` | *type-mistake* | wrong kind of value |
| `HalndeVaktGhalti` | *right-now-mistake* | runtime violations, `pakko` reassignment, panic |
| `ZeroVindJeGhalti` | *zero-point-mistake* | divide/mod by zero |
| `IndexJeGhalti` | *index-mistake* | out-of-bounds access |

## Interpreter-internal names you'll meet

The Python side prefixes everything with **Sd**:

| Internal name | Built from | What it is |
|---|---|---|
| `SdShey` | *shey* = thing | base class of every runtime value |
| `SdType` | — | the metaclass/type object (owns MRO) |
| `SdNumber` | `adad` | int/float box |
| `SdString` | `lafz` | string box |
| `SdBool` | `faislo` | boolean box |
| `SdNull` | `khali` | null singleton-ish |
| `SdList` / `SdDict` / `SdSet` | `fehrist`/`lughat`/`majmuo` | collections |
| `SdResult` | — | Ok/Ghalti enum value |
| `SdFunction` | `kaam` | compiled function object |
| `SdRange` | *silsilo* = series | lazy range object |

<div class="recap">
<p>Keywords are Romanized Sindhi; <code>ghalti</code> = mistake, <code>shey</code> = thing.</p>
<p>Error classes are readable sentences (<code>QisamJeGhalti</code> = type-mistake).</p>
<p>Interpreter internals prefix with <code>Sd</code>; types keep their Sindhi names internally (ADAD, LAFZ…).</p>
</div>
