"""Tests for arithmetic operations."""

from tests.conftest import run, extract_value


class TestAddition:
    def test_integer_addition(self):
        interp, _ = run("x = 2 + 3")
        assert extract_value(interp.variables["x"]["value"]) == 5

    def test_float_addition(self):
        interp, _ = run("x = 1.5 + 2.5")
        assert extract_value(interp.variables["x"]["value"]) == 4.0

    def test_multiple_additions(self):
        interp, _ = run("x = 1 + 2 + 3 + 4")
        assert extract_value(interp.variables["x"]["value"]) == 10


class TestSubtraction:
    def test_integer_subtraction(self):
        interp, _ = run("x = 10 - 3")
        assert extract_value(interp.variables["x"]["value"]) == 7

    def test_negative_result(self):
        interp, _ = run("x = 3 - 10")
        assert extract_value(interp.variables["x"]["value"]) == -7


class TestMultiplication:
    def test_integer_multiplication(self):
        interp, _ = run("x = 4 * 5")
        assert extract_value(interp.variables["x"]["value"]) == 20

    def test_multiply_by_zero(self):
        interp, _ = run("x = 100 * 0")
        assert extract_value(interp.variables["x"]["value"]) == 0


class TestDivision:
    def test_integer_division(self):
        interp, _ = run("x = 10 / 2")
        assert extract_value(interp.variables["x"]["value"]) == 5.0

    def test_float_division(self):
        interp, _ = run("x = 7 / 2")
        assert extract_value(interp.variables["x"]["value"]) == 3.5


class TestModulo:
    def test_modulo(self):
        interp, _ = run("x = 10 % 3")
        assert extract_value(interp.variables["x"]["value"]) == 1

    def test_modulo_no_remainder(self):
        interp, _ = run("x = 9 % 3")
        assert extract_value(interp.variables["x"]["value"]) == 0


class TestPower:
    def test_power(self):
        interp, _ = run("x = 2 ^ 3")
        assert extract_value(interp.variables["x"]["value"]) == 8

    def test_power_of_zero(self):
        interp, _ = run("x = 5 ^ 0")
        assert extract_value(interp.variables["x"]["value"]) == 1

    def test_power_of_one(self):
        interp, _ = run("x = 7 ^ 1")
        assert extract_value(interp.variables["x"]["value"]) == 7


class TestPrecedence:
    def test_mul_before_add(self):
        interp, _ = run("x = 2 + 3 * 4")
        assert extract_value(interp.variables["x"]["value"]) == 14

    def test_parentheses_override(self):
        interp, _ = run("x = (2 + 3) * 4")
        assert extract_value(interp.variables["x"]["value"]) == 20

    def test_complex_expression(self):
        interp, _ = run("x = 2 + 3 * 4 - 1")
        assert extract_value(interp.variables["x"]["value"]) == 13

    def test_nested_parentheses(self):
        interp, _ = run("x = ((2 + 3) * (4 - 1))")
        assert extract_value(interp.variables["x"]["value"]) == 15


class TestUnaryMinus:
    def test_unary_minus(self):
        interp, _ = run("x = -5")
        assert extract_value(interp.variables["x"]["value"]) == -5

    def test_unary_minus_in_expression(self):
        interp, _ = run("x = 10 + -3")
        assert extract_value(interp.variables["x"]["value"]) == 7
