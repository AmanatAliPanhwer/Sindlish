"""Tests for builtin functions: lambi and likh (as function call)."""

from tests.conftest import run, extract_value


class TestLambi:
    """len()"""

    def test_lambi_list(self):
        interp, _ = run("x = [1, 2, 3]\nval = lambi(x)")
        assert extract_value(interp.variables["val"]["value"]) == 3

    def test_lambi_string(self):
        interp, _ = run('val = lambi("hello")')
        assert extract_value(interp.variables["val"]["value"]) == 5

    def test_lambi_empty_list(self):
        interp, _ = run("val = lambi([])")
        assert extract_value(interp.variables["val"]["value"]) == 0

    def test_lambi_empty_string(self):
        interp, _ = run('val = lambi("")')
        assert extract_value(interp.variables["val"]["value"]) == 0


class TestLikhFunction:
    """likh() as a function call (via CallNode)"""

    def test_likh_single_arg(self):
        _, out = run('likh("test")')
        assert out.strip() == "test"

    def test_likh_number(self):
        _, out = run("likh(42)")
        assert out.strip() == "42"

    def test_likh_multiple_args(self):
        _, out = run('likh("a", "b")')
        assert out.strip() == "a b"
