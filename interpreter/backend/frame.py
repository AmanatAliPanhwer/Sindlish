"""
Bytecode execution frame.

A BytecodeFrame represents a single function call's execution context
within the VM, holding its own instruction stream, local variable slots,
and instruction pointer.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from ..objects.core import Cell


class BytecodeFrame:
    """
    Execution frame for the bytecode VM.

    Each function call creates a new frame with its own:
    - instructions: the bytecode to execute
    - constants: the constant pool
    - slots: local variable storage (O(1) access)
    - cells: closure cell storage (captured locals, then inherited upvalues)
    - ip: instruction pointer
    """

    __slots__ = (
        "call_metadata",
        "cell_map",
        "cells",
        "constants",
        "function_name",
        "instructions",
        "ip",
        "line_col_map",
        "name",
        "return_type",
        "slot_metadata",
        "slots",
    )

    def __init__(
        self,
        name: str,
        instructions: Sequence[tuple[object, object]],
        constants: Sequence[object],
        line_col_map: Sequence[tuple[int, int]],
        slot_count: int,
        slot_metadata: Mapping[str, object],
        func: object | None = None,
    ):
        self.name = name
        self.instructions = instructions
        self.constants = constants
        self.line_col_map = line_col_map
        self.slots: list[object | None] = [None] * slot_count
        self.slot_metadata = slot_metadata
        self.cells: list[Cell | object | None] = []
        self.cell_map: dict[str, int] = {}
        if func is not None:
            cell_names = getattr(func, "cell_names", ())
            free_specs = getattr(func, "free_specs", ())
            if cell_names or free_specs:
                cell_metadata = getattr(func, "cell_metadata", {})
                idx = 0
                for n in cell_names:
                    self.cells.append(
                        Cell(name=n, metadata=cell_metadata.get(n, {}))
                    )
                    self.cell_map[n] = idx
                    idx += 1
                inherited = tuple(getattr(func, "cells", ()) or ())
                for j, (_, n) in enumerate(free_specs):
                    if n not in self.cell_map:
                        self.cell_map[n] = len(self.cells)
                        self.cells.append(
                            inherited[j] if j < len(inherited) else None
                        )
                    idx += 1
        self.ip = 0
        self.call_metadata = {}
        self.return_type = None
        self.function_name = None

    def __repr__(self) -> str:
        return f"<BytecodeFrame {self.name} | IP: {self.ip}/{len(self.instructions)}>"
