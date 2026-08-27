"""
AST (Abstract Syntax Tree) node definitions for the Sindlish language.

Every syntactic construct in Sindlish is represented by a Node subclass.
Nodes carry source-position information (line, column) for error reporting.

Grammar summary (simplified):
    program     -> statement* EOF
    statement   -> if | while | assignment | function | return | expr
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

from __future__ import annotations

from dataclasses import dataclass, field

from .tokens import Token, TokenType


class Node:
    """Base class for all AST nodes. Carries source position.

    Subclasses are ``@dataclass(slots=True, repr=False)``; their generated
    ``__init__`` is wrapped by :meth:`__init_subclass__` so ``line``/``column``
    (owned by this base) are initialized with defaults on every construction.
    Source position is normally set afterward via :meth:`set_pos`.
    """

    __slots__ = ("column", "line")

    def __init__(self, line: int = 0, column: int = 0):
        self.line = line
        self.column = column

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "__dataclass_fields__"):
            dataclass_init = cls.__init__

            def init(self, *args, **kw):
                Node.__init__(self)
                dataclass_init(self, *args, **kw)

            cls.__init__ = init

    def set_pos(self, line: int, column: int) -> Node:
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


@dataclass(slots=True, repr=False)
class NumberNode(Node):
    """Integer or float literal."""

    value: int | float


@dataclass(slots=True, repr=False)
class StringNode(Node):
    """String literal."""

    value: str


@dataclass(slots=True, repr=False)
class BoolNode(Node):
    """Boolean literal (sach / koorh)."""

    value: bool


@dataclass(slots=True, repr=False)
class NullNode(Node):
    """Null literal (khali)."""


# ===== Variables & Assignment =====


@dataclass(slots=True, repr=False)
class VariableNode(Node):
    """Variable reference by name."""

    name: str
    slot_index: int | None = None
    scope_level: int | None = None
    deref_depth: int | None = None
    deref_name: str | None = None


@dataclass(slots=True, repr=False)
class AssignNode(Node):
    """Variable declaration/assignment with optional type annotation."""

    name: str
    value: Node
    type: TokenType | str | None = None
    is_const: bool = False
    element_type: object = None
    has_explicit_type: bool = False
    slot_index: int | None = None
    scope_level: int | None = None
    deref_depth: int | None = None
    deref_name: str | None = None


# ===== Operators =====


@dataclass(slots=True, repr=False)
class BinaryOpNode(Node):
    """Binary operation (e.g. a + b, x == y)."""

    left: Node
    op: Token
    right: Node


@dataclass(slots=True, repr=False)
class UnaryOpNode(Node):
    """Unary operation (e.g. -x, nah x)."""

    op: Token
    right: Node


@dataclass(slots=True, repr=False)
class PostfixOpNode(Node):
    """Postfix operation (? or !!)."""

    expr: Node
    op: Token


# ===== Statements =====


@dataclass(slots=True, repr=False)
class IfNode(Node):
    """If/else-if/else statement (agar/yawari/warna)."""

    condition: Node
    body: BlockNode
    else_body: BlockNode | None
    else_if_bodies: list = field(default_factory=list)

    def __post_init__(self):
        self.else_if_bodies = self.else_if_bodies or []


@dataclass(slots=True, repr=False)
class WhileNode(Node):
    """While loop (jistain)."""

    condition: Node
    body: BlockNode


@dataclass(slots=True, repr=False)
class ForNode(Node):
    """For loop (har)."""

    iterator: str
    iterable: Node
    body: BlockNode
    iterator_slot: int | None = None


@dataclass(slots=True, repr=False)
class BreakNode(Node):
    """Break statement (tor)."""


@dataclass(slots=True, repr=False)
class ContinueNode(Node):
    """Continue statement (jari)."""


@dataclass(slots=True, repr=False)
class BlockNode(Node):
    """A block of statements enclosed in { }."""

    statements: list


@dataclass(slots=True, repr=False)
class ProgramNode(Node):
    """Top-level program: a sequence of statements."""

    statements: list
    slot_count: int = 0


# ===== Collections =====


@dataclass(slots=True, repr=False)
class ListNode(Node):
    """List literal [a, b, c]."""

    elements: list


@dataclass(slots=True, repr=False)
class DictNode(Node):
    """Dictionary literal {k: v, ...}."""

    pairs: list


@dataclass(slots=True, repr=False)
class SetNode(Node):
    """Set literal {a, b, c}."""

    elements: list


@dataclass(slots=True, repr=False)
class IndexNode(Node):
    """Index access or assignment (obj[index] or obj[index] = value)."""

    left: Node
    index: Node
    value: Node | None = None


# ===== Functions =====


@dataclass(slots=True, repr=False)
class ParamNode(Node):
    """Function parameter definition."""

    name: str
    type: TokenType | str | None = None
    default: Node | None = None
    is_star: bool = False
    is_kw: bool = False
    element_type: object = None
    slot_index: int | None = None


@dataclass(slots=True, repr=False)
class FunctionNode(Node):
    """Function definition (kaam)."""

    name: str
    params: list
    body: BlockNode
    return_type: TokenType | str | None = None
    slot_count: int = 0
    cell_slots: tuple = ()
    free_slots: tuple = ()
    slot_metadata: dict = field(default_factory=dict)


@dataclass(slots=True, repr=False)
class CallNode(Node):
    """Function call.

    ``name`` is the callee: a variable name (``str``) for ``foo(...)``, or an
    expression ``Node`` for calling a computed value (``expr(...)``).
    """

    name: str | Node
    args: list
    keywords: list = field(default_factory=list)
    star_args: Node | None = None
    kw_args: Node | None = None

    def __post_init__(self):
        self.keywords = self.keywords or []


@dataclass(slots=True, repr=False)
class ReturnNode(Node):
    """Return statement (wapas)."""

    value: Node | None = None


@dataclass(slots=True, repr=False)
class MethodCallNode(Node):
    """Method call on an object (obj.method(args))."""

    instance: Node
    method_name: str
    args: list
    keywords: list = field(default_factory=list)
    star_args: Node | None = None
    kw_args: Node | None = None

    def __post_init__(self):
        self.keywords = self.keywords or []


@dataclass(slots=True, repr=False)
class GetAttrNode(Node):
    """Attribute access (obj.attr)."""

    instance: Node
    attr_name: str


# ===== Scoping =====


@dataclass(slots=True, repr=False)
class GlobalNode(Node):
    """Global variable declaration (aalmi)."""

    name: str


@dataclass(slots=True, repr=False)
class NonLocalNode(Node):
    """Non-local variable declaration (bahari)."""

    name: str


# ===== Result System =====


@dataclass(slots=True, repr=False)
class ResultConstructorNode(Node):
    """ok(value) or ghalti(value) constructor."""

    variant: str  # "OK" or "GHALTI"
    value: Node


@dataclass(slots=True, repr=False)
class ResultMethodCallNode(Node):
    """Result method: .bachao(fallback) or .lazmi(message)."""

    receiver: Node
    method_name: str
    arg: Node


@dataclass(slots=True, repr=False)
class GhaltiNode(Node):
    """Ghalti expression: ghalti(message)."""

    message: Node


@dataclass(slots=True, repr=False)
class TypeCastNode(Node):
    """Type conversion (e.g. adad(x), lafz(y))."""

    target_type: TokenType
    expr: Node
