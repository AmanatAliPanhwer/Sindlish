"""Tests for logical operators: aen (and), ya (or), nah (not)."""

from tests.helpers import run


class TestAnd:
    def test_and_both_true(self):
        interp, _ = run("x = sach aen sach")
        assert interp.variables["x"]["value"] is True

    def test_and_one_false(self):
        interp, _ = run("x = sach aen koorh")
        assert interp.variables["x"]["value"] is False

    def test_and_both_false(self):
        interp, _ = run("x = koorh aen koorh")
        assert interp.variables["x"]["value"] is False

    def test_and_with_comparisons(self):
        _, out = run('agar 5 > 3 aen 10 > 1 {\n    likh("yes")\n}')
        assert out.strip() == "yes"


class TestOr:
    def test_or_both_true(self):
        interp, _ = run("x = sach ya sach")
        assert interp.variables["x"]["value"] is True

    def test_or_one_true(self):
        interp, _ = run("x = koorh ya sach")
        assert interp.variables["x"]["value"] is True

    def test_or_both_false(self):
        interp, _ = run("x = koorh ya koorh")
        assert interp.variables["x"]["value"] is False

    def test_or_with_comparisons(self):
        _, out = run('agar 1 > 10 ya 5 > 3 {\n    likh("yes")\n}')
        assert out.strip() == "yes"


class TestNot:
    def test_not_true(self):
        interp, _ = run("x = nah sach")
        assert interp.variables["x"]["value"] is False

    def test_not_false(self):
        interp, _ = run("x = nah koorh")
        assert interp.variables["x"]["value"] is True

    def test_not_with_bang(self):
        interp, _ = run("x = !sach")
        assert interp.variables["x"]["value"] is False

    def test_not_in_condition(self):
        _, out = run('agar nah koorh {\n    likh("yes")\n}')
        assert out.strip() == "yes"


class TestCombined:
    def test_and_or_combined(self):
        interp, _ = run("x = sach ya koorh aen sach")
        assert interp.variables["x"]["value"] is True

    def test_not_and(self):
        interp, _ = run("x = nah koorh aen sach")
        assert interp.variables["x"]["value"] is True
