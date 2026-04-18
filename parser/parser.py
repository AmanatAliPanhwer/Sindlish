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
    
    def skip_newlines(self):
        while self.peek() and self.peek().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self):
        statements = []

        while self.peek() and self.peek().type != TokenType.EOF:
            
            if self.peek().type == TokenType.NEWLINE:
                self.advance()
                continue

            stmt = self.parse_statement()
            statements.append(stmt)

        return ProgramNode(statements)
    
    def parse_block(self):
        statements = []

        while True:
            token = self.peek()

            if token.type == TokenType.NEWLINE:
                self.advance()
                continue

            if token.type in (TokenType.EOF, TokenType.WARNA):
                break

            if token.type == TokenType.RBRACE:
                self.advance() # }
                break

            statements.append(self.parse_statement())

        return statements
    
    def parse_statement(self):
        token = self.peek()

        if token.type == TokenType.LIKH:
            return self.parse_print()
        
        if token.type == TokenType.AGAR:
            return self.parse_if()
        
        if token.type == TokenType.JISTAIN:
            return self.parse_while()
        
        if token.type == TokenType.IDENTIFIER:
            return self.parse_assignment()
        
        raise Exception(f"Unexpected token {token}")
    
    def parse_print(self):
        self.advance() # likh

        self.advance() # (

        expr = self.parse_expression()

        self.advance() # )

        return PrintNode(expr)
    
    def parse_if(self):
        self.advance() # agar

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise Exception("Expected '{' after condition")
        self.advance() # {

        body = self.parse_block()

        self.skip_newlines()

        else_body = None

        if self.peek().type == TokenType.WARNA:
            self.advance() # warna
            if self.peek().type != TokenType.LBRACE:
                raise Exception("Expected '{' after condition")
            self.advance() # {

            else_body = self.parse_block()

        return IfNode(condition, body, else_body)

    def parse_expression(self):
        return self.parse_comparison()
    
    def parse_primary(self):
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
        
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.advance() # )
            return expr

        raise Exception(f"Unexpected token `{token}`") 
    
    def parse_assignment(self):
        name = self.advance().value # variable name

        self.advance() # =

        value = self.parse_expression()

        return AssignNode(name, value)
    
    def parse_while(self):
        self.advance() # jistain

        condition = self.parse_expression()

        self.advance() # {

        body = self.parse_block()
        
        return WhileNode(condition, body)
    
    def parse_comparison(self):
        left = self.parse_term()

        while self.peek().type in (TokenType.GT, TokenType.LT):
            op = self.advance()
            right = self.parse_term()
            left = BinaryOpNode(left, op, right)

        return left
    
    def parse_term(self):
        left = self.parse_factor()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_factor(self):
        left = self.parse_power()

        while self.peek().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.advance()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right)

        return left
    
    def parse_power(self):
        left = self.parse_unary()

        if self.peek().type == TokenType.POW:
            op = self.advance()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right)

        return left
    
    def parse_unary(self):
        if self.peek().type == TokenType.MINUS:
            op = self.advance()
            value = self.parse_unary()
            return BinaryOpNode(NumberNode(0), op, value)
        
        return self.parse_primary()
    