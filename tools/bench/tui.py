#!/usr/bin/env python3
"""Sindlish benchmark —— interactive terminal UI.

Launch with:
    uv run tools/bench/tui.py

A keyboard-navigable menu (prompt_toolkit) to pick drivers, cases and options,
run cold-start or per-stage benchmarks with live progress, view rich-styled
results, and loop back to the menu.

Keybindings:
    ↑ / ↓            move selection
    Space            toggle a checkbox item
    Enter            confirm / run / continue
    q / Ctrl+C       back (in submenus) or quit (on main menu)
"""

from __future__ import annotations

import sys
from pathlib import Path

_BENCH_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _BENCH_DIR.parent.parent

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style

from tools.bench.core.harness import Harness, discover_cases
from tools.bench.core.registry import Registry

CASES_DIR = _BENCH_DIR / "cases"

ACCENT = "bold ansicyan"
MUTED = "ansibrightblack"
SELECTED = "reverse"


class Screen:
    """A menu+selection screen displayed as a full-screen prompt_toolkit app."""

    def __init__(self, title: str, options: list[str], multi: bool = False):
        self.title = title
        self.options = options
        self.multi = multi
        self.index = 0
        self.selected: set[str] = set()

    def toggle(self, name: str) -> None:
        if name in self.selected:
            self.selected.discard(name)
        else:
            self.selected.add(name)

    def _fragments(self, note: str) -> FormattedText:
        frags: list[tuple] = [(ACCENT, self.title), ("", "\n")]
        if note:
            frags.append((MUTED, note))
            frags.append(("", "\n"))
        frags.append(
            (
                MUTED,
                "  Space toggles, Enter confirms"
                if self.multi
                else "  Up/Down navigate, Enter select",
            )
        )
        frags.append(("", "\n\n"))
        for i, opt in enumerate(self.options):
            if self.multi:
                mark = "[x]" if opt in self.selected else "[ ]"
            else:
                mark = "  "
            prefix = ">" if i == self.index else " "
            label = f"  {prefix} {mark} {opt}"
            style = (
                SELECTED
                if i == self.index
                else ("" if opt not in self.selected else "bold ansigreen")
            )
            frags.append((style, label))
            frags.append(("", "\n"))
        frags.append(("", "\n"))
        frags.append((MUTED, "  q / Ctrl+C quits"))
        return FormattedText(frags)


def run_screen(screen: Screen, note: str = "") -> str | None:
    """Show a screen and return: the chosen option, the selected set, or 'quit'."""
    kb = KeyBindings()
    result: dict[str, object] = {"value": None}

    @kb.add("up")
    def up(_e):
        screen.index = (screen.index - 1) % len(screen.options)
        _e.app.invalidate()

    @kb.add("down")
    def down(_e):
        screen.index = (screen.index + 1) % len(screen.options)
        _e.app.invalidate()

    @kb.add("space")
    def space(_e):
        if screen.multi:
            screen.toggle(screen.options[screen.index])
            _e.app.invalidate()

    @kb.add("enter")
    def enter(_e):
        if screen.multi:
            result["value"] = sorted(screen.selected)
        else:
            result["value"] = screen.options[screen.index]
        _e.app.exit()

    @kb.add("c-q")
    @kb.add("c-c")
    def quit_app(_e):
        result["value"] = "__quit__"
        _e.app.exit()

    control = FormattedTextControl(text=lambda: screen._fragments(note), focusable=True)
    app = Application(
        layout=Layout(Window(control)),
        key_bindings=kb,
        style=Style([("reverse", "reverse")]),
        full_screen=True,
    )
    try:
        app.run()
    except KeyboardInterrupt:
        return "__quit__"
    return result["value"] or "__quit__"


def pick_options(
    title: str, all_options: list[str], current: list[str]
) -> list[str] | None:
    """Multi-select screen; returns new selection or None when cancelled."""
    screen = Screen(title, all_options, multi=True)
    screen.selected = set(current)
    got = run_screen(screen)
    if got == "__quit__":
        return None
    return got if got else None


def pick_single(title: str, options: list[str], note: str = "") -> str | None:
    """Single-select screen; returns chosen option or None when cancelled."""
    got = run_screen(Screen(title, options), note)
    return None if got == "__quit__" else got


def number_input(message: str, current: int) -> int | None:
    """Inline prompt for a positive integer; None if cancelled."""
    from prompt_toolkit.shortcuts import prompt

    try:
        raw = prompt(message + f" [{current}] > ").strip()
    except (KeyboardInterrupt, EOFError):
        return None
    if not raw:
        return current
    try:
        val = int(raw)
    except ValueError:
        return None
    return val if val > 0 else None


