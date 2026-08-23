"""
Create the single parent Refactor issue with all tasks as GitHub sub-issues.

Usage:  python tools/create_refactor_parent.py

Requires: gh CLI authenticated (gh auth login).
Idempotent-ish: skips sub-issues whose exact title already exists (open or closed).
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

GH = r"C:\Program Files\GitHub CLI\gh.exe"
if not Path(GH).exists():
    GH = "gh"


def gh(*args):
    result = subprocess.run(
        [GH, *args], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        print(f"gh failed: {args[:3]}...\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()


def gh_json(*args):
    return json.loads(gh(*args))


TASKS = [
    # (phase, extra_labels, title, body)
    (
        "phase-0",
        ["refactor"],
        "Golden bytecode snapshot harness - build the safety net",
        """Part of the interpreter refactor plan. Before touching any code we need a **golden test** that freezes current compiler output so later phases can prove they changed nothing.

**Scope**
- New `tests/test_golden_bytecode.py`
- Harness compiles ~10 representative programs through Lexer -> Parser -> Resolver -> Compiler and asserts exact `(opcode.name, arg)` listings (technique shown in `book/src/compiler.md`)
- Programs should cover: arithmetic precedence, agar/yawari/warna, jistain loop, har loop, function def+call, closures (`bahari`), typed declarations, Result ops (`?`, `!!`, `.bachao`, `.lazmi`), collections, casts

**Acceptance criteria**
- [ ] Test file exists and passes against current HEAD
- [ ] Adding a trailing comment changes nothing; changing an opcode fails loudly
- [ ] Book chapter `compiler.md` gets a one-line pointer to this test""",
    ),
    (
        "phase-0",
        ["bug", "good-first-issue"],
        "Fix conftest.py hardcoded machine-specific sys.path",
        """`tests/conftest.py` line 12:

```python
sys.path.insert(0, "d:/Code/Sindlish")
```

This breaks pytest on any machine that isn't this exact checkout path.

**Fix**: derive from the file location:

```python
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

**Acceptance criteria**
- [ ] Suite passes from repo root on any path/drive
- [ ] No other hardcoded absolute paths remain in `tests/`
- [ ] Book `testing.md` known-wart note removed""",
    ),
    (
        "phase-1",
        ["refactor"],
        "Remove dead print pipeline (TokenType.LIKH -> PrintNode -> PRINT_ITEM)",
        """`"likh"` is missing from `KEYWORDS` (`interpreter/frontend/keywords.py`), so the lexer always emits `IDENTIFIER('likh')` and printing works purely as a builtin call (`CallNode` -> `CALL_FUNCTION` -> `SimpleBuiltins.likh`).

The entire dedicated statement path is unreachable dead code kept in sync by hand:
- `tokens.py` `LIKH = auto()`
- `parser.py` LIKH branch in `parse_statement` + `parse_print()`
- `ast_nodes.py` `PrintNode`
- `resolver.py` `resolve_PrintNode`
- `compiler.py` `compile_PrintNode`
- `opcodes.py` `PRINT_ITEM`
- `vm.py` dispatch entry + `_op_print_item`

**Decision within this issue**: either delete the chain (recommended; printing stays a function) or add `"likh": TokenType.LIKH` to KEYWORDS to make it a real statement. Default: delete.

**Acceptance criteria**
- [ ] Chain deleted (or keyword added) with suite green incl. golden bytecode test
- [ ] `roadmap/TODO.md` item ticked
- [ ] Book `lexer.md` sharp-eyed callout updated to match reality""",
    ),
    (
        "phase-1",
        ["refactor"],
        "Remove vestigial machinery (refcounts, unused opcodes, env fields)",
        """AI-generated leftovers identified during docs work:
- `SdShey._ref_count` / `incref()` / `decref()` / `_dealloc()` - never called; CPython GC does the job (`objects/base.py`)
- `OpCode.DUP_TOP` + `_op_dup_top` - emitted nowhere
- `Environment.global_names` / `nonlocal_names` - written nowhere meaningful (`runtime/env.py`)

**Acceptance criteria**
- [ ] All removed, suite green
- [ ] grep confirms no remaining references
- [ ] Book `object-model.md` refcount paragraph updated ("removed in refactor")""",
    ),
    (
        "phase-2",
        ["bug", "good-first-issue"],
        "main.py ast crashes on any program containing a kaam",
        """`python main.py ast journey.sd` raises:

```
AttributeError: 'FunctionNode' object has no attribute 'slot_metadata'
```

`FunctionNode.__repr__` iterates every `__slots__` name, but `slot_metadata` is declared yet never initialized in `FunctionNode.__init__` - the resolver assigns it later, and the CLI prints pre-resolution ASTs.

**Fix**: initialize `self.slot_metadata = {}` alongside `cell_slots`/`free_slots`.

**Acceptance criteria**
- [ ] Regression test: repr of a parsed program containing a function
- [ ] `roadmap/TODO.md` ticked""",
    ),
    (
        "phase-2",
        ["bug"],
        "MRO puts self LAST - ancestors override descendants",
        """`SdType._compute_mro` returns `tuple(result) + (self,)` (`interpreter/objects/base.py`). Python's C3 merges `(self,)` as the **first sequence**, so self must come first.

Verified consequence:

```python
A.register_method("hello", from_a)
B = SdType("B", bases=(A,))
B.register_method("hello", from_b)
B.lookup_method("hello")   # -> A.hello (!!)
```

Overriding is structurally inverted for every type using inheritance. Currently dormant (no builtin sets `bases`) but load-bearing for the planned `jamaat` classes feature.

**Fix direction**: merge_seq = `[(self,)] + [base.mro for base in bases]`; result[0] must be self.

**Acceptance criteria**
- [ ] Red test first: diamond D(B,C) -> mro `(D, B, C, A)`; descendant override wins
- [ ] Golden bytecode test unaffected
- [ ] `roadmap/TODO.md` ticked; book `mro-c3.md` sharp-edge section rewritten as "how it works\"""",
    ),
    (
        "phase-2",
        ["bug"],
        "Inconsistent inheritance silently truncates the MRO",
        """Companion to the self-last MRO bug. `_c3_merge` has no failure path: when no valid head exists it breaks and returns a partial order.

Verified worst case:

```python
F, G unrelated; FA(F,G); GA(G,F); HA(FA,GA)
HA.mro == (HA,)      # both parents silently gone!
```

Python raises `TypeError: Cannot create a consistent method resolution order (MRO) for bases ...`. The old developer-docs even documented a RuntimeError branch that doesn't exist in the code.

**Fix**: raise a clean error when a merge pass finds no candidate head. Land together with (or immediately after) the ordering fix.

**Acceptance criteria**
- [ ] Red test: HA case raises instead of truncating
- [ ] Error message mirrors Python's wording style
- [ ] Book `mro-c3.md` updated""",
    ),
    (
        "phase-2",
        ["bug"],
        "Ghalti Results cannot cross typed variable slots ('RESULT' milyo)",
        """`VM._check_type` unwraps only *Ok* results. An Err flowing through `expr?` into an explicitly-typed variable hits the type comparison:

```
kaam bhag(adad a, adad b) {
    dahai r = a / b?
    wapas r
}
bhag(9, 0)
-> QisamJeGhalti: 'dahai' qisam laai dahai khapyo paye, par 'RESULT' milyo.
```

Expected: the Ghalti keeps propagating as a value (untyped slots already do this correctly).

**Fix direction**: early-return True when `isinstance(value, SdResult) and value.is_error()`.

**Acceptance criteria**
- [ ] Repro above surfaces ZeroVindJeGhalti at top level
- [ ] Regression test in `tests/test_typed_variables.py`
- [ ] Book `results.md` warning box removed/updated; TODO ticked""",
    ),
    (
        "phase-2",
        ["bug", "good-first-issue"],
        'Dict/set element-type violations say "Fehrist"',
        """`VM._check_element_type` (`interpreter/backend/vm.py`) hardcodes "Fehrist je elements jo qisam ..." in every message branch. Verified:

```
lughat[lafz, adad] ages = {"ali": "x"}
-> QisamJeGhalti: Fehrist je elements jo qisam 'adad' hujjhan lazmi aahe ...
```

...for a *lughat*. Same for majmuo.

**Fix**: thread the container name through (or per-container templates).

**Acceptance criteria**
- [ ] Messages say fehrist/lughat/majmuo correctly
- [ ] Tests assert each container variant""",
    ),
    (
        "phase-2",
        ["bug"],
        "Typed redeclaration in nested block corrupts enclosing slot metadata",
        """Inside a function, block writes reuse the nearest binding (`_find` returns outer scope; no true shadowing). Combined with explicit types:

```
kaam test() {
    adad x = 1
    agar sach {
        lafz x = "hi"
    }
    likh(x)
}
test()
-> QisamJeGhalti pointing at line 2, BEFORE anything ran!
```

The inner declaration overwrites `slot_metadata[slot]` for the whole function.

**Design decision needed inside the PR**: (a) define a fresh slot when the found scope differs from the current one (real shadowing), or (b) keep first-explicit-type-wins metadata merge. Prefer (a) - matches contributor intuition and Python mental models.

**Acceptance criteria**
- [ ] Chosen semantics documented in `book/src/resolver.md` Walkthrough 2
- [ ] Red->green regression tests for both shadowing and non-shadow cases
- [ ] TODO ticked""",
    ),
    (
        "phase-2",
        ["decision"],
        "majmuo method names: milap/bade vs SLA dictionary",
        """From `roadmap/TODO.md`: SLA dictionaries list both bade and milap as words for **union**; official intersection terms are cutting/crossing words. Current mapping: `bade -> union`, `milap -> intersection` (contradicts SLA).

**Options**
1. Keep as-is, document rationale
2. Rename intersection -> `mushtarak` (shared/common)
3. Keep both as aliases (union: bade+milap; intersection: mushtarak)

**Output**: a written decision in this issue + implementation PR if renaming.""",
    ),
    (
        "phase-3",
        ["refactor"],
        "Unify error philosophy across operators",
        """Epic. Today `/ %` return Results while `+ - ^` raise QisamJeGhalti directly - two philosophies side by side (see `roadmap/TODO.md` Quality section and `book/src/safety.md` two-doors rule).

**Deliverables**
1. A short RFC comment in this issue deciding, per operator family: parcel vs raise
2. Implementation of the decision
3. Table in `book/src/safety.md` enforcement map updated to match reality
4. Tests for each family's contract (Ok/Ghalti vs exception class)

**Ground rule**: pure Phase 3 = aligning existing behaviors to the decision; no new features.""",
    ),
    (
        "phase-4",
        ["refactor"],
        "Frontend cleanup: lexer tables, parser ladder, AST init consistency",
        """Readability pass over `frontend/`, guided by `book/src/lexer.md` + `parser.md`.

**Scope**
- Lexer: group compound-operator scanner into data-driven table where practical; docstrings match behavior
- Parser: name the precedence-ladder methods consistently; extract magic token-tuples to module constants
- AST: **every** node initializes **every** `__slots__` member in `__init__` (prevents the FunctionNode.repr crash class forever)

**Acceptance criteria**
- [ ] Suite + golden bytecode green (byte-identical output)
- [ ] No behavior diffs in golden snapshots
- [ ] Book chapters still accurate (anchors may shift; update line refs)""",
    ),
    (
        "phase-5",
        ["refactor"],
        "Resolver restructure: split modules + block-scope semantics",
        """Biggest cognitive-load hotspot (~460 lines, everything mixed). Guided by `book/src/resolver.md`.

**Split proposal**
- `analysis/scopes.py` - scope stack, slot allocation, symbol table
- `analysis/closures.py` - _FnRec, capture registration, bahari/aalmi
- `analysis/typecheck.py` - infer_type + verify matrices
- `resolver.py` becomes thin visitor orchestrating them

**Semantics work** (after the nested-block metadata bug lands): decide the final block-scoping story and encode it once, here.

**Acceptance criteria**
- [ ] Split lands with zero behavior change (except agreed scoping fix)
- [ ] Each module <= ~200 lines with chapter-linked docstring
- [ ] LSP symbols output unchanged (VS Code extension still works)""",
    ),
    (
        "phase-6",
        ["refactor"],
        "VM hygiene: dispatch generation + operand encoding consistency",
        """Guided by `book/src/opcodes.md` + `vm-stack-machine.md`.

**Scope**
- Build dispatch table programmatically from handler names (kill the 50-line manual dict)
- Standardize operand shapes: document which opcodes take int / const-idx / tuple, enforce at emit time in Compiler
- Extract call-binding logic (`_call_sd_function`) into its own module/function
- Consistent pop helpers

**Acceptance criteria**
- [ ] Byte-identical golden bytecode + suite green
- [ ] Every opcode documented in `opcodes.md` has exactly one source anchor that matches post-refactor""",
    ),
    (
        "phase-7",
        ["perf"],
        "Benchmark-guided optimization pass",
        """Only after the resolver split and VM hygiene land. Use `bench/run_benchmarks.py`; no optimization without a measurement.

**Protocol per candidate**
1. Benchmark baseline recorded in PR
2. Hypothesis stated (which hot loop / allocation)
3. Change, re-benchmark, show delta
4. Golden bytecode + suite stay green

**Likely candidates** (unverified): O(n^2) constant-pool dedupe in `add_const`; dispatch dict lookup per step; `_unwrap_val` isinstance chains; SdNumber boxing churn.""",
    ),
]

PARENT_BODY = """# Refactor: Sindlish interpreter v0.2

One parent issue to rule the whole refactor. Every task below is a **sub-issue** - one sub-issue = one branch = one PR using `.github/PULL_REQUEST_TEMPLATE.md`.

## Ground rules
1. Tests green before & after every step (`uv run pytest`) - no step larger than one PR.
2. Behavior-preserving first; behavior changes get their own issue.
3. Each PR updates the affected `book/src/` chapter and ticks `roadmap/TODO.md`.

## Reading before working
| Phase | Read first |
|---|---|
| 0-2 | `book/src/journey.md`, then the chapter cited in the issue |
| 3 | `book/src/safety.md`, `results.md` |
| 4 | `book/src/lexer.md`, `parser.md` |
| 5 | `book/src/resolver.md` |
| 6-7 | `book/src/vm-stack-machine.md`, `opcodes.md` |

## Phase order
0 Safety net -> 1 Dead weight -> 2 Correctness -> 3 Error philosophy -> 4 Frontend -> 5 Resolver -> 6 VM hygiene -> 7 Perf

## Task tracker
(Sub-issues are attached to this issue automatically; use this checklist for phase-level progress.)

- [ ] Phase 0 - safety net
- [ ] Phase 1 - dead weight
- [ ] Phase 2 - correctness fixes
- [ ] Phase 3 - error philosophy unification
- [ ] Phase 4 - frontend cleanup
- [ ] Phase 5 - resolver restructure
- [ ] Phase 6 - VM hygiene
- [ ] Phase 7 - performance pass
"""


def main():
    existing = gh_json(
        "issue",
        "list",
        "--limit",
        "200",
        "--state",
        "all",
        "--json",
        "number,title,url",
    )

    # 1. Parent issue
    parent = next((i for i in existing if i["title"].startswith("[Refactor]")), None)
    if parent:
        pnum, purl = parent["number"], parent["url"]
        print(f"parent exists: #{pnum}")
    else:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(PARENT_BODY)
            body_file = f.name
        url = gh(
            "issue",
            "create",
            "--title",
            "[Refactor] Sindlish interpreter v0.2 - master issue",
            "--body-file",
            body_file,
            "--milestone",
            "Refactor v0.2",
            "--label",
            "refactor",
        ).splitlines()[-1]
        pnum = int(url.rstrip("/").rsplit("/", 1)[-1])
        purl = url
        print(f"parent created: #{pnum} {purl}")

    # 2. Sub-issues
    titles = {i["title"] for i in existing}
    created, skipped = [], []
    for phase, extra, title, body in TASKS:
        if title in titles:
            skipped.append(title)
            continue
        with tempfile.NamedTemporaryFile(
            "w", suffix=".md", delete=False, encoding="utf-8"
        ) as f:
            f.write(f"_Refactor task - Phase `{phase}`_\n\n{body}")
            body_file = f.name
        args = [
            "issue",
            "create",
            "--title",
            title,
            "--body-file",
            body_file,
            "--milestone",
            "Refactor v0.2",
            "--label",
            phase,
            "--parent",
            str(pnum),
        ]
        for lbl in extra:
            args += ["--label", lbl]
        url = gh(*args).splitlines()[-1]
        num = int(url.rstrip("/").rsplit("/", 1)[-1])
        created.append((num, title))
        print(f"  sub-issue #{num}: {title}")

    print("\nSummary")
    print(f"  parent : #{pnum} {purl}")
    print(f"  created: {len(created)} sub-issues, skipped {len(skipped)} existing")


if __name__ == "__main__":
    main()
