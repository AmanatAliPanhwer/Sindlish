# The Lexer: Characters → Tokens

<div class="youarehere">📍 <strong>You are here:</strong> Part Two · Front of House — stage 1 of 5</div>

## 🌱 The hook

Before anyone can *understand* your program, something must simply *read* it. That's the lexer (`interpreter/frontend/lexer.py`, ~272 lines): it turns a string of characters into a list of labeled pieces called **tokens**. It doesn't know what a program *means* — only what its *words* are.

Think of it as **sorting mail**: letters arrive one character at a time; the sorter groups them into envelopes (numbers, words, symbols), stamps each envelope with where it came from (line & column), and passes the tray onward. No opinions about grammar yet.

## 🧠 Mental model: every token knows its home address

```python
# interpreter/frontend/tokens.py:87
@dataclass(frozen=True, slots=True)
class Token:
    type: TokenType  # which category (ADAD, PLUS, IDENTIFIER…)
    value: Any  # the actual payload ('x', 3, '+', "hi")
    line: int  # 1-based
    column: int  # 1-based
```

That `(line, column)` pair looks boring and is actually heroic: it's how every future error message points at *exactly* your typo instead of shrugging at the whole file.

Token categories live in `TokenType` (`tokens.py:13`) — roughly 60 of them, grouped as data types, keywords, operators, and symbols. The Sindhi keyword → token mapping is one flat dict in `keywords.py:11`, consulted by the identifier scanner:

```python
# interpreter/frontend/keywords.py:11 (excerpt)
KEYWORDS: dict[str, TokenType] = {
    "agar": TokenType.AGAR,
    "kaam": TokenType.KAAM,
    "wapas": TokenType.WAPAS,
    # …30 entries total
}
```

## 🔬 Under the hood

### The main loop: a decision tree

`generate_tokens()` (`lexer.py:267`) is one loop with a cascade of character tests:

```mermaid
flowchart TD
    A["char = peek()"] --> B{"space / tab?"}
    B -->|yes| A2["skip"] --> A
    B --> no --> C{"newline?"}
    C -->|yes| C1["emit NEWLINE token"] --> A
    C --> no --> D{"digit, or . followed by digit?"}
    D -->|yes| D1["_scan_number()"]
    D --> no --> E{"# ?"}
    E -->|yes| E1["skip to end of line"] --> A
    E --> no --> F{'" or ' ?'}
    F -->|yes| F1["_scan_string()"]
    F --> no --> G{"letter or _ ?"}
    G -->|yes| G1["_scan_identifier()<br>(then keyword lookup)"]
    G --> no --> H{"in * / > < = ! ?"}
    H -->|yes| H1["_scan_compound_operator()"]
    H --> no --> I{"single-char table<br>+ - % ^ ? ( ) { } [ ] : , ."}
    I -->|yes| I1["emit it"]
    I --> no --> J["💥 LikhaiJeGhalti:<br>'Illegal akhar X'"]
```

Three design details deserve a slow look.

### 1 · Numbers: counting dots so `3.14` works but `3.1.4` doesn't

`_scan_number()` (`lexer.py:136`) consumes digits while allowing **at most one** dot:

```python
if self._peek() == ".":
    if dot_count == 1:
        break  # second dot ends the number
    dot_count += 1
```

The dot count then decides the payload type — `int(num)` for zero dots (`ADAD`), `float(num)` otherwise (`DAHAI`). A leading `.5` also works, because the dispatch test accepts `.` when *followed by* a digit (`lexer.py:290`).

### 2 · Strings: escapes done by hand (and why)

Strings support both `"…"`/`'…'` and triple quotes for multiline text. Escapes are decoded by a small hand-written table (`lexer.py:13`):

```python
_ESCAPE_MAP = {"n": "\n", "t": "\t", '"': '"', "\\": "\\", …}
```

Why not Python's built-in escape decoding? Because the easy route once mangled non-ASCII text — `"سلام"` became mojibake. The hand-rolled `_unescape()` only touches backslash pairs and copies everything else byte-for-byte. This is recorded as fixed bug #2 in `roadmap/TODO.md`; remember it as a cautionary tale about "just use the stdlib" shortcuts in language tooling.

An unterminated literal raises immediately, with the *opening* position attached:

```python
raise LikhaiJeGhalti(
    f"String literal band natho thayo; '{quote}' na milyo.",
    start_line,
    start_col,
    self.code,
)
```

### 3 · Compound operators: one function, seven decisions

Characters like `*`, `/`, `=`, `!` can start either a one- *or* two-character operator, so they get a dedicated method (`lexer.py:238`). Its decision table, including two lovely traps:

| Sees | Next | Emits | Note |
|---|---|---|---|
| `*` | `*` | `DBLSTAR` | kwargs marker |
| `/` | `*` | *(nothing)* | starts block comment `/* … */` |
| `=` | `=` | `EQEQ` | equality, not assignment |
| `!` | `!` | `BANGBANG` | Result panic-unwrap |
| `!` | `=` | `NOTEQ` | |
| `!` | other | `NOT` | logical not |

Everything else single-char comes from the plain dict `_SINGLE_CHAR_TOKENS` (`lexer.py:47`) — that's why `+ - % ^ ? ( ) { } [ ] : , .` need no special code path.

## Watching it work

Save this to `demo.sd` and run `python main.py tokens demo.sd`:

```sd
adad jawab = 12 ^ 2
```

```text
ADAD('adad')
IDENTIFIER('jawab')
EQ('=')
ADAD(12)
POW('^')
ADAD(2)
NEWLINE('\n')
EOF(None)
```

Read the output like a sentence: *"type-word, name, gets, twelve, power-of, two."* Notice:

- `adad` arrived as token type `ADAD` — keyword lookup happened during scanning.
- Numbers already carry real Python values (`12`, not `'12'`).
- Every file ends with `EOF(None)` — the parser's guaranteed stopping signal.
- Comments never appear; they were skipped en route.

## When the lexer says no

Only three things can go wrong here, and each raises `LikhaiJeGhalti` (*writing-mistake*) instantly:

1. an unknown character (`Illegal akhar @`),
2. an unterminated string/triple-quote,
3. an unterminated `/*` block comment.

Everything grammatical — mismatched parens, missing braces — is *not* its business. That's the next chapter's problem.

<div class="recap">
<p>Lexer = mail sorter: characters → <code>Token(type, value, line, column)</code>, zero grammar knowledge.</p>
<p>Keywords become their own token types during scanning via <code>keywords.py</code>.</p>
<p>Compound operators (<code>== != !! /* */ ** >= <=</code>) share one lookahead-driven scanner.</p>
<p>Escapes are hand-decoded to keep Unicode intact — a lesson from a past mojibake bug.</p>
<p>It rejects exactly 3 things: illegal characters, unterminated strings, unterminated comments.</p>
</div>
