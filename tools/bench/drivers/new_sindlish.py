"""New/current Sindlish driver.

This implementation is reached in two ways:

1. Cold-start whole-program (default, cross-language comparison):
   ``uv run main.py run <file.sd>`` as a subprocess. Note that this measures
   the uv toolchain + CPython boot + interpreter startup together — not just
   the interpreter — and may spike if uv re-resolves dependencies.

2. In-process per-pipeline-stage (``run_stages`` / ``--stages``): imports the
   interpreter from this repo directly and times each stage (lex, parse,
   resolve, compile, vm) with ``time.perf_counter``. These numbers are for
   optimizer work (roadmap phase-7) and are intentionally kept separate from
   the cold-start table.
"""

from __future__ import annotations

from pathlib import Path

from ..core.result import BenchResult, median_ms
from .base import Driver, ShellDriver

# Root of the repo, so ``main.py`` and the ``interpreter`` package resolve.
_REPO_ROOT = Path(__file__).resolve().parents[3]


class NewSindlishShell(ShellDriver):
    """Cold-start whole-program measurement for the current implementation."""

    name = "new-sindlish"
    command_template = None  # built in __init__ via repo path

    def __init__(self, main_py: Path | None = None) -> None:
        main_py = main_py or (_REPO_ROOT / "main.py")
        self.command_template = f'uv run "{main_py}" run "{{source}}"'


class NewSindlishDriver(Driver):
    """Combined driver: cold-start subprocess + in-process stage timing."""

    name = "new-sindlish"

    def __init__(self) -> None:
        self._shell = NewSindlishShell()

    def run(self, source_path: str, repeats: int, warmup: int) -> BenchResult:
        result = self._shell.run(source_path, repeats, warmup)
        result.driver = self.name
        return result

    def run_stages(self, source_path: str, repeats: int) -> BenchResult:
        import io
        import sys
        import time

        sys.path.insert(0, str(_REPO_ROOT))

        with open(source_path, "r", encoding="utf-8") as f:
            code = f.read()

        env = _make_globals_env()

        stage_names = ["lex", "parse", "resolve", "compile", "vm"]
        stage_samples: dict[str, list[float]] = {s: [] for s in stage_names}

        # Benchmark programs may print a final result (see cases). Suppress
        # stdout so in-process measurement stays clean.
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            for _ in range(repeats):
                t = time.perf_counter()
                from interpreter.frontend.lexer import Lexer

                tokens = Lexer(code).generate_tokens()
                stage_samples["lex"].append(time.perf_counter() - t)

                t = time.perf_counter()
                from interpreter.frontend.parser import Parser

                ast = Parser(tokens, code).parse()
                stage_samples["parse"].append(time.perf_counter() - t)

                t = time.perf_counter()
                from interpreter.analysis.resolver import Resolver

                resolver = Resolver(code)
                resolver.resolve(ast)
                stage_samples["resolve"].append(time.perf_counter() - t)

                t = time.perf_counter()
                from interpreter.backend.compiler import Compiler

                instructions, constants, line_col_map = Compiler(code).compile(ast)
                stage_samples["compile"].append(time.perf_counter() - t)

                t = time.perf_counter()
                from interpreter.backend.vm import VM

                vm = VM(
                    code,
                    instructions,
                    constants,
                    env,
                    getattr(ast, "slot_count", 0),
                    resolver.slot_metadata,
                    line_col_map,
                )
                vm.run()
                stage_samples["vm"].append(time.perf_counter() - t)
        finally:
            sys.stdout = old_stdout

        stage_ms = {name: median_ms(samples) for name, samples in stage_samples.items()}
        total_samples = [sum(v) for v in zip(*(stage_samples[s] for s in stage_names))]
        total_ms = median_ms(total_samples)

        return BenchResult(
            case="",
            driver=self.name,
            command=f"<in-process run_source pipeline: {source_path}>",
            total_ms=total_ms,
            stage_times_ms=stage_ms,
            runs=repeats,
        )

    def supports_stages(self) -> bool:
        return True


def _make_globals_env():
    """Build the global environment once, mirroring Interpreter._create_globals_env."""
    from interpreter.frontend.tokens import TokenType
    from interpreter.runtime.builtins import SimpleBuiltins
    from interpreter.runtime.env import Environment

    env = Environment()
    handler = SimpleBuiltins()
    for name, func in handler.get_all().items():
        env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return env
