"""Tests for the likh (print) statement."""

from tests.conftest import run


class TestPrintString:
    def test_print_simple_string(self):
        _, out = run('likh("Salam")')
        assert out.strip() == "Salam"

    def test_print_string_with_spaces(self):
        _, out = run('likh("hello world")')
        assert out.strip() == "hello world"

    def test_print_empty_string(self):
        _, out = run('likh("")')
        assert out.strip() == ""


class TestPrintNumber:
    def test_print_integer(self):
        _, out = run("likh(42)")
        assert out.strip() == "42"

    def test_print_float(self):
        _, out = run("likh(3.14)")
        assert out.strip() == "3.14"

    def test_print_zero(self):
        _, out = run("likh(0)")
        assert out.strip() == "0"

    def test_print_negative(self):
        _, out = run("likh(-5)")
        assert out.strip() == "-5"


class TestPrintExpression:
    def test_print_arithmetic_expression(self):
        _, out = run("likh(2 + 3)")
        assert out.strip() == "5"

    def test_print_variable(self):
        _, out = run('x = "test"\nlikh(x)')
        assert out.strip() == "test"


class TestPrintEmpty:
    def test_print_empty_parens(self):
        _, out = run("likh()")
        assert out.strip() == ""

    def test_print_empty_call(self):
        """likh() with no arguments prints empty line."""
        _, out = run("likh()")
        assert out.strip() == ""


class TestPrintMultiple:
    def test_multiple_prints(self):
        _, out = run('likh("a")\nlikh("b")\nlikh("c")')
        lines = out.strip().split("\n")
        assert lines == ["a", "b", "c"]
