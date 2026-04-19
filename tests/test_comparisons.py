"""Tests for comparison operators."""

from tests.helpers import run


class TestEqual:
    def test_equal_true(self):
        interp, _ = run("x = 5 == 5")
        assert interp.variables["x"]["value"] is True

    def test_equal_false(self):
        interp, _ = run("x = 5 == 3")
        assert interp.variables["x"]["value"] is False

    def test_equal_strings(self):
        interp, _ = run('x = "a" == "a"')
        assert interp.variables["x"]["value"] is True


class TestNotEqual:
    def test_not_equal_true(self):
        interp, _ = run("x = 5 != 3")
        assert interp.variables["x"]["value"] is True

    def test_not_equal_false(self):
        interp, _ = run("x = 5 != 5")
        assert interp.variables["x"]["value"] is False


class TestGreaterThan:
    def test_gt_true(self):
        interp, _ = run("x = 10 > 5")
        assert interp.variables["x"]["value"] is True

    def test_gt_false(self):
        interp, _ = run("x = 3 > 5")
        assert interp.variables["x"]["value"] is False

    def test_gt_equal_values(self):
        interp, _ = run("x = 5 > 5")
        assert interp.variables["x"]["value"] is False


class TestLessThan:
    def test_lt_true(self):
        interp, _ = run("x = 3 < 5")
        assert interp.variables["x"]["value"] is True

    def test_lt_false(self):
        interp, _ = run("x = 10 < 5")
        assert interp.variables["x"]["value"] is False


class TestGreaterThanOrEqual:
    def test_gteq_greater(self):
        interp, _ = run("x = 10 >= 5")
        assert interp.variables["x"]["value"] is True

    def test_gteq_equal(self):
        interp, _ = run("x = 5 >= 5")
        assert interp.variables["x"]["value"] is True

    def test_gteq_less(self):
        interp, _ = run("x = 3 >= 5")
        assert interp.variables["x"]["value"] is False


class TestLessThanOrEqual:
    def test_lteq_less(self):
        interp, _ = run("x = 3 <= 5")
        assert interp.variables["x"]["value"] is True

    def test_lteq_equal(self):
        interp, _ = run("x = 5 <= 5")
        assert interp.variables["x"]["value"] is True

    def test_lteq_greater(self):
        interp, _ = run("x = 10 <= 5")
        assert interp.variables["x"]["value"] is False
