"""
Shared test helpers for Sindlish interpreter tests.

Provides run() to execute Sindlish code and helpers to extract values
from the VM for assertions.
"""

import sys
import io
import pytest

sys.path.insert(0, "d:/Code/Sindlish")

from interpreter.frontend.lexer import Lexer
from interpreter.frontend.parser import Parser
from interpreter.analysis.resolver import Resolver
from interpreter.backend.compiler import Compiler
from interpreter.backend.vm import VM
from interpreter.runtime.env import Environment
from interpreter.frontend.tokens import TokenType
from interpreter.runtime.builtins import SimpleBuiltins
from interpreter.objects import (
    SdNumber, SdString, SdBool, SdList, SdDict, SdSet, SdNull, SdResult,
    ADAD_TYPE, DAHAI_TYPE, LAFZ_TYPE, FAISLO_TYPE, FEHRIST_TYPE, LUGHAT_TYPE, MAJMUO_TYPE, KHALI_TYPE,
)


def create_globals_env():
    globals_env = Environment()
    simple_handler = SimpleBuiltins()
    for name, func in simple_handler.get_all().items():
        globals_env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return globals_env


def run(code: str):
    """
    Run Sindlish source code end-to-end and return
    (vm_instance, captured_stdout).
    """
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens, code)
    ast = parser.parse()

    resolver = Resolver(code)
    resolver.resolve(ast)

    compiler = Compiler(code)
    instructions, constants, line_col_map = compiler.compile(ast)

    globals_env = create_globals_env()
    slot_metadata = resolver.get_slot_metadata()

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        vm = VM(code, instructions, constants, globals_env, getattr(ast, "slot_count", 0), slot_metadata, line_col_map)
        vm.run()
    finally:
        sys.stdout = old_stdout

    return vm, buffer.getvalue()


def get_variable_value(vm, name):
    """
    Get variable value from VM instance.
    Prefers globals-environment records; falls back to main-frame slots.
    Extracts raw value from SdShey wrappers.
    """
    if name in vm.globals.records:
        return extract_value(vm.globals.records[name].value)

    frame = vm.frames[-1]
    if hasattr(vm, 'slot_names') and name in vm.slot_names:
        slot_idx = vm.slot_names[name]
        if 0 <= slot_idx < len(frame.slots) and frame.slots[slot_idx] is not None:
            return extract_value(frame.slots[slot_idx])
    return None


def extract_value(sd_object):
    """
    Extract Python value from a SdShey for testing.
    Recursively converts SdSheys to native Python types.
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
    elif isinstance(sd_object, SdResult):
        if sd_object.is_ok():
            return extract_value(sd_object.value)
        return sd_object
    else:
        return sd_object
