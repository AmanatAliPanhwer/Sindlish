from enum import Enum, auto


class TokenType(Enum):
    # Data Types
    ADAD = auto()  # INT
    LAFZ = auto()  # STRING
    DAHAI = auto()  # FLOAT
    FAISLO = auto()  # BOOL
    SACH = auto()  # TRUE
    KOORE = auto()  # FALSE
    KHALI = auto()  # NULL
    PAKKO = auto()  # Const
    FEHRIST = auto()  # LIST
    LUGHAT = auto()  # DICT
    MAJMUO = auto()  # SET
    KAAM = auto()  # FUNCTION
    IDENTIFIER = auto()

    # Keywords
    AGAR = auto()
    YAWARI = auto()
    WARNA = auto()
    LIKH = auto()
    JISTAIN = auto()
    BAHARI = auto()
    AALMI = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    GT = auto()
    LT = auto()
    EQ = auto()
    EQEQ = auto()
    NOTEQ = auto()
    GTEQ = auto()
    LTEQ = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Symbols
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON = auto()
    COMMA = auto()
    NEWLINE = auto()
    EOF = auto()
    DOT = auto()


class Token:
    def __init__(self, type_: TokenType, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.type}({self.value})"
