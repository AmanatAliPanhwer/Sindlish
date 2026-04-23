from .tokens import TokenType


class Node:
    def set_pos(self, line, column):
        self.line = line
        self.column = column
        return self


class NumberNode(Node):
    def __init__(self, value):
        self.value = value

    def get_type(self):
        return TokenType.ADAD if isinstance(self.value, int) else TokenType.DAHAI


class StringNode(Node):
    def __init__(self, value):
        self.value = value

    def get_type(self):
        return TokenType.LAFZ


class VariableNode(Node):
    def __init__(self, name):
        self.name = name
        self.slot_index = None
        self.scope_level = None


class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class UnaryOpNode(Node):
    def __init__(self, op, right):
        self.op = op
        self.right = right


class PrintNode(Node):
    def __init__(self, value):
        self.value = value


class IfNode(Node):
    def __init__(self, condition, body, else_body):
        self.condition = condition
        self.body = body
        self.else_body = else_body


class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements


class AssignNode(Node):
    def __init__(
        self, name, value, type=None, is_const: bool = False, element_type=None, has_explicit_type: bool = False
    ):
        self.name = name
        self.value = value
        self.type = type
        self.is_const = is_const
        self.element_type = element_type
        self.has_explicit_type = has_explicit_type
        self.slot_index = None
        self.scope_level = None


class WhileNode(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class BoolNode(Node):
    def __init__(self, value: bool):
        self.value = value

    def get_type(self):
        return TokenType.FAISLO


class NullNode(Node):
    def __init__(self):
        self.value = None


class ListNode(Node):
    def __init__(self, elements):
        self.elements = elements

    def get_type(self):
        return TokenType.FEHRIST


class IndexNode(Node):
    def __init__(self, left, index, value=None):
        self.left = left
        self.index = index
        self.value = value


class CallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args


class MethodCallNode(Node):
    def __init__(self, instance, method_name, args):
        self.instance = instance
        self.method_name = method_name
        self.args = args


class DictNode(Node):
    def __init__(self, pairs):
        self.pairs = pairs


class SetNode(Node):
    def __init__(self, elements):
        self.elements = elements

class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements

class GlobalNode(Node):
    def __init__(self, name):
        self.name = name

class NonLocalNode(Node):
    def __init__(self, name):
        self.name = name