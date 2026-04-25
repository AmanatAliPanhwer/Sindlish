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
    def __init__(self, condition, body, else_body, else_if_bodies=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
        self.else_if_bodies = else_if_bodies or []


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


class ParamNode(Node):
    def __init__(self, name, type=None, default=None, is_star=False, is_kw=False):
        self.name = name
        self.type = type
        self.default = default
        self.is_star = is_star
        self.is_kw = is_kw


class CallNode(Node):
    def __init__(self, name, args, keywords=None, star_args=None, kw_args=None):
        self.name = name
        self.args = args
        self.keywords = keywords or []
        self.star_args = star_args
        self.kw_args = kw_args


class MethodCallNode(Node):
    def __init__(self, instance, method_name, args, keywords=None, star_args=None, kw_args=None):
        self.instance = instance
        self.method_name = method_name
        self.args = args
        self.keywords = keywords or []
        self.star_args = star_args
        self.kw_args = kw_args


class GetAttrNode(Node):
    def __init__(self, instance, attr_name):
        self.instance = instance
        self.attr_name = attr_name


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

class FunctionNode(Node):
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type

class ReturnNode(Node):
    def __init__(self, value):
        self.value = value

class MatchNode(Node):
    def __init__(self, expr, cases):
        self.expr = expr
        self.cases = cases

class MatchCaseNode(Node):
    def __init__(self, pattern, body):
        self.pattern = pattern
        self.body = body

class ResultMethodCallNode(Node):
    def __init__(self, receiver, method_name, arg):
        self.receiver = receiver
        self.method_name = method_name
        self.arg = arg

class PostfixOpNode(Node):
    def __init__(self, expr, op):
        self.expr = expr
        self.op = op

class PanicNode(Node):
    def __init__(self, message):
        self.message = message

class ResultConstructorNode(Node):
    def __init__(self, variant, value):
        self.variant = variant # OK or GHALTI 
        self.value = value