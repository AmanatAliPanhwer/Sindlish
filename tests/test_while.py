"""Tests for jistain (while) loops."""

from tests.helpers import run


class TestBasicWhile:
    def test_while_counter(self):
        code = """
x = 0
jistain x < 3 {
    x = x + 1
}
"""
        interp, _ = run(code)
        assert interp.variables["x"]["value"] == 3

    def test_while_never_runs(self):
        code = """
x = 10
jistain x < 0 {
    x = x + 1
}
"""
        interp, _ = run(code)
        assert interp.variables["x"]["value"] == 10


class TestWhileWithPrint:
    def test_while_prints(self):
        code = """
x = 0
jistain x < 3 {
    likh(x)
    x = x + 1
}
"""
        _, out = run(code)
        lines = out.strip().split("\n")
        assert lines == ["0", "1", "2"]


class TestWhileWithIf:
    def test_while_with_nested_if(self):
        code = """
x = 0
jistain x < 4 {
    agar x == 2 {
        likh("found")
    }
    x = x + 1
}
"""
        _, out = run(code)
        assert out.strip() == "found"


class TestWhileAccumulation:
    def test_while_sum(self):
        code = """
total = 0
i = 1
jistain i <= 5 {
    total = total + i
    i = i + 1
}
"""
        interp, _ = run(code)
        assert interp.variables["total"]["value"] == 15
