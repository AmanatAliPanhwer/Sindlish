from .ast_nodes import *
from .tokens import TokenType
from .keywords import DATATYPES
from .errors import LikhaiJeGhalti

class Parser:
    def __init__(self, tokens, code):
        self.tokens = tokens
        self.code = code
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
            return self.parse_print().set_pos(token.line, token.column)

        if token.type == TokenType.AGAR:
            return self.parse_if().set_pos(token.line, token.column)

        if token.type == TokenType.JISTAIN:
            return self.parse_while().set_pos(token.line, token.column)

        if token.type == TokenType.PAKKO or token.type in DATATYPES:
            return self.parse_assignment().set_pos(token.line, token.column)

        if token.type == TokenType.IDENTIFIER:
            if self.peek_ahead() and self.peek_ahead().type in (
                TokenType.EQ,
                TokenType.COLON,
            ):
                return self.parse_assignment().set_pos(token.line, token.column)
            expr = self.parse_expression()

            if self.peek() and self.peek().type == TokenType.EQ:
                self.advance()  # =
                value_node = self.parse_expression()

                if isinstance(expr, IndexNode):
                    return IndexNode(expr.left, expr.index, value_node).set_pos(token.line, token.column)
                else:
                    raise LikhaiJeGhalti("Ghalat assignment target.", token.line, token.column, self.code)

            return expr

        raise LikhaiJeGhalti(f"Achanak {token.value} milyo", token.line, token.column, self.code)

    def parse_print(self):
        token = self.peek()
        self.advance()  # likh
        if self.peek() and self.peek().type == TokenType.LPAREN:
            self.advance()  # (

            if self.peek() and self.peek().type == TokenType.RPAREN:
                self.advance()
                return PrintNode(StringNode("")).set_pos(token.line, token.column)

            expr = self.parse_expression()

            if self.peek() and self.peek().type == TokenType.RPAREN:
                self.advance()  # )
                return PrintNode(expr).set_pos(token.line, token.column)
            else:
                raise LikhaiJeGhalti("likh( khan poe ')' lazmi aahe", token.line, token.column, self.code)

        if self.peek() and self.peek().type == TokenType.NEWLINE:
            self.advance()
            return PrintNode(StringNode("")).set_pos(token.line, token.column)
        expr = self.parse_expression()
        return PrintNode(expr).set_pos(token.line, token.column)

    def parse_if(self):
        token = self.peek()
        self.advance()  # agar

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti("Shart khan poe '{' lazmi aahe", token.line, token.column, self.code)
        self.advance()  # {

        body = self.parse_block()

        self.skip_newlines()

        else_body = None

        if self.peek().type == TokenType.WARNA:
            self.advance()  # warna
            if self.peek().type != TokenType.LBRACE:
                raise LikhaiJeGhalti("Warna khan poe '{' lazmi aahe", self.peek().line, self.peek().column, self.code)
            self.advance()  # {

            else_body = self.parse_block()

        return IfNode(condition, body, else_body).set_pos(token.line, token.column)

    def parse_expression(self):
        return self.parse_or()

    def parse_primary(self):
        token = self.peek()

        if token.type == TokenType.ADAD:
            self.advance()
            return NumberNode(token.value).set_pos(token.line, token.column)

        if token.type == TokenType.DAHAI:
            self.advance()
            return NumberNode(token.value).set_pos(token.line, token.column)

        if token.type == TokenType.LAFZ:
            self.advance()
            return StringNode(token.value).set_pos(token.line, token.column)

        if token.type == TokenType.SACH:
            self.advance()
            return BoolNode(True).set_pos(token.line, token.column)

        if token.type == TokenType.KOORE:
            self.advance()
            return BoolNode(False).set_pos(token.line, token.column)

        if token.type == TokenType.KHALI:
            self.advance()
            return NullNode().set_pos(token.line, token.column)

        if token.type == TokenType.LBRACKET:
            return self.parse_list().set_pos(token.line, token.column)

        if token.type == TokenType.LBRACE:
            return self.parse_dict_set().set_pos(token.line, token.column)

        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            node = VariableNode(name).set_pos(token.line, token.column)

            if self.peek() and self.peek().type == TokenType.DOT:
                self.advance()
                method_name = self.advance().value

                if not self.peek() or self.peek().type != TokenType.LPAREN:
                    raise LikhaiJeGhalti(f"Method {method_name} khan poe '(' lazmi aahe", token.line, token.column, self.code)

                args = self.parse_call_arguments()
                return MethodCallNode(node, method_name, args).set_pos(token.line, token.column)

            if self.peek() and self.peek().type == TokenType.LPAREN:
                args = self.parse_call_arguments()
                return CallNode(name, args).set_pos(token.line, token.column)

            if self.peek() and self.peek().type == TokenType.LBRACKET:
                self.advance()  # [
                index = self.parse_expression().set_pos(token.line, token.column)
                self.advance()
                return IndexNode(node, index).set_pos(token.line, token.column)
            return node

        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression().set_pos(token.line, token.column)
            self.advance()  # )
            return expr

        raise LikhaiJeGhalti(f"Achanak `{token}` milyo", token.line, token.column, self.code)

    def parse_assignment(self):
        is_const = False
        _type = None
        element_type = None
        token = self.peek()

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
                    raise LikhaiJeGhalti(
                        f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} laai [] jhay ander data type jo hovan lazmi aahe",
                        self.peek().line, self.peek().column, self.code
                    )

                if self.peek() and self.peek().type != TokenType.RBRACKET:
                    raise LikhaiJeGhalti(
                        f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} jhay element type khan poe ']' lazmi aahe",
                        self.peek().line, self.peek().column, self.code
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
                        raise LikhaiJeGhalti("Lughat jhay key type khan poe ',' lazmi aahe", self.peek().line, self.peek().column, self.code)
                    self.advance()  # ,
                    if self.peek() and self.peek().type in DATATYPES:
                        val_type = self.advance().type
                        element_type = [key_type, val_type]
                if self.peek() and self.peek().type != TokenType.RBRACKET:
                    raise LikhaiJeGhalti("Lughat jhay element types khan poe ']' lazmi aahe", self.peek().line, self.peek().column, self.code)
                self.advance()  # ]

        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(f"Variable jo naalo khapyo te, par {self.peek().type.name} milyo", self.peek().line, self.peek().column, self.code)
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
                        raise LikhaiJeGhalti(
                            f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} laai [] jhay ander data type jo hovan lazmi aahe",
                            self.peek().line, self.peek().column, self.code
                        )

                    if self.peek() and self.peek().type != TokenType.RBRACKET:
                        raise LikhaiJeGhalti(
                            f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} jhay element type khan poe ']' lazmi aahe",
                            self.peek().line, self.peek().column, self.code
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
                            raise LikhaiJeGhalti("Lughat jhay key type khan poe ',' lazmi aahe", self.peek().line, self.peek().column, self.code)
                        self.advance()  # ,
                        if self.peek() and self.peek().type in DATATYPES:
                            val_type = self.advance().type
                            element_type = [key_type, val_type]
                    if self.peek() and self.peek().type != TokenType.RBRACKET:
                        raise LikhaiJeGhalti("Lughat jhay element types khan poe ']' lazmi aahe", self.peek().line, self.peek().column, self.code)
                    self.advance()  # ]

        if self.peek() and self.peek().type == TokenType.EQ:
            self.advance()  # =
            value_node = self.parse_expression()
        else:
            if is_const:
                raise LikhaiJeGhalti(
                    f"pakkey `{name}` laai qeemat lazmi aahe.",
                    token.line, token.column, self.code
                )

            value_node = self.get_default_value_node(_type)

        return AssignNode(name, value_node, _type, is_const, element_type).set_pos(token.line, token.column)

    def parse_while(self):
        token = self.peek()
        self.advance()  # jistain

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti("Shart khan poe '{' lazmi aahe", token.line, token.column, self.code)
        self.advance()  # {

        body = self.parse_block()

        return WhileNode(condition, body).set_pos(token.line, token.column)

    def parse_or(self):
        left = self.parse_and()

        while self.peek().type == TokenType.OR:
            op = self.advance()
            right = self.parse_and()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_and(self):
        left = self.parse_not()

        while self.peek().type == TokenType.AND:
            op = self.advance()
            right = self.parse_not()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_not(self):
        if self.peek().type == TokenType.NOT:
            op = self.advance()
            value = self.parse_not()
            return BinaryOpNode(NumberNode(0), op, value).set_pos(op.line, op.column)
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
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_term(self):
        left = self.parse_factor()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_factor(self):
        left = self.parse_power()

        while self.peek().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.advance()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_power(self):
        left = self.parse_unary()

        if self.peek().type == TokenType.POW:
            op = self.advance()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_unary(self):
        if self.peek().type == TokenType.MINUS:
            op = self.advance()
            value = self.parse_unary()
            return BinaryOpNode(NumberNode(0), op, value).set_pos(op.line, op.column)

        return self.parse_primary()

    def parse_list(self):
        token = self.peek()
        self.advance()  # [
        elements = []

        if self.peek().type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                elements.append(self.parse_expression())

        if self.peek().type != TokenType.RBRACKET:
            raise LikhaiJeGhalti("Fehrist jhay aakhir mein ']' lazmi aahe", self.peek().line, self.peek().column, self.code)
        self.advance()  # ]

        return ListNode(elements).set_pos(token.line, token.column)

    def parse_call_arguments(self):
        token = self.peek()
        self.advance()  # (
        args = []
        if self.peek().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                args.append(self.parse_expression())

        if self.peek().type != TokenType.RPAREN:
            raise LikhaiJeGhalti("Arguments khan poe ')' lazmi aahe", token.line, token.column, self.code)
        self.advance()  # )
        return args

    def parse_dict_set(self):
        token = self.peek()
        self.advance()  # {

        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.advance()
            return DictNode([]).set_pos(token.line, token.column)

        first_expr = self.parse_expression()

        if self.peek() and self.peek().type == TokenType.COLON:
            self.advance()  # :
            first_val = self.parse_expression()
            pairs = [(first_expr, first_val)]

            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                key = self.parse_expression()
                if self.peek().type != TokenType.COLON:
                    raise LikhaiJeGhalti("Lughat ghalti: Key khan poe ':' lazmi aahe", self.peek().line, self.peek().column, self.code)
                self.advance()
                val = self.parse_expression()
                pairs.append((key, val))

            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti("Lughat jhay aakhir mein '}' lazmi aahe", self.peek().line, self.peek().column, self.code)
            self.advance()
            return DictNode(pairs).set_pos(token.line, token.column)
        else:
            elements = [first_expr]
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                elements.append(self.parse_expression())

            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti("Majmuo jhay aakhir mein '}' lazmi aahe", self.peek().line, self.peek().column, self.code)
            self.advance()  # }
            return SetNode(elements).set_pos(token.line, token.column)
