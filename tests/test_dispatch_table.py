"""
Dispatch table generation (issue #31, item 3.2).

The VM builds its dispatch table from handler names (``_op_<opcode.lower()>``);
these tests pin the bidirectional contract: every opcode resolves to a
handler and every ``_op_*`` method corresponds to exactly one opcode.
"""

from interpreter.backend.opcodes import OpCode

from tests.conftest import run


def _op_methods(vm):
    return sorted(
        name for name in dir(vm) if name.startswith("_op_") and callable(getattr(vm, name))
    )


def test_every_opcode_has_a_handler():
    vm, _ = run("x = 1")
    assert set(vm.dispatch_table) == set(OpCode)
    for opcode in OpCode:
        handler = vm.dispatch_table[opcode]
        assert handler.__func__ is getattr(vm, f"_op_{opcode.name.lower()}").__func__


def test_every_handler_maps_to_one_opcode():
    vm, _ = run("x = 1")
    expected = {f"_op_{op.name.lower()}" for op in OpCode}
    assert set(_op_methods(vm)) == expected


def test_dispatch_index_alignment():
    vm, _ = run("x = 1")
    for opcode, handler in vm.dispatch_table.items():
        assert vm._dispatch[int(opcode)] is handler