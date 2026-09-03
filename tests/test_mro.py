"""MRO linearization tests (issue #32, items 4.1-4.3).

Covers ``SdType._compute_mro`` / ``_c3_merge`` directly: nothing in the
language creates types with bases yet (``jamaat`` classes will), so these
tests build small type hierarchies by hand to pin down the C3 contract:

- the class itself linearizes first (``mro[0] is self``);
- a diamond ``D(B, C)`` with ``B(A)`` and ``C(A)`` linearizes to
  ``(D, B, C, A)`` and descendant overrides win;
- an inconsistent hierarchy raised the same error Python does.
"""

import pytest

from interpreter.frontend.tokens import TokenType
from interpreter.objects.base import SdType


def _type(name, bases=()):
    ty = SdType(name, TokenType.ADAD)
    ty.bases = bases
    return ty


def from_a(obj, args):
    return "A.hello"


def from_b(obj, args):
    return "B.hello"


class TestLinearization:
    def test_class_without_bases_is_its_own_mro(self):
        a = _type("A")
        assert a.mro == (a,)

    def test_single_inheritance_sits_after_ancestor(self):
        a = _type("A")
        b = _type("B", (a,))
        assert b.mro == (b, a)
        assert b.mro[0] is b

    def test_diamond_linearizes_to_d_b_c_a(self):
        a = _type("A")
        b = _type("B", (a,))
        c = _type("C", (a,))
        d = _type("D", (b, c))
        assert d.mro == (d, b, c, a)
        assert d.mro[0] is d


class TestOverride:
    def test_descendant_method_wins_over_ancestor(self):
        a = _type("A")
        a.register_method("hello", from_a)
        b = _type("B", (a,))
        b.register_method("hello", from_b)
        assert b.lookup_method("hello") is from_b

    def test_diamond_picks_first_definition_in_mro(self):
        a = _type("A")
        a.register_method("hello", from_a)
        b = _type("B", (a,))
        b.register_method("hello", from_b)
        c = _type("C", (a,))
        d = _type("D", (b, c))
        assert d.lookup_method("hello") is from_b


class TestInconsistentHierarchy:
    def test_stuck_merge_raises_type_error(self):
        f = _type("F")
        g = _type("G")
        fa = _type("FA", (f, g))
        ga = _type("GA", (g, f))
        ha = _type("HA", (fa, ga))
        with pytest.raises(TypeError, match="consistent method resolution"):
            _ = ha.mro

    def test_error_is_lazy_until_first_mro_access(self):
        f = _type("F")
        g = _type("G")
        fa = _type("FA", (f, g))
        ga = _type("GA", (g, f))
        ha = _type("HA", (fa, ga))
        with pytest.raises(TypeError, match="consistent method resolution"):
            _ = ha.mro
