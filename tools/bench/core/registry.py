"""Driver registry — maps driver names to factory callables."""

from __future__ import annotations

from collections.abc import Callable

from ..drivers.base import Driver
from ..drivers.new_sindlish import NewSindlishDriver
from ..drivers.old_sindlish import OldSindlishDriver
from ..drivers.python import PythonDriver


def _default_drivers() -> dict[str, Callable[[], Driver]]:
    return {
        "old-sindlish": lambda: OldSindlishDriver(),
        "new-sindlish": lambda: NewSindlishDriver(),
        "python": lambda: PythonDriver(),
    }


class Registry:
    """Holds driver factories keyed by driver name."""

    def __init__(self) -> None:
        self._factories = _default_drivers()

    def register(self, name: str, factory: Callable[[], Driver]) -> None:
        self._factories[name] = factory

    def names(self) -> list[str]:
        return sorted(self._factories)

    def build(self, name: str) -> Driver:
        if name not in self._factories:
            raise KeyError(
                f"Unknown driver '{name}'. Available: {', '.join(self._factories)}"
            )
        return self._factories[name]()
