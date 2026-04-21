from .ast_nodes import *
from .errors import NaleJeGhalti, HalndeVaktGhalti

class Resolver:
    def __init__(self, code):
        self.code = code
        self.scopes = [{}]
        self.slot_indices = {}
        self.next_slot = 0

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
        
        slot = self.lookup(node.name)
        if slot is None or node.type is not None:
            slot = self.define(node.name)
        
        node.slot_index = slot
        node.scope_level = 0

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
