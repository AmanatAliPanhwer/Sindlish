from .ast_nodes import *
from .tokens import TokenType
from .keywords import DATATYPES


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

    def peek_ahead(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def skip_newlines(self):
        while self.peek() and self.peek().type == TokenType.NEWLINE:
            self.advance()

    def get_default_value_node(self, var_type):
        if var_type == TokenType.ADAD:
            return NumberNode(0)
        if var_type == TokenType.DAHAI:
            return NumberNode(0.0)
        if var_type == TokenType.LAFZ:
            return StringNode("")
        if var_type == TokenType.FAISLO:
            return BoolNode(bool())
        return NullNode()

    def parse(self):
        statements = []

        while self.peek() and self.peek().type != TokenType.EOF:
            self.skip_newlines()
            if self.peek().type == TokenType.EOF:
                break

            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()

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
                self.advance()  # }
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

        if token.type == TokenType.PAKKO or token.type in DATATYPES:
            return self.parse_assignment()

        if token.type == TokenType.IDENTIFIER:
            if self.peek_ahead() and self.peek_ahead().type in (
                TokenType.EQ,
                TokenType.COLON,
            ):
                return self.parse_assignment()
            expr = self.parse_expression()

            if self.peek() and self.peek().type == TokenType.EQ:
                self.advance()  # =
                value_node = self.parse_expression()

                if isinstance(expr, IndexNode):
                    return IndexNode(expr.left, expr.index, value_node)
                else:
                    raise SyntaxError("Syntax Error: Invalid assignment target.")

            return expr

        raise Exception(f"Unexpected token {token} at line {token.line}")

    def parse_print(self):
        self.advance()  # likh
        if self.peek() and self.peek().type == TokenType.LPAREN:
            self.advance()  # (

            if self.peek() and self.peek().type == TokenType.RPAREN:
                self.advance()
                return PrintNode(StringNode(""))

            expr = self.parse_expression()

            if self.peek() and self.peek().type == TokenType.RPAREN:
                self.advance()  # )
                return PrintNode(expr)
            else:
                raise Exception("Expected ')' after print expression")

        if self.peek() and self.peek().type == TokenType.NEWLINE:
            self.advance()
            return PrintNode(StringNode(""))
        expr = self.parse_expression()
        return PrintNode(expr)

    def parse_if(self):
        self.advance()  # agar

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise Exception("Expected '{' after condition")
        self.advance()  # {

        body = self.parse_block()

        self.skip_newlines()

        else_body = None

        if self.peek().type == TokenType.WARNA:
            self.advance()  # warna
            if self.peek().type != TokenType.LBRACE:
                raise Exception("Expected '{' after condition ")
            self.advance()  # {

            else_body = self.parse_block()

        return IfNode(condition, body, else_body)

    def parse_expression(self):
        return self.parse_or()

    def parse_primary(self):
        token = self.peek()

        if token.type == TokenType.ADAD:
            self.advance()
            return NumberNode(token.value)

        if token.type == TokenType.DAHAI:
            self.advance()
            return NumberNode(token.value)

        if token.type == TokenType.LAFZ:
            self.advance()
            return StringNode(token.value)

        if token.type == TokenType.SACH:
            self.advance()
            return BoolNode(True)

        if token.type == TokenType.KOORE:
            self.advance()
            return BoolNode(False)

        if token.type == TokenType.KHALI:
            self.advance()
            return NullNode()

        if token.type == TokenType.LBRACKET:
            return self.parse_list()

        if token.type == TokenType.LBRACE:
            return self.parse_dict_set()

        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            node = VariableNode(name)

            if self.peek() and self.peek().type == TokenType.DOT:
                self.advance()
                method_name = self.advance().value

                if not self.peek() or self.peek().type != TokenType.LPAREN:
                    raise SyntaxError(f"Expected '(' after method {method_name}")

                args = self.parse_call_arguments()
                return MethodCallNode(node, method_name, args)

            if self.peek() and self.peek().type == TokenType.LPAREN:
                args = self.parse_call_arguments()
                return CallNode(name, args)

            if self.peek() and self.peek().type == TokenType.LBRACKET:
                self.advance()  # [
                index = self.parse_expression()
                self.advance()
                return IndexNode(node, index)
            return node

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.advance()  # )
            return expr

        raise Exception(f"Unexpected token `{token}`")

    def parse_assignment(self):
        is_const = False
        _type = None
        element_type = None

        if self.peek().type == TokenType.PAKKO:
            self.advance()
            is_const = True

        if self.peek().type in DATATYPES:
            _type = self.advance().type
            if (
                _type in (TokenType.FEHRIST, TokenType.MAJMUO)
                and self.peek()
                and self.peek().type == TokenType.LBRACKET
            ):
                self.advance()  # [
                if self.peek() and self.peek().type in DATATYPES:
                    element_type = self.advance().type
                else:
                    raise SyntaxError(
                        f"Expected data type inside [] for {'fehrist' if _type == TokenType.FEHRIST else 'majmuo'}"
                    )

                if self.peek() and self.peek().type != TokenType.RBRACKET:
                    raise SyntaxError(
                        f"Expected ']' after {'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} element type"
                    )
                self.advance()  # ]

            if (
                _type == TokenType.LUGHAT
                and self.peek()
                and self.peek().type == TokenType.LBRACKET
            ):
                self.advance()  # [
                if self.peek() and self.peek().type in DATATYPES:
                    key_type = self.advance().type
                    if self.peek().type != TokenType.COMMA:
                        raise SyntaxError("Expected ',' after lughat key type")
                    self.advance()  # ,
                    if self.peek() and self.peek().type in DATATYPES:
                        val_type = self.advance().type
                        element_type = [key_type, val_type]
                if self.peek() and self.peek().type != TokenType.RBRACKET:
                    raise SyntaxError("Expected ']' after lughat element types")
                self.advance()  # ]

        if self.peek().type != TokenType.IDENTIFIER:
            raise SyntaxError(f"Expected variable name, got {self.peek().type.name}")
        name = self.advance().value

        if self.peek().type == TokenType.COLON:
            self.advance()  # :
            if self.peek().type in DATATYPES:
                _type = self.advance().type
                if (
                    _type in (TokenType.FEHRIST, TokenType.MAJMUO)
                    and self.peek()
                    and self.peek().type == TokenType.LBRACKET
                ):
                    self.advance()  # [
                    if self.peek() and self.peek().type in DATATYPES:
                        element_type = self.advance().type
                    else:
                        raise SyntaxError(
                            f"Expected data type inside [] for {'fehrist' if _type == TokenType.FEHRIST else 'majmuo'}"
                        )

                    if self.peek() and self.peek().type != TokenType.RBRACKET:
                        raise SyntaxError(
                            f"Expected ']' after {'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} element type"
                        )
                    self.advance()  # ]

                if (
                    _type == TokenType.LUGHAT
                    and self.peek()
                    and self.peek().type == TokenType.LBRACKET
                ):
                    self.advance()  # [
                    if self.peek() and self.peek().type in DATATYPES:
                        key_type = self.advance().type
                        if self.peek().type != TokenType.COMMA:
                            raise SyntaxError("Expected ',' after lughat key type")
                        self.advance()  # ,
                        if self.peek() and self.peek().type in DATATYPES:
                            val_type = self.advance().type
                            element_type = [key_type, val_type]
                    if self.peek() and self.peek().type != TokenType.RBRACKET:
                        raise SyntaxError("Expected ']' after lughat element types")
                    self.advance()  # ]

        if self.peek() and self.peek().type == TokenType.EQ:
            self.advance()  # =
            value_node = self.parse_expression()
        else:
            if is_const:
                raise SyntaxError(
                    f"Syntax Error: Constant `{name}` must be initialized."
                )

            value_node = self.get_default_value_node(_type)

        return AssignNode(name, value_node, _type, is_const, element_type)

    def parse_while(self):
        self.advance()  # jistain

        condition = self.parse_expression()

        self.advance()  # {

        body = self.parse_block()

        return WhileNode(condition, body)

    def parse_or(self):
        left = self.parse_and()

        while self.peek().type == TokenType.OR:
            op = self.advance()
            right = self.parse_and()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_and(self):
        left = self.parse_not()

        while self.peek().type == TokenType.AND:
            op = self.advance()
            right = self.parse_not()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_not(self):
        if self.peek().type == TokenType.NOT:
            op = self.advance()
            value = self.parse_not()
            return BinaryOpNode(NumberNode(0), op, value)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_term()

        while self.peek().type in (
            TokenType.GT,
            TokenType.LT,
            TokenType.EQEQ,
            TokenType.NOTEQ,
            TokenType.GTEQ,
            TokenType.LTEQ,
        ):
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

    def parse_list(self):
        self.advance()  # [
        elements = []

        if self.peek().type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                elements.append(self.parse_expression())

        if self.peek().type != TokenType.RBRACKET:
            raise SyntaxError("Expected ']' at end of list")
        self.advance()  # ]

        return ListNode(elements)

    def parse_call_arguments(self):
        self.advance()  # (
        args = []
        if self.peek().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                args.append(self.parse_expression())

        if self.peek().type != TokenType.RPAREN:
            raise SyntaxError("Expected ')' after arguments")
        self.advance()  # )
        return args

    def parse_dict_set(self):
        self.advance()  # {

        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.advance()
            return DictNode([])

        first_expr = self.parse_expression()

        if self.peek() and self.peek().type == TokenType.COLON:
            self.advance()  # :
            first_val = self.parse_expression()
            pairs = [(first_expr, first_val)]

            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                key = self.parse_expression()
                if self.peek().type != TokenType.COLON:
                    raise SyntaxError("Lughat error: Expected ':' after key")
                self.advance()
                val = self.parse_expression()
                pairs.append((key, val))

            if self.peek().type != TokenType.RBRACE:
                raise SyntaxError("Expected '}' at end of lughat")
            self.advance()
            return DictNode(pairs)
        else:
            elements = [first_expr]
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                elements.append(self.parse_expression())

            if self.peek().type != TokenType.RBRACE:
                raise SyntaxError("Expected '}' at end of majmuo")
            self.advance()  # }
            return SetNode(elements)
