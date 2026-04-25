from enum import IntEnum, auto

class OpCode(IntEnum):
    # Constants and Variables
    LOAD_CONST = auto()
    LOAD_FAST = auto()    # O(1) Local slots
    STORE_FAST = auto()   # O(1) Local slots
    LOAD_GLOBAL = auto() # Dictionary-based globals
    STORE_GLOBAL = auto()
    
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
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()
    LOGICAL_NOT = auto()
    
    # Stack manipulation
    POP_TOP = auto()
    DUP_TOP = auto()
    
    # Control Flow
    JUMP_ABSOLUTE = auto()
    JUMP_IF_FALSE = auto()
    
    # Iteration
    GET_ITER = auto()
    FOR_ITER = auto()
    
    # Output
    PRINT_ITEM = auto()
    
    # Collections
    BUILD_LIST = auto()
    BUILD_DICT = auto()
    BUILD_SET = auto()
    BINARY_SUBSCRIPT = auto() # l[i]
    STORE_SUBSCRIPT = auto()  # l[i] = v
    
    # Functions and Methods
    CALL_FUNCTION = auto()
    CALL_METHOD = auto()
    GET_ATTR = auto()
    
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
