#!/usr/bin/env python3
"""In-process performance probe for the Sindlish interpreter.

Reproducible three-number yardstick for optimizer work. Run on the same
machine before and after any VM change:

    uv run tools/bench/perf_probe.py

Reported metrics:
    fib(24)          wall seconds for the classic double-recursive fib
    loop-add         wall seconds for 100,000 increment-add iterations
    f(50000)         microseconds per recursive call (single-op recursion)

Unlike the cold-start bench runner, this measures the running pipeline only
(no subprocess / uv boot), so it is comparable across git commits.
"""

from __future__ import annotations

import io
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from interpreter.analysis.resolver import Resolver
from interpreter.backend.compiler import Compiler
from interpreter.backend.vm import VM
from interpreter.frontend.lexer import Lexer
from interpreter.frontend.parser import Parser
from interpreter.frontend.tokens import TokenType
from interpreter.runtime.builtins import SimpleBuiltins
from interpreter.runtime.env import Environment

FIB_SRC = """
kaam fib(adad n) {
    agar n < 2 {
        wapas n
    } warna {
        wapas fib(n - 1) + fib(n - 2)
    }
}
likh(fib(24))
"""

LOOP_SRC = """
kaam loop_add() {
    adad total = 0
    har i mein range(100000) {
        total = total + i
    }
    wapas total
}
likh(loop_add())
"""

RECURSION_SRC = """
kaam f(adad n) {
    agar n == 0 {
        wapas 0
    } warna {
        wapas f(n - 1)
    }
}
f(50000)
"""


def _make_env() -> Environment:
    env = Environment()
    for name, func in SimpleBuiltins().get_all().items():
        env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return env


def run_source(code: str, env: Environment) -> None:
    tokens = Lexer(code).generate_tokens()
    ast = Parser(tokens, code).parse()
    resolver = Resolver(code)
    resolver.resolve(ast)
    instructions, constants, line_col_map = Compiler(code).compile(ast)
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


def timed(code: str, repeats: int = 3) -> float:
    env = _make_env()
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        best = float("inf")
        for _ in range(repeats):
            t = time.perf_counter()
            run_source(code, env)
            best = min(best, time.perf_counter() - t)
    finally:
        sys.stdout = old_stdout
    return best


def recursion_depth_reached(code: str, target: int) -> tuple[bool, int, float]:
    env = _make_env()
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        t = time.perf_counter()
        try:
            run_source(code, env)
            return True, target, time.perf_counter() - t
        except RecursionError:
            return False, target, time.perf_counter() - t
    finally:
        sys.stdout = old_stdout


def main() -> int:
    fib_s = timed(FIB_SRC)
    loop_s = timed(LOOP_SRC)
    ok, depth, rec_s = recursion_depth_reached(RECURSION_SRC, 50000)

    print(f"fib(24)       {fib_s * 1000:9.4f} ms  ({fib_s:8.4f} s)")
    print(f"loop-add 100k {loop_s * 1000:9.4f} ms  ({loop_s:8.4f} s)")
    if ok:
        print(f"f({depth})       {rec_s / depth * 1e6:8.3f} us/call  "
              f"({rec_s:7.3f} s total)")
    else:
        print(f"f({depth})       recursion failed before reaching depth {depth}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())