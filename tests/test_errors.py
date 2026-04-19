"""Tests for error cases: undefined variables, type mismatches, immutability."""

import pytest
from tests.helpers import run
from interpreter.errors import *


class TestUndefinedVariable:
    def test_undefined_variable_raises(self):
        with pytest.raises(NaleJeGhalti, match="wazahat thayal"):
            run("likh(xyz)")

    def test_undefined_in_expression(self):
        with pytest.raises(NaleJeGhalti, match="wazahat thayal"):
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
            run('lughat[lafz, adad] x = {1: 100}')


class TestImmutableKeyInSet:
    def test_mutable_value_in_set_raises(self):
        """Lists are mutable and cannot be added to a set."""
        with pytest.raises(QisamJeGhalti):
            run("x = {1, 2}\nx.addkar([1, 2])")


class TestUndefinedFunction:
    def test_undefined_function_raises(self):
        with pytest.raises(NaleJeGhalti, match="na milio"):
            run("x = foobar()")

    def test_undefined_method_raises(self):
        with pytest.raises(NaleJeGhalti, match="wazahat thayal"):
            run("x = [1, 2]\nx.nonexistent()")


class TestConstMustBeInitialized:
    def test_pakko_without_value(self):
        with pytest.raises(LikhaiJeGhalti):
            run("pakko adad x")
