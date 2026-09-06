"""Regression tests for v0.1.2 bug fixes (see roadmap/TODO.md Section 0)."""

import pytest

from interpreter.analysis.resolver import Resolver
from interpreter.errors import (
    HalndeVaktGhalti,
    IndexJeGhalti,
    LikhaiJeGhalti,
    MatalabJeGhalti,
    NaleJeGhalti,
    QisamJeGhalti,
    SindhiBaseError,
)
from interpreter.frontend.lexer import Lexer
from interpreter.frontend.parser import Parser
from interpreter.objects import SdResult
from tests.conftest import extract_value, run


def resolve_only(src: str) -> None:
    """Run only the resolver (static checks, no compilation/execution)."""
    tokens = Lexer(src).generate_tokens()
    ast = Parser(tokens, src).parse()
    Resolver(src).resolve(ast)


class TestPythonScoping:
    """Full Python block scoping: blocks never create a scope.

    A name bound inside a block belongs to the enclosing function (or the
    program globals at top level), so it is visible after the block closes.
    """

    def test_block_bound_name_survives_block_in_function(self):
        _, out = run(
            "kaam demo() { agar sach { z = 10 }\nwapas z }\nlikh(demo())"
        )
        assert "10" in out

    def test_block_bound_name_survives_block_at_top_level(self):
        _, out = run("{ w = 5 }\nlikh(w)")
        assert "5" in out

    def test_loop_iterator_leaks_after_loop(self):
        _, out = run(
            "kaam demo() { har i mein [1, 2, 3] { likh(i) }\nwapas i }\nlikh(demo())"
        )
        assert "3" in out

    def test_loop_iterator_is_global_at_top_level(self):
        _, out = run("har i mein [1, 2, 3, 4, 5] { likh(i) }\nlikh(i)")
        assert "5" in out

    def test_accumulation_still_works_inside_loop(self):
        _, out = run(
            "kaam jama() { m = 0\nhar i mein [1, 2, 3, 4] { m = m + i }\nwapas m }\nlikh(jama())"
        )
        assert "10" in out

    def test_agar_warna_branches_share_scope(self):
        _, out = run(
            "kaam pick(co) { agar co { y = 1 } warna { y = 2 }\nwapas y }\nlikh(pick(koorh))"
        )
        assert "2" in out


class TestScoping:
    def test_function_reads_top_level_variable(self):
        _interp, out = run("x = 42\nkaam foo() { wapas x }\nlikh(foo())")
        assert "42" in out

    def test_function_assigns_to_program_variable(self):
        _, out = run("x = 1\nkaam bump() { x = 99 }\nbump()\nlikh(x)")
        assert "99" in out

    def test_function_as_value(self):
        _, out = run("kaam foo() { wapas 7 }\ng = foo\nlikh(g())")
        assert "7" in out

    def test_recursion_still_works(self):
        interp, _ = run(
            "kaam fact(n) { agar n <= 1 { wapas 1 } wapas n * fact(n - 1) }\nx = fact(5)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 120

    def test_bahari_unknown_name_rejected(self):
        # bahari is supported since closures landed; unknown targets still error
        with pytest.raises(NaleJeGhalti, match="bahari"):
            run("kaam f() { bahari x }")

    def test_undefined_variable_still_raises(self):
        with pytest.raises(NaleJeGhalti):
            run("likh(xyz)")


class TestStrings:
    def test_non_ascii_roundtrip(self):
        interp, _ = run('x = "سلام"')
        assert extract_value(interp.variables["x"]["value"]) == "سلام"

    def test_escapes_decode(self):
        interp, _ = run('x = "a\\tb\\nc"')
        assert extract_value(interp.variables["x"]["value"]) == "a\tb\nc"

    def test_unknown_escape_kept_literally(self):
        interp, _ = run('x = "\\q"')
        assert extract_value(interp.variables["x"]["value"]) == "\\q"

    def test_unterminated_string_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="band"):
            run('x = "oops')

    def test_unterminated_block_comment_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="band"):
            run("/* oops")

    def test_sach_spelling(self):
        _, out = run("likh(sach)")
        assert "sach" in out


