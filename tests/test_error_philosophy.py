"""Contract tests for the unified error philosophy (issue #33, Phase 5).

One law per family, sourced from the RFC decision table on #33:

- arithmetic ``+ - * ^ / %``: success returns the raw value; any failure
  returns a Ghalti ``SdResult`` parcel (inspectable via ``.ok``/``.ghalti``,
  consumable via ``?``/``!!``/``.bachao()``/``.lazmi()``).
- comparisons ``< <= > >=``: kind mismatch raises ``QisamJeGhalti`` directly.
- ``== !=``: total booleans; never a parcel, never a raise over kinds.
- strict consumption: using a Ghalti in a further op/condition raises the
  original error class with its creation-site traceback.
- boundaries: function returns/params and typed slots unwrap Ok only; a
  Ghalti survives every boundary.
- discarded statements: an expression statement whose value is a Ghalti
  raises it at the POP_TOP (errors demand acknowledgment).
"""

import pytest

from interpreter.errors import (
    HalndeVaktGhalti,
    QisamJeGhalti,
    ZeroVindJeGhalti,
)
from interpreter.objects import SdNumber, SdResult
from tests.conftest import extract_value, run


class TestArithmeticFamilyContracts:
    """Success is a raw value; every failure is a Ghalti parcel."""

    @pytest.mark.parametrize(
        "expr,expected",
        [
            ("1 + 2", 3),
            ("10 - 3", 7),
            ("4 * 5", 20),
            ("10 / 2", 5.0),
            ("10 % 3", 1),
            ("2 ^ 3", 8),
        ],
    )
    def test_success_returns_raw_value(self, expr, expected):
        interp, _ = run(f"x = {expr}")
        value = interp.variables["x"]["value"]
        assert isinstance(value, SdNumber)
        assert extract_value(value) == expected

    @pytest.mark.parametrize(
        "expr",
        [
            '1 + "a"',
            '10 - "a"',
            '2 * "a"',
            '2 ^ "a"',
            "10 / 0",
            '10 / "a"',
            "10 % 0",
            '10 % "a"',
        ],
    )
    def test_failure_is_ghalti_parcel(self, expr):
        interp, _ = run(f"x = {expr}")
        value = interp.variables["x"]["value"]
        assert isinstance(value, SdResult), f"{expr} should yield a parcel"
        assert value.is_error()
        assert not value.is_ok()

    def test_parcel_inspectable_in_language(self):
        _, out = run('x = 10 / 0\nlikh(x.ok)\nlikh(x.ghalti)')
        assert "koorh" in out
        assert "sach" in out

    def test_parcel_consumable_via_bachao_and_lazmi(self):
        interp, _ = run("x = (10 / 0).bachao(0)")
        assert extract_value(interp.variables["x"]["value"]) == 0
        with pytest.raises(ZeroVindJeGhalti, match="oops"):
            run('x = (10 / 0).lazmi("oops")')

    def test_unary_minus_follows_arithmetic_family(self):
        interp, _ = run('x = -"a"')
        value = interp.variables["x"]["value"]
        assert isinstance(value, SdResult) and value.is_error()


class TestComparisonFamilyContracts:
    """Ordering raises on kind mismatch; equality is total."""

    @pytest.mark.parametrize(
        "expr", ['1 < "a"', '1 <= "a"', '1 > "a"', '1 >= "a"', '"a" < 1']
    )
    def test_ordering_kind_mismatch_raises(self, expr):
        with pytest.raises(QisamJeGhalti):
            run(expr)

    @pytest.mark.parametrize(
        "expr,expected",
        [
            ('1 == "a"', False),
            ('1 != "a"', True),
            ("1 == 1", True),
            ("sach == sach", True),
        ],
    )
    def test_equality_is_total(self, expr, expected):
        interp, _ = run(f"x = {expr}")
        assert extract_value(interp.variables["x"]["value"]) is expected

    def test_ordering_success_is_raw_boolean(self):
        interp, _ = run("x = 3 < 5")
        assert extract_value(interp.variables["x"]["value"]) is True


