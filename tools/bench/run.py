#!/usr/bin/env python3
"""Sindlish benchmark CLI entry point.

Usage:
    uv run tools/bench/run.py                        # cold-start all cases x drivers
    uv run tools/bench/run.py --drivers old-sindlish,new-sindlish
    uv run tools/bench/run.py --case fib
    uv run tools/bench/run.py --repeats 5 --warmup 2
    uv run tools/bench/run.py --stages               # in-process per-stage, new impl only
    uv run tools/bench/run.py --format json
    uv run tools/bench/run.py --list                 # list available drivers & cases
    uv run tools/bench/tui.py                        # interactive menu interface
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BENCH_DIR.parent.parent

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.bench.core import reporter
from tools.bench.core.harness import Harness, discover_cases
from tools.bench.core.registry import Registry

_CASES_DIR = _BENCH_DIR / "cases"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bench",
        description="Sindlish benchmark harness: compare runtimes on the "
        "same logical cases by cold-start wall time.",
    )
    parser.add_argument("--drivers", help="Comma-separated driver names")
    parser.add_argument("--case", help="Run only the named case (e.g. 'fib')")
    parser.add_argument(
        "--repeats", type=int, default=5, help="Repeats per case/driver"
    )
    parser.add_argument(
        "--warmup", type=int, default=2, help="Warmup runs before repeats"
    )
    parser.add_argument(
        "--stages",
        action="store_true",
        help="Report in-process per-pipeline-stage timings (new-sindlish only)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json", "pretty"],
        default="pretty",
        help="Output format (default: pretty; 'pretty' requires rich and a terminal)",
    )
    parser.add_argument(
        "--list", action="store_true", help="List available drivers and cases"
    )

    args = parser.parse_args(argv)

    registry = Registry()

    if args.list:
        _print_listing(registry)
        return 0

    cases = discover_cases(_CASES_DIR)
    if not cases:
        print(f"No benchmark cases found under {_CASES_DIR}")
        return 1
    if args.case:
        cases = [c for c in cases if c.name == args.case]
        if not cases:
            all_names = ", ".join(c.name for c in discover_cases(_CASES_DIR))
            print(f"Unknown case '{args.case}'. Available: {all_names}")
            return 1

    drivers = args.drivers.split(",") if args.drivers else _default_drivers()
    _validate_drivers(registry, drivers)

    harness = Harness(registry)

    # Pretty is the interactive default but only makes sense on a real TTY
    # (rich rendering of tables/services). Fall back to plain text when piping.
    use_pretty = args.format == "pretty" and sys.stdout.isatty()
    if args.format == "pretty" and not use_pretty:
        args.format = "table"

    if args.stages:
        results = _run_with_progress(
            lambda with_progress: harness.run_stages(
                cases, drivers, args.repeats, on_dispatch=with_progress
            ),
            use_pretty,
        )
    else:
        results = _run_with_progress(
            lambda with_progress: harness.run(
                cases,
                drivers,
                args.repeats,
                args.warmup,
                on_dispatch=with_progress,
            ),
            use_pretty,
        )

    if args.format == "json":
        print(reporter.to_json(results))
    elif args.format == "pretty":
        _print_pretty(results, drivers, stages=args.stages)
    else:
        if args.stages:
            print(reporter.render_stages_table(results))
        else:
            print(reporter.render_table(results, drivers))
        _print_footnote()

    return 0


def _run_with_progress(run_fn, use_pretty):
    """Execute the harness run, showing a live progress bar when interactive."""
    if not use_pretty:
        return run_fn(None)

    from rich.console import Console
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
    )

    console = Console()
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}[/]"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )
    state = {"task": None, "idx": 0, "total": 0}

    def on_dispatch(case, driver, idx, total):
        if state["task"] is None or total != state["total"]:
            if state["task"] is not None:
                progress.stop_task(state["task"])
            state["task"] = progress.add_task(f"{case}  -  {driver}", total=total)
            state["idx"] = 0
            state["total"] = total
        state["idx"] += 1
        progress.update(
            state["task"],
            description=f"{case}  -  {driver}",
            advance=1,
        )

    with progress:
        results = run_fn(on_dispatch)
    return results


def _print_pretty(results, drivers, stages=False) -> None:
    from tools.bench.core.rich_reporter import (
        console_factory,
        render_bars,
        render_stages_rich,
        render_table_rich,
    )

    console = console_factory()
    if stages:
        console.print("\n[bold]Per-stage (in-process, new implementation only)[/]")
        render_stages_rich(console, results)
        console.print(
            "[dim]NOTE: these in-process numbers are NOT comparable to the "
            "cold-start subprocess table; they are for optimizer work.[/]"
        )
    else:
        render_table_rich(console, results, list(drivers))
        console.print()
        render_bars(console, results, list(drivers))
        _print_rich_footnote(console)


def _print_rich_footnote(console) -> None:
    console.print(
        "\n[dim]Median cold-start wall latency (includes interpreter startup + "
        "imports). 'new-sindlish' runs under `uv run`, so its column measures "
        "uv + CPython + interpreter together and may spike if uv re-resolves "
        "dependencies. Try `uv run tools/bench/tui.py` for the interactive "
        "menu, or `--stages` for an in-process per-stage view.[/]"
    )


def _default_drivers() -> list[str]:
    return ["old-sindlish", "new-sindlish", "python"]


def _validate_drivers(registry: Registry, drivers: list[str]) -> None:
    available = registry.names()
    for name in drivers:
        if name not in available:
            print(f"Unknown driver '{name}'. Available: {', '.join(available)}")
            sys.exit(1)


def _print_footnote() -> None:
    print(
        "\nTimes are median cold-start wall latency (includes interpreter "
        "startup + imports). 'new-sindlish' runs under `uv run`, so its column "
        "measures uv + CPython + interpreter together and may spike if uv "
        "re-resolves dependencies. Use --stages for an in-process per-stage view."
    )


def _print_listing(registry: Registry) -> None:
    print("Drivers:")
    for name in registry.names():
        print(f"  {name}")
    cases = discover_cases(_CASES_DIR)
    print("Cases:")
    for case in cases:
        langs = ", ".join(case.sources)
        print(f"  {case.name}  [{langs}]")


if __name__ == "__main__":
    sys.exit(main())
