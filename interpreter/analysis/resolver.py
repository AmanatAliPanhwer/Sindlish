from ..errors import QisamJeGhalti
from ..frontend.ast_nodes import (
    AssignNode,
    BoolNode,
    DictNode,
    FunctionNode,
    ListNode,
    Node,
    NullNode,
    NumberNode,
    SetNode,
    StringNode,
    VariableNode,
)
from ..frontend.tokens import TokenType


class Resolver:
    def __init__(self, code):
        self.code = code
        self.scopes = [{}]
        self.function_scopes = [set()]
        self.declared_globals = set()
        self.global_var_names = set()
        self.slot_indices = {}
        self.next_slot = 0
        self.slot_metadata = {}  # slot_index -> {"is_const": bool, "type": TokenType, "element_type": any}
        self.symbols = [] # List of {"name": str, "type": TokenType, "line": int, "col": int, "kind": str}
        self.is_repl = False

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
            found = self._find(node.name)
            if found and found[0] == "slot" and found[2] > 0:
                meta = self.slot_metadata.get(found[1], {})
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

        found = self._find(node.name)
        goes_global = (
            node.name in self.declared_globals
            or len(self.scopes) == 1
            or (found is not None and found[2] == 0)
        )

        if goes_global:
            # Program-level variables live in the globals environment;
            # const/type enforcement happens at runtime via STORE_GLOBAL.
            self.global_var_names.add(node.name)
            node.scope_level = 1
            node.slot_index = -1
            return

        if found is None or found[0] == "function":
            slot = self.define(node.name, node)
        else:
            slot = found[1]

        node.slot_index = slot
        node.scope_level = 0

        if node.has_explicit_type and node.type is not None:
            self.slot_metadata[slot] = {
                "is_const": node.is_const,
                "type": node.type,
                "element_type": node.element_type,
                "has_explicit_type": True
            }
        elif slot not in self.slot_metadata:
            self.slot_metadata[slot] = {
                "is_const": node.is_const,
                "type": None,
                "element_type": node.element_type,
                "has_explicit_type": False
            }

    def push_scope(self):
        self.scopes.append({})
        self.function_scopes.append(set())

    def pop_scope(self):
        self.scopes.pop()
        self.function_scopes.pop()

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

    def define_function(self, name, node=None):
        """Register a function name without allocating a frame slot.

        Function values live in the globals environment, so references
        compile to LOAD_GLOBAL instead of reading an empty local slot.
        """
        self.function_scopes[-1].add(name)
        if node:
            self.symbols.append({
                "name": name,
                "type": getattr(node, 'type', None),
                "line": getattr(node, 'line', 0),
                "col": getattr(node, 'column', 0),
                "kind": "function"
            })

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _find(self, name):
        """Find a name across scopes.

        Returns ("slot", slot_index, owner_scope_index), ("function", None,
        owner_scope_index), ("global", -1, 0) for program-level variables,
        or None when the name is unknown. Scope indices >= 1 hold frame-local
        slots; scope 0 is the program-global scope whose variables live in
        the globals environment.
        """
        for i in range(len(self.scopes) - 1, 0, -1):
            if name in self.function_scopes[i]:
                return ("function", None, i)
            if name in self.scopes[i]:
                return ("slot", self.scopes[i][name], i)
        if name in self.function_scopes[0]:
            return ("function", None, 0)
        if name in self.global_var_names:
            return ("global", -1, 0)
        return None
    
    def get_slot_metadata(self):
        return self.slot_metadata

    def resolve_VariableNode(self, node):
        found = self._find(node.name)
        if (
            found is not None
            and found[0] == "slot"
            and found[2] > 0
            and node.name not in self.declared_globals
        ):
            node.slot_index = found[1]
            node.scope_level = 0
        else:
            node.scope_level = 1

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
        # Function names live in the globals environment, not in frame slots
        self.define_function(node.name, node)

        # Then we push a new scope for params and body
        old_next_slot = self.next_slot
        old_slot_metadata = self.slot_metadata
        self.next_slot = 0
        self.slot_metadata = {}

        self.push_scope()
        for param in node.params:
            param_slot = self.define(param.name, param)
            param.slot_index = param_slot
        self.resolve(node.body)
        node.slot_count = self.next_slot
        node.slot_metadata = self.slot_metadata
        self.pop_scope()

        self.next_slot = old_next_slot
        self.slot_metadata = old_slot_metadata

    def resolve_GlobalNode(self, node):
        self.declared_globals.add(node.name)
        self.global_var_names.add(node.name)

    def resolve_NonLocalNode(self, node):
        raise QisamJeGhalti(
            "'bahari' (closures) abhi support natho; hale roadmap mein aahe.",
            getattr(node, 'line', 0),
            getattr(node, 'column', 0),
            self.code,
        )

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
