"""The bytecode instruction set.

Each :class:`OpCode` value is the index into the VM's contiguous dispatch
table (see :class:`.vm.VM`); the enumerator is deliberately mono-directional
(``auto()``) so opcodes stay packed from 1 upward.
"""

from __future__ import annotations

from enum import IntEnum, auto


class OpCode(IntEnum):
    # Constants and Variables
    LOAD_CONST = auto()
    LOAD_FAST = auto()  # O(1) Local slots
    STORE_FAST = auto()  # O(1) Local slots
    LOAD_GLOBAL = auto()  # Dictionary-based globals
    STORE_GLOBAL = auto()
    LOAD_DEREF = auto()  # Closure cells (captured locals)
    STORE_DEREF = auto()

    # Primitive Value Push
    PUSH_NULL = auto()
    PUSH_TRUE = auto()
    PUSH_FALSE = auto()

    # Arithmetic
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()
    BINARY_POW = auto()
    BINARY_MOD = auto()

    # Comparisons
    COMPARE_EQ = auto()
    COMPARE_NE = auto()
    COMPARE_LT = auto()
    COMPARE_LE = auto()
    COMPARE_GT = auto()
    COMPARE_GE = auto()

    # Logical
    LOGICAL_NOT = auto()

    # Stack manipulation
    POP_TOP = auto()

    # Control Flow
    JUMP_ABSOLUTE = auto()
    JUMP_IF_FALSE = auto()
    JUMP_IF_FALSE_OR_POP = auto()
    JUMP_IF_TRUE_OR_POP = auto()

    # Iteration
    GET_ITER = auto()
    FOR_ITER = auto()

    # Collections
    BUILD_LIST = auto()
    BUILD_DICT = auto()
    BUILD_SET = auto()
    BINARY_SUBSCRIPT = auto()  # l[i]
    STORE_SUBSCRIPT = auto()  # l[i] = v

    # Functions and Methods
    CALL_FUNCTION = auto()
    CALL_VALUE = auto()  # Call a function value from the stack (f()())
    CALL_METHOD = auto()
    GET_ATTR = auto()
    MAKE_FUNCTION = auto()

    # Result System and Errors
    MAKE_OK = auto()
    MAKE_ERROR = auto()
    CALL_BACHAO = auto()
    CALL_LAZMI = auto()
    POSTFIX_QMARK = auto()
    POSTFIX_BANGBANG = auto()
    PANIC = auto()
    TYPECAST = auto()

    # Completion
    RETURN_VALUE = auto()
    HALT = auto()


# Operand shapes per opcode. The compiler enforces these at emit time and at
# back-patch time; the VM handlers rely on them implicitly (see
# ``OPERAND_SHAPES`` in :mod:`.compiler` for the validating predicate and
# ``book/src/opcodes.md`` for the documented encoding table).
#
# Shape labels:
#   ``none``       -- no operand (arg is ``None``)
#   ``int``        -- a small int (pool / slot / cell / name index, jump
#                     target, build count, ``MAKE_FUNCTION`` default count)
#   ``token``      -- a ``TokenType`` cast target (``TYPECAST``)
#   ``call``       -- ``(name_idx, nargs, has_kwargs)`` for named/method calls
#   ``callvalue``  -- ``(nargs, has_kwargs)`` for expression-callee calls
#   ``store``      -- ``STORE_GLOBAL``: either a bare ``name_idx`` (function
#                     definitions) or ``(idx, is_const, type, element_type)``
#                     enforcement tuple
OPERAND_SHAPES: dict[OpCode, str] = {
    # Constants and Variables
    OpCode.LOAD_CONST: "int",
    OpCode.LOAD_FAST: "int",
    OpCode.STORE_FAST: "int",
    OpCode.LOAD_GLOBAL: "int",
    OpCode.STORE_GLOBAL: "store",
    OpCode.LOAD_DEREF: "int",
    OpCode.STORE_DEREF: "int",
    # Primitive Value Push
    OpCode.PUSH_NULL: "none",
    OpCode.PUSH_TRUE: "none",
    OpCode.PUSH_FALSE: "none",
    # Arithmetic
    OpCode.BINARY_ADD: "none",
    OpCode.BINARY_SUB: "none",
    OpCode.BINARY_MUL: "none",
    OpCode.BINARY_DIV: "none",
    OpCode.BINARY_POW: "none",
    OpCode.BINARY_MOD: "none",
    # Comparisons
    OpCode.COMPARE_EQ: "none",
    OpCode.COMPARE_NE: "none",
    OpCode.COMPARE_LT: "none",
    OpCode.COMPARE_LE: "none",
    OpCode.COMPARE_GT: "none",
    OpCode.COMPARE_GE: "none",
    # Logical
    OpCode.LOGICAL_NOT: "none",
    # Stack manipulation
    OpCode.POP_TOP: "none",
    # Control Flow
    OpCode.JUMP_ABSOLUTE: "int",
    OpCode.JUMP_IF_FALSE: "int",
    OpCode.JUMP_IF_FALSE_OR_POP: "int",
    OpCode.JUMP_IF_TRUE_OR_POP: "int",
    # Iteration
    OpCode.GET_ITER: "none",
    OpCode.FOR_ITER: "int",
    # Collections
    OpCode.BUILD_LIST: "int",
    OpCode.BUILD_DICT: "int",
    OpCode.BUILD_SET: "int",
    OpCode.BINARY_SUBSCRIPT: "none",
    OpCode.STORE_SUBSCRIPT: "none",
    # Functions and Methods
    OpCode.CALL_FUNCTION: "call",
    OpCode.CALL_VALUE: "callvalue",
    OpCode.CALL_METHOD: "call",
    OpCode.GET_ATTR: "int",
    OpCode.MAKE_FUNCTION: "int",
    # Result System and Errors
    OpCode.MAKE_OK: "none",
    OpCode.MAKE_ERROR: "none",
    OpCode.CALL_BACHAO: "none",
    OpCode.CALL_LAZMI: "none",
    OpCode.POSTFIX_QMARK: "none",
    OpCode.POSTFIX_BANGBANG: "none",
    OpCode.PANIC: "none",
    OpCode.TYPECAST: "token",
    # Completion
    OpCode.RETURN_VALUE: "none",
    OpCode.HALT: "none",
}
