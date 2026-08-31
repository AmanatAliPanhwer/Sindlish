"""Tests for the AST pretty-printer (Rich Tree) used by `sindlish ast`."""

import io

from rich.console import Console

from interpreter.frontend.ast_formatter import _child_nodes, _node_label, build_ast_tree
from interpreter.frontend.ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolNode,
    BreakNode,
    CallNode,
    ContinueNode,
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
    NonLocalNode,
    NullNode,
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
from interpreter.frontend.tokens import Token, TokenType


def _tok(ttype, value=None):
    return Token(ttype, value, 1, 1)


def render(tree):
    """Render a Rich Tree to plain text via a StringIO console."""
    buf = io.StringIO()
    console = Console(file=buf, width=100, force_terminal=False, no_color=True)
    console.print(tree)
    return buf.getvalue().rstrip("\n")


# ===== Seam 1: _node_label =====


class TestNodeLabelMinimal:
    def test_number(self):
        assert _node_label(NumberNode(value=5), verbose=False) == "NumberNode [5]"

    def test_float_number(self):
        assert _node_label(NumberNode(value=3.5), verbose=False) == "NumberNode [3.5]"

    def test_string(self):
        assert (
            _node_label(StringNode(value="hello"), verbose=False)
            == 'StringNode ["hello"]'
        )

    def test_long_string_truncated(self):
        long = "a" * 100
        label = _node_label(StringNode(value=long), verbose=False)
        assert label.startswith('StringNode ["')
        assert "..." in label
        assert len(label) < 70

    def test_multiline_string_collapsed(self):
        label = _node_label(StringNode(value="line1\n  line2\tline3"), verbose=False)
        assert "\n" not in label
        assert "  " not in label
        assert 'line1 line2 line3' in label

    def test_bool(self):
        assert _node_label(BoolNode(value=True), verbose=False) == "BoolNode [True]"

    def test_null(self):
        assert _node_label(NullNode(), verbose=False) == "NullNode"

    def test_variable(self):
        assert (
            _node_label(VariableNode(name="x"), verbose=False) == "VariableNode [x]"
        )

    def test_assign_with_type(self):
        node = AssignNode(name="x", value=NumberNode(1), type=TokenType.ADAD)
        assert _node_label(node, verbose=False) == "AssignNode [x: ADAD]"

    def test_assign_without_type(self):
        node = AssignNode(name="x", value=NumberNode(1))
        assert _node_label(node, verbose=False) == "AssignNode [x]"

    def test_binary_op(self):
        node = BinaryOpNode(
            left=NumberNode(1), op=_tok(TokenType.PLUS, "+"), right=NumberNode(2)
        )
        assert _node_label(node, verbose=False) == "BinaryOpNode [+]"

    def test_unary_op(self):
        node = UnaryOpNode(op=_tok(TokenType.MINUS, "-"), right=NumberNode(1))
        assert _node_label(node, verbose=False) == "UnaryOpNode [-]"

    def test_postfix_op(self):
        node = PostfixOpNode(expr=VariableNode("x"), op=_tok(TokenType.QMARK, "?"))
        assert _node_label(node, verbose=False) == "PostfixOpNode [?]"

    def test_for(self):
        node = ForNode(iterator="i", iterable=VariableNode("xs"), body=BlockNode([]))
        assert _node_label(node, verbose=False) == "ForNode [i]"

    def test_function(self):
        node = FunctionNode(name="kaam1", params=[], body=BlockNode([]))
        assert _node_label(node, verbose=False) == "FunctionNode [kaam1]"

    def test_param_with_type(self):
        node = ParamNode(name="x", type=TokenType.ADAD)
        assert _node_label(node, verbose=False) == "ParamNode [x: ADAD]"

    def test_param_without_type(self):
        node = ParamNode(name="x")
        assert _node_label(node, verbose=False) == "ParamNode [x]"

    def test_method_call(self):
        node = MethodCallNode(
            instance=VariableNode("s"), method_name="lambi", args=[]
        )
        assert _node_label(node, verbose=False) == "MethodCallNode [lambi]"

    def test_get_attr(self):
        node = GetAttrNode(instance=VariableNode("obj"), attr_name="attr1")
        assert _node_label(node, verbose=False) == "GetAttrNode [attr1]"

    def test_global(self):
        assert _node_label(GlobalNode(name="g"), verbose=False) == "GlobalNode [g]"

    def test_nonlocal(self):
        assert (
            _node_label(NonLocalNode(name="n"), verbose=False) == "NonLocalNode [n]"
        )

    def test_result_constructor_ok(self):
        node = ResultConstructorNode(variant="OK", value=NumberNode(1))
        assert _node_label(node, verbose=False) == "ResultConstructorNode [OK]"

    def test_result_method(self):
        node = ResultMethodCallNode(
            receiver=VariableNode("r"), method_name="bachao", arg=NumberNode(0)
        )
        assert _node_label(node, verbose=False) == "ResultMethodCallNode [bachao]"

    def test_type_cast(self):
        node = TypeCastNode(target_type=TokenType.ADAD, expr=VariableNode("x"))
        assert _node_label(node, verbose=False) == "TypeCastNode [ADAD]"

    def test_plain_nodes_no_key(self):
        assert _node_label(IfNode(None, None, None), verbose=False) == "IfNode"
        assert _node_label(WhileNode(None, None), verbose=False) == "WhileNode"
        assert _node_label(BreakNode(), verbose=False) == "BreakNode"
        assert _node_label(ContinueNode(), verbose=False) == "ContinueNode"
        assert _node_label(BlockNode([]), verbose=False) == "BlockNode"
        assert _node_label(ProgramNode([]), verbose=False) == "ProgramNode"
        assert _node_label(IndexNode(None, None), verbose=False) == "IndexNode"
        assert _node_label(CallNode("f", []), verbose=False) == "CallNode"
        assert _node_label(ReturnNode(), verbose=False) == "ReturnNode"
        assert _node_label(GhaltiNode(None), verbose=False) == "GhaltiNode"

    def test_list_count(self):
        node = ListNode([NumberNode(1), NumberNode(2), NumberNode(3)])
        assert _node_label(node, verbose=False) == "ListNode [3]"

    def test_list_empty(self):
        assert _node_label(ListNode([]), verbose=False) == "ListNode (empty)"

    def test_dict_count(self):
        node = DictNode([(StringNode("a"), NumberNode(1))])
        assert _node_label(node, verbose=False) == "DictNode [1]"

    def test_dict_empty(self):
        assert _node_label(DictNode([]), verbose=False) == "DictNode (empty)"

    def test_set_count(self):
        node = SetNode([NumberNode(1)])
        assert _node_label(node, verbose=False) == "SetNode [1]"

    def test_set_empty(self):
        assert _node_label(SetNode([]), verbose=False) == "SetNode (empty)"


