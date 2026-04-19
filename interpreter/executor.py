from .ast_nodes import *
from .tokens import TokenType
from .builtins import SimpleBuiltins, MethodBuiltins


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.simple_handler = SimpleBuiltins()
        self.method_handler = MethodBuiltins()

    def check_type_match(self, name, value, expected_type, element_type=None):
        if expected_type == TokenType.ADAD and not isinstance(value, int):
            raise TypeError(f"`{name}` is locked to adad (int).")
        if expected_type == TokenType.DAHAI and not isinstance(value, float):
            raise TypeError(f"`{name}` is locked to dehai (float).")
        if expected_type == TokenType.LAFZ and not isinstance(value, str):
            raise TypeError(f"`{name}` is locked to lafz (string).")

        if expected_type == TokenType.FEHRIST:
            if not isinstance(value, list):
                raise TypeError(f"`{name}` is locked to fehrist (list).")

            # If an inner type was specified (like fehrist[adad]), check every item
            if element_type is not None:
                for index, item in enumerate(value):
                    # Reuse check_type_match to validate each element
                    self.check_type_match(f"{name}[{index}]", item, element_type)

        if expected_type == TokenType.MAJMUO:
            if not isinstance(value, set):
                raise TypeError(f"{name} must be a majmuo")
            if element_type:
                for item in value:
                    self.check_type_match(f"element of {name}", item, element_type)

        if expected_type == TokenType.LUGHAT:
            if not isinstance(value, dict):
                raise TypeError(f"{name} must be a lughat")
            if element_type and len(element_type) == 2:
                k_type, v_type = element_type
                for k, v in value.items():
                    self.check_type_match("key", k, k_type)
                    self.check_type_match("value", v, v_type)

    def ensure_immutable(self, value, container_name):
        if isinstance(value, (list, dict, set)):
            raise TypeError(
                f"A `{type(value).__name__}` cannot be a key/member in a `{container_name}` (it's mutable)."
            )
        return value

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node)

    def no_visit_method(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")

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
            raise Exception(f"Variable `{node.name}` is not defined")
        return self.variables[node.name]["value"]

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

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

        raise Exception("Unknown Opration")

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
                raise RuntimeError(
                    f"Error: `{node.name}` is pakko (constant) and cannot be changed."
                )

            if var_data["type"] is not None:
                self.check_type_match(
                    node.name, new_value, var_data["type"], var_data.get("element_type")
                )

            var_data["value"] = new_value
        else:
            if node.type is not None:
                self.check_type_match(
                    node.name, new_value, node.type, node.element_type
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
        left_val: list = self.visit(node.left)
        index_val = self.visit(node.index)
        value_val = self.visit(node.value) if node.value is not None else None

        if isinstance(left_val, list):
            if not isinstance(index_val, int):
                raise TypeError("Fehrist index must be an adad (int)")
            try:
                if value_val:
                    left_val[index_val] = value_val
            except IndexError:
                raise RuntimeError(f"Fihrist index out of range: {index_val}")
        elif isinstance(left_val, dict):
            self.ensure_immutable(index_val, "lughat")
            try:
                if value_val:
                    left_val[index_val] = value_val
            except IndexError:
                raise RuntimeError(f"Lughat index out of range: {index_val}")
        else:
            raise TypeError("Only fehrist and lughat support index assignment")
        return left_val[index_val]

    def visit_CallNode(self, node):
        args = [self.visit(arg) for arg in node.args]

        func = SimpleBuiltins.functions.get(node.name)
        if func:
            return func(self.simple_handler, args)

        raise RuntimeError(f"Function `{node.name}` is not defined")

    def visit_MethodCallNode(self, node):
        obj = self.visit(node.instance)
        args = [self.visit(arg) for arg in node.args]

        method = MethodBuiltins.methods.get(node.method_name)
        if method:
            return method(self.method_handler, obj, args)

        raise RuntimeError(f"Function `{node.method_name}` is not defined")

    def visit_DictNode(self, node):
        return {self.visit(k): self.visit(v) for k, v in node.pairs}

    def visit_SetNode(self, node):
        return {self.visit(el) for el in node.elements}
