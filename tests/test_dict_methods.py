"""Tests for dictionary method calls."""

from tests.conftest import run, extract_value


class TestHasil:
    """get"""

    def test_hasil_existing_key(self):
        interp, _ = run('x = {"a": 1}\nval = x.hasil("a")')
        assert extract_value(interp.variables["val"]["value"]) == 1

    def test_hasil_missing_key_default(self):
        interp, _ = run('x = {"a": 1}\nval = x.hasil("z", 0)')
        assert extract_value(interp.variables["val"]["value"]) == 0

    def test_hasil_missing_key_none(self):
        interp, _ = run('x = {"a": 1}\nval = x.hasil("z")')
        assert extract_value(interp.variables["val"]["value"]) is None


class TestCabeyon:
    """keys"""

    def test_cabeyon(self):
        interp, _ = run('x = {"a": 1, "b": 2}\nval = x.cabeyon()')
        assert sorted(extract_value(interp.variables["val"]["value"])) == ["a", "b"]


class TestRaqamon:
    """values"""

    def test_raqamon(self):
        interp, _ = run('x = {"a": 1, "b": 2}\nval = x.raqamon()')
        assert sorted(extract_value(interp.variables["val"]["value"])) == [1, 2]


class TestSyon:
    """items"""

    def test_syon(self):
        interp, _ = run('x = {"a": 1}\nval = x.syon()')
        assert extract_value(interp.variables["val"]["value"]) == [["a", 1]]


class TestUpdate:
    """update"""

    def test_update_adds_keys(self):
        interp, _ = run('x = {"a": 1}\nx.update({"b": 2})')
        assert extract_value(interp.variables["x"]["value"]) == {"a": 1, "b": 2}

    def test_update_overwrites(self):
        interp, _ = run('x = {"a": 1}\nx.update({"a": 99})')
        assert extract_value(interp.variables["x"]["value"]) == {"a": 99}


class TestDictKadh:
    """pop"""

    def test_kadh_removes_key(self):
        interp, _ = run('x = {"a": 1, "b": 2}\nval = x.kadh("a")')
        assert extract_value(interp.variables["val"]["value"]) == 1
        assert "a" not in extract_value(interp.variables["x"]["value"])


class TestSyonkadh:
    """popitem"""

    def test_syonkadh(self):
        interp, _ = run('x = {"a": 1}\nval = x.syonkadh()')
        assert extract_value(interp.variables["x"]["value"]) == {}


class TestDefaultrakh:
    """setdefault"""

    def test_defaultrakh_new_key(self):
        interp, _ = run('x = {"a": 1}\nx.defaultrakh("b", 2)')
        assert extract_value(interp.variables["x"]["value"]) == {"a": 1, "b": 2}

    def test_defaultrakh_existing_key(self):
        interp, _ = run('x = {"a": 1}\nx.defaultrakh("a", 99)')
        assert extract_value(interp.variables["x"]["value"]) == {"a": 1}


class TestDictNakal:
    """copy"""

    def test_nakal_copies(self):
        interp, _ = run('x = {"a": 1}\ny = x.nakal()')
        assert extract_value(interp.variables["y"]["value"]) == {"a": 1}


class TestDictSaf:
    """clear"""

    def test_saf_clears(self):
        interp, _ = run('x = {"a": 1, "b": 2}\nx.saf()')
        assert extract_value(interp.variables["x"]["value"]) == {}
