"""Tests for error cases: undefined variables, type mismatches, immutability."""

import pytest

from interpreter.errors import *
from tests.conftest import run


class TestUndefinedVariable:
    def test_undefined_variable_raises(self):
        with pytest.raises(NaleJeGhalti, match="na milyo"):
            run("likh(xyz)")

    def test_undefined_in_expression(self):
        with pytest.raises(NaleJeGhalti, match="na milyo"):
            run("x = abc + 1")


class TestConstReassignment:
    def test_const_reassignment_raises(self):
        with pytest.raises(HalndeVaktGhalti, match="pakko"):
            run("pakko adad x = 10\nx = 20")


class TestTypeMismatch:
    def test_adad_rejects_string(self):
        with pytest.raises(QisamJeGhalti, match="adad"):
            run('adad x = "hello"')

    def test_lafz_rejects_int(self):
        with pytest.raises(QisamJeGhalti, match="lafz"):
            run("lafz x = 42")

    def test_dahai_rejects_int(self):
        with pytest.raises(QisamJeGhalti, match="dahai"):
            run("dahai x = 42")

    def test_fehrist_typed_rejects_wrong_element(self):
        with pytest.raises(QisamJeGhalti):
            run('fehrist[adad] x = [1, "two"]')

    def test_lughat_typed_rejects_wrong_key(self):
        with pytest.raises(QisamJeGhalti):
            run("lughat[lafz, adad] x = {1: 100}")

    def test_param_type_mismatch(self):
        with pytest.raises(QisamJeGhalti, match="Parameter.*khapyo paye"):
            run('kaam foo(adad x) { wapas x }\nfoo("hello")')

    def test_return_type_mismatch(self):
        with pytest.raises(QisamJeGhalti, match="Wapas khe.*khapyo paye"):
            run('kaam foo() -> adad { wapas "hello" }\nfoo()')

    def test_majmuo_element_error_says_majmuo(self):
        with pytest.raises(QisamJeGhalti, match="Majmuo"):
            run('majmuo[adad] x = {1, "two", 3}')

    def test_lughat_element_error_says_lughat(self):
        with pytest.raises(QisamJeGhalti, match="Lughat"):
            run('lughat[lafz, adad] x = {"a": 1, "b": "x"}')


class TestImmutableKeyInSet:
    def test_mutable_value_in_set_raises(self):
        """Lists are mutable and cannot be added to a set."""
        with pytest.raises(QisamJeGhalti):
            run("x = {1, 2}\nx.addkar([1, 2])")


class TestUndefinedFunction:
    def test_undefined_function_raises(self):
        with pytest.raises(NaleJeGhalti, match="na milyo"):
            run("x = foobar()")

    def test_undefined_method_raises(self):
        with pytest.raises(NaleJeGhalti, match="wazahat na milyo"):
            run("x = [1, 2]\nx.nonexistent()")


class TestConstMustBeInitialized:
    def test_pakko_without_value(self):
        with pytest.raises(LikhaiJeGhalti):
            run("pakko adad x")


class TestPanicStatement:
    def test_bare_ghalti_statement_panics(self):
        """A standalone ghalti(msg) statement is THE panic form (v0.2)."""
        with pytest.raises(HalndeVaktGhalti, match="boom"):
            run('x = 1\nghalti("boom")')

    def test_kharabi_keyword_is_retired(self):
        """kharabi was removed in the v0.2 refactor — it lexes as a plain
        identifier now, so it dies as an unknown name at runtime."""
        with pytest.raises(NaleJeGhalti, match="kharabi"):
            run('kharabi("old spellings die")')
