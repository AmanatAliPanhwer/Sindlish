"""Output formatting for benchmark results — text tables and JSON."""

from __future__ import annotations

import json

from .result import BenchResult


def _value_str(result: BenchResult) -> str:
    if result.error:
        return f"ERR ({result.error})"
    return f"{result.total_ms:.2f} ms"


def render_table(results: dict[str, list[BenchResult]], driver_names: list[str]) -> str:
    """Render the cold-start comparison table: rows = cases, cols = drivers."""
    all_results = [r for rs in results.values() for r in rs]
    value_fmt: dict[str, dict[str, str]] = {}
    for r in all_results:
        value_fmt.setdefault(r.case, {})[r.driver] = _value_str(r)

    headers = ["case"] + driver_names
    rows_display: dict[str, list[str]] = {}
    for case_name in sorted(results):
        row = [case_name]
        for dname in driver_names:
            row.append(value_fmt.get(case_name, {}).get(dname, "-"))
        rows_display[case_name] = row

    widths = [len(h) for h in headers]
    for row in rows_display.values():
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    lines = [_fmt_row(headers, widths)]
    for case_name in sorted(rows_display):
        lines.append(_fmt_row(rows_display[case_name], widths))
    return "\n".join(lines)


def render_stages_table(results: dict[str, list[BenchResult]]) -> str:
    """Render the per-pipeline-stage table for in-process drivers."""
    stage_names = ["lex", "parse", "resolve", "compile", "vm", "total"]
    headers = ["case", "driver"] + stage_names
    rows: list[list[str]] = []
    for case_name, case_results in sorted(results.items()):
        for res in case_results:
            if res.error:
                rows.append([case_name, res.driver, f"ERR ({res.error})"])
                continue
            cells = [case_name, res.driver]
            for s in stage_names[:-1]:
                cells.append(f"{res.stage_times_ms.get(s, 0.0):.2f}")
            cells.append(f"{res.total_ms:.2f}")
            rows.append(cells)

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(cell))

    lines = [_fmt_row(headers, widths)]
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        lines.append(_fmt_row(padded, widths))
    return "\n".join(lines)


def to_json(results: dict[str, list[BenchResult]]) -> str:
    payload = {}
    for case_name, case_results in results.items():
        payload[case_name] = [
            {
                "driver": r.driver,
                "command": r.command,
                "total_ms": round(r.total_ms, 4),
                "stage_times_ms": {k: round(v, 4) for k, v in r.stage_times_ms.items()},
                "runs": r.runs,
                "error": r.error,
            }
            for r in case_results
        ]
    return json.dumps(payload, indent=2)


def _fmt_row(cells: list[str], widths: list[int]) -> str:
    return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)).rstrip()
