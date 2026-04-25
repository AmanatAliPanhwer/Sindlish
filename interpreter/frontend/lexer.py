"""
Lexer (tokenizer) for the Sindlish language.

Converts raw source code into a flat list of Token objects.
Uses a dispatch-table approach for single-character tokens and
dedicated methods for multi-character / complex tokens.
"""

import codecs
from .tokens import Token, TokenType
from .keywords import KEYWORDS
from ..errors import LikhaiJeGhalti


# ── Single-character token dispatch table ───────────────────────
_SINGLE_CHAR_TOKENS: dict[str, TokenType] = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "%": TokenType.MOD,
    "^": TokenType.POW,
    "?": TokenType.QMARK,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
}

# Characters that START a potential multi-char operator
_COMPOUND_STARTERS = frozenset("*/><=!")


class Lexer:
    """
    Tokenizer for Sindlish source code.

    Scans source left-to-right, producing a list of Tokens.
    Tracks line and column for accurate error reporting.
    """

    __slots__ = ('code', 'pos', 'line', 'column')

    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    # ── Character access ────────────────────────────────────────

    def _peek(self) -> str | None:
        """Return current character without consuming it."""
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None

    def _peek_ahead(self) -> str | None:
        """Return the character after current without consuming."""
        if self.pos + 1 < len(self.code):
            return self.code[self.pos + 1]
        return None

    def _advance(self) -> str:
        """Consume and return current character, updating position."""
        char = self._peek()
        self.pos += 1
        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    # ── Complex token scanners ──────────────────────────────────

    def _scan_number(self) -> Token:
        """Scan an integer or float literal."""
        num = ""
        dot_count = 0
        start_col = self.column

        while self._peek() and (self._peek().isdigit() or self._peek() == "."):
            if self._peek() == ".":
                if dot_count == 1:
                    break
                dot_count += 1
            num += self._advance()

        if dot_count == 0:
            return Token(TokenType.ADAD, int(num), self.line, self.column)
        else:
            return Token(TokenType.DAHAI, float(num), self.line, self.column)

    def _scan_string(self) -> Token:
        """Scan a single-line or triple-quoted string literal."""
        quote = self._advance()
        start_col = self.column
        start_line = self.line

        # Check for triple-quote
        is_multiline = False
        if self._peek() == quote and self._peek_ahead() == quote:
            self._advance()
            self._advance()
            is_multiline = True

        string_content = ""

        while self._peek() is not None:
            # Triple-quote end
            if (
                self._peek() == quote
                and self.pos + 2 < len(self.code)
                and self.code[self.pos + 1] == quote
                and self.code[self.pos + 2] == quote
            ):
                self._advance()
                self._advance()
                self._advance()
                break
            else:
                # Single-quote end
                if self._peek() == quote:
                    self._advance()
                    break

            # Escape sequences
            if self._peek() == "\\":
                string_content += self._advance()
                if self._peek() is not None:
                    string_content += self._advance()
                continue

            string_content += self._advance()

        try:
            final_string = codecs.decode(string_content, "unicode_escape")
        except UnicodeDecodeError:
            final_string = string_content

        return Token(TokenType.LAFZ, final_string, start_line, start_col)

    def _scan_identifier(self) -> Token:
        """Scan an identifier or keyword."""
        ident = ""
        start_col = self.column

        while self._peek() and (self._peek().isalnum() or self._peek() == "_"):
            ident += self._advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, self.line, start_col)

    def _skip_line_comment(self) -> None:
        """Skip a single-line comment (# ...)."""
        while self._peek() is not None and self._peek() != "\n":
            self._advance()

    def _skip_block_comment(self) -> None:
        """Skip a block comment (/* ... */)."""
        while self._peek() is not None:
            if self._peek() == "*" and self._peek_ahead() == "/":
                self._advance()  # *
                self._advance()  # /
                break
            self._advance()

    def _scan_compound_operator(self, char: str) -> Token:
        """
        Scan operators that may be 1 or 2 characters.

        Handles:  * **  / /*  > >=  < <=  = ==  ! != !!
        """
        line, col = self.line, self.column
        next_char = self._peek_ahead()

        if char == "*":
            if next_char == "*":
                self._advance()
                self._advance()
                return Token(TokenType.DBLSTAR, "**", line, col)
            self._advance()
            return Token(TokenType.MUL, "*", line, col)

        if char == "/":
            if next_char == "*":
                self._advance()
                self._advance()
                self._skip_block_comment()
                return None  # Signal: no token produced
            self._advance()
            return Token(TokenType.DIV, "/", line, col)

        if char == ">":
            if next_char == "=":
                self._advance()
                self._advance()
                return Token(TokenType.GTEQ, ">=", line, col)
            self._advance()
            return Token(TokenType.GT, ">", line, col)

        if char == "<":
            if next_char == "=":
                self._advance()
                self._advance()
                return Token(TokenType.LTEQ, "<=", line, col)
            self._advance()
            return Token(TokenType.LT, "<", line, col)

        if char == "=":
            if next_char == "=":
                self._advance()
                self._advance()
                return Token(TokenType.EQEQ, "==", line, col)
            self._advance()
            return Token(TokenType.EQ, "=", line, col)

        if char == "!":
            if next_char == "=":
                self._advance()
                self._advance()
                return Token(TokenType.NOTEQ, "!=", line, col)
            if next_char == "!":
                self._advance()
                self._advance()
                return Token(TokenType.BANGBANG, "!!", line, col)
            self._advance()
            return Token(TokenType.NOT, "!", line, col)

        # Should never reach here
        raise LikhaiJeGhalti(f"Illegal akhar {char}.", line, col, self.code)

    # ── Main tokenization entry point ───────────────────────────

    def generate_tokens(self) -> list[Token]:
        """
        Tokenize the entire source code.

        Returns a list of Token objects, ending with an EOF token.
        """
        tokens: list[Token] = []

        while self.pos < len(self.code):
            char = self._peek()

            # ── Whitespace ──
            if char in " \t":
                self._advance()
                continue

            # ── Newline ──
            if char == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, self.column))
                self._advance()
                continue

            # ── Numbers ──
            if char.isdigit() or (
                char == "." and self._peek_ahead() and self._peek_ahead().isdigit()
            ):
                tokens.append(self._scan_number())
                continue

            # ── Line comments ──
            if char == "#":
                self._skip_line_comment()
                continue

            # ── Strings ──
            if char in ('"', "'"):
                tokens.append(self._scan_string())
                continue

            # ── Identifiers / Keywords ──
            if char.isalpha() or char == "_":
                tokens.append(self._scan_identifier())
                continue

            # ── Compound operators (multi-char) ──
            if char in _COMPOUND_STARTERS:
                token = self._scan_compound_operator(char)
                if token is not None:
                    tokens.append(token)
                continue

            # ── Single-character tokens (dispatch table) ──
            token_type = _SINGLE_CHAR_TOKENS.get(char)
            if token_type is not None:
                tokens.append(Token(token_type, char, self.line, self.column))
                self._advance()
                continue

            # ── Unknown character ──
            raise LikhaiJeGhalti(f"Illegal akhar {char}.", self.line, self.column, self.code)

        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens
