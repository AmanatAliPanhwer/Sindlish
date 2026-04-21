"""
Shared test helper for Sindlish interpreter tests.
"""

import sys
import io

sys.path.insert(0, "d:/Code/Sindlish")

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.executor import Interpreter
from interpreter.objects.primitives import SdNumber, SdString, SdBool, SdList, SdDict, SdSet, SdNull


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


def extract_value(sd_object):
    """
    Extract Python value from a SdObject for testing.
    Recursively converts SdObjects to native Python types.
    """
    if isinstance(sd_object, SdNumber):
        return sd_object.value
    elif isinstance(sd_object, SdString):
        return sd_object.value
    elif isinstance(sd_object, SdBool):
        return sd_object.value
    elif isinstance(sd_object, SdNull):
        return None
    elif isinstance(sd_object, SdList):
        return [extract_value(elem) for elem in sd_object.elements]
    elif isinstance(sd_object, SdDict):
        return {extract_value(k) if not isinstance(k, str) else k: extract_value(v) for k, v in sd_object.items()}
    elif isinstance(sd_object, SdSet):
        return {extract_value(elem) for elem in sd_object.elements}
    else:
        return sd_object
