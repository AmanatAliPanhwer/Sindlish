"""
Golden bytecode harness (issue #31, item 3.1).

Compiles representative programs through the full pipeline (lex → parse →
resolve → compile) and asserts the exact ``(opcode.name, arg)`` listing.
Args are normalized to a stable, comparable form so goldens do not depend
on object identity or enum reprs.

Adding an opcode, changing an instruction's operand shape, or reordering
emission will turn these tests red — exactly as intended. See
`book/src/compiler.md` for the bytecode snapshot pointer.
"""

import pytest

from interpreter.analysis.resolver import Resolver
from interpreter.backend.compiler import Compiler
from interpreter.frontend.lexer import Lexer
from interpreter.frontend.parser import Parser
from interpreter.frontend.tokens import TokenType
from interpreter.objects import SdFunction


def _norm(arg):
    """Reduce an operand to a comparable form."""
    if isinstance(arg, tuple):
        return tuple(_norm(x) for x in arg)
    if isinstance(arg, list):
        return [_norm(x) for x in arg]
    if isinstance(arg, TokenType):
        return ("token", arg.name)
    if arg is None or isinstance(arg, int):
        return arg
    return repr(arg)


def compile_instructions(code):
    """Compile ``code`` and return ``((OpCode, arg), ...)`` with raw operands."""
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens, code)
    ast = parser.parse()

    resolver = Resolver(code)
    resolver.resolve(ast)

    compiler = Compiler(code)
    instructions, _constants, _line_col_map = compiler.compile(ast)
    return tuple(instructions)


def compile_listing(code):
    """Compile ``code`` and return ``((opcode.name, normalized_arg), ...)``."""
    return tuple(
        (op.name, _norm(arg)) for op, arg in compile_instructions(code)
    )


def compile_program(code):
    """Compile ``code`` and return ``(ast, instructions, constants)``."""
    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens, code)
    ast = parser.parse()

    resolver = Resolver(code)
    resolver.resolve(ast)

    compiler = Compiler(code)
    instructions, constants, _line_col_map = compiler.compile(ast)
    return ast, instructions, constants


