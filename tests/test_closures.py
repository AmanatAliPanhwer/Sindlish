"""
Closure and bahari (nonlocal) tests.

Closures use shared cells: a local captured by an inner function becomes a
Cell, and inner functions read/write through it by reference.
"""

import pytest

from interpreter.errors import HalndeVaktGhalti, QisamJeGhalti, SindhiBaseError
from tests.conftest import run


def _run_expect_error(code):
    with pytest.raises(SindhiBaseError) as exc_info:
        run(code)
    return str(exc_info.value)


class TestClosures:
    def test_make_adder(self):
        _, out = run("""
kaam banao(n) {
    kaam wadho(x) {
        wapas x + n
    }
    wapas wadho
}
das = banao(10)
vis = banao(20)
likh(das(5))
likh(vis(5))
""")
        assert out.split() == ["15", "25"]

    def test_counter_with_bahari(self):
        _, out = run("""
kaam shuru() {
    ginti = 0
    kaam wadhao() {
        bahari ginti
        ginti = ginti + 1
        wapas ginti
    }
    wapas wadhao
}
c = shuru()
likh(c())
likh(c())
likh(c())
""")
        assert out.split() == ["1", "2", "3"]

    def test_read_without_bahari(self):
        _, out = run("""
kaam banao(msg) {
    kaam chhapo() {
        likh(msg)
    }
    chhapo()
}
banao("salam")
""")
        assert "salam" in out

    def test_cell_survives_frame_death(self):
        _, out = run("""
kaam banao() {
    x = 41
    kaam barhao() {
        bahari x
        x = x + 1
        wapas x
    }
    wapas barhao
}
f = banao()
likh(f())
likh(f())
""")
        assert out.split() == ["42", "43"]

    def test_two_closures_share_cell(self):
        _, out = run("""
kaam shuru() {
    balans = 100
    kaam wadhao(rakam) {
        bahari balans
        balans = balans + rakam
        wapas balans
    }
    kaam ghat(rakam) {
        bahari balans
        balans = balans - rakam
        wapas balans
    }
    wapas [wadhao, ghat]
}
pair = shuru()
wadhao = pair[0]
ghat = pair[1]
likh(wadhao(50))
likh(ghat(30))
likh(wadhao(5))
""")
        assert out.split() == ["150", "120", "125"]

    def test_grandparent_capture(self):
        _, out = run("""
kaam bahirli() {
    x = 10
    kaam darmiyani() {
        kaam andarli() {
            wapas x * 2
        }
        wapas andarli
    }
    wapas darmiyani
}
f = bahirli()()
likh(f())
""")
        assert "20" in out

    def test_independent_cells_per_call(self):
        _, out = run("""
kaam banao() {
    n = 0
    kaam barhao() {
        bahari n
        n = n + 1
        wapas n
    }
    wapas barhao
}
pehrio = banao()
biji = banao()
pehrio()
pehrio()
likh(pehrio())
likh(biji())
""")
        assert out.split() == ["3", "1"]

    def test_bahari_write_visible_in_owner(self):
        _, out = run("""
kaam shuru() {
    natijo = 0
    kaam hisaab() {
        bahari natijo
        natijo = 6 * 7
    }
    hisaab()
    likh(natijo)
}
shuru()
""")
        assert "42" in out


class TestBahariErrors:
    def test_bahari_unknown_name(self):
        err = _run_expect_error("""
kaam f() {
    bahari majood_natho
}
f()
""")
        assert "majood_natho" in err

    def test_bahari_at_program_level(self):
        err = _run_expect_error("bahari x")
        assert "bahari" in err and ("kaam" in err or "andar" in err)

    def test_assign_outer_without_bahari(self):
        err = _run_expect_error("""
kaam bahar() {
    x = 0
    kaam andar() {
        x = 5
    }
}
""")
        assert "bahari x" in err

    def test_global_still_works_inside_functions(self):
        _, out = run("""
shumar = 0
kaam wadho() {
    aalmi shumar
    shumar = shumar + 5
}
wadho()
wadho()
likh(shumar)
""")
        assert "10" in out


