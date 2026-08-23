# Testing the Interpreter

<div class="youarehere">📍 <strong>You are here:</strong> Part Eight · Living Here — 2 of 3</div>

## 🧠 The shape of the suite

25 pytest files, one per feature area (`test_arithmetic.py`, `test_closures.py`, `test_typed_variables.py`, …). Run everything with:

```bash
uv run pytest        # or: python -m pytest
```

The magic is in `tests/conftest.py` — a 100-line harness every test shares.

## 🔬 The harness

```python
vm, out = run("adad x = 5  likh(x)")  # full pipeline, stdout captured
assert get_variable_value(vm, "x") == 5
```

- **`run(code)`** executes the *real* five-stage pipeline (no mocks) and returns the VM plus captured output. Tests assert on end-state values and printed text — behavior, not implementation.
- **`get_variable_value(vm, name)`** prefers globals records, falls back to main-frame slots.
- **`extract_value(obj)`** recursively unwraps `SdShey`s into plain Python (`SdList → list`, Ok parcels unwrap, Ghalti stays a Result so you can assert on failure states).

Error-path tests use `pytest.raises` around `run()`:

```python
with pytest.raises(QisamJeGhalti):
    run("lafz s = 42")
```

## Conventions that keep the suite healthy

1. **Bug fixes earn regression tests** — `tests/test_bugfixes.py` mirrors `roadmap/TODO.md`'s fixed-items list; every `[x]` there has a matching test here.
2. **One concept per test function**, Sindlish snippet as a triple-quoted string at the top — readable even for non-Pythonistas.
3. **Snapshot bytecode when compiler behavior matters**: compile in the test and compare `(opcode.name, arg)` lists against expected tuples (see [opcodes.md](opcodes.md) for the vocabulary).


> 💡 When you fix any bug from this book's "known sharp edges" callouts, add the failing snippet *as* the regression test before fixing — cheapest insurance in the repo.

<div class="recap">
<p>Behavior-level tests over the real pipeline via <code>conftest.run()</code>.</p>
<p><code>test_bugfixes.py</code> pairs 1:1 with fixed TODO items.</p>
<p>Hardcoded sys.path is a logged wart.</p>
</div>
