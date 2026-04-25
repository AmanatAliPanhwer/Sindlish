from ..frontend.ast_nodes import (
    Node, ProgramNode, BlockNode,
    NumberNode, StringNode, BoolNode, NullNode,
    VariableNode, AssignNode,
    BinaryOpNode, UnaryOpNode, PostfixOpNode,
    PrintNode, IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    ListNode, DictNode, SetNode, IndexNode,
    FunctionNode, ParamNode, CallNode, ReturnNode,
    MethodCallNode, GetAttrNode,
    ResultConstructorNode, ResultMethodCallNode, KharabiNode,
)
from ..errors import NaleJeGhalti, HalndeVaktGhalti, QisamJeGhalti
from ..frontend.tokens import TokenType

class Resolver:
    def __init__(self, code):
        self.code = code
        self.scopes = [{}]
        self.slot_indices = {}
        self.next_slot = 0
        self.slot_metadata = {}  # slot_index -> {"is_const": bool, "type": TokenType, "element_type": any}
        self.symbols = [] # List of {"name": str, "type": TokenType, "line": int, "col": int, "kind": str}

    def infer_type(self, node):
        if isinstance(node, NumberNode):
            return TokenType.ADAD if isinstance(node.value, int) else TokenType.DAHAI
        elif isinstance(node, StringNode):
            return TokenType.LAFZ
        elif isinstance(node, BoolNode):
            return TokenType.FAISLO
        elif isinstance(node, NullNode):
            return TokenType.KHALI
        elif isinstance(node, ListNode):
            return TokenType.FEHRIST
        elif isinstance(node, DictNode):
            return TokenType.LUGHAT
        elif isinstance(node, SetNode):
            return TokenType.MAJMUO
        elif isinstance(node, VariableNode):
            slot = self.lookup(node.name)
            if slot is not None:
                meta = self.slot_metadata.get(slot, {})
                return meta.get("type")
            return None
        return None

    def resolve(self, node):
        if node is None:
            return
        method_name = f"resolve_{type(node).__name__}"
        method = getattr(self, method_name, self.no_resolve_method)
        return method(node)

    def no_resolve_method(self, node):
        """Default visitor that recursively resolves all Node attributes."""
        if not hasattr(node, '__slots__'):
            return
            
        for attr in node.__slots__:
            if attr in ('line', 'column'):
                continue
            
            val = getattr(node, attr)
            self._resolve_recursive(val)

    def _resolve_recursive(self, val):
        if isinstance(val, Node):
            self.resolve(val)
        elif isinstance(val, (list, tuple)):
            for item in val:
                self._resolve_recursive(item)

    def resolve_ProgramNode(self, node):
        for stmt in node.statements:
            self.resolve(stmt)
        node.slot_count = self.next_slot

    def resolve_BlockNode(self, node):
        self.push_scope()
        for stmt in node.statements:
            self.resolve(stmt)
        self.pop_scope()

    def _verify_assignment_types(self, node):
        inferred_type = self.infer_type(node.value)
        if inferred_type is not None and inferred_type != node.type:
            line = getattr(node, 'line', 0)
            column = getattr(node, 'column', 0)
            raise QisamJeGhalti(
                f"Qisam natho mile: {node.type.name.lower()} khapyo paye, par {inferred_type.name.lower()} milyo.",
                line, column, self.code
            )
        
        if node.type in (TokenType.FEHRIST, TokenType.MAJMUO) and node.element_type is not None:
            if isinstance(node.value, ListNode):
                for elem in node.value.elements:
                    elem_type = self.infer_type(elem)
                    if elem_type != node.element_type:
                        line = getattr(elem, 'line', 0)
                        column = getattr(elem, 'column', 0)
                        raise QisamJeGhalti(
                            f"Fehrist je elements jo qisam {node.element_type.name.lower()} hujjhan lazmi aahe, par {elem_type.name.lower()} milyo.",
                            line, column, self.code
                        )
            elif isinstance(node.value, SetNode):
                for elem in node.value.elements:
                    elem_type = self.infer_type(elem)
                    if elem_type != node.element_type:
                        line = getattr(elem, 'line', 0)
                        column = getattr(elem, 'column', 0)
                        raise QisamJeGhalti(
                            f"Majmuo je elements jo qisam {node.element_type.name.lower()} hujjhan lazmi aahe, par {elem_type.name.lower()} milyo.",
                            line, column, self.code
                        )

    def resolve_AssignNode(self, node):
        self.resolve(node.value)
        
        if node.has_explicit_type and node.type is not None:
            self._verify_assignment_types(node)
        
        slot = self.lookup(node.name)
        if slot is None:
            slot = self.define(node.name, node)
        
        node.slot_index = slot
        node.scope_level = 0
        
        if slot not in self.slot_metadata:
            self.slot_metadata[slot] = {
                "is_const": node.is_const,
                "type": node.type,
                "element_type": node.element_type,
                "has_explicit_type": node.has_explicit_type
            }

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def define(self, name, node=None):
        if name in self.scopes[-1]:
            return self.scopes[-1][name]
        
        slot = self.next_slot
        self.next_slot += 1
        
        self.scopes[-1][name] = slot
        
        # Track symbol for LSP
        if node:
            self.symbols.append({
                "name": name,
                "type": getattr(node, 'type', None),
                "line": getattr(node, 'line', 0),
                "col": getattr(node, 'column', 0),
                "kind": "variable" if isinstance(node, AssignNode) else "function"
            })
            
        return slot

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None
    
    def get_slot_metadata(self):
        return self.slot_metadata

    def resolve_VariableNode(self, node):
        slot = self.lookup(node.name)
        if slot is None:
            node.scope_level = 1
        else:
            node.slot_index = slot
            node.scope_level = 0

    def resolve_IfNode(self, node):
        self.resolve(node.condition)
        self.resolve(node.body)
        if node.else_if_bodies:
            for else_if_condition, else_if_body in node.else_if_bodies:
                self.resolve(else_if_condition)
                self.resolve(else_if_body)
        if node.else_body:
            self.resolve(node.else_body)

    def resolve_WhileNode(self, node):
        self.resolve(node.condition)
        self.resolve(node.body)

    def resolve_ForNode(self, node):
        self.resolve(node.iterable)
        
        # Iterator variable is defined in a new scope inside the loop
        self.push_scope()
        slot = self.define(node.iterator, node)
        # We need to store this slot info in the ForNode for the compiler
        node.iterator_slot = slot
        
        self.resolve(node.body)
        self.pop_scope()

    def resolve_BreakNode(self, node):
        pass

    def resolve_ContinueNode(self, node):
        pass

    def resolve_CallNode(self, node):
        for arg in node.args:
            self.resolve(arg)

    def resolve_MethodCallNode(self, node):
        self.resolve(node.instance)
        for arg in node.args:
            self.resolve(arg)

    def resolve_GetAttrNode(self, node):
        self.resolve(node.instance)

    def resolve_BinaryOpNode(self, node):
        self.resolve(node.left)
        self.resolve(node.right)

    def resolve_PrintNode(self, node):
        self.resolve(node.value)

    def resolve_ListNode(self, node):
        for el in node.elements:
            self.resolve(el)

    def resolve_DictNode(self, node):
        for k, v in node.pairs:
            self.resolve(k)
            self.resolve(v)

    def resolve_SetNode(self, node):
        for el in node.elements:
            self.resolve(el)

    def resolve_IndexNode(self, node):
        self.resolve(node.left)
        self.resolve(node.index)
        if node.value:
            self.resolve(node.value)

    def resolve_FunctionNode(self, node):
        # We define the function name in the CURRENT scope
        self.define(node.name, node)
        
        # Then we push a new scope for params and body
        old_next_slot = self.next_slot
        self.next_slot = 0
        
        self.push_scope()
        for param in node.params:
            param_slot = self.define(param.name, param)
            param.slot_index = param_slot
        self.resolve(node.body)
        node.slot_count = self.next_slot
        self.pop_scope()
        
        self.next_slot = old_next_slot

    def resolve_ReturnNode(self, node):
        if node.value:
            self.resolve(node.value)

    def resolve_ResultMethodCallNode(self, node):
        self.resolve(node.receiver)
        self.resolve(node.arg)

    def resolve_PostfixOpNode(self, node):
        self.resolve(node.expr)

    def resolve_KharabiNode(self, node):
        self.resolve(node.message)

    def resolve_ResultConstructorNode(self, node):
        self.resolve(node.value)
