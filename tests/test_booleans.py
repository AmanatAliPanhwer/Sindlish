"""Tests for boolean values (sach / koorh)."""

from tests.conftest import run, extract_value


class TestBooleanLiterals:
    def test_sach(self):
        interp, _ = run("x = sach")
        assert extract_value(interp.variables["x"]["value"]) is True

    def test_koorh(self):
        interp, _ = run("x = koorh")
        assert extract_value(interp.variables["x"]["value"]) is False


class TestBooleanInCondition:
    def test_sach_in_if(self):
        _, out = run('agar sach {\n    likh("yes")\n}')
        assert out.strip() == "yes"

    def test_koorh_in_if(self):
        _, out = run('agar koorh {\n    likh("yes")\n} warna {\n    likh("no")\n}')
        assert out.strip() == "no"


class TestBooleanFromComparison:
    def test_equality_true(self):
        interp, _ = run("x = 5 == 5")
        assert extract_value(interp.variables["x"]["value"]) is True

    def test_equality_false(self):
        interp, _ = run("x = 5 == 3")
        assert extract_value(interp.variables["x"]["value"]) is False

    def test_inequality_true(self):
        interp, _ = run("x = 5 != 3")
        assert extract_value(interp.variables["x"]["value"]) is True
