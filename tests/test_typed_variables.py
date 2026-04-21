"""Tests for typed variable declarations and default values."""

import pytest
from tests.helpers import run, extract_value
from interpreter.errors import QisamJeGhalti


class TestAdad:
    def test_adad_default(self):
        interp, _ = run("adad x")
        assert extract_value(interp.variables["x"]["value"]) == 0

    def test_adad_with_value(self):
        interp, _ = run("adad x = 42")
        assert extract_value(interp.variables["x"]["value"]) == 42

    def test_adad_rejects_string(self):
        with pytest.raises(QisamJeGhalti):
            run('adad x = "hello"')

    def test_adad_rejects_float(self):
        with pytest.raises(QisamJeGhalti):
            run("adad x = 3.14")


class TestDahai:
    def test_dahai_default(self):
        interp, _ = run("dahai x")
        assert extract_value(interp.variables["x"]["value"]) == 0.0

    def test_dahai_with_value(self):
        interp, _ = run("dahai x = 3.14")
        assert extract_value(interp.variables["x"]["value"]) == 3.14

    def test_dahai_rejects_string(self):
        with pytest.raises(QisamJeGhalti):
            run('dahai x = "hello"')

    def test_dahai_rejects_int(self):
        with pytest.raises(QisamJeGhalti):
            run("dahai x = 42")


class TestLafz:
    def test_lafz_default(self):
        interp, _ = run("lafz x")
        assert extract_value(interp.variables["x"]["value"]) == ""

    def test_lafz_with_value(self):
        interp, _ = run('lafz x = "hello"')
        assert extract_value(interp.variables["x"]["value"]) == "hello"

    def test_lafz_rejects_int(self):
        with pytest.raises(QisamJeGhalti):
            run("lafz x = 42")


class TestFaislo:
    def test_faislo_default(self):
        interp, _ = run("faislo x")
        assert extract_value(interp.variables["x"]["value"]) is False

    def test_faislo_sach(self):
        interp, _ = run("faislo x = sach")
        assert extract_value(interp.variables["x"]["value"]) is True

    def test_faislo_koorh(self):
        interp, _ = run("faislo x = koorh")
        assert extract_value(interp.variables["x"]["value"]) is False


class TestKhali:
    def test_khali_default(self):
        interp, _ = run("khali x")
        assert extract_value(interp.variables["x"]["value"]) is None

    def test_khali_reassign(self):
        interp, _ = run("khali x\nx = 100")
        assert extract_value(interp.variables["x"]["value"]) == 100


class TestPostfixTypeAnnotation:
    def test_postfix_adad(self):
        interp, _ = run("x: adad = 10")
        assert extract_value(interp.variables["x"]["value"]) == 10

    def test_postfix_lafz(self):
        interp, _ = run('x: lafz = "hi"')
        assert extract_value(interp.variables["x"]["value"]) == "hi"

    def test_postfix_type_mismatch(self):
        with pytest.raises(QisamJeGhalti):
            run('x: adad = "hello"')
