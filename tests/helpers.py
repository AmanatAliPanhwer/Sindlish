"""
Shared test helper for Sindlish interpreter tests.
"""

import sys
import io

sys.path.insert(0, "d:/Code/Sindlish")

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.executor import Interpreter


def run(code: str) -> tuple[Interpreter, str]:
    """
    Run Sindlish source code end-to-end and return
    (interpreter_instance, captured_stdout).
    """
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens, code)
    ast = parser.parse()

    interp = Interpreter(code)

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        interp.visit(ast)
    finally:
        sys.stdout = old_stdout

    return interp, buffer.getvalue()
