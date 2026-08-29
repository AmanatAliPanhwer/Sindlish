"""Old Sindlish driver — the installed (published) sindlish executable.

This is the version reachable via ``sindlish`` on PATH, e.g. the 0.1.0
installed at ``C:\\Program Files (x86)\\Sindlish\\sindlish.exe``. It is
measured as a cold subprocess exactly like any other command, so its wall time
includes its own interpreter startup.
"""

from __future__ import annotations

from .base import ShellDriver


class OldSindlishDriver(ShellDriver):
    """Run ``sindlish run <file.sd>`` as a cold subprocess."""

    name = "old-sindlish"
    command_template = 'sindlish run "{source}"'