# --------------------------------------------------------------------------- #
# Results rendering (rich)                                                     #
# --------------------------------------------------------------------------- #


def render_results(results, drivers, stages) -> None:
    from rich.console import Console

    from tools.bench.core.rich_reporter import (
        render_bars,
        render_stages_rich,
        render_table_rich,
    )

    console = Console()
    console.clear()
    console.rule("[bold cyan]Benchmark results[/]")
    if stages:
        render_stages_rich(console, results)
        console.print(
            "[dim]These in-process numbers are NOT comparable to the "
            "cold-start subprocess table; they are for optimizer work.[/]\n"
        )
    else:
        console.print()
        render_table_rich(console, results, list(drivers))
        console.print()
        render_bars(console, results, list(drivers))
    console.print("[dim]Press Enter to return to the menu...[/]")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        pass


# --------------------------------------------------------------------------- #
# Main loop                                                                    #
# --------------------------------------------------------------------------- #


def main() -> int:
    registry = Registry()
    harness = Harness(registry)
    drivers = registry.names()
    cases = [c.name for c in discover_cases(CASES_DIR)]
    repeats = 5
    warmup = 2

    from rich.console import Console

    console = Console()

    while True:
        note = (
            f"drivers: {', '.join(drivers) or '(none)'}   "
            f"cases: {', '.join(cases) or '(none)'}   "
            f"repeats: {repeats} x warmup: {warmup}"
        )
        choice = pick_single(
            "Sindlish Benchmark",
            [
                "Run benchmarks (cold-start)",
                "Run per-stage (in-process, new impl)",
                "Configure",
                "Quit",
            ],
            note=note,
        )
        if choice is None or choice == "Quit":
            break

        selected_cases = [c for c in discover_cases(CASES_DIR) if c.name in cases]

        if choice == "Run benchmarks (cold-start)":

            def run_cold(
                on_dispatch, sc=selected_cases, d=drivers, r=repeats, w=warmup
            ):
                return harness.run(
                    sc,
                    d,
                    r,
                    w,
                    on_dispatch=on_dispatch,
                )

            results = _benchmark_with_progress(console, run_cold)
            render_results(results, drivers, stages=False)

        elif choice == "Run per-stage (in-process, new impl)":

            def run_stage(on_dispatch, sc=selected_cases, d=drivers, r=repeats):
                return harness.run_stages(
                    sc,
                    d,
                    r,
                    on_dispatch=on_dispatch,
                )

            results = _benchmark_with_progress(console, run_stage)
            render_results(results, drivers, stages=True)

        elif choice == "Configure":
            drivers, cases, repeats, warmup = _configure(
                registry,
                drivers,
                cases,
                repeats,
                warmup,
            )

    console.print("[bold cyan]Bye![/]")
    return 0


def _benchmark_with_progress(console, run_fn):
    """Run a harness call wrapped in a live progress bar spanning the whole run.

    ``run_fn(on_dispatch)`` is invoked with a callback that the harness calls
    before each dispatch so the bar tracks (case, driver) progress.
    """
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}[/]"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("benchmarking...", total=0)

        def on_dispatch(case, driver, idx, total):
            if total != progress.tasks[task].total:
                progress.update(task, total=total if total else 1)
            progress.update(task, description=f"{case}  -  {driver}", advance=1)

        return run_fn(on_dispatch)


def _configure(registry, drivers, cases, repeats, warmup):
    while True:
        choice = pick_single(
            "Configure",
            [
                "Select drivers",
                "Select cases",
                "Set repeats",
                "Set warmup",
                "Back",
            ],
            note=(
                f"drivers: {', '.join(drivers)}   "
                f"cases: {', '.join(cases)}   "
                f"repeats: {repeats}   warmup: {warmup}"
            ),
        )
        if choice is None or choice == "Back":
            return drivers, cases, repeats, warmup

        if choice == "Select drivers":
            got = pick_options(
                "Select drivers (space to toggle)",
                registry.names(),
                drivers,
            )
            if got:
                drivers = got

        elif choice == "Select cases":
            got = pick_options(
                "Select cases (space to toggle)",
                [c.name for c in discover_cases(CASES_DIR)],
                cases,
            )
            if got:
                cases = got

        elif choice == "Set repeats":
            val = number_input("Repeats per case/driver", repeats)
            if val is not None:
                repeats = val

        elif choice == "Set warmup":
            val = number_input("Warmup runs", warmup)
            if val is not None:
                warmup = val


if __name__ == "__main__":
    sys.exit(main())
