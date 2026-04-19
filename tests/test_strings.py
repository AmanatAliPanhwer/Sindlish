"""Tests for string literals, escape sequences, and multiline strings."""

from tests.helpers import run


class TestStringLiterals:
    def test_double_quoted(self):
        interp, _ = run('x = "hello"')
        assert interp.variables["x"]["value"] == "hello"

    def test_single_quoted(self):
        interp, _ = run("x = 'hello'")
        assert interp.variables["x"]["value"] == "hello"

    def test_empty_string(self):
        interp, _ = run('x = ""')
        assert interp.variables["x"]["value"] == ""

    def test_string_with_spaces(self):
        interp, _ = run('x = "hello world"')
        assert interp.variables["x"]["value"] == "hello world"


class TestStringConcatenation:
    def test_concat(self):
        interp, _ = run('x = "hello" + " " + "world"')
        assert interp.variables["x"]["value"] == "hello world"


class TestEscapeSequences:
    def test_newline(self):
        interp, _ = run('x = "a\\nb"')
        assert interp.variables["x"]["value"] == "a\nb"

    def test_tab(self):
        interp, _ = run('x = "a\\tb"')
        assert interp.variables["x"]["value"] == "a\tb"


class TestMultilineStrings:
    def test_triple_double_quote(self):
        code = 'x = """line1\nline2\nline3"""'
        interp, _ = run(code)
        assert "line1" in interp.variables["x"]["value"]
        assert "line2" in interp.variables["x"]["value"]
