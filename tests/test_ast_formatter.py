"""Tests for the AST pretty-printer used by `sindlish ast`.

The formatter renders the same content the AST's ``__repr__`` produces but
spread across indented, colorized lines instead of one run-on line.
"""

import io

from rich.console import Console

from interpreter.frontend.ast_formatter import (
    TYPE_STYLE,
    VALUE_STYLE,
    build_ast_text,
    print_ast,
)
from interpreter.frontend.ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    CallNode,
    FunctionNode,
    ListNode,
    NumberNode,
    ProgramNode,
    ReturnNode,
    VariableNode,
)
from interpreter.frontend.tokens import Token, TokenType


def _tok(ttype, value=None):
    return Token(ttype, value, 1, 1)


def plain(program) -> str:
    return build_ast_text(program).plain


def styles(program) -> set:
    return {s.style for s in build_ast_text(program).spans if s.style}


class TestBuildAstText:
    def test_scalar_node_is_single_line(self):
        text = plain(ProgramNode([NumberNode(5)]))
        assert text.startswith("ProgramNode(")
        assert "NumberNode(" in text
        assert "value=5" in text

    def test_multiline_indentation(self):
        text = plain(ProgramNode([NumberNode(5)]))
        assert "\n" in text
        # the statements list child is indented deeper than the root
        lines = text.split("\n")
        root = lines[0]
        assert not root.startswith("    ")
        assert any(l.startswith("    statements=[") for l in lines)
        assert any(l.startswith("        NumberNode(") for l in lines)

    def test_no_box_drawing_pipes(self):
        text = plain(ProgramNode([NumberNode(5)]))
        for char in ("├", "└", "│", "─"):
            assert char not in text

    def test_preserves_all_repr_fields(self):
        node = AssignNode(name="x", value=NumberNode(5), is_const=True)
        text = plain(ProgramNode([node]))
        assert "is_const=True" in text
        assert "has_explicit_type=False" in text
        assert "element_type=None" in text

    def test_nested_binary_expression_indents(self):
        node = BinaryOpNode(
            left=NumberNode(1), op=_tok(TokenType.PLUS, "+"), right=NumberNode(2)
        )
        text = plain(ProgramNode([node]))
        assert "op=PLUS" in text
        assert "left=" in text
        assert "right=" in text

    def test_empty_list_inline(self):
        text = plain(ProgramNode([CallNode("f", [])]))
        assert "args=[]" in text

    def test_empty_container(self):
        text = plain(ProgramNode([ListNode([])]))
        assert "elements=[]" in text

    def test_func_node_has_params_and_body(self):
        fn = FunctionNode(
            name="jorr",
            params=[VariableNode("a"), VariableNode("b")],
            body=BlockNode([ReturnNode(NumberNode(1))]),
        )
        text = plain(ProgramNode([fn]))
        assert "param" in text
        assert "body=" in text
        assert "return_type=None" in text


class TestColors:
    def test_type_names_colored(self):
        s = styles(ProgramNode([NumberNode(5)]))
        assert TYPE_STYLE in s

    def test_values_colored(self):
        s = styles(ProgramNode([NumberNode(5)]))
        assert VALUE_STYLE in s

    def test_root_program_colored(self):
        s = styles(ProgramNode([]))
        assert TYPE_STYLE in s


class TestPrintAst:
    def test_print_writes_to_stdout(self, monkeypatch):
        buf = io.StringIO()
        console = Console(file=buf, force_terminal=False, no_color=True)
        monkeypatch.setattr("interpreter.frontend.ast_formatter.Console", lambda: console)
        print_ast(ProgramNode([NumberNode(5)]))
        out = buf.getvalue()
        assert "ProgramNode(" in out
        assert "value=5" in out