# ===== Seam 1 (verbose): _node_label with verbose=True =====


class TestNodeLabelVerbose:
    def test_number_full(self):
        label = _node_label(NumberNode(value=5), verbose=True)
        assert label.startswith("NumberNode(")
        assert "value=5" in label

    def test_binary_op_full_shows_op(self):
        node = BinaryOpNode(
            left=NumberNode(1), op=_tok(TokenType.PLUS, "+"), right=NumberNode(2)
        )
        node.set_pos(3, 5)
        label = _node_label(node, verbose=True)
        assert label.startswith("BinaryOpNode(")
        assert "op=PLUS" in label
        # children (left/right) are shown as branches, not inlined
        assert "right=NumberNode" not in label
        assert "left=" not in label

    def test_verbose_includes_scalar_fields(self):
        node = AssignNode(name="x", value=NumberNode(1), is_const=True)
        label = _node_label(node, verbose=True)
        assert label.startswith("AssignNode(")
        assert 'name="x"' in label
        assert "is_const=True" in label
        # child value is a branch, not inlined
        assert "value=NumberNode" not in label

    def test_verbose_scalar_is_distinct_from_minimal(self):
        node = NumberNode(value=5)
        assert _node_label(node, verbose=True) != _node_label(node, verbose=False)


# ===== Seam 2: _child_nodes =====


