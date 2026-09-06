# Add a Feature End-to-End

<div class="youarehere">📍 <strong>You are here:</strong> Part Eight · Living Here — 3 of 3</div>

Theory's done. Here's the full journey of a real change — adding an imaginary builtin-style keyword `lambi`-like function is too easy, so let's do something that touches **every stage**: a new binary operator `?&` ("and-if-not-null"… pick your own dream op; the steps are identical).

Use this as a checklist template for any feature.

## The 9-step ladder

| # | Stage | File | What to do |
|--:|---|---|---|
| 1 | Token | `frontend/tokens.py` | add `QAMP = auto()` to `TokenType` |
| 2 | Lexing | `frontend/lexer.py` | single char? → `_SINGLE_CHAR_TOKENS`. Compound? → `_scan_compound_operator` |
| 3 | Parse rule | `frontend/parser.py` | slot it into the precedence ladder (`parse_factor` for mul-strength) building `BinaryOpNode` |
| 4 | Resolve | `analysis/resolver.py` | usually nothing (generic visitor recurses); only touch if your node introduces names/scopes |
| 5 | Opcode | `backend/opcodes.py` | add `BINARY_QAMP = auto()` |
| 6 | Compile | `backend/compiler.py` | map token → opcode in `compile_BinaryOpNode`'s `op_map` |
| 7 | Execute | `backend/vm.py` | handler `_op_binary_qamp` + register in `_setup_dispatch_table` |
| 8 | Semantics | `objects/numbers.py` etc. | decide: dunder (`__qamp__`) or Result-returning like `/`? Follow [safety.md](safety.md)'s two-doors rule |
| 9 | Test + docs | `tests/`, this book | behavior test first (red), implement to green, update the relevant chapter |

## Worked micro-example: what each step looks like in diff form

```python
# tokens.py
QAMP = auto()                    # ?&

# lexer.py  (_scan_compound_operator)
if char == "?":
    if next_char == "&":
        self._advance(); self._advance()
        return Token(TokenType.QAMP, "?&", line, col)
    # fall through: plain QMARK handled elsewhere

# parser.py  (parse_factor loop tuple)
while self.peek().type in (MUL, DIV, MOD, QAMP):
    … left = BinaryOpNode(left, op, right) …

# compiler.py  (op_map)
TokenType.QAMP: OpCode.BINARY_QAMP,

# vm.py
def _op_binary_qamp(self, frame, arg, line, column):
    right = self._unwrap_val(self.pop(), line, column)
    left = self._unwrap_val(self.pop(), line, column)
    self.push(self._binary_op_result(left, right, "__qamp__", line, column))
self.dispatch_table[OpCode.BINARY_QAMP] = self._op_binary_qamp
```

## Choosing where semantics live

The fork in step 8 decides your feature's personality:

- **Always-succeeds operation** (concat, compare): plain dunder on the object classes; raise `QisamJeGhalti` for bad pairs. Cheap and simple.
- **Can-fail operation** (division-like): return `Ok/Ghalti` from the dunder so users get parcels, not crashes — mirror `__truediv__` in `objects/numbers.py:50`. A plain-raising dunder (`__add__` etc.) works too: `_binary_op_result` (`backend/vm.py:489`) wraps the raise into the same parcel. Ordering comparisons differ — kind mismatches **raise** `QisamJeGhalti` per the RFC in issue #33.

## Feature checklist before opening the PR

- [ ] tests red → green (`uv run pytest`)
- [ ] error paths produce *pretty* reports (run via CLI once)
- [ ] bytecode snapshot test if compile output changed — extend `tests/test_golden_bytecode.py` or expect red
- [ ] book chapter updated (grep `book/src/` for neighbors of your feature)
- [ ] if you found bugs along the way → `roadmap/TODO.md`

That's the whole loop: token → tree → slots → bytecode → stack → tests. Every chapter you've read exists to make one of those nine rows feel familiar.

<div class="recap">
<p>Nine stages, nine files, one checklist.</p>
<p>Pick dunder vs Result by asking "can it fail?"</p>
<p>Tests-first + book-update keeps docs true.</p>
</div>
