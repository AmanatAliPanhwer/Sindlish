"""
Token definitions for the Sindlish language.

Defines the TokenType enum (all lexical categories) and the Token
dataclass representing a single lexical unit with its position.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """
    All token categories in the Sindlish language.

    Organized into: data types, keywords, operators, and symbols.
    """

    # ── Data Types ──────────────────────────────────────────────
    ADAD = auto()       # INT
    LAFZ = auto()       # STRING
    DAHAI = auto()      # FLOAT
    FAISLO = auto()     # BOOL
    SACH = auto()       # TRUE
    KOORE = auto()      # FALSE
    KHALI = auto()      # NULL
    PAKKO = auto()      # CONST
    FEHRIST = auto()    # LIST
    LUGHAT = auto()     # DICT
    MAJMUO = auto()     # SET
    KAAM = auto()       # FUNCTION
    IDENTIFIER = auto()

    # ── Keywords ────────────────────────────────────────────────
    AGAR = auto()       # IF
    YAWARI = auto()     # ELSE IF
    WARNA = auto()      # ELSE
    LIKH = auto()       # PRINT
    JISTAIN = auto()    # WHILE
    BAHARI = auto()     # NONLOCAL
    AALMI = auto()      # GLOBAL
    WAPAS = auto()      # RETURN
    MATCH = auto()      # MATCH
    OK = auto()         # OK (Result)
    GHALTI = auto()     # PANIC or ERROR (Result)
    KHARABI = auto()    # Deprecated PANIC
    HAR = auto()        # FOR
    TOR = auto()        # BREAK
    JARI = auto()       # CONTINUE
    MEIN = auto()       # IN

    # ── Operators ───────────────────────────────────────────────
    PLUS = auto()       # +
    MINUS = auto()      # -
    MUL = auto()        # *
    DIV = auto()        # /
    MOD = auto()        # %
    POW = auto()        # ^
    GT = auto()         # >
    LT = auto()         # <
    EQ = auto()         # =
    EQEQ = auto()      # ==
    NOTEQ = auto()      # !=
    GTEQ = auto()       # >=
    LTEQ = auto()       # <=
    AND = auto()        # aen
    OR = auto()         # ya
    NOT = auto()        # nah / !
    QMARK = auto()      # ?
    BANGBANG = auto()   # !!
    DBLSTAR = auto()    # ** (kwargs)

    # ── Symbols ─────────────────────────────────────────────────
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    COLON = auto()      # :
    COMMA = auto()      # ,
    DOT = auto()        # .
    NEWLINE = auto()    # \n
    EOF = auto()        # End of file


@dataclass(frozen=True, slots=True)
class Token:
    """
    A single lexical token produced by the Lexer.

    Attributes:
        type:   The category of this token (a TokenType value).
        value:  The literal value carried by the token.
        line:   1-based line number in source code.
        column: 1-based column number in source code.
    """
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"{self.type.name}({self.value!r})"
