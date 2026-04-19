"""Tests for agar (if) / warna (else) control flow."""

from tests.helpers import run


class TestIfTrue:
    def test_if_true_executes_body(self):
        _, out = run('agar 1 > 0 {\n    likh("yes")\n}')
        assert out.strip() == "yes"

    def test_if_false_skips_body(self):
        _, out = run('agar 0 > 1 {\n    likh("yes")\n}')
        assert out.strip() == ""


class TestIfElse:
    def test_else_branch(self):
        _, out = run('agar 0 > 1 {\n    likh("if")\n} warna {\n    likh("else")\n}')
        assert out.strip() == "else"

    def test_if_branch_when_true(self):
        _, out = run('agar 5 > 3 {\n    likh("if")\n} warna {\n    likh("else")\n}')
        assert out.strip() == "if"


class TestNestedIf:
    def test_nested_if(self):
        code = """
x = 10
agar x > 5 {
    agar x > 8 {
        likh("big")
    } warna {
        likh("medium")
    }
} warna {
    likh("small")
}
"""
        _, out = run(code)
        assert out.strip() == "big"

    def test_nested_if_else_branch(self):
        code = """
x = 7
agar x > 5 {
    agar x > 8 {
        likh("big")
    } warna {
        likh("medium")
    }
} warna {
    likh("small")
}
"""
        _, out = run(code)
        assert out.strip() == "medium"


class TestIfWithMultipleStatements:
    def test_multiple_statements_in_body(self):
        code = """
x = 1
agar x == 1 {
    likh("a")
    likh("b")
    likh("c")
}
"""
        _, out = run(code)
        lines = out.strip().split("\n")
        assert lines == ["a", "b", "c"]