class TestChildNodes:
    def test_binary_op_children_in_order(self):
        node = BinaryOpNode(
            left=NumberNode(1), op=_tok(TokenType.PLUS, "+"), right=NumberNode(2)
        )
        children = _child_nodes(node, verbose=False)
        assert [(name, type(c).__name__) for name, c in children] == [
            ("left", "NumberNode"),
            ("right", "NumberNode"),
        ]

    def test_number_has_no_children(self):
        assert _child_nodes(NumberNode(5), verbose=False) == []

    def test_assign_value_is_child(self):
        node = AssignNode(name="x", value=NumberNode(1))
        children = _child_nodes(node, verbose=False)
        names = [n for n, _ in children]
        assert "value" in names

    def test_if_children(self):
        node = IfNode(
            condition=VariableNode("c"),
            body=BlockNode([ReturnNode(NumberNode(1))]),
            else_body=BlockNode([]),
        )
        children = _child_nodes(node, verbose=False)
        names = [n for n, _ in children]
        assert names == ["condition", "body", "else_body"]

    def test_tuple_pairs_in_dict(self):
        node = DictNode(
            [(StringNode("k"), NumberNode(1)), (StringNode("k2"), NumberNode(2))]
        )
        children = _child_nodes(node, verbose=False)
        # each pair should be a group node
        assert len(children) == 2
        for name, group in children:
            assert name.startswith("pair[")
            assert isinstance(group, list)

    def test_statement_list_children(self):
        node = ProgramNode([NumberNode(1), NumberNode(2)])
        children = _child_nodes(node, verbose=False)
        assert len(children) == 2
        for name, c in children:
            assert name.startswith("item[")
            assert isinstance(c, NumberNode)


# ===== Seam 3: build_ast_tree (end-to-end render) =====


class TestBuildTree:
    def test_program_renders_tree(self):
        program = ProgramNode([AssignNode(name="x", value=NumberNode(5))])
        tree = build_ast_tree(program, verbose=False)
        text = render(tree)
        assert "ProgramNode" in text
        assert "AssignNode [x]" in text
        assert "NumberNode [5]" in text

    def test_nested_binary_expression(self):
        program = ProgramNode(
            [
                AssignNode(
                    name="y",
                    value=BinaryOpNode(
                        left=NumberNode(1),
                        op=_tok(TokenType.PLUS, "+"),
                        right=NumberNode(2),
                    ),
                )
            ]
        )
        tree = build_ast_tree(program, verbose=False)
        text = render(tree)
        assert "BinaryOpNode [+]" in text
        assert "NumberNode [1]" in text
        assert "NumberNode [2]" in text

    def test_returns_a_rich_tree(self):
        tree = build_ast_tree(ProgramNode([]), verbose=False)
        assert tree.__class__.__name__ == "Tree"

    def test_verbose_root_does_not_inline_children(self):
        program = ProgramNode(
            [AssignNode(name="x", value=NumberNode(5)), AssignNode(name="y", value=NumberNode(6))]
        )
        tree = build_ast_tree(program, verbose=True)
        text = render(tree)
        # the root label keeps its own fields only, not children inlined
        assert text.startswith("ProgramNode(")
        assert "value=NumberNode" not in text.split("\n")[0]
        # children still appear as branches
        assert 'AssignNode(name="x"' in text
        assert 'AssignNode(name="y"' in text

    def test_verbose_dict_pairs_render_as_subgroups(self):
        program = ProgramNode(
            [DictNode([(StringNode("k"), NumberNode(1))])]
        )
        tree = build_ast_tree(program, verbose=True)
        text = render(tree)
        assert "pair[0]" in text
        assert "key:" in text
        assert "value:" in text
