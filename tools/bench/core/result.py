"""Benchmark result data structures."""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field


def median_ms(samples: list[float]) -> float:
    """Return the median of a list of durations in seconds -> milliseconds."""
    if not samples:
        return 0.0
    return statistics.median(samples) * 1000.0


@dataclass
class BenchResult:
    """Outcome of running one case through one driver."""

    case: str
    driver: str
    command: str
    total_ms: float
    samples_ms: list[float] = field(default_factory=list)
    stage_times_ms: dict[str, float] = field(default_factory=dict)
    runs: int = 0
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.error is None
