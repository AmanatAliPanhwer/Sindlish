"""
Call binding order (issue #31, item 3.4).

``CallPlan`` (``interpreter/objects/core.py``) precomputes per-call metadata;
the VM's binding loop resolves each parameter as ``kwargs > positional >
defaults``. These tests pin the metadata directly and the ordering
end-to-end through the real call path.
"""

import pytest

from interpreter.errors import LikhaiJeGhalti
from interpreter.frontend.ast_nodes import ParamNode
from interpreter.frontend.tokens import TokenType
from interpreter.objects import SdNumber
from interpreter.objects.core import CallPlan
from interpreter.objects.numbers import ADAD_TYPE
from interpreter.objects.strings import LAFZ_TYPE

from tests.conftest import extract_value, run


def _plan(*params, defaults=(), cell_names=()):
    return CallPlan(list(params), defaults=defaults, cell_names=cell_names)


def _param(name, **kwargs):
    return ParamNode(name=name, **kwargs)


class TestCallPlanMetadata:
    def test_arity_counts_only_non_variadic_params(self):
        plan = _plan(_param("a"), _param("b"), _param("*r", is_star=True),
                     _param("**k", is_kw=True))
        assert plan.arity == 2

    def test_defaults_map_holds_defaulted_values(self):
        plan = _plan(
            _param("a", default=SdNumber(5)),
            _param("b"),
            defaults=(SdNumber(5),),
        )
        assert plan.has_defaults
        assert plan.defaults_map["a"] == SdNumber(5)
        assert "b" not in plan.defaults_map

    def test_known_names_none_when_kw_param_present(self):
        assert _plan(_param("a"), _param("**k", is_kw=True)).known_names is None
        assert _plan(_param("a"), _param("b")).known_names == frozenset({"a", "b"})

    def test_simple_requires_no_defaults_no_cells_no_variadics(self):
        assert _plan(_param("a")).simple
        assert not _plan(_param("a", default=SdNumber(1)), defaults=()).simple
        assert not _plan(_param("a"), cell_names=("a",)).simple
        assert not _plan(_param("*r", is_star=True)).simple
        assert not _plan(
            _param("xs", type=TokenType.FEHRIST, element_type=TokenType.ADAD)
        ).simple

    def test_expected_types_follow_param_types(self):
        plan = _plan(
            _param("n", type=TokenType.ADAD),
            _param("s", type=TokenType.LAFZ),
            _param("x"),
        )
        assert plan.expected_types == (ADAD_TYPE, LAFZ_TYPE, None)


class TestBindingOrder:
    def test_kwargs_take_precedence_over_defaults(self):
        interp, _ = run(
            "kaam f(a = 1, b = 2) { wapas a * 10 + b }\nx = f(b = 9)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 19

    def test_positional_fills_first_then_kwargs_then_defaults(self):
        interp, _ = run(
            "kaam f(a, b, c = 3) { wapas a * 100 + b * 10 + c }\n"
            "x = f(1, 2)\ny = f(1, 2, c = 9)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 123
        assert extract_value(interp.variables["y"]["value"]) == 129

    def test_mixed_positional_and_kwargs(self):
        interp, _ = run(
            "kaam f(a, b, c, d = 4) { wapas a + b + c + d }\n"
            "x = f(1, d = 2, b = 3, c = 10)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 16

    def test_missing_required_argument_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="lazmi aahe"):
            run("kaam f(a, b) { wapas a + b }\nf(1)")

    def test_too_many_positional_arguments_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="wadhoo"):
            run("kaam f(a, b) { wapas a + b }\nf(1, 2, 3)")

    def test_unknown_keyword_argument_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="Achanak keyword"):
            run("kaam f(a) { wapas a }\nf(b = 1)")