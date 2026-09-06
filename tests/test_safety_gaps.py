"""Closed safety-gap tests for the error philosophy (issue #33 follow-up).

Each test pins a gap that used to misbehave (silently pass, hang, or leak a
raw Python message) and now lands in the correct error class via the
end-to-end interface (``tests.conftest.run``).
"""

import pytest

from interpreter.backend.vm import VM
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
        with pytest.raises(MatalabJeGhalti, match=r"(?i)dobara"):
            run("kaam f(a) { wapas a }\nf(a=1, a=2)")

    def test_duplicate_keyword_via_kwargs_dict_raises_arity_error(self):
        with pytest.raises(MatalabJeGhalti, match=r"(?i)dobara"):
            run('kaam f(a) { wapas a }\nf(a=1, **{"a": 2})')

    def test_unique_kwargs_dict_still_works(self):
        _, out = run('kaam f(a) { wapas a }\nlikh(f(**{"a": 5}))')
        assert out.strip() == "5"


class TestSilsiloArguments:
    @pytest.mark.parametrize(
        "code",
        [
            "silsilo('a', 'b')",
            "silsilo(1, 'b')",
            "silsilo(1, 2, 'c')",
        ],
    )
    def test_non_numeric_argument_is_clean_type_error(self, code):
        with pytest.raises(QisamJeGhalti, match=r"(?i)adad"):
            run(code)

    @pytest.mark.parametrize(
        "code",
        [
            "silsilo(1.5, 5)",
            "silsilo(1, 2.9, 1)",
            "silsilo(1, 5, 0.5)",
        ],
    )
    def test_decimal_argument_is_rejected_not_truncated(self, code):
        with pytest.raises(QisamJeGhalti, match=r"(?i)adad"):
            run(code)

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

    def test_error_parcel_passes_through_wadha(self):
        _, out = run("fehrist[adad] x = [1]\nx.wadha(1 / 0)\nlikh(x[1])")
        assert "Zero (0)" in out

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

    def test_max_allowed_depth_still_runs(self):
        n = VM.MAX_FRAME_DEPTH - 2
        code = (
            "kaam d(n) { agar n < 1 { wapas 0 } wapas d(n - 1) }\n"
            f"likh(d({n}))"
        )
        _, out = run(code)
        assert out.strip() == "0"

    def test_first_depth_beyond_cap_raises(self):
        n = VM.MAX_FRAME_DEPTH - 1
        code = (
            "kaam d(n) { agar n < 1 { wapas 0 } wapas d(n - 1) }\n"
            f"d({n})"
        )
        with pytest.raises(HalndeVaktGhalti, match="hadd"):
            run(code)