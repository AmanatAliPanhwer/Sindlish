"""Rich-based rendering for the benchmark tool.

These helpers depend on ``rich`` (a dev dependency) and produce the styled
one-shot report / live progress used by both the CLI and the interactive TUI.
They are kept separate from :mod:`.reporter` so the plain-text/JSON path stays
stdlib-only.
"""

from __future__ import annotations

from rich import box
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .result import BenchResult

# Driver -> accent colour for consistent identity across screens.
DRIVER_COLORS = {
    "old-sindlish": "magenta",
    "new-sindlish": "cyan",
    "python": "yellow",
}


def _short_driver(name: str) -> str:
    """Map a driver name to a short stable tag."""
    return {
        "old-sindlish": "old",
        "new-sindlish": "new",
        "python": "py",
    }.get(name, name)


def _cell_text(result: BenchResult) -> Text:
    """Colour the timing cell; green for success, red for errors."""
    if result.error:
        return Text(f"ERR ({result.error})", style="bold red")
    return Text(f"{result.total_ms:>8.2f} ms", style="bold green")


def render_table_rich(
    console: Console,
    results: dict[str, list[BenchResult]],
    driver_names: list[str],
) -> None:
    """Print a colourised comparison table with a fastest-driver marker."""
    table = Table(title="Cold-start wall time", box=box.ROUNDED, title_style="bold")
    table.add_column("case", style="bold")
    for dname in driver_names:
        table.add_column(
            _short_driver(dname),
            justify="right",
            header_style=DRIVER_COLORS.get(dname, "white"),
        )

    for case_name in sorted(results):
        by_driver: dict[str, BenchResult] = {r.driver: r for r in results[case_name]}
        ok = [r for r in results[case_name] if r.succeeded and r.total_ms > 0]
        fastest_driver = min(ok, key=lambda r: r.total_ms).driver if ok else None
        row: list[Text] = [Text(case_name)]
        for dname in driver_names:
            res = by_driver.get(dname)
            cell = _cell_text(res) if res else Text("-", style="dim")
            if res and res.driver == fastest_driver:
                cell.append("  (fastest)", style="bold green")
            row.append(cell)
        table.add_row(*row)
    console.print(table)
    console.print(
        "green = lower is faster - (fastest) marks the quickest driver per case",
        style="dim",
    )


def render_stages_rich(
    console: Console,
    results: dict[str, list[BenchResult]],
) -> None:
    """Print a colourised per-pipeline-stage table."""
    stage_names = ["lex", "parse", "resolve", "compile", "vm", "total"]
    table = Table(title="In-process per-stage timings (ms)", box=box.ROUNDED)
    table.add_column("case", style="bold")
    table.add_column("driver", style="bold")
    for s in stage_names:
        table.add_column(s, justify="right", header_style="cyan")

    for case_name in sorted(results):
        for res in results[case_name]:
            if res.error:
                table.add_row(
                    case_name, res.driver, Text(f"ERR ({res.error})", style="red")
                )
                continue
            if res.stage_times_ms:
                cells = [
                    f"{res.stage_times_ms.get(s, 0.0):.2f}" for s in stage_names[:-1]
                ]
                # Colour the dominant stage differently to highlight hotspots.
                dominant = max(
                    stage_names[:-1], key=lambda s: res.stage_times_ms.get(s, 0.0)
                )
                rows = [
                    Text(c, style="bold red" if s == dominant else "white")
                    for s, c in zip(stage_names[:-1], cells)
                ]
            else:
                rows = [Text("-", style="dim") for _ in stage_names[:-1]]
            table.add_row(
                case_name,
                res.driver,
                *rows,
                f"{res.total_ms:.2f}",
            )
    console.print(table)
    console.print("red marks the dominant (slowest) stage per run", style="dim")


def render_bars(
    console: Console,
    results: dict[str, list[BenchResult]],
    driver_names: list[str],
) -> None:
    """Print a normalised comparison-bar panel per case."""
    groups: list[Panel] = []
    for case_name in sorted(results):
        by_driver = {r.driver: r for r in results[case_name]}
        ok = [r for r in results[case_name] if r.succeeded and r.total_ms > 0]
        if not ok:
            continue
        worst = max(r.total_ms for r in ok)
        lines: list[Text] = []
        for dname in driver_names:
            res = by_driver.get(dname)
            if not res or not res.succeeded:
                lines.append(
                    Text(f"  {_short_driver(dname):<4} unavailable", style="dim")
                )
                continue
            ratio = res.total_ms / worst if worst else 0.0
            bar_len = max(1, int(ratio * 20))
            bar = "#" * bar_len
            color = DRIVER_COLORS.get(dname, "white")
            t = Text()
            t.append(f"  {_short_driver(dname):<4} ", style=color)
            t.append(bar, style=color)
            t.append(f" {res.total_ms:>8.2f} ms", style="bold")
            lines.append(t)
        groups.append(Panel(Group(*lines), title=case_name, box=box.SIMPLE))
    console.print(Group(*groups))


def console_factory() -> Console:
    """Build a shared Console with a consistent colour scheme.

    On Windows this reconfigures ``sys.stdout`` to UTF-8 when possible so rich's
    box-drawing glyphs render correctly even on legacy console hosts.
    """
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    return Console(theme=Theme({"bench.title": "bold cyan"}))
