"""
Shared test helper for Sindlish interpreter tests.
"""

import sys
import io

sys.path.insert(0, "d:/Code/Sindlish")

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.resolver import Resolver
from interpreter.compiler import Compiler
from interpreter.vm import VM
from interpreter.env import Environment
from interpreter.tokens import TokenType
from interpreter.builtins import SimpleBuiltins
from interpreter.objects.primitives import SdNumber, SdString, SdBool, SdList, SdDict, SdSet, SdNull


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

    slot_names = {}
    for stmt in ast.statements:
        if hasattr(stmt, 'name') and hasattr(stmt, 'slot_index') and stmt.slot_index is not None:
            slot_names[stmt.name] = stmt.slot_index

    compiler = Compiler(code)
    instructions, constants, line_col_map = compiler.compile(ast)

    globals_env = create_globals_env()

    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        vm = VM(code, instructions, constants, globals_env, getattr(ast, "slot_count", 0), resolver.get_slot_metadata(), line_col_map)
        vm.slot_names = slot_names
        vm.slot_metadata = resolver.get_slot_metadata()
        vm.run()
    finally:
        sys.stdout = old_stdout

    return vm, buffer.getvalue()


def get_variable_value(vm, name):
    """
    Get variable value from VM instance.
    Checks slot_names mapping if available, otherwise checks all slots.
    Extracts raw value from SdObject wrappers.
    """
    if hasattr(vm, 'variables'):
        value = None

        # Check if we have a slot_names mapping
        if hasattr(vm, 'slot_names') and name in vm.slot_names:
            slot_idx = vm.slot_names[name]
            key = f"slot_{slot_idx}"
            var = vm.variables.get(key, {})
            if var:
                value = var.get("value")

        # Fallback: check all slots for the name (slot_X format)
        if value is None:
            for key in vm.variables:
                if vm.variables[key].get("name") == name:
                    value = vm.variables[key].get("value")

        # Extract raw value from SdObject wrappers
        if value is not None:
            return extract_value(value)
    return None


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