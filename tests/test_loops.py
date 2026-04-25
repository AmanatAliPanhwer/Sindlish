"""Tests for har (for) and kar-jistain (do-while) loops."""

from tests.conftest import run, extract_value


class TestForLoop:
    def test_for_list(self):
        code = """
nums = [1, 2, 3]
total = 0
har n mein nums {
    total = total + n
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["total"]["value"]) == 6

    def test_for_range_1(self):
        code = """
total = 0
har i mein range(5) {
    total = total + i
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["total"]["value"]) == 10

    def test_for_range_start_stop(self):
        code = """
total = 0
har i mein range(2, 5) {
    total = total + i
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["total"]["value"]) == 9

    def test_for_nested(self):
        code = """
count = 0
har i mein range(3) {
    har j mein range(2) {
        count = count + 1
    }
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["count"]["value"]) == 6


class TestLoopControl:
    def test_while_break(self):
        code = """
x = 0
jistain x < 10 {
    agar x == 3 {
        tor
    }
    x = x + 1
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["x"]["value"]) == 3

    def test_for_break(self):
        code = """
total = 0
har i mein range(10) {
    agar i == 5 {
        tor
    }
    total = total + i
}
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["total"]["value"]) == 10 # 0+1+2+3+4

    def test_while_continue(self):
        code = """
x = 0
total = 0
jistain x < 5 {
    x = x + 1
    agar x == 3 {
        jari
    }
    total = total + x
}
"""
        interp, _ = run(code)
        # 1 + 2 + (skip 3) + 4 + 5 = 12
        assert extract_value(interp.variables["total"]["value"]) == 12

    def test_for_continue(self):
        code = """
total = 0
har i mein range(5) {
    agar i == 2 {
        jari
    }
    total = total + i
}
"""
        interp, _ = run(code)
        # 0 + 1 + (skip 2) + 3 + 4 = 8
        assert extract_value(interp.variables["total"]["value"]) == 8