class TestParserErrors:
    def test_unclosed_block_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="'}'"):
            run("agar sach { likh(1)")

    def test_chained_comparison_raises(self):
        with pytest.raises(LikhaiJeGhalti, match="Chained"):
            run("x = 1 < 2 < 3")

    def test_match_reserved_with_clear_message(self):
        with pytest.raises(LikhaiJeGhalti, match="match"):
            run("match x { }")


class TestParams:
    def test_default_param_evaluated(self):
        _, out = run(
            'kaam greet(naam = "Dost") { wapas "Salam " + naam }\nlikh(greet())'
        )
        assert "Salam Dost" in out

    def test_typed_default_param(self):
        _, out = run("kaam f(adad a = 5) { wapas a * 2 }\nlikh(f())")
        assert "10" in out

    def test_elem_typed_param_accepts(self):
        """Element-typed params (fehrist[adad] etc.) accept well-typed args."""
        _, out = run("kaam s(fehrist[adad] xs) { wapas xs[0] }\nlikh(s([1, 2, 3]))")
        assert "1" in out

    def test_elem_typed_param_rejects_wrong_element(self):
        with pytest.raises(QisamJeGhalti, match="Fehrist je elements jo qisam 'adad'"):
            run('kaam f(fehrist[adad] xs) { wapas 0 }\nf(["a"])')

    def test_elem_typed_majmuo_param_rejects(self):
        with pytest.raises(QisamJeGhalti, match="Majmuo je elements jo qisam 'adad'"):
            run('kaam f(majmuo[adad] s) { wapas 0 }\nf({1, "x"})')

    def test_elem_typed_lughat_param_rejects_value(self):
        with pytest.raises(QisamJeGhalti, match="Lughat je elements jo qisam 'adad'"):
            run('kaam f(lughat[lafz, adad] d) { wapas 0 }\nf({"a": "x"})')

    def test_elem_typed_lughat_param_rejects_key(self):
        with pytest.raises(QisamJeGhalti, match="Lughat je element jo qisam 'lafz'"):
            run('kaam f(lughat[lafz, adad] d) { wapas 0 }\nf({1: "x"})')

    def test_typed_store_message_names_real_container(self):
        # Original #31/3.6 repro: a typed lughat assignment failure used to say
        # "Fehrist je elements…" regardless of the container. Resolved at
        # store time (resolver.py), so the type names arrive lower-cased.
        with pytest.raises(QisamJeGhalti, match="Lughat je elements jo qisam adad"):
            run('lughat[lafz, adad] ages = {"ali": "x"}')
        with pytest.raises(QisamJeGhalti, match="Majmuo je elements jo qisam adad"):
            run('majmuo[adad] setone = {"x", 1}')
        with pytest.raises(QisamJeGhalti, match="Fehrist je elements jo qisam adad"):
            run("fehrist[adad] ax = [1, 'x']")

    def test_elem_typed_param_default_validated(self):
        _, out = run("kaam f(fehrist[adad] xs = [10]) { wapas xs[0] }\nlikh(f())")
        assert "10" in out

    def test_elem_typed_param_default_rejects_wrong_element(self):
        with pytest.raises(QisamJeGhalti, match="Fehrist"):
            run('kaam f(fehrist[adad] xs = ["bad"]) { wapas 0 }\nlikh(f())')

    def test_colon_form_param_with_element_type(self):
        # `x : fehrist[adad]` (colon form) must fully consume the bracketed
        # element type and enforce it, not leave `[adad]` unconsumed.
        _, out = run("kaam g(x : fehrist[adad]) { wapas x[0] }\nlikh(g([7]))")
        assert "7" in out
        with pytest.raises(QisamJeGhalti, match="Fehrist"):
            run('kaam g(x : fehrist[adad]) { wapas x[0] }\nlikh(g(["a"]))')

    def test_call_site_overrides_default(self):
        _, out = run(
            'kaam greet(naam = "Dost") { wapas "Salam " + naam }\nlikh(greet("Ali"))'
        )
        assert "Salam Ali" in out

    def test_missing_required_param_raises(self):
        with pytest.raises(MatalabJeGhalti, match="lazmi"):
            run("kaam f(a) { wapas a }\nf()")


