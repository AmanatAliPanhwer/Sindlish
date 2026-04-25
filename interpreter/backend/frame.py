"""
Bytecode execution frame.

A BytecodeFrame represents a single function call's execution context
within the VM, holding its own instruction stream, local variable slots,
and instruction pointer.
"""

from ..runtime.env import Environment


class BytecodeFrame:
    """
    Execution frame for the bytecode VM.

    Each function call creates a new frame with its own:
    - instructions: the bytecode to execute
    - constants: the constant pool
    - slots: local variable storage (O(1) access)
    - ip: instruction pointer
    """

    __slots__ = ('name', 'instructions', 'constants', 'line_col_map',
                 'slots', 'slot_metadata', 'ip', 'call_metadata')

    def __init__(self, name: str, instructions: list, constants: list,
                 line_col_map: dict, slot_count: int, slot_metadata: dict):
        self.name = name
        self.instructions = instructions
        self.constants = constants
        self.line_col_map = line_col_map
        self.slots = [None] * slot_count
        self.slot_metadata = slot_metadata
        self.ip = 0
        self.call_metadata = {}

    def __repr__(self) -> str:
        return f"<BytecodeFrame {self.name} | IP: {self.ip}/{len(self.instructions)}>"
