"""
Keyword and datatype mappings for the Sindlish language.

Maps Sindlish keyword strings to their corresponding TokenType values,
and defines which TokenTypes are considered data-type annotations.
"""

from .tokens import TokenType

# ── Keyword → TokenType lookup ──────────────────────────────────
KEYWORDS: dict[str, TokenType] = {
    "agar":    TokenType.AGAR,
    "yawari":  TokenType.YAWARI,
    "warna":   TokenType.WARNA,
    "jistain": TokenType.JISTAIN,
    "aen":     TokenType.AND,
    "ya":      TokenType.OR,
    "nah":     TokenType.NOT,
    "adad":    TokenType.ADAD,
    "lafz":    TokenType.LAFZ,
    "dahai":   TokenType.DAHAI,
    "faislo":  TokenType.FAISLO,
    "sach":    TokenType.SACH,
    "koorh":   TokenType.KOORE,
    "khali":   TokenType.KHALI,
    "pakko":   TokenType.PAKKO,
    "fehrist": TokenType.FEHRIST,
    "lughat":  TokenType.LUGHAT,
    "majmuo":  TokenType.MAJMUO,
    "bahari":  TokenType.BAHARI,
    "aalmi":   TokenType.AALMI,
    "kaam":    TokenType.KAAM,
    "wapas":   TokenType.WAPAS,
    "match":   TokenType.MATCH,
    "ok":      TokenType.OK,
    "ghalti":  TokenType.GHALTI,
    "kharabi": TokenType.KHARABI,
    "har":     TokenType.HAR,
    "tor":     TokenType.TOR,
    "jari":    TokenType.JARI,
    "mein":    TokenType.MEIN,
}

# ── Data-type TokenTypes (used in type annotations) ─────────────
DATATYPES: tuple[TokenType, ...] = (
    TokenType.ADAD,
    TokenType.LAFZ,
    TokenType.DAHAI,
    TokenType.FAISLO,
    TokenType.KHALI,
    TokenType.FEHRIST,
    TokenType.LUGHAT,
    TokenType.MAJMUO,
)
