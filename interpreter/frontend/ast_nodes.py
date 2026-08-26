"""
AST (Abstract Syntax Tree) node definitions for the Sindlish language.

Every syntactic construct in Sindlish is represented by a Node subclass.
Nodes carry source-position information (line, column) for error reporting.

Grammar summary (simplified):
    program     -> statement* EOF
    statement   -> print | if | while | assignment | function | return | expr
    expression  -> or
    or          -> and ("ya" and)*
    and         -> not ("aen" not)*
    not         -> "nah" not | comparison
    comparison  -> term (("==" | "!=" | ">" | "<" | ">=" | "<=") term)*
    term        -> factor (("+" | "-") factor)*
    factor      -> power (("*" | "/" | "%") power)*
    power       -> unary ("^" power)?
    unary       -> "-" unary | postfix
    postfix     -> primary ("?" | "!!" | "." method)*
    primary     -> NUMBER | STRING | BOOL | NULL | IDENT | "(" expr ")" | list | dict | set
"""

from .tokens import TokenType


class Node:
    """Base class for all AST nodes. Carries source position."""

    __slots__ = ("column", "line")

    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    def set_pos(self, line: int, column: int) -> "Node":
        """Set source position and return self (for chaining)."""
        self.line = line
        self.column = column
        return self

    def __repr__(self) -> str:
        fields = {
            k: getattr(self, k) for k in self.__slots__ if k not in ("line", "column")
        }
        field_str = ", ".join(f"{k}={v!r}" for k, v in fields.items())
        return f"{type(self).__name__}({field_str})"


# ===== Literals =====


