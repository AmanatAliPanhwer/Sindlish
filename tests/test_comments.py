"""Tests for comments: single-line # and multiline /* */."""

from tests.conftest import run, extract_value


class TestSingleLineComment:
    def test_comment_ignored(self):
        interp, _ = run("# this is a comment\nx = 42")
        assert extract_value(interp.variables["x"]["value"]) == 42

    def test_comment_after_code(self):
        interp, _ = run("x = 10 # assign ten")
        assert extract_value(interp.variables["x"]["value"]) == 10

    def test_multiple_comments(self):
        code = """
# first comment
x = 1
# second comment
y = 2
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["x"]["value"]) == 1
        assert extract_value(interp.variables["y"]["value"]) == 2


class TestMultilineComment:
    def test_multiline_ignored(self):
        code = """
/* this is
a multiline
comment */
x = 99
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["x"]["value"]) == 99

    def test_multiline_between_statements(self):
        code = """
x = 1
/* skip this */
y = 2
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["x"]["value"]) == 1
        assert extract_value(interp.variables["y"]["value"]) == 2

    def test_multiline_with_code_like_content(self):
        code = """
/* likh("should not print")
x = 999 */
x = 42
"""
        interp, _ = run(code)
        assert extract_value(interp.variables["x"]["value"]) == 42