class TestTruthiness:
    def test_dict_is_truthy(self):
        _, out = run('d = {1: 2}\nagar d { likh("truthy") } warna { likh("falsy") }')
        assert "truthy" in out

    def test_empty_dict_is_falsy(self):
        _, out = run('d = {}\nagar d { likh("t") } warna { likh("f") }')
        assert "f" in out

    def test_set_truthiness(self):
        _, out = run('s = {1}\nagar s { likh("yes") } warna { likh("no") }')
        assert "yes" in out

    def test_empty_list_is_falsy(self):
        _, out = run('l = []\nagar l { likh("t") } warna { likh("f") }')
        assert "f" in out

    def test_nah_on_number_is_logical(self):
        _, out = run("likh(nah 5)")
        assert "koorh" in out

    def test_nah_on_empty_string(self):
        _, out = run('agar nah "" { likh("empty") }')
        assert "empty" in out


class TestShortCircuit:
    def test_and_does_not_evaluate_right_operand(self):
        _, out = run(
            'x = 0\nagar x != 0 aen 10 / x > 1 { likh("boom") } warna { likh("safe") }'
        )
        assert "safe" in out

    def test_or_returns_first_truthy(self):
        interp, _ = run("x = khali ya 5")
        assert extract_value(interp.variables["x"]["value"]) == 5

    def test_or_short_circuits(self):
        _, out = run('x = sach ya 10 / 0\nlikh("alive")')
        assert "alive" in out


class TestResultTyping:
    def test_dahai_accepts_division_result(self):
        interp, _ = run("dahai d = 10 / 2")
        assert extract_value(interp.variables["d"]["value"]) == 5.0

    def test_adad_rejects_division_float(self):
        with pytest.raises(QisamJeGhalti, match="DAHAI"):
            run("adad x = 10 / 2")

    def test_error_results_stay_results(self):
        _interp, out = run(
            'kaam vind(a, b) { wapas a / b }\nr = vind(5, 0)\nagar r.ghalti { likh("failed") }'
        )
        assert "failed" in out

    def test_error_result_propagates_through_typed_slot(self):
        # An Err flowing through `expr?` into an explicitly-typed slot must
        # survive as a value (TODO:57), not raise "RESULT milyo" at the store.
        interp, _ = run(
            "kaam bhag(adad a, adad b) { dahai r = a / b?\nwapas r }\n"
            "val = bhag(9, 0)"
        )
        assert interp.variables["val"]["value"].is_error()

    def test_while_terminates_on_result_condition(self):
        interp, _ = run("n = 2\njistain ok(n > 0) { n = n - 1 }")
        assert extract_value(interp.variables["n"]["value"]) == 0


