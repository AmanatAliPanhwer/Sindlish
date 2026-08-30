# The Compiler: AST → Bytecode

<div class="youarehere">📍 <strong>You are here:</strong> Part Seven · The Engine Room — 1 of 4</div>

## 🌱 The hook

The annotated AST still speaks in trees; CPUs speak in lists. The compiler (`interpreter/backend/compiler.py`, ~500 lines) flattens the tree into **bytecode** — a flat list of `(opcode, arg)` tuples plus a **constant pool** of pre-built values. It's a mechanical translator: no decisions, no surprises, deterministic output you can snapshot in tests. These exact listings are pinned in `tests/test_golden_bytecode.py` — any change to emission or operand shapes turns those tests red.

## 🧠 Mental model: post-order walk

Compiling an expression means: *compile children first (left to right), then emit the parent's opcode*. That's it. Precedence was already baked into the tree's shape by the parser, so the compiler never thinks about it again:

```sd
adad x = 3 + 4 * 2
```

becomes the verified listing below — operands in evaluation order, operations after their operands (postfix notation):

```text
 0  LOAD_CONST     0   ; SdNumber(3)
 1  LOAD_CONST     1   ; SdNumber(4)
 2  LOAD_CONST     2   ; SdNumber(2)
 3  BINARY_MUL
 4  BINARY_ADD
 5  STORE_GLOBAL   (name='x', is_const=False, type=ADAD, elem=None)
 6  HALT
```

Read it like RPN: `3 4 2 * +`.

## 🔬 Under the hood

### Emission & the constant pool

Two tiny helpers run everything: `emit(opcode, arg)` appends `(opcode, arg)` and records its line/column for future error reports; `add_const(value)` dedupes values so `"likh"` or `SdNumber(1)` appear once and get shared indexes.

### Jumps: emit now, patch later

The one genuinely tricky part of any compiler is jumping *forward* to positions that don't exist yet. Sindlish uses classic backpatching — emit with a dummy target, remember the slot, patch when known:

```python
jump_idx = self.emit(OpCode.JUMP_IF_FALSE, 0)   # placeholder
… compile body …
self.instructions[jump_idx] = (OpCode.JUMP_IF_FALSE, len(self.instructions))
```

`agar/yawari/warna` chains keep a list of "jump to end" slots and patch them all once the end is reached. Loops are simpler: backward jumps already know their target (the top).

Verified shape of `agar 5 > 3 { likh(1) } warna { likh(2) }`:

```text
 0 LOAD_CONST 5      3 JUMP_IF_FALSE →8    6 POP_TOP        9 CALL_FUNCTION likh
 1 LOAD_CONST 3      4 LOAD_CONST 1        7 JUMP_ABSOLUTE →11   10 POP_TOP
 2 COMPARE_GT        5 CALL_FUNCTION likh  8 LOAD_CONST 2   11 HALT
```

### Loops & the loop stack

While compiling a loop body the compiler keeps `(start, exit_jump_slot, break_slots)` on `self.loop_stack`. `tor` emits an absolute jump whose target gets patched at loop end; `jari` jumps straight to the remembered start (for `har` loops that means *next item*, since the iterator lives just above the start).

### Functions compile into their own pocket universe

`compile_FunctionNode` swaps out `self.instructions` for a fresh list, compiles the body there (with an implicit `PUSH_NULL → MAKE_OK → RETURN_VALUE` tail), restores state, then stores the resulting `SdFunction` into the *parent's* constant pool. The function value reaches runtime via `LOAD_CONST` + `MAKE_FUNCTION` (which binds evaluated defaults and links closure cells) followed by `STORE_GLOBAL` — functions are globals, per [resolver.md](resolver.md).

### Returns always wrap

`wapas expr` compiles to `<expr>; MAKE_OK; RETURN_VALUE`. The auto-wrap pairs with the VM's boundary rule: returning unwraps Ok, passes Ghalti untouched ([results.md](results.md)). Bare `wapas` returns `Ok(khali)`.

### Statement expressions must not leak

A bare expression statement leaves a value on the stack; `compile_BlockNode` appends `POP_TOP` after such statements so the stack stays balanced. In function bodies, the final expression instead gets `MAKE_OK; RETURN_VALUE` — Ruby-style implicit returns.

<div class="recap">
<p>Post-order emission; precedence lives in the tree, not here.</p>
<p><code>add_const</code> dedupes; <code>line_col_map</code> remembers positions for errors.</p>
<p>Forward jumps = emit-placeholder + backpatch; loops use a stack for break/continue targets.</p>
<p>Functions compile to separate instruction arrays stored as constants.</p>
</div>
