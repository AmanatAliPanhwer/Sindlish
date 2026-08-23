"""Backend sub-package: bytecode compilation and VM execution."""

from .compiler import Compiler
from .frame import BytecodeFrame
from .opcodes import OpCode
from .vm import VM

__all__ = ["VM", "BytecodeFrame", "Compiler", "OpCode"]
