"""Tests for set literals and typed sets."""

import pytest
from tests.helpers import run, extract_value
from interpreter.errors import QisamJeGhalti


class TestSetLiteral:
    def test_int_set(self):
        interp, _ = run("x = {1, 2, 3}")
        assert extract_value(interp.variables["x"]["value"]) == {1, 2, 3}

    def test_string_set(self):
        interp, _ = run('x = {"a", "b", "c"}')
        assert extract_value(interp.variables["x"]["value"]) == {"a", "b", "c"}

    def test_single_element_set(self):
        interp, _ = run("x = {42}")
        assert extract_value(interp.variables["x"]["value"]) == {42}


class TestTypedSet:
    def test_typed_majmuo_adad(self):
        interp, _ = run("majmuo[adad] x = {1, 2, 3}")
        assert extract_value(interp.variables["x"]["value"]) == {1, 2, 3}

    def test_typed_majmuo_rejects_wrong_type(self):
        with pytest.raises(QisamJeGhalti):
            run('majmuo[adad] x = {1, "two", 3}')
