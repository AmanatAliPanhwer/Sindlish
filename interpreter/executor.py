from .ast_nodes import *
from .tokens import TokenType
from .builtins import SimpleBuiltins, MethodBuiltins
from .errors import (
    NaleJeGhalti,
    QisamJeGhalti,
    HalndeVaktGhalti,
    ZeroVindJeGhalti,
    IndexJeGhalti,
    LikhaiJeGhalti,
)
from .objects.primitives import (
    SdBool,
    SdDict,
    SdList,
    SdNull,
    SdNumber,
    SdSet,
    SdString,
)
from .env import Environment, VariableRecord
from .frame import Frame


class Interpreter:
    def __init__(self, code):
        self.simple_handler = SimpleBuiltins()
        self.method_handler = MethodBuiltins()
        self.code = code

        self.globals = Environment()
        self.call_stack = []

        for name, func in self.simple_handler.get_all().items():
            self.globals.define(
                name, value=func, var_type=TokenType.KAAM, is_const=True
            )

    @property
    def current_frame(self):
        """Always returns the top of the call stack."""
        return self.call_stack[-1]

    @property
    def current_env(self):
        """Existing code uses self.current_env.
        This routes it to the current frame."""
        return self.current_frame.env

    @current_env.setter
    def current_env(self, new_env):
        """Allows push_scope and pop_scope to modify the current frame's environment."""
        self.current_frame.env = new_env

    @property
    def variables(self):
        """Return global variables in test's-friendly format."""
        return {
            name: {
                "value": record.value,
                "is_const": record.is_const,
                "type": record.type,
            }
            for name, record in self.globals.records.items()
        }

    def push_frame(self, name: str, statements: list, parent_env: Environment):
        """Pauses the current execution context and pushes a new Frame."""
        new_frame = Frame(name, statements, parent_env)
        self.call_stack.append(new_frame)
        return new_frame

    def pop_frame(self):
        """Completes the current function and returns to the previous Frame."""
        return self.call_stack.pop()

    def push_scope(self):
        self.current_env = Environment(parent=self.current_env)

    def pop_scope(self):
        if self.current_env.parent:
            self.current_env = self.current_env.parent

    def run(self, program_node):
        """
        The heart of the state machine.
        Replaces the recursive Python 'for' loop for top-level execution.
        """
        global_frame = Frame("<module>", program_node.statements, slot_count=getattr(program_node, "slot_count", 0))
        global_frame.env = self.globals
        self.call_stack.append(global_frame)

        while self.call_stack:
            frame = self.current_frame

            if frame.ip >= len(frame.statements):
                self.pop_frame()
                continue

            current_node = frame.statements[frame.ip]
            frame.ip += 1

            self.visit(current_node)

    def check_type_match(
        self, name, value, expected_type, element_type=None, node=None
    ):
        line = node.line if node else 1
        col = node.column if node else 1

        if expected_type == TokenType.ADAD and (
            not isinstance(value, SdNumber) or value.type.token_type != TokenType.ADAD
        ):
            raise QisamJeGhalti(
                f"`{name}` adad (int) laai makhsoos aahe.", line, col, self.code
            )
        if expected_type == TokenType.DAHAI and (
            not isinstance(value, SdNumber) or value.type.token_type != TokenType.DAHAI
        ):
            raise QisamJeGhalti(
                f"`{name}` dahai (float) laai makhsoos aahe.", line, col, self.code
            )
        if expected_type == TokenType.LAFZ and not isinstance(value, SdString):
            raise QisamJeGhalti(
                f"`{name}` lafz (string) laai makhsoos aahe.", line, col, self.code
            )

        if expected_type == TokenType.FEHRIST:
            if not isinstance(value, SdList):
                raise QisamJeGhalti(
                    f"`{name}` fehrist (list) laai makhsoos aahe.", line, col, self.code
                )
            if element_type is not None:
                for index, item in enumerate(value.elements):
                    self.check_type_match(
                        f"{name}[{index}]", item, element_type, node=node
                    )

        if expected_type == TokenType.MAJMUO:
            if not isinstance(value, SdSet):
                raise QisamJeGhalti(
                    f"`{name}` majmuo (set) laai makhsoos aahe.", line, col, self.code
                )
            if element_type:
                for item in value.elements:
                    self.check_type_match(
                        f"element of {name}", item, element_type, node=node
                    )

        if expected_type == TokenType.LUGHAT:
            if not isinstance(value, SdDict):
                raise QisamJeGhalti(
                    f"`{name}` lughat (dict) laai makhsoos aahe.", line, col, self.code
                )
            if element_type and len(element_type) == 2:
                k_type, v_type = element_type
                for k, v in value.items():
                    self.check_type_match("key", k, k_type, node=node)
                    self.check_type_match("value", v, v_type, node=node)

    def ensure_immutable(self, value, container_name, node):
        if isinstance(value, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(
                f"`{value.type.name}` kahan `{container_name}` ji key ya member natho bani sakhay (he mutable aahe).",
                node.line,
                node.column,
                self.code,
            )
        return value

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise NaleJeGhalti(
            f"{type(node).__name__} laai ko visit method na aahe.",
            getattr(node, "line", 1),
            getattr(node, "column", 1),
            self.code,
        )

    def visit_ProgramNode(self, node):
        self.run(node)

    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        print(str(value))
        return None

    def visit_NumberNode(self, node):
        return SdNumber(node.value)

    def visit_StringNode(self, node):
        return SdString(node.value)

    def visit_VariableNode(self, node):
        if node.scope_level == 0:
            return self.current_frame.slots[node.slot_index]
        
        target_env = self.current_env
        env = self.current_env

        while env is not None:
            if node.name in env.global_names:
                target_env = self.globals
                break
            if node.name in env.nonlocal_names:
                target = env.parent.resolve_scope(node.name) if env.parent else None
                if target:
                    target_env = target
                break
            if node.name in env.records:
                break
            env = env.parent

        record = target_env.lookup_record(node.name, node, self.code)
        return record.value

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        op_map = {
            TokenType.PLUS: "__add__",
            TokenType.MINUS: "__sub__",
            TokenType.MUL: "__mul__",
            TokenType.DIV: "__div__",
            TokenType.MOD: "__mod__",
            TokenType.POW: "__pow__",
            TokenType.EQEQ: "__eq__",
            TokenType.NOTEQ: "__ne__",
            TokenType.GT: "__gt__",
            TokenType.LT: "__lt__",
            TokenType.GTEQ: "__ge__",
            TokenType.LTEQ: "__le__",
            TokenType.AND: "__and__",
            TokenType.OR: "__or__",
        }

        method_name = op_map.get(node.op.type)
        if node.op.type == TokenType.NOT:
            return right.call_method("__invert__", [], node, self.code)
        if not method_name:
            raise HalndeVaktGhalti(
                f"Operator '{node.op}' hal filhal supported na aahe. :(",
                node.line,
                node.column,
                self.code,
            )

        return left.call_method(method_name, [right], node, self.code)

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)

        if condition:
            if isinstance(node.body, BlockNode):
                self.visit(node.body)

        elif node.else_body:
            if isinstance(node.else_body, BlockNode):
                self.visit(node.else_body)

    def visit_AssignNode(self, node):
        value = self.visit(node.value)

        if node.scope_level == 0:
            if node.slot_index is not None:
                if node.type is not None:
                    self.check_type_match(node.name, value, node.type, node.element_type, node)
                self.current_frame.slots[node.slot_index] = value
                return value

        if node.type is not None:
            self.check_type_match(node.name, value, node.type, node.element_type, node)
            return self.current_env.define(
                node.name,
                value=value,
                var_type=node.type,
                is_const=node.is_const,
                element_type=node.element_type,
            )

        target_env = self.current_env
        env = self.current_env

        while env is not None:
            if node.name in env.global_names:
                target_env = self.globals
                break
            if node.name in env.nonlocal_names:
                target = env.parent.resolve_scope(node.name) if env.parent else None
                if not target:
                    raise HalndeVaktGhalti(
                        f"bahari nalo '{node.name}' baahar na milyo.",
                        node.line,
                        node.column,
                        self.code,
                    )
                target_env = target
                break
            if node.name in env.records:
                target_env = env
                break
            env = env.parent

        existing_env = target_env.lookup(node.name)

        if existing_env:
            var = existing_env.records[node.name]

            if var.is_const:
                raise HalndeVaktGhalti(
                    f"`{node.name}` pakko (constant) aahe aen tabdeel natho kare sakhjay.",
                    node.line,
                    node.column,
                    self.code,
                )

            if var.type is not None:
                self.check_type_match(
                    node.name, value, var.type, var.element_type, node
                )

            existing_env.assign(node.name, value, node, self.code)
        else:
            target_env.define(
                node.name,
                value=value,
                is_const=node.is_const,
                element_type=node.element_type,
            )

    def visit_WhileNode(self, node):
        while self.visit(node.condition):
            self.visit(node.body)

    def visit_BoolNode(self, node):
        return SdBool(node.value)

    def visit_NullNode(self, node):
        return SdNull()

    def visit_ListNode(self, node):
        elements = [self.visit(el) for el in node.elements]
        return SdList(elements=elements)

    def visit_IndexNode(self, node):
        left_val = self.visit(node.left)
        index_val = self.visit(node.index)
        value_val = self.visit(node.value) if node.value is not None else None

        if isinstance(left_val, SdNull) or left_val is None:
            raise HalndeVaktGhalti(
                "Fehrist khali (Null) aahe, indexing mumkin na aahe.",
                node.line,
                node.column,
                self.code,
            )

        if isinstance(left_val, (SdList, SdDict)):
            if isinstance(left_val, SdList) and not isinstance(index_val, SdNumber):
                raise QisamJeGhalti(
                    "Fehrist jo index adad (int) hovan lazmi aahe.",
                    node.line,
                    node.column,
                    self.code,
                )

            try:
                if value_val is not None:
                    left_val.call_method(
                        "__setitem__", [index_val, value_val], node, self.code
                    )
                return left_val.call_method("__getitem__", [index_val], node, self.code)
            except (IndexError, KeyError) as e:
                raise IndexJeGhalti(
                    f"Index error: {str(e)}",
                    node.line,
                    node.column,
                    self.code,
                )
        else:
            raise QisamJeGhalti(
                "Sirf fehrist aen lughat index assignment support kanda aahin.",
                node.line,
                node.column,
                self.code,
            )

    def visit_CallNode(self, node):
        var_entry = self.current_env.lookup_record(node.name, node, self.code)

        if var_entry.type != TokenType.KAAM:
            raise QisamJeGhalti(
                f"`{node.name}` kaam (function) na aahe, par `{var_entry.type}` aahe",
                node.line,
                node.column,
                self.code,
            )

        func = var_entry.value
        args = [self.visit(arg) for arg in node.args]
        try:
            return func(self.simple_handler, args)
        except (
            QisamJeGhalti,
            HalndeVaktGhalti,
            NaleJeGhalti,
            ZeroVindJeGhalti,
            IndexJeGhalti,
            LikhaiJeGhalti,
        ):
            raise
        except Exception as e:
            raise HalndeVaktGhalti(str(e), node.line, node.column, self.code)

    def visit_MethodCallNode(self, node):
        obj = self.visit(node.instance)
        args = [self.visit(arg) for arg in node.args]

        method = MethodBuiltins.methods.get(node.method_name)
        if method:
            try:
                return method(self.method_handler, obj, args)
            except (
                QisamJeGhalti,
                HalndeVaktGhalti,
                NaleJeGhalti,
                ZeroVindJeGhalti,
                IndexJeGhalti,
                LikhaiJeGhalti,
            ):
                raise
            except TypeError as e:
                raise QisamJeGhalti(str(e), node.line, node.column, self.code)
            except Exception as e:
                raise HalndeVaktGhalti(str(e), node.line, node.column, self.code)

        raise NaleJeGhalti(
            f"Method `{node.method_name}` je wazahat thayal (defined) na aahe.",
            node.line,
            node.column,
            self.code,
        )

    def visit_DictNode(self, node):
        pairs = {}
        for k_node, v_node in node.pairs:
            k = self.visit(k_node)
            self.ensure_immutable(k, "lughat", k_node)
            v = self.visit(v_node)
            pairs[k] = v
        return SdDict(pairs)

    def visit_SetNode(self, node):
        elements = set()
        for el_node in node.elements:
            el = self.visit(el_node)
            self.ensure_immutable(el, "majmuo", el_node)
            elements.add(el)
        return SdSet(elements=elements)

    def visit_BlockNode(self, node):
        self.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.pop_scope()

    def visit_GlobalNode(self, node):
        self.current_env.global_names.add(node.name)

    def visit_NonLocalNode(self, node):
        if not self.current_env.parent:
            raise HalndeVaktGhalti(
                "bahari lazmi andare (nested) block mein hovan khapay",
                node.line,
                node.column,
                self.code,
            )
        target = self.current_env.parent.resolve_scope(node.name)
        if not target or target is self.globals:
            raise NaleJeGhalti(
                f"bahari nalo '{node.name}' baahar na milyo.",
                node.line,
                node.column,
                self.code,
            )
        self.current_env.nonlocal_names.add(node.name)
