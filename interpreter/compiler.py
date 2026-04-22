from .ast_nodes import *
from .opcodes import OpCode
from .tokens import TokenType
from .objects.primitives import SdNumber, SdString, SdBool, SdNull

class Compiler:
    def __init__(self, code):
        self.code = code
        self.instructions = []
        self.constants = []
        self.line_col_map = {}

    def emit(self, opcode, arg=None, line=0, column=0):
        idx = len(self.instructions)
        self.instructions.append((opcode, arg))
        self.line_col_map[idx] = (line, column)
        return idx

    def add_const(self, value):
        # Check content equality for SdObjects - must also match inner value TYPE
        for i, c in enumerate(self.constants):
            if type(c) == type(value) and type(c.value) == type(value.value) and getattr(c, 'value', None) == getattr(value, 'value', None):
                return i
        self.constants.append(value)
        return len(self.constants) - 1

    def compile(self, node):
        if node is None:
            return
        method_name = f"compile_{type(node).__name__}"
        method = getattr(self, method_name, self.no_compile_method)
        return method(node)

    def no_compile_method(self, node):
        raise Exception(f"Compiler can't handle node type: {type(node).__name__}")

    def compile_ProgramNode(self, node):
        for stmt in node.statements:
            self.compile(stmt)
        self.emit(OpCode.HALT, line=0, column=0)
        return self.instructions, self.constants, self.line_col_map

    def compile_AssignNode(self, node):
        self.compile(node.value)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        if node.scope_level == 0:
            self.emit(OpCode.STORE_FAST, node.slot_index, line, column)
        else:
            const_idx = self.add_const(SdString(node.name))
            self.emit(OpCode.STORE_GLOBAL, const_idx, line, column)

    def compile_VariableNode(self, node):
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        if node.scope_level == 0:
            self.emit(OpCode.LOAD_FAST, node.slot_index, line, column)
        else:
            const_idx = self.add_const(SdString(node.name))
            self.emit(OpCode.LOAD_GLOBAL, const_idx, line, column)

    def compile_NumberNode(self, node):
        const_idx = self.add_const(SdNumber(node.value))
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.LOAD_CONST, const_idx, line, column)

    def compile_StringNode(self, node):
        const_idx = self.add_const(SdString(node.value))
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.LOAD_CONST, const_idx, line, column)

    def compile_BoolNode(self, node):
        if node.value:
            self.emit(OpCode.PUSH_TRUE, line=getattr(node, 'line', 0), column=getattr(node, 'column', 0))
        else:
            self.emit(OpCode.PUSH_FALSE, line=getattr(node, 'line', 0), column=getattr(node, 'column', 0))

    def compile_NullNode(self, node):
        self.emit(OpCode.PUSH_NULL, line=getattr(node, 'line', 0), column=getattr(node, 'column', 0))

    def compile_BinaryOpNode(self, node):
        self.compile(node.left)
        self.compile(node.right)
        
        op_map = {
            TokenType.PLUS: OpCode.BINARY_ADD,
            TokenType.MINUS: OpCode.BINARY_SUB,
            TokenType.MUL: OpCode.BINARY_MUL,
            TokenType.DIV: OpCode.BINARY_DIV,
            TokenType.POW: OpCode.BINARY_POW,
            TokenType.MOD: OpCode.BINARY_MOD,
            TokenType.EQEQ: OpCode.COMPARE_EQ,
            TokenType.NOTEQ: OpCode.COMPARE_NE,
            TokenType.LT: OpCode.COMPARE_LT,
            TokenType.LTEQ: OpCode.COMPARE_LE,
            TokenType.GT: OpCode.COMPARE_GT,
            TokenType.GTEQ: OpCode.COMPARE_GE,
            TokenType.AND: OpCode.LOGICAL_AND,
            TokenType.OR: OpCode.LOGICAL_OR,
        }
        opcode = op_map.get(node.op.type)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        if opcode:
            self.emit(opcode, line=line, column=column)
        else:
            raise Exception(f"Unknown binary operator: {node.op.type}")

    def compile_UnaryOpNode(self, node):
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        if node.op.type == TokenType.NOT:
            self.compile(node.right)
            self.emit(OpCode.LOGICAL_NOT, line=line, column=column)
        elif node.op.type == TokenType.MINUS:
            zero_idx = self.add_const(SdNumber(0))
            self.emit(OpCode.LOAD_CONST, zero_idx, line=line, column=column)
            self.compile(node.right)
            self.emit(OpCode.BINARY_SUB, line=line, column=column)
        elif node.op.type == TokenType.PLUS:
            self.compile(node.right)

    def compile_PrintNode(self, node):
        self.compile(node.value)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.PRINT_ITEM, line=line, column=column)

    def compile_BlockNode(self, node):
        for stmt in node.statements:
            self.compile(stmt)

    def compile_IfNode(self, node):
        self.compile(node.condition)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, line, column)
        
        self.compile(node.body)
        
        if node.else_body:
            jump_abs_instr = self.emit(OpCode.JUMP_ABSOLUTE, 0, line, column)
            self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))
            self.compile(node.else_body)
            self.instructions[jump_abs_instr] = (OpCode.JUMP_ABSOLUTE, len(self.instructions))
        else:
            self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))

    def compile_WhileNode(self, node):
        loop_start = len(self.instructions)
        self.compile(node.condition)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, line, column)
        
        self.compile(node.body)
        self.emit(OpCode.JUMP_ABSOLUTE, loop_start, line, column)
        
        self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))

    def compile_ListNode(self, node):
        for el in node.elements:
            self.compile(el)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.BUILD_LIST, len(node.elements), line=line, column=column)

    def compile_DictNode(self, node):
        for k, v in node.pairs:
            self.compile(k)
            self.compile(v)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.BUILD_DICT, len(node.pairs), line=line, column=column)

    def compile_SetNode(self, node):
        for el in node.elements:
            self.compile(el)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.BUILD_SET, len(node.elements), line=line, column=column)

    def compile_IndexNode(self, node):
        self.compile(node.left)
        self.compile(node.index)
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        if node.value:
            self.compile(node.value)
            self.emit(OpCode.STORE_SUBSCRIPT, line=line, column=column)
        else:
            self.emit(OpCode.BINARY_SUBSCRIPT, line=line, column=column)

    def compile_CallNode(self, node):
        for arg in node.args:
            self.compile(arg)
        const_idx = self.add_const(SdString(node.name))
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.CALL_FUNCTION, (const_idx, len(node.args)), line=line, column=column)

    def compile_MethodCallNode(self, node):
        self.compile(node.instance)
        for arg in node.args:
            self.compile(arg)
        const_idx = self.add_const(SdString(node.method_name))
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        self.emit(OpCode.CALL_METHOD, (const_idx, len(node.args)), line=line, column=column)
