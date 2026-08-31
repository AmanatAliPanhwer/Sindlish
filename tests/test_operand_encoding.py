"""
Operand-encoding conformance (issue #31, item 3.3).

``OPERAND_SHAPES`` in ``interpreter/backend/opcodes.py`` is the single source
of truth for what operand each opcode carries. These tests pin that table:
every opcode has an entry, every entry names a real opcode, every instruction
the compiler emits conforms to its declared shape, and the compiler rejects
mismatched operands at emit time.
"""

import pytest

from interpreter.backend.compiler import Compiler
from interpreter.backend.opcodes import OPERAND_SHAPES, OpCode
from interpreter.frontend.tokens import TokenType

from tests.test_golden_bytecode import PROGRAMS, compile_instructions, compile_listing


def _shape_fits(shape, arg):
    """Mirror of the compiler's ``_operand_fits``, kept independent."""
    if shape == "none":
        return arg is None
    if shape == "int":
        return isinstance(arg, int)
    if shape == "token":
        return isinstance(arg, TokenType)
    if shape == "call":
        return (
            isinstance(arg, tuple)
            and len(arg) == 3
            and isinstance(arg[0], int)
            and isinstance(arg[1], int)
            and isinstance(arg[2], bool)
        )
    if shape == "callvalue":
        return (
            isinstance(arg, tuple)
            and len(arg) == 2
            and isinstance(arg[0], int)
            and isinstance(arg[1], bool)
        )
    if shape == "store":
        if isinstance(arg, int):
            return True
        return (
            isinstance(arg, tuple)
            and len(arg) == 4
            and isinstance(arg[0], int)
            and isinstance(arg[1], bool)
        )
    return False


def test_each_opcode_has_a_shape():
    assert set(OPERAND_SHAPES) == set(OpCode)


def test_shapes_are_known_labels():
    assert set(OPERAND_SHAPES.values()) <= {
        "none",
        "int",
        "token",
        "call",
        "callvalue",
        "store",
    }


def test_emitted_instructions_fit_their_shapes():
    for _name, source, _expected in PROGRAMS:
        for op, arg in compile_instructions(source):
            assert _shape_fits(OPERAND_SHAPES[op], arg), (
                f"{op.name} arg {arg!r} violates shape "
                f"'{OPERAND_SHAPES[op]}'"
            )


def test_expression_callee_is_callvalue():
    listing = compile_listing("kaam make() { wapas 1 }\nz = make()()")
    assert ("CALL_VALUE", (0, False)) in listing


def test_emit_rejects_none_for_int_shape():
    compiler = Compiler("")
    with pytest.raises(ValueError, match="LOAD_CONST"):
        compiler.emit(OpCode.LOAD_CONST)


def test_emit_rejects_arg_for_none_shape():
    compiler = Compiler("")
    with pytest.raises(ValueError, match="BINARY_ADD"):
        compiler.emit(OpCode.BINARY_ADD, 5)


def test_emit_rejects_bad_call_tuple():
    compiler = Compiler("")
    with pytest.raises(ValueError, match="CALL_FUNCTION"):
        compiler.emit(OpCode.CALL_FUNCTION, (1, 2))


def test_emit_accepts_valid_shapes():
    compiler = Compiler("")
    assert compiler.emit(OpCode.HALT) == 0
    assert compiler.emit(OpCode.JUMP_ABSOLUTE, 3) == 1
    compiler.emit(OpCode.STORE_GLOBAL, (1, False, None, None))
    compiler.emit(OpCode.STORE_GLOBAL, 2)
    assert len(compiler.instructions) == 4