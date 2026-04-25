"""Tests for variable assignment and dynamic typing."""

from tests.conftest import run, extract_value


class TestBasicAssignment:
    def test_assign_integer(self):
        interp, _ = run("x = 10")
        assert extract_value(interp.variables["x"]["value"]) == 10

    def test_assign_string(self):
        interp, _ = run('x = "hello"')
        assert extract_value(interp.variables["x"]["value"]) == "hello"

    def test_assign_float(self):
        interp, _ = run("x = 3.14")
        assert extract_value(interp.variables["x"]["value"]) == 3.14


class TestReassignment:
    def test_reassign_same_type(self):
        interp, _ = run("x = 1\nx = 2")
        assert extract_value(interp.variables["x"]["value"]) == 2

    def test_reassign_different_type(self):
        interp, _ = run('x = 10\nx = "hello"')
        assert extract_value(interp.variables["x"]["value"]) == "hello"


class TestDynamicTyping:
    def test_int_to_string(self):
        interp, _ = run('x = 42\nx = "text"')
        assert extract_value(interp.variables["x"]["value"]) == "text"

    def test_string_to_int(self):
        interp, _ = run('x = "text"\nx = 42')
        assert extract_value(interp.variables["x"]["value"]) == 42

    def test_int_to_float(self):
        interp, _ = run("x = 5\nx = 5.5")
        assert extract_value(interp.variables["x"]["value"]) == 5.5


class TestMultipleVariables:
    def test_multiple_variables(self):
        interp, _ = run("a = 1\nb = 2\nc = 3")
        assert extract_value(interp.variables["a"]["value"]) == 1
        assert extract_value(interp.variables["b"]["value"]) == 2
        assert extract_value(interp.variables["c"]["value"]) == 3

    def test_variable_in_expression(self):
        interp, _ = run("a = 5\nb = a + 10")
        assert extract_value(interp.variables["b"]["value"]) == 15

    def test_self_referencing_reassignment(self):
        interp, _ = run("x = 5\nx = x + 1")
        assert extract_value(interp.variables["x"]["value"]) == 6
