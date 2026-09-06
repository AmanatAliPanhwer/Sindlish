"""Closed safety-gap tests for the error philosophy (issue #33 follow-up).

Each test pins a gap that used to misbehave (silently pass, hang, or leak a
raw Python message) and now lands in the correct error class via the
end-to-end interface (``tests.conftest.run``).
"""

import pytest

from interpreter.errors import (
    HalndeVaktGhalti,
    MatalabJeGhalti,
    QisamJeGhalti,
    TarteebJeGhalti,
)
from tests.conftest import run


class TestTopLevelReturn:
    def test_return_outside_function_is_structure_error(self):
        with pytest.raises(TarteebJeGhalti, match="wapas"):
            run("wapas 5")


class TestDuplicateKeyword:
    def test_duplicate_keyword_argument_raises_arity_error(self):
        with pytest.raises(MatalabJeGhalti, match="(?i)dobara"):
            run("kaam f(a) { wapas a }\nf(a=1, a=2)")


class TestSilsiloArguments:
    def test_non_numeric_argument_is_clean_type_error(self):
        with pytest.raises(QisamJeGhalti, match="(?i)adad"):
            run("silsilo('a', 'b')")

    def test_numeric_arguments_still_build_range(self):
        _, out = run("likh(silsilo(1, 5, 2))")
        assert "silsilo(1, 5, 2)" in out


class TestTypedElementChecks:
    def test_wadha_rejects_wrong_element_type(self):
        with pytest.raises(QisamJeGhalti, match="elements"):
            run("fehrist[adad] x = [1]\nx.wadha('str')")

    def test_wajh_rejects_wrong_element_type(self):
        with pytest.raises(QisamJeGhalti, match="elements"):
            run("fehrist[adad] x = [1]\nx.wajh(0, 'str')")

    def test_subscript_assign_rejects_wrong_element_type(self):
        with pytest.raises(QisamJeGhalti, match="elements"):
            run("fehrist[adad] x = [1]\nx[0] = 'str'")

    def test_right_type_wadha_still_works(self):
        _, out = run("fehrist[adad] x = [1]\nx.wadha(2)\nlikh(x)")
        assert out.strip() == "[1, 2]"

    def test_untyped_list_accepts_anything(self):
        _, out = run('x = [1]\nx.wadha("str")\nlikh(x)')
        assert out.strip() == "[1, str]"


class TestRecursionDepth:
    def test_runaway_recursion_raises_depth_error(self):
        with pytest.raises(HalndeVaktGhalti, match="hadd"):
            run("kaam rec(a) { rec(a) }\nrec(0)")

    def test_deep_bounded_recursion_still_runs(self):
        code = (
            "kaam d(n) { agar n < 1 { wapas 0 } wapas d(n - 1) }\n"
            "likh(d(9000))"
        )
        _, out = run(code)
        assert out.strip() == "0"