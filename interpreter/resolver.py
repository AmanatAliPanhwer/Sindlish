from .ast_nodes import *
from .errors import NaleJeGhalti, HalndeVaktGhalti, QisamJeGhalti

class Resolver:
    def __init__(self, code):
        self.code = code
        self.scopes = [{}]
        self.slot_indices = {}
        self.next_slot = 0
        self.slot_metadata = {}  # slot_index -> {"is_const": bool, "type": TokenType, "element_type": any}

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
        for attr in vars(node):
            val = getattr(node, attr)
            if isinstance(val, Node):
                self.resolve(val)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, Node):
                        self.resolve(item)
                    elif isinstance(item, tuple):
                        for sub_item in item:
                            if isinstance(sub_item, Node):
                                self.resolve(sub_item)

    def resolve_ProgramNode(self, node):
        for stmt in node.statements:
            self.resolve(stmt)
        node.slot_count = self.next_slot

    def resolve_BlockNode(self, node):
        self.push_scope()
        for stmt in node.statements:
            self.resolve(stmt)
        self.pop_scope()

    def resolve_AssignNode(self, node):
        self.resolve(node.value)
        
        if node.has_explicit_type and node.type is not None:
            inferred_type = self.infer_type(node.value)
            if inferred_type is not None and inferred_type != node.type:
                line = getattr(node, 'line', 0)
                column = getattr(node, 'column', 0)
                raise QisamJeGhalti(
                    f"qisam jhared: `{node.type.name}` aahe, magar value jo milyo wo `{inferred_type.name}` aahe.",
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
                                f"fehrist je elements laai `{node.element_type.name}` qisam lazmi aahe, magar `{elem_type.name}` milyo.",
                                line, column, self.code
                            )
                elif isinstance(node.value, SetNode):
                    for elem in node.value.elements:
                        elem_type = self.infer_type(elem)
                        if elem_type != node.element_type:
                            line = getattr(elem, 'line', 0)
                            column = getattr(elem, 'column', 0)
                            raise QisamJeGhalti(
                                f"majmuo je elements laai `{node.element_type.name}` qisam lazmi aahe, magar `{elem_type.name}` milyo.",
                                line, column, self.code
                            )
        
        slot = self.lookup(node.name)
        if slot is None:
            slot = self.define(node.name)
        
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

    def define(self, name):
        if name in self.scopes[-1]:
            return self.scopes[-1][name]
        
        slot = self.next_slot
        self.next_slot += 1
        
        self.scopes[-1][name] = slot
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

    def resolve_CallNode(self, node):
        for arg in node.args:
            self.resolve(arg)

    def resolve_MethodCallNode(self, node):
        self.resolve(node.instance)
        for arg in node.args:
            self.resolve(arg)

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
