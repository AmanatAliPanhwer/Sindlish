from .tokens import TokenType

KEYWORDS = {
    "agar": TokenType.AGAR,
    "yawari": TokenType.YAWARI,
    "warna": TokenType.WARNA,
    "jistain": TokenType.JISTAIN,
    "aen": TokenType.AND,
    "ya": TokenType.OR,
    "nah": TokenType.NOT,
    "adad": TokenType.ADAD,
    "lafz": TokenType.LAFZ,
    "dahai": TokenType.DAHAI,
    "faislo": TokenType.FAISLO,
    "sach": TokenType.SACH,
    "koorh": TokenType.KOORE,
    "khali": TokenType.KHALI,
    "pakko": TokenType.PAKKO,
    "fehrist": TokenType.FEHRIST,
    "lughat": TokenType.LUGHAT,
    "majmuo": TokenType.MAJMUO,
    "bahari": TokenType.BAHARI,
    "aalmi": TokenType.AALMI
}

DATATYPES = (
    TokenType.ADAD,
    TokenType.LAFZ,
    TokenType.DAHAI,
    TokenType.FAISLO,
    TokenType.KHALI,
    TokenType.FEHRIST,
    TokenType.LUGHAT,
    TokenType.MAJMUO,
)