PROGRAMS = [
    (
        "arithmetic_precedence",
        "x = 2 + 3 * 4 - 5",
        (
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("LOAD_CONST", 2),
            ("BINARY_MUL", None),
            ("BINARY_ADD", None),
            ("LOAD_CONST", 3),
            ("BINARY_SUB", None),
            ("STORE_GLOBAL", (4, False, None, None)),
            ("HALT", None),
        ),
    ),
    (
        "agar_yawari_warna",
        'x = 5\nagar x > 5 {\n    likh("big")\n} yawari x > 3 {\n    '
        'likh("mid")\n} warna {\n    likh("small")\n}',
        (
            ("LOAD_CONST", 0),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("LOAD_GLOBAL", 1),
            ("LOAD_CONST", 0),
            ("COMPARE_GT", None),
            ("JUMP_IF_FALSE", 10),
            ("LOAD_CONST", 2),
            ("CALL_FUNCTION", (3, 1, False)),
            ("POP_TOP", None),
            ("JUMP_ABSOLUTE", 21),
            ("LOAD_GLOBAL", 1),
            ("LOAD_CONST", 4),
            ("COMPARE_GT", None),
            ("JUMP_IF_FALSE", 18),
            ("LOAD_CONST", 5),
            ("CALL_FUNCTION", (3, 1, False)),
            ("POP_TOP", None),
            ("JUMP_ABSOLUTE", 21),
            ("LOAD_CONST", 6),
            ("CALL_FUNCTION", (3, 1, False)),
            ("POP_TOP", None),
            ("HALT", None),
        ),
    ),
    (
        "jistain_backward_jump",
        "n = 3\njistain n > 0 {\n    n = n - 1\n}",
        (
            ("LOAD_CONST", 0),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("LOAD_GLOBAL", 1),
            ("LOAD_CONST", 2),
            ("COMPARE_GT", None),
            ("JUMP_IF_FALSE", 11),
            ("LOAD_GLOBAL", 1),
            ("LOAD_CONST", 3),
            ("BINARY_SUB", None),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("JUMP_ABSOLUTE", 2),
            ("HALT", None),
        ),
    ),
    (
        "har_loop",
        "jama = 0\nhar i mein range(1, 6) {\n    jama = jama + i\n}",
        (
            ("LOAD_CONST", 0),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("LOAD_CONST", 2),
            ("LOAD_CONST", 3),
            ("CALL_FUNCTION", (4, 2, False)),
            ("GET_ITER", None),
            ("FOR_ITER", 13),
            ("STORE_GLOBAL", (5, False, None, None)),
            ("LOAD_GLOBAL", 1),
            ("LOAD_GLOBAL", 5),
            ("BINARY_ADD", None),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("JUMP_ABSOLUTE", 6),
            ("HALT", None),
        ),
    ),
    (
        "function_def_and_call",
        "kaam fact(n) {\n    agar n <= 1 {\n        wapas 1\n    }\n"
        "    wapas n * fact(n - 1)\n}\nx = fact(5)",
        (
            ("LOAD_CONST", 2),
            ("MAKE_FUNCTION", 0),
            ("STORE_GLOBAL", 1),
            ("LOAD_CONST", 3),
            ("CALL_FUNCTION", (1, 1, False)),
            ("STORE_GLOBAL", (4, False, None, None)),
            ("HALT", None),
        ),
    ),
    (
        "closure_capture_bahari",
        "kaam shuru() {\n    ginti = 0\n    kaam wadhao() {\n        "
        "bahari ginti\n        ginti = ginti + 1\n    }\n    wadhao()\n"
        "    wapas ginti\n}\nx = shuru()",
        (
            ("LOAD_CONST", 4),
            ("MAKE_FUNCTION", 0),
            ("STORE_GLOBAL", 5),
            ("CALL_FUNCTION", (5, 0, False)),
            ("STORE_GLOBAL", (6, False, None, None)),
            ("HALT", None),
        ),
    ),
    (
        "typed_collections",
        'fehrist[adad] a = [1, 2, 3]\nlughat[lafz, adad] b = {"ek": 1}\n'
        "majmuo[adad] c = {1, 2}",
        (
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("LOAD_CONST", 2),
            ("BUILD_LIST", 3),
            ("STORE_GLOBAL", (3, False, ("token", "FEHRIST"), ("token", "ADAD"))),
            ("LOAD_CONST", 4),
            ("LOAD_CONST", 0),
            ("BUILD_DICT", 1),
            (
                "STORE_GLOBAL",
                (
                    5,
                    False,
                    ("token", "LUGHAT"),
                    [("token", "LAFZ"), ("token", "ADAD")],
                ),
            ),
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("BUILD_SET", 2),
            ("STORE_GLOBAL", (6, False, ("token", "MAJMUO"), ("token", "ADAD"))),
            ("HALT", None),
        ),
    ),
    (
        "result_ops",
        "kaam vind(a, b) {\n    wapas a / b\n}\nr = vind(5, 0)\n"
        'x = r.bachao(0)\nagar r.ghalti {\n    likh("failed")\n}\n'
        "dahai q = vind(8, 0)?\nz = vind(4, 2).lazmi(0)",
        (
            ("LOAD_CONST", 0),
            ("MAKE_FUNCTION", 0),
            ("STORE_GLOBAL", 1),
            ("LOAD_CONST", 2),
            ("LOAD_CONST", 3),
            ("CALL_FUNCTION", (1, 2, False)),
            ("STORE_GLOBAL", (4, False, None, None)),
            ("LOAD_GLOBAL", 4),
            ("LOAD_CONST", 3),
            ("CALL_BACHAO", None),
            ("STORE_GLOBAL", (5, False, None, None)),
            ("LOAD_GLOBAL", 4),
            ("GET_ATTR", 6),
            ("JUMP_IF_FALSE", 17),
            ("LOAD_CONST", 7),
            ("CALL_FUNCTION", (8, 1, False)),
            ("POP_TOP", None),
            ("LOAD_CONST", 9),
            ("LOAD_CONST", 3),
            ("CALL_FUNCTION", (1, 2, False)),
            ("POSTFIX_QMARK", None),
            ("STORE_GLOBAL", (10, False, ("token", "DAHAI"), None)),
            ("LOAD_CONST", 11),
            ("LOAD_CONST", 12),
            ("CALL_FUNCTION", (1, 2, False)),
            ("LOAD_CONST", 3),
            ("CALL_LAZMI", None),
            ("STORE_GLOBAL", (13, False, None, None)),
            ("HALT", None),
        ),
    ),
    (
        "collection_builds",
        'a = [1, 2, 3]\nb = {"x": 1, "y": 2}\nc = {1, 2, 3}\na[1] = 9',
        (
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("LOAD_CONST", 2),
            ("BUILD_LIST", 3),
            ("STORE_GLOBAL", (3, False, None, None)),
            ("LOAD_CONST", 4),
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 5),
            ("LOAD_CONST", 1),
            ("BUILD_DICT", 2),
            ("STORE_GLOBAL", (6, False, None, None)),
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("LOAD_CONST", 2),
            ("BUILD_SET", 3),
            ("STORE_GLOBAL", (7, False, None, None)),
            ("LOAD_GLOBAL", 3),
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 8),
            ("STORE_SUBSCRIPT", None),
            ("HALT", None),
        ),
    ),
    (
        "casts",
        'x = lafz(42)\ny = adad("42")',
        (
            ("LOAD_CONST", 0),
            ("TYPECAST", ("token", "LAFZ")),
            ("STORE_GLOBAL", (1, False, None, None)),
            ("LOAD_CONST", 2),
            ("TYPECAST", ("token", "ADAD")),
            ("STORE_GLOBAL", (3, False, None, None)),
            ("HALT", None),
        ),
    ),
