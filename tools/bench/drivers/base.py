"""Driver protocol used by the benchmark harness."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.result import BenchResult


class Driver(ABC):
    """Adaptor that knows how to execute a benchmark case under one runtime.

    The harness is language-agnostic: it only calls ``run`` (cold-start, whole
    program) and, optionally, ``run_stages`` (in-process per-pipeline-stage).

    Driver naming convention: command-style name used on the CLI and in
    reporting, e.g. ``old-sindlish``, ``new-sindlish``, ``python``.
    """

    name: str = "unnamed"

    @abstractmethod
    def run(self, source_path: str, repeats: int, warmup: int) -> BenchResult:
        """Time the case as a cold-start whole program.

        ``source_path`` points at the driver-appropriate source file for the
        case. Returns a populated :class:`BenchResult`.
        """

    def run_stages(self, source_path: str, repeats: int) -> BenchResult:
        """(Optional) Time the case in-process, per pipeline stage.

        Only the current in-process implementation provides this. Drivers that
        cannot (e.g. external subprocess runtimes) should raise
        ``NotImplementedError``.
        """
        raise NotImplementedError(
            f"Driver '{self.name}' does not support in-process stage timing."
        )

    def supports_stages(self) -> bool:
        return False


class ShellDriver(Driver):
    """Base driver that runs a benchmark as an external subprocess.

    This is the default for any runtime reached through a CLI command, and is
    the measurement model for the cross-language cold-start comparison.
    """

    name: str = "shell"
    #: Template for the command. ``{source}`` is substituted with the file path.
    command_template: str = "{source}"

    def __init__(self, command_template: str | None = None) -> None:
        if command_template is not None:
            self.command_template = command_template

    def _build_command(self, source_path: str) -> list[str]:
        rendered = self.command_template.format(source=source_path)
        # Split respecting simple quoting so paths with spaces survive.
        return _split_command(rendered)

    def run(self, source_path: str, repeats: int, warmup: int) -> BenchResult:
        import time

        cmd = self._build_command(source_path)
        command_str = " ".join(cmd)

        # Warmup pass lets OS caches settle.
        for _ in range(warmup):
            _subprocess(cmd)

        samples: list[float] = []
        for _ in range(repeats):
            t0 = time.perf_counter()
            ret = _subprocess(cmd)
            t1 = time.perf_counter()
            if ret != 0:
                return BenchResult(
                    case="",
                    driver=self.name,
                    command=command_str,
                    total_ms=0.0,
                    error=f"command exited with code {ret}",
                )
            samples.append(t1 - t0)

        from ..core.result import median_ms

        return BenchResult(
            case="",
            driver=self.name,
            command=command_str,
            total_ms=median_ms(samples),
            samples_ms=list(samples),
            runs=repeats,
        )

    def run_stages(self, source_path: str, repeats: int) -> BenchResult:
        # A black-box subprocess cannot be split into interpreter stages.
        raise NotImplementedError(
            f"Driver '{self.name}' is a subprocess runner and cannot report "
            "per-pipeline-stage timings."
        )

    def supports_stages(self) -> bool:
        return False


def _subprocess(cmd: list[str]) -> int:
    import subprocess
    import sys

    kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
    proc = subprocess.run(cmd, **kwargs, check=False)
    return proc.returncode


def _split_command(s: str) -> list[str]:
    """Split a command string into argv, handling double-quoted segments.

    ``shlex`` with ``posix=False`` keeps quotes as literal characters, which
    breaks ``subprocess.run`` with a list on Windows (CreateProcess would pass
    the quotes through). We split and then strip the surrounding quotes.
    """
    import shlex

    tokens = shlex.split(s, posix=False)
    cleaned = []
    for tok in tokens:
        if len(tok) >= 2 and tok[0] == tok[-1] == '"':
            tok = tok[1:-1]
        cleaned.append(tok)
    return cleaned
