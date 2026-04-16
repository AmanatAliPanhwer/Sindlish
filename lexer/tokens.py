from enum import Enum, auto

class TokenType(Enum):

    # Data Types
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords
    AGAR = auto()
    WARNA = auto()
    LIKH = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MUL = auto()
    DIV = auto()
    GT = auto()
    LT = auto()
    EQ = auto()

    # Symbols
    LPAREN = auto()
    RPAREN = auto()
    COLON = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.type}({self.value})"