(
        "method_call",
        'd = {"a": 1}\nz = d.hasil("a")',
        (
            ("LOAD_CONST", 0),
            ("LOAD_CONST", 1),
            ("BUILD_DICT", 1),
            ("STORE_GLOBAL", (2, False, None, None)),
            ("LOAD_GLOBAL", 2),
            ("LOAD_CONST", 0),
            ("CALL_METHOD", (3, 1, False)),
            ("STORE_GLOBAL", (4, False, None, None)),
            ("HALT", None),
        ),
    ),
]


@pytest.mark.parametrize("name,source,expected", PROGRAMS, ids=[p[0] for p in PROGRAMS])
def test_golden_bytecode_listing(name, source, expected):
    assert compile_listing(source) == expected


def _sdfunction_constants(constants):
    return [c for c in constants if isinstance(c, SdFunction)]


def test_function_constant_emits_return_without_make_ok():
    # ``fact``'s body: recursive fn with an explicit ``wapas`` (RETURN_VALUE)
    # and an implicit trailing expression (RETURN_VALUE) -- no MAKE_OK on the
    # return path; the implicit bare return is PUSH_NULL + RETURN_VALUE.
    _ast, _instructions, constants = compile_program(
        "kaam fact(n) {\n    agar n <= 1 {\n        wapas 1\n    }\n"
        "    wapas n * fact(n - 1)\n}\nx = fact(5)"
    )
    fact = next(f for f in _sdfunction_constants(constants) if f.name == "fact")
    assert [(op.name, arg) for op, arg in fact.instructions] == [
        ("LOAD_FAST", 0),
        ("LOAD_CONST", 0),
        ("COMPARE_LE", None),
        ("JUMP_IF_FALSE", 6),
        ("LOAD_CONST", 0),
        ("RETURN_VALUE", None),
        ("LOAD_FAST", 0),
        ("LOAD_FAST", 0),
        ("LOAD_CONST", 0),
        ("BINARY_SUB", None),
        ("CALL_FUNCTION", (1, 1, False)),
        ("BINARY_MUL", None),
        ("RETURN_VALUE", None),
        ("PUSH_NULL", None),
        ("RETURN_VALUE", None),
    ]
    assert "MAKE_OK" not in [op.name for op, arg in fact.instructions]


def test_function_constant_bare_wapas_is_push_null_return():
    # A bare ``wapas`` returns khali: PUSH_NULL + RETURN_VALUE, no MAKE_OK.
    _ast, _instructions, constants = compile_program(
        "kaam nada() {\n    wapas\n}\nnada()"
    )
    nada = next(f for f in _sdfunction_constants(constants) if f.name == "nada")
    assert [(op.name, arg) for op, arg in nada.instructions] == [
        ("PUSH_NULL", None),
        ("RETURN_VALUE", None),
        ("PUSH_NULL", None),
        ("RETURN_VALUE", None),
    ]
    assert "MAKE_OK" not in [op.name for op, arg in nada.instructions]