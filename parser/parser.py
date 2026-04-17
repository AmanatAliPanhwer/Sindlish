from ast_sind.nodes import  *
from lexer.tokens import TokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def advance(self):
        token = self.peek()
        self.pos += 1
        return token
    
    def parse_statement(self):
        token = self.peek()

        if token.type == TokenType.LIKH:
            return self.parse_print()
        
        if token.type == TokenType.AGAR:
            return self.parse_if()
        
        if token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        
        raise Exception(f"Unexpected token {token}")
    
    def parse(self):
        statements = []

        while self.peek() and self.peek().type != TokenType.EOF:
            
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue

            stmt = self.parse_statement()
            statements.append(stmt)

        return ProgramNode(statements)
    
    def parse_print(self):
        self.advance() # likh

        self.advance() # (

        expr = self.parse_expression()

        self.advance() # )

        return PrintNode(expr)
    
    def parse_if(self):
        self.advance() # agar

        condition = self.parse_expression()

        self.advance() # :

        self.advance() # NEWLINE

        body = []
        
        # Parse If
        while self.peek().type != TokenType.EOF and self.peek().type != TokenType.WARNA:
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue

            body.append(self.parse_statement())

        else_body = []

        if self.peek().type == TokenType.WARNA:
            self.advance() # warna
            self.advance() # :
            self.advance() # NEWLINE

            while self.peek().type != TokenType.EOF:
                if self.peek().type == TokenType.NEWLINE:
                    self.advance()
                    continue

                else_body.append(self.parse_statement())

        return IfNode(condition, body, else_body)

    def parse_expression(self):
        left = self.parse_term()

        while self.peek().type in (TokenType.GT, TokenType.LT):
            op = self.advance()
            right = self.parse_term()

            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_term(self):
        token = self.peek()

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)
        
        if token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value)
        
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return VariableNode(token.value)

        raise Exception(f"Unexpected token `{token}`") 
    
    def parse_assignment(self):
        name = self.advance().value # variable name

        self.advance() # =

        value = self.parse_expression()

        return AssignNode(name, value)
    