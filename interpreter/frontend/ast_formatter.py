"""Indented, colorized pretty-printer for Sindlish AST nodes.

Renders the same content the AST's ``__repr__`` produces (every field,
excluding the source-position ``line``/``column`` that ``__repr__`` also
skips) but spread across multiple lines with indentation and color, so the
structure is readable instead of one long run-on line.
"""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from .ast_nodes import Node

INDENT = "    "

TYPE_STYLE = "cyan"
KEY_STYLE = "bold"
VALUE_STYLE = "yellow"


def _is_node(value) -> bool:
    return isinstance(value, Node)


def _is_complex(value) -> bool:
    """True when the value is or contains AST nodes (needs multi-line nesting)."""
    if _is_node(value):
        return True
    if isinstance(value, (list, tuple)):
        return any(_is_complex(v) for v in value)
    return False


def _scalar_text(value) -> Text:
    """Render a scalar value, colorized by kind."""
    return Text(repr(value), style=VALUE_STYLE)


def _lines_value(value, depth: int) -> list[tuple[int, Text]]:
    """Return the indented lines representing *value* at nesting *depth*."""
    if _is_node(value):
        return _lines_node(value, depth)
    if isinstance(value, list):
        return _lines_list(value, depth)
    if isinstance(value, tuple):
        return _lines_tuple(value, depth)
    if isinstance(value, dict):
        return [(depth, Text(repr(value)))]
    return [(depth, _scalar_text(value))]


def _with_comma(last: tuple[int, Text]) -> tuple[int, Text]:
    line, text = last
    if isinstance(text, Text):
        text = text.copy()
    else:
        text = Text(text)
    text.append(",")
    return (line, text)


def _lines_node(node: Node, depth: int) -> list[tuple[int, Text]]:
    name = type(node).__name__
    lines: list[tuple[int, Text]] = [(depth, Text(name, style=TYPE_STYLE) + "(")]

    for key in type(node).__slots__:
        if key in ("line", "column"):
            continue
        value = getattr(node, key, None)

        if _is_complex(value):
            field_lines = _lines_value(value, depth + 1)
            first_line, first_text = field_lines[0]
            field_lines[0] = (first_line, Text(f"{key}=", style=KEY_STYLE) + first_text)
            field_lines[-1] = _with_comma(field_lines[-1])
            lines.extend(field_lines)
        else:
            text = Text(f"{key}=", style=KEY_STYLE) + _scalar_text(value) + ","
            lines.append((depth + 1, text))

    lines.append((depth, ")"))
    return lines


def _lines_list(items: list, depth: int) -> list[tuple[int, Text]]:
    if not items:
        return [(depth, Text("[]"))]
    lines: list[tuple[int, Text]] = [(depth, "[")]
    for item in items:
        item_lines = _lines_value(item, depth + 1)
        item_lines[-1] = _with_comma(item_lines[-1])
        lines.extend(item_lines)
    lines.append((depth, "]"))
    return lines


def _lines_tuple(items, depth: int) -> list[tuple[int, Text]]:
    if not items:
        return [(depth, Text("()"))]
    lines: list[tuple[int, Text]] = [(depth, "(")]
    for item in items:
        item_lines = _lines_value(item, depth + 1)
        item_lines[-1] = _with_comma(item_lines[-1])
        lines.extend(item_lines)
    lines.append((depth, ")"))
    return lines


def build_ast_text(program: Node) -> Text:
    """Build the indented, colorized Text representation of a parsed AST."""
    lines = [Text(INDENT * line).append(text) for line, text in _lines_node(program, 0)]
    out = Text()
    for i, line in enumerate(lines):
        out.append(line)
        if i != len(lines) - 1:
            out.append("\n")
    return out


def print_ast(program: Node) -> None:
    """Print a parsed AST as colored, indented text to stdout."""
    Console().print(build_ast_text(program))
