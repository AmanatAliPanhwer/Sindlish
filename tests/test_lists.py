"""Tests for list literals, indexing, and typed lists."""

from tests.helpers import run
import pytest


class TestListLiteral:
    def test_empty_list(self):
        interp, _ = run("x = []")
        assert interp.variables["x"]["value"] == []

    def test_int_list(self):
        interp, _ = run("x = [1, 2, 3]")
        assert interp.variables["x"]["value"] == [1, 2, 3]

    def test_string_list(self):
        interp, _ = run('x = ["a", "b", "c"]')
        assert interp.variables["x"]["value"] == ["a", "b", "c"]

    def test_mixed_list(self):
        interp, _ = run('x = [1, "two", 3]')
        assert interp.variables["x"]["value"] == [1, "two", 3]


class TestListIndexing:
    def test_first_element(self):
        _, out = run("x = [10, 20, 30]\nlikh(x[0])")
        assert out.strip() == "10"

    def test_last_element(self):
        _, out = run("x = [10, 20, 30]\nlikh(x[2])")
        assert out.strip() == "30"

    def test_negative_index(self):
        _, out = run("x = [10, 20, 30]\nlikh(x[-1])")
        assert out.strip() == "30"


class TestTypedList:
    def test_typed_list_adad(self):
        interp, _ = run("fehrist[adad] x = [1, 2, 3]")
        assert interp.variables["x"]["value"] == [1, 2, 3]

    def test_typed_list_rejects_wrong_type(self):
        with pytest.raises(TypeError):
            run('fehrist[adad] x = [1, "two", 3]')


class TestListAssignment:
    def test_index_assignment(self):
        interp, _ = run("x = [1, 2, 3]\nx[0] = 99")
        assert interp.variables["x"]["value"] == [99, 2, 3]
