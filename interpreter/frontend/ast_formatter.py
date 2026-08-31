"""Rich Tree pretty-printer for Sindlish AST nodes.

Used by the ``sindlish ast`` CLI command to render a colorized, indented
tree of an AST instead of the flat one-line ``repr`` dump.
"""

from __future__ import annotations

import re

from rich.markup import escape
from rich.tree import Tree

from .ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolNode,
    CallNode,
    DictNode,
    ForNode,
    FunctionNode,
    GetAttrNode,
    GhaltiNode,
    GlobalNode,
    IfNode,
    IndexNode,
    ListNode,
    MethodCallNode,
    Node,
    NonLocalNode,
    NumberNode,
    ParamNode,
    PostfixOpNode,
    ProgramNode,
    ResultConstructorNode,
    ResultMethodCallNode,
    ReturnNode,
    SetNode,
    StringNode,
    TypeCastNode,
    UnaryOpNode,
    VariableNode,
    WhileNode,
)

TRUNCATE = 50
ELISION = "..."

TYPE_STYLE = "cyan"
VALUE_STYLE = "yellow"


def _truncate(text: str, limit: int = TRUNCATE) -> str:
    """Collapse runs of whitespace/newlines and truncate to *limit* chars.

    Whitespace is normalised so multiline values stay on a single line in
    the tree output.
    """
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - len(ELISION)] + ELISION


def _token_str(token) -> str:
    """Return a compact display string for an operator/keyword token."""
    if token is None:
        return ""
    value = getattr(token, "value", None)
    if value is None or value == "":
        return getattr(token.type, "name", "?")
    return str(value)


def _is_child_value(value) -> bool:
    """Return True if *value* represents AST children (rather than a scalar)."""
    if isinstance(value, Node):
        return True
    if isinstance(value, (list, tuple)):
        return any(isinstance(v, Node) for v in value)
    return False


def _verbose_label(node: Node) -> str:
    """Build a per-node verbose label showing only its own scalar fields.

    Child nodes are not inlined (they become separate tree branches), and
    synthetic ``hints`` slots are omitted for readability. Scalar fields
    match the node's ``__repr__`` rendering.
    """
    parts = []
    for k in type(node).__slots__:
        if k in ("line", "column", "hints"):
            continue
        value = getattr(node, k, None)
        if _is_child_value(value):
            continue
        if isinstance(value, str):
            value = f'"{_truncate(value)}"'
        else:
            value = f"{value!r}"
        parts.append(f"{k}={value}")
    field_str = ", ".join(parts)
    return f"{type(node).__name__}({field_str})"


def _node_label(node: Node, verbose: bool) -> str:
    """Return the display label for an AST node.

    In the minimal view the label is ``Type [key_value]`` (or just ``Type``
    when no key applies); in the verbose view it shows the node's own
    scalar fields without inlining its children.
    """
    if verbose:
        return _verbose_label(node)

    name = type(node).__name__
    key = _key_value(node)
    if key is None:
        return name
    if isinstance(node, (ListNode, DictNode, SetNode)) and _count(node) == 0:
        return f"{name} (empty)"
    return f"{name} [{key}]"


def _key_value(node: Node) -> str | None:
    """Return the compact key value shown in a minimal label, or None."""
    if isinstance(node, NumberNode):
        return str(node.value)
    if isinstance(node, (StringNode,)):
        return f'"{_truncate(node.value)}"'
    if isinstance(node, BoolNode):
        return str(node.value)
    if isinstance(node, (VariableNode,)):
        return node.name
    if isinstance(node, (GlobalNode, NonLocalNode)):
        return node.name
    if isinstance(node, AssignNode):
        parts = [node.name]
        if node.type is not None:
            parts.append(_type_name(node.type))
        return ": ".join(parts)
    if isinstance(node, BinaryOpNode):
        return _token_str(node.op)
    if isinstance(node, UnaryOpNode):
        return _token_str(node.op)
    if isinstance(node, PostfixOpNode):
        return _token_str(node.op)
    if isinstance(node, ForNode):
        return node.iterator
    if isinstance(node, FunctionNode):
        return node.name
    if isinstance(node, ParamNode):
        parts = [node.name]
        if node.type is not None:
            parts.append(_type_name(node.type))
        return ": ".join(parts)
    if isinstance(node, MethodCallNode):
        return node.method_name
    if isinstance(node, ResultMethodCallNode):
        return node.method_name
    if isinstance(node, GetAttrNode):
        return node.attr_name
    if isinstance(node, ResultConstructorNode):
        return node.variant
    if isinstance(node, TypeCastNode):
        return _type_name(node.target_type)
    if isinstance(node, ListNode):
        return _count_label(len(node.elements))
    if isinstance(node, SetNode):
        return _count_label(len(node.elements))
    if isinstance(node, DictNode):
        return _count_label(len(node.pairs))

    return None


def _type_name(t) -> str:
    """Render a type reference (TokenType, str, or None) as a display string."""
    if t is None:
        return ""
    name = getattr(t, "name", None)
    if name is not None:
        return name
    return str(t)


