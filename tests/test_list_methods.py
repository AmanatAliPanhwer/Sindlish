"""Tests for list method calls."""

from tests.conftest import run, extract_value


class TestWadha:
    """append"""

    def test_wadha_adds_element(self):
        interp, _ = run("x = [1, 2]\nx.wadha(3)")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2, 3]

    def test_wadha_string(self):
        interp, _ = run('x = ["a"]\nx.wadha("b")')
        assert extract_value(interp.variables["x"]["value"]) == ["a", "b"]


class TestWadhayo:
    """extend"""

    def test_wadhayo_extends(self):
        interp, _ = run("x = [1, 2]\nx.wadhayo([3, 4])")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2, 3, 4]


class TestWajh:
    """insert"""

    def test_wajh_at_beginning(self):
        interp, _ = run("x = [2, 3]\nx.wajh(0, 1)")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2, 3]

    def test_wajh_at_middle(self):
        interp, _ = run("x = [1, 3]\nx.wajh(1, 2)")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2, 3]


class TestHata:
    """remove"""

    def test_hata_removes_value(self):
        interp, _ = run("x = [1, 2, 3]\nx.hata(2)")
        assert extract_value(interp.variables["x"]["value"]) == [1, 3]


class TestKadh:
    """pop"""

    def test_kadh_last(self):
        interp, _ = run("x = [1, 2, 3]\nval = x.kadh()")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2]
        assert extract_value(interp.variables["val"]["value"]) == 3

    def test_kadh_by_index(self):
        interp, _ = run("x = [1, 2, 3]\nval = x.kadh(0)")
        assert extract_value(interp.variables["x"]["value"]) == [2, 3]
        assert extract_value(interp.variables["val"]["value"]) == 1


class TestTarteeb:
    """sort"""

    def test_tarteeb_sorts(self):
        interp, _ = run("x = [3, 1, 2]\nx.tarteeb()")
        assert extract_value(interp.variables["x"]["value"]) == [1, 2, 3]


class TestUlto:
    """reverse"""

    def test_ulto_reverses(self):
        interp, _ = run("x = [1, 2, 3]\nx.ulto()")
        assert extract_value(interp.variables["x"]["value"]) == [3, 2, 1]


class TestGarn:
    """count"""

    def test_garn_counts(self):
        interp, _ = run("x = [1, 2, 2, 3]\nval = x.garn(2)")
        assert extract_value(interp.variables["val"]["value"]) == 2

    def test_garn_zero(self):
        interp, _ = run("x = [1, 2, 3]\nval = x.garn(99)")
        assert extract_value(interp.variables["val"]["value"]) == 0


class TestIndex:
    """index"""

    def test_index_finds(self):
        interp, _ = run("x = [10, 20, 30]\nval = x.index(20)")
        assert extract_value(interp.variables["val"]["value"]) == 1


class TestNakal:
    """copy"""

    def test_nakal_copies(self):
        interp, _ = run("x = [1, 2, 3]\ny = x.nakal()")
        assert extract_value(interp.variables["y"]["value"]) == [1, 2, 3]


class TestSaf:
    """clear"""

    def test_saf_clears(self):
        interp, _ = run("x = [1, 2, 3]\nx.saf()")
        assert extract_value(interp.variables["x"]["value"]) == []
