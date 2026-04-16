import re
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
    
    def make_number(self):
        num = ""
        start_col = self.column
        while self.peek() and self.peek().isdigit():
            num += self.advance()
        
        return Token(TokenType.NUMBER, int(num), self.line, start_col)
    
    def make_string(self):
        quote = self.advance()
        string = ""
        start_col = self.column

        while self.peek() and self.peek() != quote:
            string += self.advance()
        
        self.advance()

        return Token(TokenType.STRING, string, self.line, start_col)
    
    def make_identifier(self):
        ident = ""
        start_col = self.column

        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            ident += self.advance()

        token_type = KEYWORDS.get(ident, TokenType.IDENTIFIER)
        return Token(token_type, ident, self.line, start_col)

    
    def generate_tokens(self):
        tokens = []
        
        while self.pos < len(self.code):
            char = self.peek()

            # Skip spaces
            if char in " \t":
                self.advance()
                continue
                
            # Newline
            if char == "\n":
                tokens.append(Token(TokenType.NEWLINE, "\\n", self.line, self.column))
                self.advance()
                continue
        
            # Numbers
            if char.isdigit():
                tokens.append(self.make_number())
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
                tokens.append(Token(TokenType.DIV, "/", self.line, self.column))
                self.advance()
                continue

            if char == ">":
                tokens.append(Token(TokenType.GT, ">", self.line, self.column))
                self.advance()
                continue

            if char == "<":
                tokens.append(Token(TokenType.LT, "<", self.line, self.column))
                self.advance()
                continue

            if char == "=":
                tokens.append(Token(TokenType.EQ, "=", self.line, self.column))
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
            
            # Unknown character
            raise Exception(f"Illigal character `{char}` at line {self.line}")
        
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens

