import re
import codecs
from .tokens import Token, TokenType
from .keywords import KEYWORDS


class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1

    def peek(self) -> str | None:
        if self.pos < len(self.code):
            return self.code[self.pos]
        return None

    def advance(self):
        char = self.peek()
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char
    
    def peek_ahead(self) -> str | None:
        if self.pos + 1 < len(self.code):
            return self.code[self.pos + 1]
        return None

    def make_number(self):
        num = ""
        dot_count = 0
        start_col = self.column
        while self.peek() and (self.peek().isdigit() or self.peek() == "."):
            if self.peek() == ".":
                if dot_count == 1:
                    break
                dot_count += 1
            num += self.advance()

        if dot_count == 0:
            return Token(TokenType.ADAD, int(num), self.line, self.column)
        else:
            return Token(TokenType.DAHAI, float(num), self.line, self.column)

    def make_string(self):
        quote = self.advance()
        start_col = self.column
        start_line = self.line

        is_multiline = False
        if self.peek() == quote and self.peek_ahead() == quote:
            self.advance()
            self.advance()
            is_multiline = True

        string_content = ""

        while self.peek() is not None:
            if self.peek() == quote and self.pos + 2 < len(self.code) and self.code[self.pos+1] == quote and self.code[self.pos+2] == quote:
                self.advance()
                self.advance()
                self.advance()
                break
            else:
                if self.peek() == quote:
                    self.advance()
                    break
            
            if self.peek() == "\\":
                string_content += self.advance()
                if self.peek() is not None:
                    string_content += self.advance()
                continue

            string_content += self.advance()

        try:
            final_string = codecs.decode(string_content, 'unicode_escape')
        except UnicodeDecodeError:
            final_string = string_content
        return Token(TokenType.LAFZ, final_string, start_line, start_col)

    def make_identifier(self):
        ident = ""
        start_col = self.column

        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            ident += self.advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, self.line, start_col)

    def skip_comment(self):
        while self.peek() is not None and self.peek() != "\n":
            self.advance()

    def skip_multiline_comments(self):
        while self.peek() is not None:
            if self.peek() == "*" and self.peek_ahead() == "/":
                self.advance() # *
                self.advance() # /
                break
            self.advance()

    def generate_tokens(self):
        tokens = []

        while self.pos < len(self.code):
            char = self.peek()

            # Skip spaces and NEWLINES
            if char in " \t":
                self.advance()
                continue

            if char == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, self.column))
                self.advance()
                continue

            if char == "{":
                tokens.append(Token(TokenType.LBRACE, "{", self.line, self.column))
                self.advance()
                continue

            if char == "}":
                tokens.append(Token(TokenType.RBRACE, "}", self.line, self.column))
                self.advance()
                continue

            # Numbers
            if char.isdigit() or (char == "." and self.peek_ahead() and self.peek_ahead().isdigit()):
                tokens.append(self.make_number())
                continue

            if char == "#":
                self.skip_comment()
                continue

            # Strings
            if char in ('"', "'"):
                tokens.append(self.make_string())
                continue

            # Identifiers / Keywords
            if char.isalpha() or char == "_":
                tokens.append(self.make_identifier())
                continue

            # Operators
            if char == "+":
                tokens.append(Token(TokenType.PLUS, "+", self.line, self.column))
                self.advance()
                continue

            if char == "-":
                tokens.append(Token(TokenType.MINUS, "-", self.line, self.column))
                self.advance()
                continue

            if char == "*":
                tokens.append(Token(TokenType.MUL, "*", self.line, self.column))
                self.advance()
                continue

            if char == "/":
                if self.peek_ahead() == "*":
                    self.advance()
                    self.advance()
                    self.skip_multiline_comments()
                    continue
                else:
                    tokens.append(Token(TokenType.DIV, "/", self.line, self.column))
                    self.advance()
                    continue

            if char == "%":
                tokens.append(Token(TokenType.MOD, "%", self.line, self.column))
                self.advance()
                continue

            if char == "^":
                tokens.append(Token(TokenType.POW, "^", self.line, self.column))
                self.advance()
                continue

            if char == ">":
                if self.peek_ahead() == "=":
                    tokens.append(Token(TokenType.GTEQ, ">=", self.line, self.column))
                    self.advance()
                    self.advance()
                    continue
                else:
                    tokens.append(Token(TokenType.GT, ">", self.line, self.column))
                    self.advance()
                    continue

            if char == "<":
                if self.peek_ahead() == "=":
                    tokens.append(Token(TokenType.LTEQ, "<=", self.line, self.column))
                    self.advance()
                    self.advance()
                    continue
                else:
                    tokens.append(Token(TokenType.LT, "<", self.line, self.column))
                    self.advance()
                    continue

            if char == "=":
                if self.peek_ahead() == "=":
                    tokens.append(Token(TokenType.EQEQ, "==", self.line, self.column))
                    self.advance()
                    self.advance()
                    continue
                else:
                    tokens.append(Token(TokenType.EQ, "=", self.line, self.column))
                    self.advance()
                    continue

            if char == "!":
                if self.peek_ahead() == "=":
                    tokens.append(Token(TokenType.NOTEQ, "!=", self.line, self.column))
                    self.advance()
                    self.advance()
                    continue
                else:
                    tokens.append(Token(TokenType.NOT, "!", self.line, self.column))
                    self.advance()
                    continue

            if char == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.line, self.column))
                self.advance()
                continue

            if char == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.line, self.column))
                self.advance()
                continue

            if char == ":":
                tokens.append(Token(TokenType.COLON, ":", self.line, self.column))
                self.advance()
                continue

            if char == ",":
                tokens.append(Token(TokenType.COMMA, ",", self.line, self.column))
                self.advance()
                continue

            if char == "[":
                tokens.append(Token(TokenType.LBRACKET, "[", self.line, self.column))
                self.advance()
                continue

            if char == "]":
                tokens.append(Token(TokenType.RBRACKET, "]", self.line, self.column))
                self.advance()
                continue

            if char == ".":
                tokens.append(Token(TokenType.DOT, ".", self.line, self.column))
                self.advance()
                continue

            # Unknown character
            raise Exception(f"Illigal character `{char}` at line {self.line}")

        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens
