"""Tests for the benchmark harness (tools/bench).

These tests exercise case discovery, the cold-start subprocess drivers, the
in-process per-stage driver, and the BOM-less guarantee of the ``.sd`` cases
(the old 0.1.0 sindlish rejects a UTF-8 BOM).
"""

import sys
from pathlib import Path

import pytest

_BENCH_DIR = Path(__file__).resolve().parents[1] / "tools" / "bench"
_REPO_ROOT = _BENCH_DIR.parents[1]

sys.path.insert(0, str(_REPO_ROOT))

from tools.bench.core.harness import Harness, discover_cases
from tools.bench.core.registry import Registry

CASES_DIR = _BENCH_DIR / "cases"


@pytest.fixture()
def harness() -> Harness:
    return Harness(Registry())


def test_discover_cases_groups_by_stem():
    cases = discover_cases(CASES_DIR)
    names = {c.name for c in cases}
    assert {"fib", "loops", "factorial"} <= names
    for case in cases:
        assert "sindlish" in case.sources
        assert "python" in case.sources


def test_all_sd_cases_are_bom_less():
    """Old sindlish 0.1.0 errors on a UTF-8 BOM; every committed case must be clean."""
    for source in (CASES_DIR / "sindlish").glob("*.sd"):
        raw = source.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), f"{source.name} has a UTF-8 BOM"


@pytest.mark.parametrize("case_name", ["fib", "loops", "factorial"])
def test_sd_and_py_cases_exist(case_name):
    assert (CASES_DIR / "sindlish" / f"{case_name}.sd").exists()
    assert (CASES_DIR / "python" / f"{case_name}.py").exists()


def test_cold_start_run_produces_positive_medians(harness):
    """Run a fast case cold through all three drivers, assert sane timings."""
    cases = [c for c in discover_cases(CASES_DIR) if c.name == "factorial"]
    results = harness.run(cases, ["old-sindlish", "new-sindlish", "python"], 1, 0)
    for case_name, case_results in results.items():
        assert case_name == "factorial"
        drivers = {r.driver for r in case_results}
        assert drivers == {"old-sindlish", "new-sindlish", "python"}
        for r in case_results:
            assert r.succeeded, f"{r.driver} failed: {r.error}"
            assert r.total_ms > 0
            assert r.runs == 1


def test_stages_mode_full_breakdown(harness):
    """new-sindlish stage mode reports all five pipeline stages."""
    cases = [c for c in discover_cases(CASES_DIR) if c.name == "loops"]
    results = harness.run_stages(cases, ["new-sindlish", "python"], 1)
    for case_results in results.values():
        # python driver does not support stages and should be excluded.
        assert all(r.driver == "new-sindlish" for r in case_results)
        for r in case_results:
            assert r.succeeded
            for stage in ["lex", "parse", "resolve", "compile", "vm"]:
                assert stage in r.stage_times_ms
                assert r.stage_times_ms[stage] >= 0
            assert r.total_ms >= 0


def test_unknown_driver_raises(harness):
    with pytest.raises(KeyError):
        harness.registry.build("definitely-not-a-driver")


def test_on_dispatch_callback_invoked_per_dispatch(harness):
    """The progress callback fires once per (case, driver) dispatch."""
    cases = [c for c in discover_cases(CASES_DIR) if c.name == "factorial"]
    calls: list[tuple] = []

    def on_dispatch(case, driver, idx, total):
        calls.append((case, driver, idx, total))

    harness.run(cases, ["python"], 1, 0, on_dispatch=on_dispatch)
    assert len(calls) == 1
    assert calls[0] == ("factorial", "python", 0, 1)


def test_rich_reporter_renders(harness):
    """Rich-based renderers produce output without crashing."""
    rich = pytest.importorskip("rich")
    from tools.bench.core.result import BenchResult
    from tools.bench.core.rich_reporter import (
        render_bars,
        render_stages_rich,
        render_table_rich,
    )

    r1 = BenchResult(case="fib", driver="old-sindlish", command="x", total_ms=3000.0)
    r2 = BenchResult(case="fib", driver="new-sindlish", command="x", total_ms=500.0)
    r1.stage_times_ms = {
        "lex": 0.1,
        "parse": 0.2,
        "resolve": 0.3,
        "compile": 0.4,
        "vm": 100.0,
    }

    import io

    buf = io.StringIO()
    console = rich.console.Console(file=buf, width=100, color_system=None)
    render_table_rich(console, {"fib": [r1, r2]}, ["old-sindlish", "new-sindlish"])
    render_bars(console, {"fib": [r1, r2]}, ["old-sindlish", "new-sindlish"])
    render_stages_rich(console, {"fib": [r1]})
    out = buf.getvalue()
    assert "fib" in out
    assert "old" in out and "new" in out