class TestStrictConsumption:
    """Using a Ghalti in a further operation raises the ORIGINAL class."""

    @pytest.mark.parametrize(
        "expr,error_cls,match",
        [
            ("10 / 0", ZeroVindJeGhalti, "Zero"),
            ("10 % 0", ZeroVindJeGhalti, "Zero"),
            ('10 / "a"', QisamJeGhalti, "vand"),
            ('1 + "a"', QisamJeGhalti, "jore"),
            ('10 % "a"', QisamJeGhalti, "pachi"),
        ],
    )
    def test_error_class_survives_strict_consumption(self, expr, error_cls, match):
        with pytest.raises(error_cls, match=match):
            run(f"x = {expr}\ny = x + 1")

    def test_use_in_condition_raises(self):
        with pytest.raises(ZeroVindJeGhalti):
            run("x = 9 / 0\nagar x { likh('never') }")

    def test_creation_site_traceback_is_kept(self):
        with pytest.raises(ZeroVindJeGhalti) as exc:
            run("kaam bhag(a, b) { wapas a / b }\nr = bhag(9, 0)\ns = r * 2")
        assert any("bhag" in e.context_name for e in exc.value.traceback)


class TestGhaltiAcrossTypedBoundaries:
    """Ghalti is the only Result that survives a boundary; Ok unwraps."""

    def test_ghalti_passes_typed_slot(self):
        # Already fixed in #30; kept here as the family contract.
        interp, _ = run(
            "kaam bhag(adad a, adad b) { dahai r = a / b?\nwapas r }\nval = bhag(9, 0)"
        )
        value = interp.variables["val"]["value"]
        assert isinstance(value, SdResult) and value.is_error()

    def test_ghalti_passes_typed_param_simple(self):
        _, out = run(
            'kaam f(adad x) { likh("got", x.ghalti) }\nr = 9 / 0\nf(r)'
        )
        assert "got sach" in out

    def test_ghalti_passes_typed_param_with_defaults(self):
        _, out = run(
            'kaam f(adad x, adad y = 2) { likh("got", x.ghalti) }\nr = 9 / 0\nf(r)'
        )
        assert "got sach" in out

    def test_ghalti_passes_typed_return(self):
        interp, _ = run(
            "kaam bhag(adad a, adad b) -> dahai { wapas a / b }\nval = bhag(9, 0)"
        )
        value = interp.variables["val"]["value"]
        assert isinstance(value, SdResult) and value.is_error()

    def test_oki_survives_boundary_unwrapped(self):
        interp, _ = run("kaam dabaao() { wapas ok(7) }\nx = dabaao()")
        value = interp.variables["x"]["value"]
        assert isinstance(value, SdNumber)
        assert extract_value(value) == 7


class TestDiscardedErrorStatement:
    """A bare expression statement whose value is a Ghalti raises it."""

    def test_issue33_example_surfaces_at_top_level(self):
        with pytest.raises(ZeroVindJeGhalti, match="Zero"):
            run(
                "kaam bhag(adad a, adad b) {\n"
                "    dahai r = a / b?\n"
                "    wapas r\n"
                "}\n"
                'likh("pre")\n'
                "bhag(9, 0)\n"
                'likh("post")'
            )

    def test_bare_division_statement_raises(self):
        with pytest.raises(ZeroVindJeGhalti, match="Zero"):
            run('likh("pre")\n9 / 0\nlikh("post")')

    def test_bare_error_from_function_raises(self):
        with pytest.raises(HalndeVaktGhalti):
            run('kaam check(adad a) { wapas ghalti("nope") }\ncheck(1)')

    def test_discard_raises_inside_function_body_too(self):
        with pytest.raises(ZeroVindJeGhalti):
            run('kaam f() { 9 / 0\nlikh("never") }\nf()')

    def test_store_print_inspect_stay_quiet(self):
        _, out = run('likh("pre")\nx = 9 / 0\nlikh(x)\nlikh(x.ghalti)\nlikh("post")')
        assert "pre" in out
        assert "Zero (0) saan vand" in out
        assert "sach" in out
        assert "post" in out

    def test_discarded_ok_is_fine(self):
        _, out = run("ok(5)\nlikh('alive')")
        assert "alive" in out

    def test_bare_ghalti_statement_still_panics(self):
        with pytest.raises(HalndeVaktGhalti, match="boom"):
            run('x = 1\nghalti("boom")')


class TestErrorClassNormalization:
    """% (and the latent //) must carry the same classes as / ."""

    def test_mod_zero_carries_zero_vind_je_ghalti(self):
        with pytest.raises(ZeroVindJeGhalti, match="Zero"):
            run("x = 9 % 0\ny = x + 1")

    def test_mod_kind_mismatch_carries_qisam_je_ghalti(self):
        with pytest.raises(QisamJeGhalti, match="pachi"):
            run('x = 9 % "a"\ny = x + 1')