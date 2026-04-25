from ..frontend.ast_nodes import (
    Node, ProgramNode, BlockNode,
    NumberNode, StringNode, BoolNode, NullNode,
    VariableNode, AssignNode,
    BinaryOpNode, UnaryOpNode, PostfixOpNode,
    PrintNode, IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    ListNode, DictNode, SetNode, IndexNode,
    FunctionNode, ParamNode, CallNode, ReturnNode,
    MethodCallNode, GetAttrNode,
    ResultConstructorNode, ResultMethodCallNode, KharabiNode, TypeCastNode,
)
from .opcodes import OpCode
from ..frontend.tokens import TokenType
from ..objects import SdNumber, SdString, SdBool, SdNull, SdResult, SdFunction

class Compiler:
    def __init__(self, code):
        self.code = code
        self.instructions = []
        self.constants = []
        self.line_col_map = {}
        self.loop_stack = [] # Stack of (start_label, end_label)

    def emit(self, opcode, arg=None, node=None, line=None, column=None):
        if node:
            line = getattr(node, 'line', line or 0)
            column = getattr(node, 'column', column or 0)
        
        idx = len(self.instructions)
        self.instructions.append((opcode, arg))
        self.line_col_map[idx] = (line or 0, column or 0)
        return idx

    def add_const(self, value):
        # Check content equality for SdSheys
        for i, c in enumerate(self.constants):
            if type(c) == type(value):
                if hasattr(c, 'value') and hasattr(value, 'value'):
                    if type(c.value) == type(value.value) and c.value == value.value:
                        return i
                elif c == value:
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
        raise Exception(f"Compiler node qisam {type(node).name} khe handle natho kare saghjay.")

    def compile_ProgramNode(self, node):
        for stmt in node.statements:
            self.compile(stmt)
        self.emit(OpCode.HALT, line=0, column=0)
        return self.instructions, self.constants, self.line_col_map

    def compile_AssignNode(self, node):
        self.compile(node.value)
        if node.scope_level == 0:
            self.emit(OpCode.STORE_FAST, node.slot_index, node=node)
        else:
            const_idx = self.add_const(SdString(node.name))
            self.emit(OpCode.STORE_GLOBAL, const_idx, node=node)

    def compile_VariableNode(self, node):
        if node.scope_level == 0:
            self.emit(OpCode.LOAD_FAST, node.slot_index, node=node)
        else:
            const_idx = self.add_const(SdString(node.name))
            self.emit(OpCode.LOAD_GLOBAL, const_idx, node=node)

    def compile_NumberNode(self, node):
        const_idx = self.add_const(SdNumber(node.value))
        self.emit(OpCode.LOAD_CONST, const_idx, node=node)

    def compile_StringNode(self, node):
        const_idx = self.add_const(SdString(node.value))
        self.emit(OpCode.LOAD_CONST, const_idx, node=node)

    def compile_BoolNode(self, node):
        if node.value:
            self.emit(OpCode.PUSH_TRUE, node=node)
        else:
            self.emit(OpCode.PUSH_FALSE, node=node)

    def compile_NullNode(self, node):
        self.emit(OpCode.PUSH_NULL, node=node)

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
        if opcode:
            self.emit(opcode, node=node)
        else:
            raise Exception(f"Na-maloom binary operator: {node.op.type}.")

    def compile_UnaryOpNode(self, node):
        if node.op.type == TokenType.NOT:
            self.compile(node.right)
            self.emit(OpCode.LOGICAL_NOT, node=node)
        elif node.op.type == TokenType.MINUS:
            zero_idx = self.add_const(SdNumber(0))
            self.emit(OpCode.LOAD_CONST, zero_idx, node=node)
            self.compile(node.right)
            self.emit(OpCode.BINARY_SUB, node=node)
        elif node.op.type == TokenType.PLUS:
            self.compile(node.right)

    def compile_PrintNode(self, node):
        self.compile(node.value)
        self.emit(OpCode.PRINT_ITEM, node=node)

    EXPRESSION_NODES = (
        NumberNode, StringNode, BoolNode, NullNode, VariableNode,
        BinaryOpNode, UnaryOpNode, ListNode, DictNode, SetNode,
        IndexNode, CallNode, MethodCallNode, ResultConstructorNode,
        ResultMethodCallNode, PostfixOpNode, GetAttrNode, TypeCastNode
    )

    def compile_TypeCastNode(self, node):
        self.compile(node.expr)
        const_idx = self.add_const(SdString(node.target_type.name))
        self.emit(OpCode.TYPECAST, const_idx, node=node)

    def compile_BlockNode(self, node, is_function_body=False):
        num_stmts = len(node.statements)
        for i, stmt in enumerate(node.statements):
            is_last = (i == num_stmts - 1)
            self.compile(stmt)
            
            if isinstance(stmt, self.EXPRESSION_NODES):
                if is_function_body and is_last:
                    # Wrap in Ok and return
                    self.emit(OpCode.MAKE_OK, node=stmt)
                    self.emit(OpCode.RETURN_VALUE, node=stmt)
                else:
                    # Statement expression - pop its value
                    self.emit(OpCode.POP_TOP, node=stmt)

    def compile_IfNode(self, node: IfNode):
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        
        end_jumps = []
        
        # Initial 'agar'
        self.compile(node.condition)
        jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)
        
        self.compile(node.body)
        
        if node.else_if_bodies or node.else_body:
            # Jump to end after successful 'agar' body
            end_jumps.append(self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node))
            
            # Patch the initial agar's false jump to the first yawari or warna
            self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))

            for else_if_condition, else_if_body in node.else_if_bodies:
                self.compile(else_if_condition)
                jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)
                
                self.compile(else_if_body)
                
                # Jump to end after successful 'yawari' body
                end_jumps.append(self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node))
                
                # Patch this yawari's false jump to the next one or warna
                self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))
                
            if node.else_body:
                self.compile(node.else_body)
                
            # Patch all jumps to the end
            end_pos = len(self.instructions)
            for instr_idx in end_jumps:
                opcode, _ = self.instructions[instr_idx]
                self.instructions[instr_idx] = (opcode, end_pos)
        else:
            # Just one agar, patch its false jump to here (the end)
            self.instructions[jump_if_false_instr] = (OpCode.JUMP_IF_FALSE, len(self.instructions))

    def compile_WhileNode(self, node):
        loop_start = len(self.instructions)
        
        self.compile(node.condition)
        exit_jump_idx = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)
        
        # loop_stack: (continue_target, exit_jump_idx, break_jump_indices)
        self.loop_stack.append((loop_start, exit_jump_idx, []))
        
        self.compile(node.body)
        
        self.emit(OpCode.JUMP_ABSOLUTE, loop_start, node=node)
        
        exit_label = len(self.instructions)
        self.instructions[exit_jump_idx] = (OpCode.JUMP_IF_FALSE, exit_label)
        
        # Patch all breaks
        _, _, breaks = self.loop_stack.pop()
        for break_idx in breaks:
            self.instructions[break_idx] = (OpCode.JUMP_ABSOLUTE, exit_label)

    def compile_ForNode(self, node):
        self.compile(node.iterable)
        self.emit(OpCode.GET_ITER, node=node)
        
        loop_start = len(self.instructions)
        
        # FOR_ITER pops a value and pushes it, or jumps if done
        exit_jump_idx = self.emit(OpCode.FOR_ITER, 0, node=node)
        
        # Store iterator value in the variable
        self.emit(OpCode.STORE_FAST, node.iterator_slot, node=node)
        
        # continue in 'for' should go to loop_start (to get next item)
        self.loop_stack.append((loop_start, exit_jump_idx, []))
        
        self.compile(node.body)
        
        self.emit(OpCode.JUMP_ABSOLUTE, loop_start, node=node)
        
        exit_label = len(self.instructions)
        self.instructions[exit_jump_idx] = (OpCode.FOR_ITER, exit_label)
        
        # Patch all breaks
        _, _, breaks = self.loop_stack.pop()
        for break_idx in breaks:
            self.instructions[break_idx] = (OpCode.JUMP_ABSOLUTE, exit_label)

    def compile_BreakNode(self, node):
        if not self.loop_stack:
            raise Exception("tor (break) loop khaan baahar istamal natho kare saghjay.")
        
        idx = self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node)
        self.loop_stack[-1][2].append(idx)

    def compile_ContinueNode(self, node):
        if not self.loop_stack:
            raise Exception("jari (continue) loop khaan baahar istamal natho kare saghjay.")
        
        start_label = self.loop_stack[-1][0]
        self.emit(OpCode.JUMP_ABSOLUTE, start_label, node=node)

    def compile_ListNode(self, node):
        for el in node.elements:
            self.compile(el)
        self.emit(OpCode.BUILD_LIST, len(node.elements), node=node)

    def compile_DictNode(self, node):
        for k, v in node.pairs:
            self.compile(k)
            self.compile(v)
        self.emit(OpCode.BUILD_DICT, len(node.pairs), node=node)

    def compile_SetNode(self, node):
        for el in node.elements:
            self.compile(el)
        self.emit(OpCode.BUILD_SET, len(node.elements), node=node)

    def compile_IndexNode(self, node):
        self.compile(node.left)
        self.compile(node.index)
        if node.value:
            self.compile(node.value)
            self.emit(OpCode.STORE_SUBSCRIPT, node=node)
        else:
            self.emit(OpCode.BINARY_SUBSCRIPT, node=node)

    def _compile_call_args(self, node):
        for arg in node.args:
            self.compile(arg)
        if hasattr(node, 'keywords') and node.keywords:
            for name, val in node.keywords:
                const_idx = self.add_const(SdString(name))
                self.emit(OpCode.LOAD_CONST, const_idx, node=node)
                self.compile(val)
        
        # Note: star_args and kw_args are parsed but not yet supported by VM opcodes
        # We can add handling here once VM supports CALL_FUNCTION_VAR
        
        total_args = len(node.args)
        if hasattr(node, 'keywords') and node.keywords:
            total_args += len(node.keywords) * 2
        return total_args

    def compile_CallNode(self, node):
        total_args = self._compile_call_args(node)
        const_idx = self.add_const(SdString(node.name))
        self.emit(OpCode.CALL_FUNCTION, (const_idx, total_args), node=node)

    def compile_MethodCallNode(self, node):
        self.compile(node.instance)
        total_args = self._compile_call_args(node)
        const_idx = self.add_const(SdString(node.method_name))
        self.emit(OpCode.CALL_METHOD, (const_idx, total_args), node=node)

    def compile_GetAttrNode(self, node):
        self.compile(node.instance)
        const_idx = self.add_const(SdString(node.attr_name))
        self.emit(OpCode.GET_ATTR, const_idx, node=node)

    def compile_ResultConstructorNode(self, node):
        self.compile(node.value)
        if node.variant == "OK":
            self.emit(OpCode.MAKE_OK, node=node)
        else:
            self.emit(OpCode.MAKE_ERROR, node=node)

    def compile_ResultMethodCallNode(self, node):
        self.compile(node.receiver)
        self.compile(node.arg)
        if node.method_name == "bachao":
            self.emit(OpCode.CALL_BACHAO, node=node)
        elif node.method_name == "lazmi":
            self.emit(OpCode.CALL_LAZMI, node=node)

    def compile_PostfixOpNode(self, node):
        self.compile(node.expr)
        if node.op.type == TokenType.QMARK:
            self.emit(OpCode.POSTFIX_QMARK, node=node)
        elif node.op.type == TokenType.BANGBANG:
            self.emit(OpCode.POSTFIX_BANGBANG, node=node)

    def compile_KharabiNode(self, node):
        self.compile(node.message)
        self.emit(OpCode.PANIC, node=node)

    def compile_FunctionNode(self, node):
        line = getattr(node, 'line', 0)
        column = getattr(node, 'column', 0)
        
        # Save current state
        old_instructions = self.instructions
        old_line_col_map = self.line_col_map
        self.instructions = []
        self.line_col_map = {}
        
        # Compile body - call compile_BlockNode directly to pass is_function_body=True
        self.compile_BlockNode(node.body, is_function_body=True)
        
        # Implicit return at end (if not already returned by compile_BlockNode)
        self.emit(OpCode.PUSH_NULL, node=node)
        self.emit(OpCode.MAKE_OK, node=node)
        self.emit(OpCode.RETURN_VALUE, node=node)
        
        func_instructions = self.instructions
        func_line_col_map = self.line_col_map
        
        # Restore state
        self.instructions = old_instructions
        self.line_col_map = old_line_col_map
        
        # Create function object
        func_obj = SdFunction(
            node.name,
            node.params,
            func_instructions,
            self.constants,
            func_line_col_map,
            getattr(node, 'slot_count', 0),
            {}, # metadata
            node.return_type
        )
        
        const_idx = self.add_const(func_obj)
        self.emit(OpCode.LOAD_CONST, const_idx, node=node)
        
        # Store as global
        name_idx = self.add_const(SdString(node.name))
        self.emit(OpCode.STORE_GLOBAL, name_idx, node=node)

    def compile_ReturnNode(self, node):
        if node.value:
            self.compile(node.value)
        else:
            self.emit(OpCode.PUSH_NULL, node=node)
        
        # Auto-wrap in Ok (VM will pass through if already Result)
        self.emit(OpCode.MAKE_OK, node=node)
        self.emit(OpCode.RETURN_VALUE, node=node)
