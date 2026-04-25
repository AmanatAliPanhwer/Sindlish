"""Tests for set method calls."""

from tests.conftest import run, extract_value


class TestAddkar:
    """add"""

    def test_addkar(self):
        interp, _ = run("x = {1, 2}\nx.addkar(3)")
        assert 3 in extract_value(interp.variables["x"]["value"])

    def test_addkar_duplicate(self):
        interp, _ = run("x = {1, 2}\nx.addkar(2)")
        assert extract_value(interp.variables["x"]["value"]) == {1, 2}


class TestChad:
    """discard"""

    def test_chad_existing(self):
        interp, _ = run("x = {1, 2, 3}\nx.chad(2)")
        assert extract_value(interp.variables["x"]["value"]) == {1, 3}

    def test_chad_missing_no_error(self):
        interp, _ = run("x = {1, 2}\nx.chad(99)")
        assert extract_value(interp.variables["x"]["value"]) == {1, 2}


class TestSetHata:
    """remove"""

    def test_hata(self):
        interp, _ = run("x = {1, 2, 3}\nx.hata(2)")
        assert extract_value(interp.variables["x"]["value"]) == {1, 3}


class TestBade:
    """union"""

    def test_bade(self):
        interp, _ = run("a = {1, 2}\nb = {2, 3}\nval = a.bade(b)")
        assert extract_value(interp.variables["val"]["value"]) == {1, 2, 3}


class TestMilap:
    """intersection"""

    def test_milap(self):
        interp, _ = run("a = {1, 2, 3}\nb = {2, 3, 4}\nval = a.milap(b)")
        assert extract_value(interp.variables["val"]["value"]) == {2, 3}


class TestFarq:
    """difference"""

    def test_farq(self):
        interp, _ = run("a = {1, 2, 3}\nb = {2, 3, 4}\nval = a.farq(b)")
        assert extract_value(interp.variables["val"]["value"]) == {1}


class TestSymmetricFarq:
    """symmetric_difference"""

    def test_symmetric_farq(self):
        interp, _ = run("a = {1, 2, 3}\nb = {2, 3, 4}\nval = a.symmetric_farq(b)")
        assert extract_value(interp.variables["val"]["value"]) == {1, 4}


class TestNandohisoahe:
    """issubset"""

    def test_subset_true(self):
        interp, _ = run("a = {1, 2}\nb = {1, 2, 3}\nval = a.nandohisoahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is True

    def test_subset_false(self):
        interp, _ = run("a = {1, 2, 4}\nb = {1, 2, 3}\nval = a.nandohisoahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is False


class TestWadohisoahe:
    """issuperset"""

    def test_superset_true(self):
        interp, _ = run("a = {1, 2, 3}\nb = {1, 2}\nval = a.wadohisoahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is True

    def test_superset_false(self):
        interp, _ = run("a = {1, 2}\nb = {1, 2, 3}\nval = a.wadohisoahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is False


class TestAlaghahe:
    """isdisjoint"""

    def test_disjoint_true(self):
        interp, _ = run("a = {1, 2}\nb = {3, 4}\nval = a.alaghahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is True

    def test_disjoint_false(self):
        interp, _ = run("a = {1, 2}\nb = {2, 3}\nval = a.alaghahe(b)")
        assert extract_value(interp.variables["val"]["value"]) is False


class TestSetKadh:
    """pop (no args for set)"""

    def test_kadh_removes_one(self):
        interp, _ = run("x = {1, 2, 3}\nx.kadh()")
        assert len(extract_value(interp.variables["x"]["value"])) == 2


class TestSetUpdate:
    """update"""

    def test_update(self):
        interp, _ = run("x = {1, 2}\nx.update({3, 4})")
        assert extract_value(interp.variables["x"]["value"]) == {1, 2, 3, 4}


class TestSetSaf:
    """clear"""

    def test_saf(self):
        interp, _ = run("x = {1, 2, 3}\nx.saf()")
        assert extract_value(interp.variables["x"]["value"]) == set()
