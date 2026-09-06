"""Contract tests for the error-class taxonomy (issue #33 follow-ups).

Documents the decisions from the error-philosophy audit:

- ``IndexJeGhalti`` is alive: positional out-of-bounds (list/string/range)
  and Python ``IndexError`` laundering land here; a missing dict key stays
  ``QisamJeGhalti`` (a lookup miss, not an index).
- "Method not found" is one class: ``NaleJeGhalti`` everywhere.
- Argument-count mistakes have their own class: ``MatalabJeGhalti`` —
  required-parameter-empty, too-many-positional, unknown keyword, and
  builtin arity. Parse-time *typecast* arity stays ``LikhaiJeGhalti``.
- ``bahari`` misuse is split by what it really is: structure misuse at
  program level -> ``TarteebJeGhalti``; an outer name that does not exist ->
  ``NaleJeGhalti``.
"""

import pytest

from interpreter.errors import (
    IndexJeGhalti,
    MatalabJeGhalti,
    NaleJeGhalti,
    QisamJeGhalti,
    TarteebJeGhalti,
)
from tests.conftest import run


class TestIndexJeGhaltiIsAlive:
    """Positional out-of-bounds is its own class, not a type error."""

    @pytest.mark.parametrize(
        "code",
        [
            "x = [1, 2, 3]\ny = x[9]",
            "x = [1, 2, 3]\ny = x[-9]",
            'y = "abcf"[9]',
            "y = silsilo(3)[7]",
            "x = [1, 2]\ny = x[9]",
            "x = [1, 2]\nx[5] = 9",
        ],
    )
    def test_positional_oob_is_index_error(self, code):
        with pytest.raises(IndexJeGhalti, match="hadd khaan bahar"):
            run(code)

    def test_pop_out_of_range_is_index_error(self):
        with pytest.raises(IndexJeGhalti):
            run("x = [1, 2]\nx.kadh(9)")

    def test_non_numeric_index_stays_type_error(self):
        with pytest.raises(QisamJeGhalti):
            run('x = [1, 2]\ny = x["a"]')

    def test_missing_dict_key_stays_qisam(self):
        # A dict miss is a lookup problem, not a positional index.
        with pytest.raises(QisamJeGhalti, match="na mili"):
            run('x = {1: 2}\ny = x[9]')


class TestMethodNotFoundIsNale:
    """A missing method/attribute is a name problem, one class."""

    @pytest.mark.parametrize(
        "code",
        [
            "x = 5\nx.palwan(0)",
            'x = "lafz"\nx.ghoomjo(1)',
        ],
    )
    def test_missing_method_raises_nale(self, code):
        with pytest.raises(NaleJeGhalti):
            run(code)


class TestMatalabJeGhalti:
    """Argument-count mistakes surface as one dedicated class."""

    @pytest.mark.parametrize(
        "code",
        [
            "kaam f(a, b) { wapas a + b }\nf(1)",  # missing required
            "kaam f(a) { wapas a }\nf(1, 2)",  # too many positional
            "kaam f(a) { wapas a }\nf(b = 1)",  # unknown keyword
            "lambi(1, 2)",  # builtin arity
            "lambi()",
            "silsilo(1, 2, 3, 4)",
            "qisam()",
        ],
    )
    def test_arity_mistakes_raise_matalab(self, code):
        with pytest.raises(MatalabJeGhalti):
            run(code)

    def test_zero_step_is_not_arity(self):
        with pytest.raises(Exception) as exc_info:
            run("silsilo(0, 10, 0)")
        assert not isinstance(exc_info.value, MatalabJeGhalti)

    def test_typecast_arity_is_still_syntax(self):
        # Parser-side typecast arity stays a syntax error.
        with pytest.raises(Exception) as exc_info:
            run("majmuo(1, 2)")
        assert exc_info.value.__class__.__name__ == "LikhaiJeGhalti"


class TestBahariMisuseSplit:
    """The two bahari failures mean two different things."""

    def test_bahari_at_program_level_is_structure(self):
        with pytest.raises(TarteebJeGhalti, match="bahari"):
            run("bahari x")

    def test_bahari_unknown_outer_name_is_name_error(self):
        with pytest.raises(NaleJeGhalti, match="bahari"):
            run("kaam f() { bahari x }")

    def test_closure_write_without_bahari_is_structure(self):
        with pytest.raises(TarteebJeGhalti, match="bahari count"):
            run(
                "kaam outer() {\n"
                "    adad count = 0\n"
                "    kaam inner() { count = 1 }\n"
                "}\n"
                "outer()"
            )