def _count_label(count: int) -> str:
    return str(count)


def _count(node) -> int:
    if isinstance(node, (ListNode, SetNode)):
        return len(node.elements)
    if isinstance(node, DictNode):
        return len(node.pairs)
    return 0


def _child_nodes(node: Node, verbose: bool) -> list[tuple[str, Node]]:
    """Return the ordered child relationships ``(field_name, child)``.

    List-valued fields yield one ``item[i]`` entry per element; key/value
    pairs and statements are grouped so each is annotated once.
    """
    if isinstance(node, ProgramNode):
        return _indexed(node.statements, "item[{i}]")

    if isinstance(node, BlockNode):
        return _indexed(node.statements, "item[{i}]")

    if isinstance(node, ListNode):
        return _indexed(node.elements, "item[{i}]")

    if isinstance(node, SetNode):
        return _indexed(node.elements, "item[{i}]")

    if isinstance(node, DictNode):
        result = []
        for i, (k, v) in enumerate(node.pairs):
            result.append((f"pair[{i}]", [("key", k), ("value", v)]))
        return result

    if isinstance(node, IfNode):
        children = [("condition", node.condition), ("body", node.body)]
        if node.else_body is not None:
            children.append(("else_body", node.else_body))
        for i, (cond, body) in enumerate(node.else_if_bodies):
            children.append((f"else_if[{i}]", [("condition", cond), ("body", body)]))
        return children

    if isinstance(node, BinaryOpNode):
        return [("left", node.left), ("right", node.right)]

    if isinstance(node, UnaryOpNode):
        return [("right", node.right)]

    if isinstance(node, PostfixOpNode):
        return [("expr", node.expr)]

    if isinstance(node, AssignNode):
        return [("value", node.value)]

    if isinstance(node, VariableNode):
        return []

    if isinstance(node, WhileNode):
        return [("condition", node.condition), ("body", node.body)]

    if isinstance(node, ForNode):
        return [("iterable", node.iterable), ("body", node.body)]

    if isinstance(node, FunctionNode):
        children = []
        for i, p in enumerate(node.params):
            children.append((f"param[{i}]", p))
        children.append(("body", node.body))
        return children

    if isinstance(node, CallNode):
        children = [("callee", node.name)] if not isinstance(node.name, str) else []
        children += _call_children(node.args, node.star_args, node.kw_args)
        return children

    if isinstance(node, MethodCallNode):
        children = [("instance", node.instance)]
        children += _call_children(node.args, node.star_args, node.kw_args)
        return children

    if isinstance(node, ReturnNode):
        return [("value", node.value)] if node.value is not None else []

    if isinstance(node, IndexNode):
        children = [("left", node.left), ("index", node.index)]
        if node.value is not None:
            children.append(("value", node.value))
        return children

    if isinstance(node, GetAttrNode):
        return [("instance", node.instance)]

    if isinstance(node, ResultConstructorNode):
        return [("value", node.value)]

    if isinstance(node, ResultMethodCallNode):
        return [("receiver", node.receiver), ("arg", node.arg)]

    if isinstance(node, GhaltiNode):
        return [("message", node.message)]

    if isinstance(node, TypeCastNode):
        return [("expr", node.expr)]

    return []


def _indexed(items: list, label_fmt: str) -> list[tuple[str, Node]]:
    return [(label_fmt.format(i=i), item) for i, item in enumerate(items)]


def _call_children(
    args: list, star_args, kw_args, prefix: str = "arg"
) -> list[tuple[str, Node]]:
    """Build child entries for a call's positional args plus star/kw args."""
    children = []
    for i, a in enumerate(args):
        children.append((f"{prefix}[{i}]", a))
    if star_args is not None:
        children.append(("star_args", star_args))
    if kw_args is not None:
        children.append(("kw_args", kw_args))
    return children


def _add_children(tree: Tree, children: list[tuple[str, Node]], verbose: bool) -> None:
    for field_name, child in children:
        if isinstance(child, list):
            group = tree.add(field_name, style=TYPE_STYLE)
            _add_children(group, child, verbose)
            continue
        branch = tree.add(
            f"{field_name}: {escape(_node_label(child, verbose))}",
            style=VALUE_STYLE if verbose else TYPE_STYLE,
        )
        _add_children(branch, _child_nodes(child, verbose), verbose)


def build_ast_tree(program: Node, verbose: bool = False) -> Tree:
    """Build a Rich Tree representation of a parsed AST."""
    label = _node_label(program, verbose)
    tree = Tree(escape(label), style=TYPE_STYLE if not verbose else VALUE_STYLE)
    _add_children(tree, _child_nodes(program, verbose), verbose)
    return tree


def print_ast_tree(program: Node, verbose: bool = False) -> None:
    """Print a parsed AST as a colorized Rich Tree to stdout."""
    from rich.console import Console

    Console().print(build_ast_tree(program, verbose=verbose))
