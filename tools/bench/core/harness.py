"""Benchmark harness — discover cases, run drivers, collect results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .registry import Registry
from .result import BenchResult


@dataclass
class Case:
    """A logical benchmark (e.g. 'fib') with one source file per language."""

    name: str
    sources: dict[str, Path] = field(default_factory=dict)


def discover_cases(cases_dir: Path) -> list[Case]:
    """Group ``<name>.<ext>`` files under ``cases_dir`` into logical cases.

    Every file inside a subdirectory of ``cases_dir`` is collected; files with
    the same stem (across any language subdirectories) form one :class:`Case`.
    """
    by_name: dict[str, Case] = {}
    if not cases_dir.exists():
        return []
    for lang_dir in sorted(cases_dir.iterdir()):
        if not lang_dir.is_dir():
            continue
        for source in sorted(lang_dir.glob("*")):
            if not source.is_file():
                continue
            stem = source.stem
            case = by_name.setdefault(stem, Case(name=stem))
            case.sources[lang_dir.name] = source
    return [by_name[name] for name in sorted(by_name)]


def case_source(case: Case, dirname: str) -> Path | None:
    """Return the source file for a case under a given language directory."""
    return case.sources.get(dirname)


class Harness:
    """Executes a set of cases through the requested drivers."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()
        #: Map driver name -> the language dirname it reads source from.
        self.driver_sources: dict[str, str] = {
            "old-sindlish": "sindlish",
            "new-sindlish": "sindlish",
            "python": "python",
        }

    def run(
        self,
        cases: list[Case],
        drivers: list[str],
        repeats: int,
        warmup: int,
        on_dispatch=None,
    ) -> dict[str, list[BenchResult]]:
        """Run each case through each driver (cold-start whole program).

        ``on_dispatch(case_name, driver_name, index, total)`` is invoked before
        each dispatch for live progress reporting.

        Returns ``{case_name: [BenchResult, ...]}``.
        """
        results: dict[str, list[BenchResult]] = {}
        plan = _dispatch_plan(cases, drivers)
        total = len(plan)
        for idx, (case, driver_name) in enumerate(plan):
            driver = self.registry.build(driver_name)
            lang_dir = self.driver_sources.get(driver_name, driver_name)
            source = case_source(case, lang_dir)
            if on_dispatch:
                on_dispatch(case.name, driver_name, idx, total)
            if source is None:
                continue
            result = driver.run(str(source), repeats, warmup)
            result.case = case.name
            results.setdefault(case.name, []).append(result)
        return results

    def run_stages(
        self,
        cases: list[Case],
        drivers: list[str],
        repeats: int,
        on_dispatch=None,
    ) -> dict[str, list[BenchResult]]:
        """In-process per-pipeline-stage timing for supporting drivers.

        Uses the ``sindlish`` source of each case (the in-process drivers read
        Sindlish source), running only for drivers whose
        ``supports_stages()`` is true.
        """
        results: dict[str, list[BenchResult]] = {}
        plan = _dispatch_plan(cases, drivers, stages_only=True)
        total = len(plan)
        for idx, (case, driver_name) in enumerate(plan):
            driver = self.registry.build(driver_name)
            if not driver.supports_stages():
                continue
            if on_dispatch:
                on_dispatch(case.name, driver_name, idx, total)
            source = case_source(case, "sindlish") or case_source(case, driver_name)
            if source is None:
                continue
            result = driver.run_stages(str(source), repeats)
            result.case = case.name
            results.setdefault(case.name, []).append(result)
        return results


def _dispatch_plan(
    cases: list[Case],
    drivers: list[str],
    stages_only: bool = False,
) -> list[tuple[Case, str]]:
    """Flatten (case, driver) pairs in a stable order for progress tracking."""
    return [(case, d) for case in cases for d in drivers]
