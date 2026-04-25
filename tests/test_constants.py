"""Tests for pakko (constant) declarations."""

import pytest
from tests.conftest import run, extract_value
from interpreter.errors import HalndeVaktGhalti, LikhaiJeGhalti


class TestConstantDeclaration:
    def test_const_int(self):
        interp, _ = run("pakko adad x = 42")
        assert extract_value(interp.variables["x"]["value"]) == 42
        assert interp.variables["x"]["is_const"] is True

    def test_const_string(self):
        interp, _ = run('pakko lafz name = "Sindlish"')
        assert extract_value(interp.variables["name"]["value"]) == "Sindlish"
        assert interp.variables["name"]["is_const"] is True

    def test_const_float(self):
        interp, _ = run("pakko dahai pi = 3.14")
        assert extract_value(interp.variables["pi"]["value"]) == 3.14
        assert interp.variables["pi"]["is_const"] is True


class TestConstantReassignment:
    def test_const_cannot_be_reassigned(self):
        with pytest.raises(HalndeVaktGhalti):
            run("pakko adad x = 10\nx = 20")

    def test_const_string_cannot_be_reassigned(self):
        with pytest.raises(HalndeVaktGhalti):
            run('pakko lafz s = "a"\ns = "b"')


class TestConstantMustBeInitialized:
    def test_const_without_value_raises(self):
        with pytest.raises(LikhaiJeGhalti):
            run("pakko adad x")
