"""Tests for dictionary literals, indexing, and typed dicts."""

import pytest
from tests.helpers import run
from interpreter.errors import QisamJeGhalti


class TestDictLiteral:
    def test_empty_dict(self):
        interp, _ = run("x = {}")
        assert interp.variables["x"]["value"] == {}

    def test_string_keys(self):
        interp, _ = run('x = {"a": 1, "b": 2}')
        assert interp.variables["x"]["value"] == {"a": 1, "b": 2}

    def test_int_keys(self):
        interp, _ = run("x = {1: 10, 2: 20}")
        assert interp.variables["x"]["value"] == {1: 10, 2: 20}


class TestDictIndexing:
    def test_access_by_key(self):
        _, out = run('x = {"a": 42}\nlikh(x["a"])')
        assert out.strip() == "42"

    def test_assignment_by_key(self):
        interp, _ = run('x = {"a": 1}\nx["a"] = 99')
        assert interp.variables["x"]["value"] == {"a": 99}

    def test_new_key_assignment(self):
        interp, _ = run('x = {"a": 1}\nx["b"] = 2')
        assert interp.variables["x"]["value"] == {"a": 1, "b": 2}


class TestTypedDict:
    def test_typed_lughat(self):
        interp, _ = run('lughat[lafz, adad] x = {"score": 100}')
        assert interp.variables["x"]["value"] == {"score": 100}

    def test_typed_lughat_wrong_key_type(self):
        with pytest.raises(QisamJeGhalti):
            run('lughat[lafz, adad] x = {1: 100}')

    def test_typed_lughat_wrong_value_type(self):
        with pytest.raises(QisamJeGhalti):
            run('lughat[lafz, adad] x = {"score": "high"}')
