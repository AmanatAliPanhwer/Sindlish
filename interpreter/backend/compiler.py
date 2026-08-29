from ..errors import TarteebJeGhalti
from ..frontend.ast_nodes import (
    BinaryOpNode,
    BoolNode,
    CallNode,
    DictNode,
    GetAttrNode,
    IfNode,
    IndexNode,
    ListNode,
    MethodCallNode,
    NullNode,
    NumberNode,
    PostfixOpNode,
    ResultConstructorNode,
    ResultMethodCallNode,
    SetNode,
    StringNode,
    TypeCastNode,
    UnaryOpNode,
    VariableNode,
)
from ..frontend.tokens import TokenType
from ..objects import SdFunction, SdNumber, SdString
from .markers import KwargMarker, KwargsDictMarker, StarArgsMarker
from .opcodes import OpCode

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
}


EXPRESSION_NODES = (
    NumberNode,
    StringNode,
    BoolNode,
    NullNode,
    VariableNode,
    BinaryOpNode,
    UnaryOpNode,
    ListNode,
    DictNode,
    SetNode,
    IndexNode,
    CallNode,
    MethodCallNode,
    ResultConstructorNode,
    ResultMethodCallNode,
    PostfixOpNode,
    GetAttrNode,
    TypeCastNode,
)


