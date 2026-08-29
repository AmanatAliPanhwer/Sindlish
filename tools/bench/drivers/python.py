"""Python baseline driver — runs a case as a cold subprocess of CPython."""

from __future__ import annotations

import sys

from .base import ShellDriver


class PythonDriver(ShellDriver):
    """Run ``python <file.py>`` as an external process and time it cold."""

    name = "python"

    def __init__(self, executable: str | None = None) -> None:
        exe = executable or sys.executable
        self.command_template = f'"{exe}" {{source}}'