class NumberNode(Node):
    """Integer or float literal."""

    __slots__ = ("value",)

    def __init__(self, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value



class StringNode(Node):
    """String literal."""

    __slots__ = ("value",)

    def __init__(self, value: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value



class BoolNode(Node):
    """Boolean literal (sach / koorh)."""

    __slots__ = ("value",)

    def __init__(self, value: bool, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value



class NullNode(Node):
    """Null literal (khali)."""

    __slots__ = ("value",)

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = None


# ===== Variables & Assignment =====


class VariableNode(Node):
    """Variable reference by name."""

    __slots__ = (
        "deref_depth",
        "deref_name",
        "name",
        "scope_level",
        "slot_index",
    )

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name
        self.slot_index = None
        self.scope_level = None
        self.deref_depth = None
        self.deref_name = None


class AssignNode(Node):
    """Variable declaration/assignment with optional type annotation."""

    __slots__ = (
        "deref_depth",
        "deref_name",
        "element_type",
        "has_explicit_type",
        "is_const",
        "name",
        "scope_level",
        "slot_index",
        "type",
        "value",
    )

    def __init__(
        self,
        name: str,
        value,
        type=None,
        is_const: bool = False,
        element_type=None,
        has_explicit_type: bool = False,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.name = name
        self.value = value
        self.type = type
        self.is_const = is_const
        self.element_type = element_type
        self.has_explicit_type = has_explicit_type
        self.slot_index = None
        self.scope_level = None
        self.deref_depth = None
        self.deref_name = None


# ===== Operators =====


class BinaryOpNode(Node):
    """Binary operation (e.g. a + b, x == y)."""

    __slots__ = ("left", "op", "right")

    def __init__(self, left, op, right, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.op = op
        self.right = right


class UnaryOpNode(Node):
    """Unary operation (e.g. -x, nah x)."""

    __slots__ = ("op", "right")

    def __init__(self, op, right, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.op = op
        self.right = right


class PostfixOpNode(Node):
    """Postfix operation (? or !!)."""

    __slots__ = ("expr", "op")

    def __init__(self, expr, op, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr
        self.op = op


# ===== Statements =====


class IfNode(Node):
    """If/else-if/else statement (agar/yawari/warna)."""

    __slots__ = ("body", "condition", "else_body", "else_if_bodies")

    def __init__(
        self,
        condition,
        body,
        else_body,
        else_if_bodies=None,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.condition = condition
        self.body = body
        self.else_body = else_body
        self.else_if_bodies = else_if_bodies or []


class WhileNode(Node):
    """While loop (jistain)."""

    __slots__ = ("body", "condition")

    def __init__(self, condition, body, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.condition = condition
        self.body = body


class ForNode(Node):
    """For loop (har)."""

    __slots__ = ("body", "iterable", "iterator", "iterator_slot")

    def __init__(self, iterator: str, iterable, body, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.iterator = iterator
        self.iterable = iterable
        self.body = body
        self.iterator_slot = None


class BreakNode(Node):
    """Break statement (tor)."""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)


class ContinueNode(Node):
    """Continue statement (jari)."""

    def __init__(self, line: int = 0, column: int = 0):
        super().__init__(line, column)


class BlockNode(Node):
    """A block of statements enclosed in { }."""

    __slots__ = ("statements",)

    def __init__(self, statements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements


class ProgramNode(Node):
    """Top-level program: a sequence of statements."""

    __slots__ = ("slot_count", "statements")

    def __init__(self, statements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.statements = statements
        self.slot_count = 0


# ===== Collections =====


class ListNode(Node):
    """List literal [a, b, c]."""

    __slots__ = ("elements",)

    def __init__(self, elements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.elements = elements




class DictNode(Node):
    """Dictionary literal {k: v, ...}."""

    __slots__ = ("pairs",)

    def __init__(self, pairs: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.pairs = pairs



class SetNode(Node):
    """Set literal {a, b, c}."""

    __slots__ = ("elements",)

    def __init__(self, elements: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.elements = elements



class IndexNode(Node):
    """Index access or assignment (obj[index] or obj[index] = value)."""

    __slots__ = ("index", "left", "value")

    def __init__(self, left, index, value=None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.left = left
        self.index = index
        self.value = value


# ===== Functions =====


class ParamNode(Node):
    """Function parameter definition."""

    __slots__ = (
        "default",
        "is_kw",
        "is_star",
        "name",
        "slot_index",
        "type",
    )

    def __init__(
        self,
        name: str,
        type=None,
        default=None,
        is_star: bool = False,
        is_kw: bool = False,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.name = name
        self.type = type
        self.default = default
        self.is_star = is_star
        self.is_kw = is_kw
        self.slot_index = None


class FunctionNode(Node):
    """Function definition (kaam)."""

    __slots__ = (
        "body",
        "cell_slots",
        "free_slots",
        "name",
        "params",
        "return_type",
        "slot_count",
        "slot_metadata",
    )

    def __init__(
        self,
        name: str,
        params: list,
        body,
        return_type=None,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.name = name
        self.params = params
        self.body = body
        self.return_type = return_type
        self.slot_count = 0
        self.cell_slots = ()
        self.free_slots = ()
        self.slot_metadata = {}


class CallNode(Node):
    """Function call."""

    __slots__ = ("args", "keywords", "kw_args", "name", "star_args")

    def __init__(
        self,
        name: str,
        args: list,
        keywords=None,
        star_args=None,
        kw_args=None,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.name = name
        self.args = args
        self.keywords = keywords or []
        self.star_args = star_args
        self.kw_args = kw_args


class ReturnNode(Node):
    """Return statement (wapas)."""

    __slots__ = ("value",)

    def __init__(self, value=None, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.value = value


class MethodCallNode(Node):
    """Method call on an object (obj.method(args))."""

    __slots__ = (
        "args",
        "instance",
        "keywords",
        "kw_args",
        "method_name",
        "star_args",
    )

    def __init__(
        self,
        instance,
        method_name: str,
        args: list,
        keywords=None,
        star_args=None,
        kw_args=None,
        line: int = 0,
        column: int = 0,
    ):
        super().__init__(line, column)
        self.instance = instance
        self.method_name = method_name
        self.args = args
        self.keywords = keywords or []
        self.star_args = star_args
        self.kw_args = kw_args


class GetAttrNode(Node):
    """Attribute access (obj.attr)."""

    __slots__ = (
        "attr_name",
        "instance",
    )

    def __init__(self, instance, attr_name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.instance = instance
        self.attr_name = attr_name


# ===== Scoping =====


class GlobalNode(Node):
    """Global variable declaration (aalmi)."""

    __slots__ = ("name",)

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name


class NonLocalNode(Node):
    """Non-local variable declaration (bahari)."""

    __slots__ = ("name",)

    def __init__(self, name: str, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.name = name


# ===== Pattern Matching =====


class MatchNode(Node):
    """Match expression."""

    __slots__ = (
        "cases",
        "expr",
    )

    def __init__(self, expr, cases: list, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.expr = expr
        self.cases = cases


class MatchCaseNode(Node):
    """A single case in a match expression."""

    __slots__ = ("body", "pattern")

    def __init__(self, pattern, body, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.pattern = pattern
        self.body = body


# ===== Result System =====


class ResultConstructorNode(Node):
    """ok(value) or ghalti(value) constructor."""

    __slots__ = ("value", "variant")

    def __init__(self, variant: str, value, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.variant = variant  # "OK" or "GHALTI"
        self.value = value


class ResultMethodCallNode(Node):
    """Result method: .bachao(fallback) or .lazmi(message)."""

    __slots__ = ("arg", "method_name", "receiver")

    def __init__(self, receiver, method_name: str, arg, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.receiver = receiver
        self.method_name = method_name
        self.arg = arg


class GhaltiNode(Node):
    """Ghalti expression: ghalti(message)."""

    __slots__ = ("message",)

    def __init__(self, message, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.message = message


class TypeCastNode(Node):
    """Type conversion (e.g. adad(x), lafz(y))."""

    __slots__ = ("expr", "target_type")

    def __init__(self, target_type: TokenType, expr, line: int = 0, column: int = 0):
        super().__init__(line, column)
        self.target_type = target_type
        self.expr = expr