class Compiler:
    def __init__(self, code):
        self.code = code
        self.instructions = []
        self.constants = []
        # TODO: Work on converting line col map to a list
        self.line_col_map = {}
        self.loop_stack = []  # Stack of (start_label, end_label)
        self.fn_stack = []  # FunctionNode context chain for closure resolution

    def _deref_index(self, depth, name):
        """Index of a free variable in the current function's cell table."""
        fn = self.fn_stack[-1]
        return fn.hints.free_slots.index((depth, name))

    def emit(self, opcode, arg=None, node=None, line=None, column=None):
        if node:
            line = getattr(node, "line", line or 0)
            column = getattr(node, "column", column or 0)

        idx = self._current_pc()
        self.instructions.append((opcode, arg))
        self.line_col_map[idx] = (line or 0, column or 0)
        return idx

    def _current_pc(self):
        """Index of the next instruction to emit (the current program counter)."""
        return len(self.instructions)

    def _patch(self, idx, opcode, arg):
        """Overwrite the instruction at ``idx`` (used for back-patching jumps)."""
        self.instructions[idx] = (opcode, arg)

    def add_const(self, value):
        """Intern ``value`` into the shared constant table, returning its index.

        One constant table is shared across the whole program: function objects
        store indices into this same table, so a literal used inside a nested
        function reuses the program-level slot. Dedup uses type equality plus
        content equality for ``SdShey`` objects (e.g. two ``SdNumber(5)`` share
        one slot).
        """
        for i, existing in enumerate(self.constants):
            if type(existing) is type(value):
                if hasattr(value, "value") and existing.value == value.value:
                    return i
            elif existing == value:
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
        line = getattr(node, "line", 0)
        column = getattr(node, "column", 0)
        raise TarteebJeGhalti(
            f"Compiler node qisam {type(node).__name__} khe handle natho kare saghjay.",
            line,
            column,
            self.code,
        )

    def compile_ProgramNode(self, node):
        for stmt in node.statements:
            self.compile(stmt)
        self.emit(OpCode.HALT, line=0, column=0)
        return self.instructions, self.constants, self.line_col_map

    def compile_AssignNode(self, node):
        hints = node.hints
        self.compile(node.value)
        if hints.scope_level == 2:
            self.emit(
                OpCode.STORE_DEREF,
                self._deref_index(hints.deref_depth, hints.deref_name),
                node=node,
            )
            return
        if hints.scope_level == 0:
            fn = self.fn_stack[-1] if self.fn_stack else None
            cell_slots = getattr(fn.hints, "cell_slots", ()) if fn is not None else ()
            if node.name in cell_slots:
                self.emit(OpCode.STORE_DEREF, cell_slots.index(node.name), node=node)
            else:
                self.emit(OpCode.STORE_FAST, hints.slot_index, node=node)
        else:
            const_idx = self.add_const(SdString(node.name))
            has_explicit_type = hints.has_explicit_type and hints.type is not None
            info = (
                const_idx,
                bool(hints.is_const),
                hints.type if has_explicit_type else None,
                hints.element_type,
            )
            self.emit(OpCode.STORE_GLOBAL, info, node=node)

    def compile_VariableNode(self, node):
        hints = node.hints
        if hints.scope_level == 2:
            self.emit(
                OpCode.LOAD_DEREF,
                self._deref_index(hints.deref_depth, hints.deref_name),
                node=node,
            )
        elif hints.scope_level == 0:
            fn = self.fn_stack[-1] if self.fn_stack else None
            cell_slots = getattr(fn.hints, "cell_slots", ()) if fn is not None else ()
            if node.name in cell_slots:
                self.emit(OpCode.LOAD_DEREF, cell_slots.index(node.name), node=node)
            else:
                self.emit(OpCode.LOAD_FAST, hints.slot_index, node=node)
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
        if node.op.type == TokenType.AND:
            self.compile(node.left)
            jump_idx = self.emit(OpCode.JUMP_IF_FALSE_OR_POP, 0, node=node)
            self.compile(node.right)
            self._patch(jump_idx, OpCode.JUMP_IF_FALSE_OR_POP, self._current_pc())
            return

        if node.op.type == TokenType.OR:
            self.compile(node.left)
            jump_idx = self.emit(OpCode.JUMP_IF_TRUE_OR_POP, 0, node=node)
            self.compile(node.right)
            self._patch(jump_idx, OpCode.JUMP_IF_TRUE_OR_POP, self._current_pc())
            return

        self.compile(node.left)
        self.compile(node.right)
        opcode = op_map.get(node.op.type)
        if opcode:
            self.emit(opcode, node=node)
        else:
            line = getattr(node, "line", 0)
            column = getattr(node, "column", 0)
            raise TarteebJeGhalti(
                f"Na-maloom binary operator: {node.op.type}.",
                line,
                column,
                self.code,
            )

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

    def compile_TypeCastNode(self, node):
        self.compile(node.expr)
        self.emit(OpCode.TYPECAST, node.target_type, node=node)

    def compile_BlockNode(self, node, is_function_body=False):
        num_stmts = len(node.statements)
        for i, stmt in enumerate(node.statements):
            is_last = i == num_stmts - 1

            # Special case for implicit return in function body
            if is_function_body and is_last:
                self.compile(stmt)
                if isinstance(stmt, EXPRESSION_NODES):
                    self.emit(OpCode.MAKE_OK, node=stmt)
                    self.emit(OpCode.RETURN_VALUE, node=stmt)
                else:
                    self.emit(OpCode.PUSH_NULL, node=stmt)
                    self.emit(OpCode.MAKE_OK, node=stmt)
                    self.emit(OpCode.RETURN_VALUE, node=stmt)
                continue

            self.compile(stmt)

            if isinstance(stmt, EXPRESSION_NODES):
                self.emit(OpCode.POP_TOP, node=stmt)

    def compile_IfNode(self, node: IfNode):
        end_jumps = []

        self.compile(node.condition)
        jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)

        self.compile(node.body)

        if node.else_if_bodies or node.else_body:
            end_jumps.append(self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node))
            self._patch(jump_if_false_instr, OpCode.JUMP_IF_FALSE, self._current_pc())

            for else_if_condition, else_if_body in node.else_if_bodies:
                self.compile(else_if_condition)
                jump_if_false_instr = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)
                self.compile(else_if_body)
                end_jumps.append(self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node))
                self._patch(
                    jump_if_false_instr, OpCode.JUMP_IF_FALSE, self._current_pc()
                )

            if node.else_body:
                self.compile(node.else_body)

            # Patch all jumps to the end
            end_pos = self._current_pc()
            for instr_idx in end_jumps:
                opcode = self.instructions[instr_idx][0]
                self._patch(instr_idx, opcode, end_pos)
        else:
            self._patch(jump_if_false_instr, OpCode.JUMP_IF_FALSE, self._current_pc())

    def compile_WhileNode(self, node):
        loop_start = self._current_pc()

        self.compile(node.condition)
        exit_jump_idx = self.emit(OpCode.JUMP_IF_FALSE, 0, node=node)

        # loop_stack: (continue_target, exit_jump_idx, break_jump_indices)
        self.loop_stack.append((loop_start, exit_jump_idx, []))

        self.compile(node.body)

        self.emit(OpCode.JUMP_ABSOLUTE, loop_start, node=node)

        exit_label = self._current_pc()
        self._patch(exit_jump_idx, OpCode.JUMP_IF_FALSE, exit_label)

        breaks = self.loop_stack.pop()[-1]
        for break_idx in breaks:
            self._patch(break_idx, OpCode.JUMP_ABSOLUTE, exit_label)

    def compile_ForNode(self, node):
        self.compile(node.iterable)
        self.emit(OpCode.GET_ITER, node=node)

        loop_start = self._current_pc()

        exit_jump_idx = self.emit(OpCode.FOR_ITER, 0, node=node)

        if node.hints.iterator_slot == -1:
            const_idx = self.add_const(SdString(node.iterator))
            self.emit(OpCode.STORE_GLOBAL, (const_idx, False, None, None), node=node)
        else:
            self.emit(OpCode.STORE_FAST, node.hints.iterator_slot, node=node)

        self.loop_stack.append((loop_start, exit_jump_idx, []))

        self.compile(node.body)

        self.emit(OpCode.JUMP_ABSOLUTE, loop_start, node=node)

        exit_label = self._current_pc()
        self._patch(exit_jump_idx, OpCode.FOR_ITER, exit_label)

        breaks = self.loop_stack.pop()[-1]
        for break_idx in breaks:
            self._patch(break_idx, OpCode.JUMP_ABSOLUTE, exit_label)

    def compile_BreakNode(self, node):
        if not self.loop_stack:
            line = getattr(node, "line", 0)
            column = getattr(node, "column", 0)
            raise TarteebJeGhalti(
                "tor (break) loop khaan baahar istamal natho kare saghjay.",
                line,
                column,
                self.code,
            )

        idx = self.emit(OpCode.JUMP_ABSOLUTE, 0, node=node)
        self.loop_stack[-1][2].append(idx)

    def compile_ContinueNode(self, node):
        if not self.loop_stack:
            line = getattr(node, "line", 0)
            column = getattr(node, "column", 0)
            raise TarteebJeGhalti(
                "jari (continue) loop khaan baahar istamal natho kare saghjay.",
                line,
                column,
                self.code,
            )

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
        total_args = 0

        for arg in node.args:
            self.compile(arg)
            total_args += 1

        if getattr(node, "star_args", None) is not None:
            star_idx = self.add_const(StarArgsMarker())
            self.emit(OpCode.LOAD_CONST, star_idx, node=node)
            self.compile(node.star_args)
            total_args += 2

        if getattr(node, "kw_args", None) is not None:
            kw_idx = self.add_const(KwargsDictMarker())
            self.emit(OpCode.LOAD_CONST, kw_idx, node=node)
            self.compile(node.kw_args)
            total_args += 2

        if getattr(node, "keywords", None):
            for name, val in node.keywords:
                marker_idx = self.add_const(KwargMarker(name))
                self.emit(OpCode.LOAD_CONST, marker_idx, node=node)
                self.compile(val)
                total_args += 2

        return total_args

    def compile_CallNode(self, node):
        if isinstance(node.name, str):
            callee = node.hints.callee_variable
            if callee is not None:
                # Local/captured callee: load the variable onto the stack,
                # then args; CALL_VALUE pops args then the callee.
                # (CALL_FUNCTION only looks up globals, so it can't call locals.)
                self.compile(callee)
                total_args = self._compile_call_args(node)
                self.emit(OpCode.CALL_VALUE, total_args, node=node)
            else:
                total_args = self._compile_call_args(node)
                const_idx = self.add_const(SdString(node.name))
                self.emit(OpCode.CALL_FUNCTION, (const_idx, total_args), node=node)
        else:
            # Expression callee (f()(), factory results): callee first,
            # then args; CALL_VALUE pops args then the callee.
            self.compile(node.name)
            total_args = self._compile_call_args(node)
            self.emit(OpCode.CALL_VALUE, total_args, node=node)

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

    def compile_GhaltiNode(self, node):
        self.compile(node.message)
        self.emit(OpCode.PANIC, node=node)

    def compile_GlobalNode(self, node):
        pass

    def compile_NonLocalNode(self, node):
        # Declaration only: the resolver registered the capture
        pass

    def _compile_function_body(self, node):
        """Compile ``node.body`` into a fresh instruction buffer.

        Returns ``(instructions, line_col_map)`` for the body. The buffer is
        swapped out and back so nested functions never corrupt the enclosing
        function's in-progress output; ``fn_stack`` is pushed so closure
        resolution (``_deref_index``) sees this function as the innermost.
        """
        old_instructions = self.instructions
        old_line_col_map = self.line_col_map
        self.instructions = []
        self.line_col_map = {}

        self.fn_stack.append(node)
        self.compile_BlockNode(node.body, is_function_body=True)

        body_instructions = self.instructions
        body_line_col_map = self.line_col_map

        self.fn_stack.pop()
        self.instructions = old_instructions
        self.line_col_map = old_line_col_map
        return body_instructions, body_line_col_map

    def compile_FunctionNode(self, node):

        func_instructions, func_line_col_map = self._compile_function_body(node)

        hints = node.hints
        func_obj = SdFunction(
            node.name,
            node.params,
            func_instructions,
            self.constants,
            func_line_col_map,
            hints.slot_count,
            hints.slot_metadata,
            node.return_type,
            cell_names=hints.cell_slots or (),
            free_specs=hints.free_slots or (),
            cell_metadata=hints.cell_metadata,
        )

        const_idx = self.add_const(func_obj)

        num_defaults = 0
        for param in node.params:
            if param.default is not None:
                self.compile(param.default)
                num_defaults += 1

        self.emit(OpCode.LOAD_CONST, const_idx, node=node)
        self.emit(OpCode.MAKE_FUNCTION, num_defaults, node=node)

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