class TestCallArgs:
    def test_string_args_never_become_kwargs(self):
        interp, _ = run('kaam f(a, b) { wapas a + b }\nx = f("a", "b")')
        assert extract_value(interp.variables["x"]["value"]) == "ab"

    def test_explicit_keyword_arguments(self):
        interp, _ = run("kaam f(a, b) { wapas a - b }\nx = f(b = 2, a = 10)")
        assert extract_value(interp.variables["x"]["value"]) == 8

    def test_star_unpacking(self):
        interp, _ = run(
            "kaam jorr(a, b, c) { wapas a + b + c }\nnums = [10, 20, 30]\nx = jorr(*nums)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 60

    def test_double_star_unpacking(self):
        _, out = run(
            "kaam profile(naamo, umaro) { likh(naamo)\nlikh(umaro) }\n"
            'info = {"naamo": "Ali", "umaro": 25}\nprofile(**info)'
        )
        assert "Ali" in out
        assert "25" in out

    def test_star_param_collects_extras(self):
        interp, _ = run("kaam jama(*hisa) { wapas lambi(hisa) }\nx = jama(1, 2, 3)")
        assert extract_value(interp.variables["x"]["value"]) == 3

    def test_kw_param_collects_extras(self):
        interp, _ = run(
            "kaam f(**baqiyaa) { wapas lambi(baqiyaa) }\nx = f(p = 1, q = 2)"
        )
        assert extract_value(interp.variables["x"]["value"]) == 2

    def test_unknown_kwarg_raises(self):
        with pytest.raises(MatalabJeGhalti, match="Achanak keyword"):
            run("kaam f(a) { wapas a }\nf(b = 1)")

    def test_extra_positional_raises(self):
        with pytest.raises(MatalabJeGhalti, match="wadhoo"):
            run("kaam f(a) { wapas a }\nf(1, 2)")

    def test_builtin_rejects_kwargs(self):
        with pytest.raises(QisamJeGhalti):
            run('likh("x", sep = "-")')


class TestCollectionsAndBuiltins:
    def test_lambi_of_dict(self):
        interp, _ = run("d = {1: 2, 3: 4}\nx = lambi(d)")
        assert extract_value(interp.variables["x"]["value"]) == 2

    def test_majmuo_extra_args_rejected(self):
        with pytest.raises(LikhaiJeGhalti, match="sirf hikro argument"):
            run("majmuo(1, 2)")

    def test_silsilo_zero_step_raises(self):
        with pytest.raises(HalndeVaktGhalti, match="step"):
            run("silsilo(0, 10, 0)")

    def test_set_literal_unhashable_clean_error(self):
        with pytest.raises(QisamJeGhalti, match="hashable"):
            run("s = {[1, 2]}")

    def test_dict_literal_unhashable_key_clean_error(self):
        with pytest.raises(QisamJeGhalti, match="hashable"):
            run("d = {[1]: 2}")


class TestDeclarations:
    def test_redeclared_type_metadata_updates(self):
        interp, _ = run('adad x = 1\nlafz x = "a"')
        assert extract_value(interp.variables["x"]["value"]) == "a"

    def test_pakko_global_enforced(self):
        with pytest.raises(HalndeVaktGhalti, match="pakko"):
            run("pakko x = 1\nx = 2")

    def test_typed_global_reassignment_checked(self):
        with pytest.raises(QisamJeGhalti, match="lafz"):
            run('lafz s = "ok"\ns = 5')

    def test_aalmi_declaration_accepted(self):
        _, out = run("aalmi counter\ncounter = 5\nlikh(counter)")
        assert "5" in out


class TestStaticDictTypes:
    """Resolver statically verifies lughat literal key/value types.

    Mirrors the fehrist/majmuo literal checks so `check`/LSP diagnostics catch
    bad dict literals without executing the program.
    """

    def test_lughat_literal_bad_value_statically_rejected(self):
        with pytest.raises(QisamJeGhalti, match="Lughat"):
            resolve_only('lughat[lafz, adad] ages = {"ali": "x"}')

    def test_lughat_literal_bad_key_statically_rejected(self):
        with pytest.raises(QisamJeGhalti, match="Lughat"):
            resolve_only("lughat[lafz, adad] ages = {1: 'ok'}")

    def test_lughat_literal_valid_passes_static_resolve(self):
        resolve_only('lughat[lafz, adad] ages = {"ali": 30}')

    def test_mixed_lughat_literal_rejects_second_bad_value(self):
        with pytest.raises(QisamJeGhalti, match="Lughat"):
            resolve_only('lughat[lafz, adad] ages = {"ali": 30, "ayo": "x"}')

    def test_untyped_value_defers_to_runtime_check(self):
        # Dynamic (non-literal) values are not provable at resolve time, so the
        # element check on the age entry must defer to runtime, not raise.
        resolve_only('x = 1\ny = x\nlughat[lafz, adad] ages = {"age": y}')

    def test_typed_fehrist_still_checks_elements(self):
        # The element check must fire even when the whole-literal type matches.
        with pytest.raises(QisamJeGhalti, match="Fehrist"):
            resolve_only("fehrist[adad] x = [1, 'a']")

    def test_typed_lughat_with_string_value_raises_clean_error(self):
        with pytest.raises(QisamJeGhalti, match="Qisam natho mile"):
            resolve_only('lughat[lafz, adad] x = "hi"')

    def test_untyped_literal_collection_defers(self):
        # An untyped (element_type is None) fehrist never element-checks.
        resolve_only("fehrist x = [1, 'a']")

    def test_fehrist_decl_wrong_container_literal_clean_error(self):
        # A lughat literal under a fehrist annotation is a container mismatch,
        # not an element problem — and must not crash on DictNode element access.
        with pytest.raises(QisamJeGhalti, match="Qisam natho mile"):
            resolve_only('fehrist[adad] x = {1: "a"}')

    def test_lughat_decl_wrong_container_literal_clean_error(self):
        with pytest.raises(QisamJeGhalti, match="Qisam natho mile"):
            resolve_only("lughat[lafz, adad] d = [1, 2]")


class TestCapturedTypeInference:
    """Captured slot type inference uses the OWNER function's metadata.

    Slot indices restart per function, so resolving a captured outer name
    through the current function's same-index slot metadata would infer the
    wrong type and raise a false QisamJeGhalti.
    """

    def test_captured_outer_slot_uses_owner_metadata(self):
        src = (
            "kaam outer() {\n"
            "    adad n = 10\n"
            "    kaam inner() {\n"
            '        lafz z = "hi"\n'
            "        adad x = n\n"
            "        wapas x\n"
            "    }\n"
            "    wapas inner\n"
            "}\n"
            "likh(outer()())\n"
        )
        _, out = run(src)
        assert "10" in out


class TestCallArgResolution:
    """Keyword, star, and kw-args values resolve like positional arguments."""

    def test_keyword_value_local_reference_resolves(self):
        src = (
            "kaam f(x) { wapas x }\n"
            "kaam g() {\n"
            "    adad v = 42\n"
            "    wapas f(x = v)\n"
            "}\n"
            "likh(g())\n"
        )
        _, out = run(src)
        assert "42" in out

    def test_star_unpack_local_reference_resolves(self):
        src = (
            "kaam f(x) { wapas x }\n"
            "kaam g() {\n"
            "    a = [5]\n"
            "    wapas f(*a)\n"
            "}\n"
            "likh(g())\n"
        )
        _, out = run(src)
        assert "5" in out

    def test_kw_unpack_local_reference_resolves(self):
        src = (
            "kaam f(x) { wapas x }\n"
            "kaam g() {\n"
            '    d = {"x": 7}\n'
            "    wapas f(**d)\n"
            "}\n"
            "likh(g())\n"
        )
        _, out = run(src)
        assert "7" in out


class TestTypeSticks:
    """The first explicit type on a slot sticks (TODO.md:54).

    A typed redeclaration of an already-typed function-local slot must raise
    a clean error at the redeclaration site — never corrupt the outer slot's
    metadata so an earlier line fails at runtime.
    """

    def test_conflicting_typed_redeclaration_raises_at_redeclaration(self):
        src = (
            "kaam test() {\n"
            "  adad x = 1\n"
            "  agar sach {\n"
            '    lafz x = "hi"\n'
            "  }\n"
            "}\n"
            "likh(test())"
        )
        with pytest.raises(QisamJeGhalti) as exc:
            run(src)
        assert exc.value.line == 4

    def test_same_type_redeclaration_in_block_allowed(self):
        interp, _ = run(
            "kaam test() { adad x = 1\nagar sach { adad x = 2 }\nwapas x }\nz = test()"
        )
        assert extract_value(interp.variables["z"]["value"]) == 2

    def test_untyped_slot_can_gain_first_explicit_type(self):
        interp, _ = run(
            "kaam test() { x = 1\nagar sach { adad x = 2 }\nwapas x }\nz = test()"
        )
        assert extract_value(interp.variables["z"]["value"]) == 2

    def test_typed_local_then_different_type_local_line_reported(self):
        src = "kaam f() {\n  adad a = 1\n  dahai a = 2.5\n  wapas a\n}\nlikh(f())"
        with pytest.raises(QisamJeGhalti) as exc:
            run(src)
        assert exc.value.line == 3


class TestFunctionLocalConstraints:
    def test_pakko_enforced_in_function(self):
        with pytest.raises(HalndeVaktGhalti, match="pakko"):
            run("kaam f() { pakko k = 1\nk = 2 }\nf()")

    def test_typed_local_enforced_in_function(self):
        with pytest.raises(QisamJeGhalti, match="lafz"):
            run('kaam f() { lafz s = "ok"\ns = 5 }\nf()')

    def test_pakko_in_block_inside_function(self):
        with pytest.raises(HalndeVaktGhalti, match="pakko"):
            run("kaam f() { agar sach { pakko b = 9\nb = 10 } }\nf()")

    def test_function_metadata_does_not_leak_to_main_frame(self):
        interp, _ = run(
            'adad x = 5\nkaam f() { lafz y = "s"\ny = "t"\nwapas y }\nx = 6'
        )
        assert extract_value(interp.variables["x"]["value"]) == 6


class TestLazysilsilo:
    def test_har_loop_over_silsilo(self):
        interp, _ = run("jama = 0\nhar i mein silsilo(1, 101) { jama = jama + i }")
        assert extract_value(interp.variables["jama"]["value"]) == 5050

    def test_lambi_is_constant_time(self):
        interp, _ = run("x = lambi(silsilo(0, 1000000000, 5))")
        assert extract_value(interp.variables["x"]["value"]) == 200000000

    def test_silsilo_does_not_materialize(self):
        interp, _ = run(
            "x = 0\nhar v mein silsilo(1000000000000, 1000000000010) { x = v }"
        )
        assert extract_value(interp.variables["x"]["value"]) == 1000000000009

    def test_negative_step(self):
        _interp, out = run("r = silsilo(10, 0, -2)\nlikh(r[2])")
        assert "6" in out

    def test_indexing_and_length(self):
        interp, _ = run("r = silsilo(1, 20, 3)\na = r[4]\nb = lambi(r)")
        assert extract_value(interp.variables["a"]["value"]) == 13
        assert extract_value(interp.variables["b"]["value"]) == 7

    def test_str_representation(self):
        _, out = run("likh(silsilo(1, 5, 2))")
        assert "silsilo(1, 5, 2)" in out

    def test_truthiness(self):
        _, out = run(
            'agar silsilo(5, 5) { likh("t") } warna { likh("f") }\nagar silsilo(1) { likh("big") }'
        )
        assert "f" in out
        assert "big" in out

    def test_out_of_bounds_index_raises(self):
        with pytest.raises(IndexJeGhalti, match="bahar"):
            run("r = silsilo(3)\nr[7]")


class TestResultSemantics:
    def test_arithmetic_returns_raw_success(self):
        # Successful arithmetic is a raw value (raw = success); only Err
        # results survive as SdResult. See roadmap/TODO.md on Result boxing.
        interp, _ = run("x = 2 + 3")
        stored = interp.variables["x"]["value"]
        assert not isinstance(stored, SdResult)
        assert extract_value(stored) == 5

    def test_wrapped_results_chain(self):
        interp, out = run("x = 2 + 3\ny = x * 2\nlikh(y)")
        assert extract_value(interp.variables["y"]["value"]) == 10
        assert "10" in out

    def test_type_mismatch_becomes_err(self):
        interp, _ = run('s = "a" + 1')
        stored = interp.variables["s"]["value"]
        assert isinstance(stored, SdResult) and stored.is_error()

    def test_division_by_zero_is_err(self):
        interp, _ = run("r = 10 / 0")
        assert interp.variables["r"]["value"].is_error()

    def test_ghalti_gate(self):
        _, out = run(
            'kaam vind(a, b) { wapas a / b }\nr = vind(5, 0)\nagar r.ghalti { likh("caught") }'
        )
        assert "caught" in out

    def test_bachao_fallback(self):
        _, out = run(
            "kaam vind(a, b) { wapas a / b }\nval = vind(5, 0).bachao(0)\nlikh(val)"
        )
        assert "0" in out

    def test_err_in_operation_raises_strict(self):
        with pytest.raises(SindhiBaseError):
            run("y = (10 / 0) + 1")

    def test_err_in_condition_raises_strict(self):
        with pytest.raises(SindhiBaseError):
            run('agar 10 / 0 { likh("x") }')

    def test_ok_in_condition_unwraps(self):
        _, out = run('agar (2 + 3) > 4 { likh("yes") } warna { likh("no") }')
        assert "yes" in out

    def test_typed_declaration_accepts_wrapped_result(self):
        interp, _ = run("dahai d = 10 / 2")
        assert extract_value(interp.variables["d"]["value"]) == 5.0