class TestCellEnforcement:
    """Cells carry const/type metadata; empty cells cannot be read."""

    def test_typed_cell_write_with_matching_type_ok(self):
        _, out = run("""
kaam f() {
    adad x = 10
    kaam g() {
        bahari x
        x = 20
    }
    g()
    likh(x)
}
f()
""")
        assert "20" in out

    def test_const_cell_write_in_inner_raises(self):
        with pytest.raises(HalndeVaktGhalti):
            run("""
kaam f() {
    pakko adad x = 10
    kaam g() {
        bahari x
        x = 20
    }
    g()
}
f()
""")

    def test_const_cell_owner_write_after_capture_raises(self):
        with pytest.raises(HalndeVaktGhalti):
            run("""
kaam f() {
    pakko adad x = 10
    kaam g() {
        bahari x
        wapas x
    }
    h = g()
    x = 20
}
f()
""")

    def test_typed_cell_wrong_type_write_in_inner_raises(self):
        with pytest.raises(QisamJeGhalti):
            run("""
kaam f() {
    adad x = 10
    kaam g() {
        bahari x
        x = "na"
    }
    g()
}
f()
""")

    def test_empty_cell_read_raises(self):
        with pytest.raises(HalndeVaktGhalti):
            run("""
kaam f(fa) {
    agar fa {
        x = 42
    }
    kaam g() {
        bahari x
        wapas x
    }
    wapas g
}
h = f(koorh)
likh(h())
""")


class TestResultBoundaries:
    """Function returns unwrap Ok; inspection methods treat raw values as success."""

    def test_arithmetic_on_call_result(self):
        # Latent bug: before return-unwrap, stored call results stayed boxed
        _, out = run("""
kaam fact(n) {
    agar n <= 1 { wapas 1 }
    wapas n * fact(n - 1)
}
x = fact(5)
likh(x + 1)
""")
        assert "121" in out

    def test_bachao_on_success_value(self):
        _, out = run("""
kaam theek() { wapas 7 }
n = theek()
likh(n.bachao(0))
""")
        assert "7" in out

    def test_ok_on_raw_value(self):
        _, out = run("""
kaam do() { wapas 3 }
n = do()
agar n.ok() { likh("sach") } warna { likh("ghalt") }
""")
        assert "sach" in out

    def test_err_still_propagates_through_return(self):
        _, out = run("""
kaam kharab() {
    wapas 10 / 0
}
n = kharab()
agar n.ghalti() { likh("pakdo") } warna { likh("natho") }
""")
        assert "pakdo" in out


class TestLocalCalleeCalls:
    """Calling a function stored in a function-local variable (issue #30 2.6).

    Named calls must route locals through CALL_VALUE instead of a globals-only
    name lookup, or `h = banao(); h()` fails with 'Nalo h na milyo.'
    """

    def test_call_function_local_by_name(self):
        _, out = run("""
kaam banao() {
    kaam f() { wapas 7 }
    wapas f
}
kaam g() {
    h = banao()
    wapas h()
}
likh(g())
""")
        assert "7" in out

    def test_call_local_callee_with_arguments(self):
        _, out = run("""
kaam wadho(a, b) {
    wapas a + b
}
kaam g() {
    fn = wadho
    wapas fn(2, 3)
}
likh(g())
""")
        assert "5" in out

    def test_call_captured_callee_from_inner_function(self):
        _, out = run("""
kaam banao() {
    kaam f() { wapas 9 }
    wapas f
}
kaam p() {
    h = banao()
    kaam q() {
        wapas h()
    }
    wapas q
}
likh(p()())
""")
        assert "9" in out

    def test_chained_call_of_local_factory(self):
        _, out = run("""
kaam banao() {
    kaam f() { wapas 11 }
    wapas f
}
kaam g() {
    mk = banao
    h = mk()
    wapas h()
}
likh(g())
""")
        assert "11" in out
