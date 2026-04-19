from .ast_nodes import *
from .tokens import TokenType
from .builtins import SimpleBuiltins, MethodBuiltins
from .errors import NaleJeGhalti, QisamJeGhalti, HalndeVaktGhalti, ZeroVindJeGhalti, IndexJeGhalti


class Interpreter:
    def __init__(self, code):
        self.simple_handler = SimpleBuiltins()
        self.method_handler = MethodBuiltins()
        self.code = code
        self.variables = {
            name: {
                "value": func,
                "type": TokenType.KAAM,
                "is_const": True
            } 
            for name, func in self.simple_handler.get_all().items()
        }

    def check_type_match(self, name, value, expected_type, element_type=None, node=None):
        line = node.line if node else 1
        col = node.column if node else 1
        
        if expected_type == TokenType.ADAD and not isinstance(value, int):
            raise QisamJeGhalti(f"`{name}` adad (int) laai makhsoos aahe.", line, col, self.code)
        if expected_type == TokenType.DAHAI and not isinstance(value, float):
            raise QisamJeGhalti(f"`{name}` dahai (float) laai makhsoos aahe.", line, col, self.code)
        if expected_type == TokenType.LAFZ and not isinstance(value, str):
            raise QisamJeGhalti(f"`{name}` lafz (string) laai makhsoos aahe.", line, col, self.code)

        if expected_type == TokenType.FEHRIST:
            if not isinstance(value, list):
                raise QisamJeGhalti(f"`{name}` fehrist (list) laai makhsoos aahe.", line, col, self.code)
            if element_type is not None:
                for index, item in enumerate(value):
                    self.check_type_match(f"{name}[{index}]", item, element_type, node=node)

        if expected_type == TokenType.MAJMUO:
            if not isinstance(value, set):
                raise QisamJeGhalti(f"`{name}` majmuo (set) laai makhsoos aahe.", line, col, self.code)
            if element_type:
                for item in value:
                    self.check_type_match(f"element of {name}", item, element_type, node=node)

        if expected_type == TokenType.LUGHAT:
            if not isinstance(value, dict):
                raise QisamJeGhalti(f"`{name}` lughat (dict) laai makhsoos aahe.", line, col, self.code)
            if element_type and len(element_type) == 2:
                k_type, v_type = element_type
                for k, v in value.items():
                    self.check_type_match("key", k, k_type, node=node)
                    self.check_type_match("value", v, v_type, node=node)

    def ensure_immutable(self, value, container_name, node):
        if isinstance(value, (list, dict, set)):
            raise QisamJeGhalti(
                f"`{type(value).__name__}` kahan `{container_name}` ji key ya member natho bani sakhay (he mutable aahe).",
                node.line, node.column, self.code
            )
        return value

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise NaleJeGhalti(f"{type(node).__name__} laai ko visit method na aahe.", getattr(node, 'line', 1), getattr(node, 'column', 1), self.code)

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        print(value)

    def visit_NumberNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value

    def visit_VariableNode(self, node):
        if node.name not in self.variables:
            raise NaleJeGhalti(f"Variable `{node.name}` je wazahat thayal (defined) na aahe.", node.line, node.column, self.code)
        return self.variables[node.name]["value"]

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        try:
            if node.op.type == TokenType.GT:
                return left > right
            if node.op.type == TokenType.LT:
                return left < right
            if node.op.type == TokenType.PLUS:
                return left + right
            if node.op.type == TokenType.MINUS:
                return left - right
            if node.op.type == TokenType.MUL:
                return left * right
            if node.op.type == TokenType.DIV:
                if right == 0:
                    raise ZeroVindJeGhalti("buren (zero) san vand (divide) natho kare sakhjay.", node.line, node.column, self.code)
                return left / right
            if node.op.type == TokenType.MOD:
                return left % right
            if node.op.type == TokenType.POW:
                return left**right
            if node.op.type == TokenType.EQEQ:
                return left == right
            if node.op.type == TokenType.NOTEQ:
                return left != right
            if node.op.type == TokenType.LTEQ:
                return left <= right
            if node.op.type == TokenType.GTEQ:
                return left >= right
            if node.op.type == TokenType.AND:
                return left and right
            if node.op.type == TokenType.OR:
                return left or right
            if node.op.type == TokenType.NOT:
                return not right
        except ZeroDivisionError:
            raise ZeroVindJeGhalti("buren (zero) san vand (divide) natho kare sakhjay.", node.line, node.column, self.code)
        except TypeError as e:
            raise QisamJeGhalti(str(e), node.line, node.column, self.code)

        raise HalndeVaktGhalti("Na-maloom operation", node.line, node.column, self.code)

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)

        if condition:
            for stmt in node.body:
                self.visit(stmt)

        else:
            if node.else_body:
                for stmt in node.else_body:
                    self.visit(stmt)

    def visit_AssignNode(self, node):
        new_value = self.visit(node.value)

        if node.name in self.variables:
            var_data = self.variables[node.name]

            if var_data["is_const"]:
                raise HalndeVaktGhalti(
                    f"`{node.name}` pakko (constant) aahe aen tabdeel natho kare sakhjay.",
                    node.line, node.column, self.code
                )

            if var_data["type"] is not None:
                self.check_type_match(
                    node.name, new_value, var_data["type"], var_data.get("element_type"), node=node
                )

            var_data["value"] = new_value
        else:
            if node.type is not None:
                self.check_type_match(
                    node.name, new_value, node.type, node.element_type, node=node
                )

            self.variables[node.name] = {
                "value": new_value,
                "type": node.type,
                "is_const": node.is_const,
                "element_type": node.element_type,
            }

    def visit_WhileNode(self, node):
        while self.visit(node.condition):
            for stmt in node.body:
                self.visit(stmt)

    def visit_BoolNode(self, node):
        return node.value

    def visit_NullNode(self, node):
        return None

    def visit_ListNode(self, node):
        return [self.visit(element) for element in node.elements]

    def visit_IndexNode(self, node):
        left_val = self.visit(node.left)
        index_val = self.visit(node.index)
        value_val = self.visit(node.value) if node.value is not None else None

        if isinstance(left_val, list):
            if not isinstance(index_val, int):
                raise QisamJeGhalti("Fehrist jo index adad (int) hovan lazmi aahe.", node.line, node.column, self.code)
            try:
                if value_val:
                    left_val[index_val] = value_val
                return left_val[index_val]
            except IndexError:
                raise IndexJeGhalti(f"Fehrist jo index hadd khan baahar aahe: {index_val}", node.line, node.column, self.code)
        elif isinstance(left_val, dict):
            self.ensure_immutable(index_val, "lughat", node)
            try:
                if value_val:
                    left_val[index_val] = value_val
                return left_val[index_val]
            except (IndexError, KeyError):
                raise IndexJeGhalti(f"Lughat jo index na milyo: {index_val}", node.line, node.column, self.code)
        else:
            raise QisamJeGhalti("Sirf fehrist aen lughat index assignment support kanda aahin.", node.line, node.column, self.code)

    def visit_CallNode(self, node):
        if node.name not in self.variables:
            raise NaleJeGhalti(f"Function `{node.name}` na milio", node.line, node.column, self.code)
        
        var_entry = self.variables[node.name]

        if var_entry["type"] != TokenType.KAAM:
            raise QisamJeGhalti(f"`{node.name}` kaam (function) na aahe, par `{var_entry['type'].name}` aahe", node.line, node.column, self.code)

        func = var_entry["value"]
        args = [self.visit(arg) for arg in node.args]
        return func(self.simple_handler, args)

    def visit_MethodCallNode(self, node):
        obj = self.visit(node.instance)
        args = [self.visit(arg) for arg in node.args]

        method = MethodBuiltins.methods.get(node.method_name)
        if method:
            try:
                return method(self.method_handler, obj, args)
            except TypeError as e:
                raise QisamJeGhalti(str(e), node.line, node.column, self.code)
            except Exception as e:
                raise HalndeVaktGhalti(str(e), node.line, node.column, self.code)

        raise NaleJeGhalti(f"Method `{node.method_name}` je wazahat thayal (defined) na aahe.", node.line, node.column, self.code)

    def visit_DictNode(self, node):
        return {self.visit(k): self.visit(v) for k, v in node.pairs}

    def visit_SetNode(self, node):
        return {self.visit(el) for el in node.elements}
