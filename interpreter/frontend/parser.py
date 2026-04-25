from .ast_nodes import (
    Node, ProgramNode, BlockNode,
    NumberNode, StringNode, BoolNode, NullNode,
    VariableNode, AssignNode,
    BinaryOpNode, UnaryOpNode, PostfixOpNode,
    PrintNode, IfNode, WhileNode, ForNode, BreakNode, ContinueNode,
    ListNode, DictNode, SetNode, IndexNode,
    FunctionNode, ParamNode, CallNode, ReturnNode,
    MethodCallNode, GetAttrNode,
    GlobalNode, NonLocalNode,
    ResultConstructorNode, ResultMethodCallNode, KharabiNode, TypeCastNode,
)
from .tokens import TokenType
from .keywords import DATATYPES
from ..errors import LikhaiJeGhalti

class Parser:
    def __init__(self, tokens, code):
        self.tokens = tokens
        self.code = code
        self.pos = 0

    def previous(self):
        return self.tokens[self.pos - 1] if self.pos > 0 else None

    def _at_pos(self, node, token=None):
        """Helper to stamp a node with position info."""
        t = token or self.previous()
        if t:
            node.set_pos(t.line, t.column)
        return node

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

    def get_default_value_node(self, var_type, token=None):
        if var_type == TokenType.ADAD:
            return self._at_pos(NumberNode(0), token)
        if var_type == TokenType.DAHAI:
            return self._at_pos(NumberNode(0.0), token)
        if var_type == TokenType.LAFZ:
            return self._at_pos(StringNode(""), token)
        if var_type == TokenType.FAISLO:
            return self._at_pos(BoolNode(False), token)
        return self._at_pos(NullNode(), token)

    def parse(self):
        statements = []

        while self.peek() and self.peek().type != TokenType.EOF:
            self.skip_newlines()
            if self.peek().type == TokenType.EOF:
                break

            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()

        return self._at_pos(ProgramNode(statements), self.tokens[0] if self.tokens else None)

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

        return BlockNode(statements).set_pos(token.line, token.column)

    def parse_statement(self):
        token = self.peek()

        if token.type == TokenType.LIKH:
            return self.parse_print().set_pos(token.line, token.column)

        if token.type == TokenType.AGAR:
            return self.parse_if().set_pos(token.line, token.column)

        if token.type == TokenType.JISTAIN:
            return self.parse_while().set_pos(token.line, token.column)

        if token.type == TokenType.KAAM:
            return self.parse_function_def().set_pos(token.line, token.column)

        if token.type == TokenType.WAPAS:
            return self.parse_return().set_pos(token.line, token.column)

        if token.type == TokenType.HAR:
            return self.parse_for().set_pos(token.line, token.column)

        if token.type == TokenType.TOR:
            self.advance() # tor
            return BreakNode().set_pos(token.line, token.column)

        if token.type == TokenType.JARI:
            self.advance() # jari
            return ContinueNode().set_pos(token.line, token.column)

        if token.type == TokenType.PAKKO or (
            token.type in DATATYPES and self.peek_ahead() and (
                self.peek_ahead().type == TokenType.IDENTIFIER or 
                (token.type in (TokenType.FEHRIST, TokenType.LUGHAT, TokenType.MAJMUO) and self.peek_ahead().type == TokenType.LBRACKET)
            )
        ):
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
        
        if token.type == TokenType.LBRACE:
            self.advance() # {
            statements = self.parse_block()
            return statements
        
        if token.type == TokenType.AALMI:
            self.advance() # aalmi
            if self.peek() and self.peek().type != TokenType.IDENTIFIER:
                raise LikhaiJeGhalti("'aalmi' khaan poe variable jo naalo lazmi aahe.", token.line, token.column, self.code)
            name = self.advance().value
            return GlobalNode(name).set_pos(token.line, token.column)
        
        if token.type == TokenType.BAHARI:
            self.advance() # bahari
            if self.peek() and self.peek().type != TokenType.IDENTIFIER:
                raise LikhaiJeGhalti("'bahari' khaan poe variable jo naalo lazmi aahe.", token.line, token.column, self.code)
            name = self.advance().value
            return NonLocalNode(name).set_pos(token.line, token.column)

        # Catch-all for expression statements
        try:
            expr = self.parse_expression()
            # If it's a standalone ghalti(...) call, it should panic (Trigger Panic)
            if isinstance(expr, ResultConstructorNode) and expr.variant == "GHALTI":
                return KharabiNode(expr.value).set_pos(token.line, token.column)
            return expr
        except LikhaiJeGhalti:
            raise
        except:
            raise LikhaiJeGhalti(f"Achanak {token.value} milyo.", token.line, token.column, self.code)

    def _parse_function_params(self):
        params = []
        if self.peek().type != TokenType.RPAREN:
            while True:
                is_star = False
                is_kw = False

                if self.peek().type == TokenType.MUL:
                    self.advance() # *
                    is_star = True
                elif self.peek().type == TokenType.DBLSTAR:
                    self.advance() # **
                    is_kw = True

                # Support "adad a" syntax
                type_node = None
                if self.peek().type in DATATYPES:
                    type_node = self.advance().type.name.lower()

                if self.peek().type != TokenType.IDENTIFIER:
                    raise LikhaiJeGhalti("Parameter jo naalo lazmi aahe.", self.peek().line, self.peek().column, self.code)
                param_name = self.advance().value

                # Support "a: adad" syntax
                if type_node is None and self.peek().type == TokenType.COLON:
                    self.advance() # :
                    if self.peek().type in DATATYPES:
                        type_node = self.advance().type.name.lower()
                    elif self.peek().type == TokenType.IDENTIFIER:
                        type_node = self.advance().value
                    else:
                        raise LikhaiJeGhalti("Type annotation lazmi aahe.", self.peek().line, self.peek().column, self.code)

                default_value = None
                if self.peek().type == TokenType.EQ:
                    self.advance() # =
                    default_value = self.parse_expression()

                params.append(ParamNode(param_name, type_node, default_value, is_star, is_kw))

                if self.peek().type == TokenType.COMMA:
                    self.advance()
                    if self.peek().type == TokenType.RPAREN:
                        break # Allow trailing comma
                else:
                    break

        if self.peek().type != TokenType.RPAREN:
            raise LikhaiJeGhalti("Parameters khaan poe ')' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance() # )
        return params

    def _parse_return_type(self):
        return_type = None
        if self.peek().type == TokenType.MINUS:
            if self.peek_ahead() and self.peek_ahead().type == TokenType.GT:
                self.advance() # -
                self.advance() # >
                if self.peek().type == TokenType.IDENTIFIER:
                    return_type = self.advance().value
                elif self.peek().type in DATATYPES:
                    return_type = self.advance().type.name.lower()
        return return_type

    def parse_function_def(self):
        token = self.advance() # kaam
        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti("'kaam' khaan poe kaam jo naalo lazmi aahe.", self.peek().line, self.peek().column, self.code)
        name = self.advance().value

        if self.peek().type != TokenType.LPAREN:
             raise LikhaiJeGhalti("Function je naale khaan poe '(' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance() # (

        params = self._parse_function_params()
        return_type = self._parse_return_type()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti("Function body khaan pehriyan '{' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance() # {

        body = self.parse_block()
        return FunctionNode(name, params, body, return_type)

    def parse_return(self):
        token = self.advance() # wapas
        value = None
        if self.peek().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            value = self.parse_expression()
        return ReturnNode(value)

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
                raise LikhaiJeGhalti("'likh(' khaan poe ')' lazmi aahe.", token.line, token.column, self.code)

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
            raise LikhaiJeGhalti("Shart (condition) khaan poe '{' lazmi aahe.", token.line, token.column, self.code)
        self.advance()  # {

        body = self.parse_block()

        self.skip_newlines()

        else_if_bodies = []

        while self.peek().type == TokenType.YAWARI:
            self.advance() # yawari
            else_if_condition = self.parse_expression()
            if self.peek().type != TokenType.LBRACE:
                raise LikhaiJeGhalti("'yawari' je shart khaan poe '{' lazmi aahe.", self.peek().line, self.peek().column, self.code)
            self.advance() # {
            else_if_body = self.parse_block()
            else_if_bodies.append((else_if_condition, else_if_body))
            self.skip_newlines()

        else_body = None

        if self.peek().type == TokenType.WARNA:
            self.advance()  # warna
            if self.peek().type != TokenType.LBRACE:
                raise LikhaiJeGhalti("'warna' khaan poe '{' lazmi aahe.", self.peek().line, self.peek().column, self.code)
            self.advance()  # {

            else_body = self.parse_block()

        return IfNode(condition, body, else_body, else_if_bodies).set_pos(token.line, token.column)

    def parse_expression(self):
        return self.parse_or()

    def parse_primary(self):
        token = self.peek()

        if token.type in DATATYPES:
            if self.peek_ahead() and self.peek_ahead().type == TokenType.LPAREN:
                target_type = self.advance().type
                args, keywords, star_args, kw_args = self.parse_call_arguments()
                if len(args) != 1 or keywords or star_args or kw_args:
                     # Special case: allow majmuo() with 0 args for empty set
                     if target_type == TokenType.MAJMUO and len(args) == 0:
                         return SetNode([]).set_pos(token.line, token.column)
                     raise LikhaiJeGhalti(f"Typecasting '{token.value}' khe sirf 1 argument khapay.", token.line, token.column, self.code)
                return TypeCastNode(target_type, args[0]).set_pos(token.line, token.column)

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

        if token.type == TokenType.OK:
            self.advance()
            if self.peek().type != TokenType.LPAREN:
                raise LikhaiJeGhalti("'ok' khaan poe '(' lazmi aahe.", token.line, token.column, self.code)
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                 raise LikhaiJeGhalti("'ok' khe sirf 1 argument khapay.", token.line, token.column, self.code)
            return ResultConstructorNode("OK", args[0]).set_pos(token.line, token.column)

        if token.type == TokenType.GHALTI:
            self.advance()
            if self.peek().type != TokenType.LPAREN:
                raise LikhaiJeGhalti("'ghalti' khaan poe '(' lazmi aahe.", token.line, token.column, self.code)
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                 raise LikhaiJeGhalti("'ghalti' khe sirf 1 argument khapay.", token.line, token.column, self.code)
            return ResultConstructorNode("GHALTI", args[0]).set_pos(token.line, token.column)

        if token.type == TokenType.KHARABI:
            self.advance()
            if self.peek().type != TokenType.LPAREN:
                raise LikhaiJeGhalti("'kharabi' khaan poe '(' lazmi aahe.", token.line, token.column, self.code)
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                 raise LikhaiJeGhalti("'kharabi' khe sirf 1 argument khapay.", token.line, token.column, self.code)
            return KharabiNode(args[0]).set_pos(token.line, token.column)


        if token.type == TokenType.LBRACKET:
            return self.parse_list().set_pos(token.line, token.column)

        if token.type == TokenType.LBRACE:
            return self.parse_dict_set().set_pos(token.line, token.column)
        

        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            


            node = VariableNode(name).set_pos(token.line, token.column)

            if self.peek() and self.peek().type == TokenType.LPAREN:
                args, keywords, star_args, kw_args = self.parse_call_arguments()
                return CallNode(name, args, keywords, star_args, kw_args).set_pos(token.line, token.column)

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

        raise LikhaiJeGhalti(f"Achanak {token} milyo.", token.line, token.column, self.code)

    def _parse_type_annotation(self):
        _type = self.advance().type
        element_type = None

        if _type in (TokenType.FEHRIST, TokenType.MAJMUO) and self.peek() and self.peek().type == TokenType.LBRACKET:
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

        elif _type == TokenType.LUGHAT and self.peek() and self.peek().type == TokenType.LBRACKET:
            self.advance()  # [
            if self.peek() and self.peek().type in DATATYPES:
                key_type = self.advance().type
                if self.peek().type not in (TokenType.COMMA, TokenType.COLON):
                    raise LikhaiJeGhalti("Lughat je key type khaan poe ',' ya ':' lazmi aahe.", self.peek().line, self.peek().column, self.code)
                self.advance()  # , or :
                if self.peek() and self.peek().type in DATATYPES:
                    val_type = self.advance().type
                    element_type = [key_type, val_type]
            if self.peek() and self.peek().type != TokenType.RBRACKET:
                raise LikhaiJeGhalti("Lughat je element types khaan poe ']' lazmi aahe.", self.peek().line, self.peek().column, self.code)
            self.advance()  # ]
            
        return _type, element_type

    def parse_assignment(self):
        is_const = False
        _type = None
        element_type = None
        token = self.peek()

        if self.peek().type == TokenType.PAKKO:
            self.advance()
            is_const = True

        if self.peek().type in DATATYPES:
            _type, element_type = self._parse_type_annotation()

        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(f"Variable jo naalo khapyo paye, par {self.peek().type.name} milyo.", self.peek().line, self.peek().column, self.code)
        name = self.advance().value

        if self.peek().type == TokenType.COLON:
            self.advance()  # :
            if self.peek().type in DATATYPES:
                _type, element_type = self._parse_type_annotation()

        if self.peek() and self.peek().type == TokenType.EQ:
            self.advance()  # =
            value_node = self.parse_expression()
        else:
            if is_const:
                raise LikhaiJeGhalti(f"Pakkey `{name}` laai value lazmi aahe.", token.line, token.column, self.code)

            value_node = self.get_default_value_node(_type)

        return AssignNode(name, value_node, _type, is_const, element_type, _type is not None).set_pos(token.line, token.column)

    def parse_while(self):
        token = self.peek()
        self.advance()  # jistain

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti("Shart (condition) khaan poe '{' lazmi aahe.", token.line, token.column, self.code)
        self.advance()  # {

        body = self.parse_block()

        return WhileNode(condition, body).set_pos(token.line, token.column)

    def parse_for(self):
        token = self.peek()
        self.advance()  # har

        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti("'har' khaan poe variable jo naalo lazmi aahe.", self.peek().line, self.peek().column, self.code)
        
        iterator_name = self.advance().value

        # 'mein' is now mandatory: har i mein range(5)
        if self.peek().type != TokenType.MEIN:
            raise LikhaiJeGhalti("Variable khaan poe 'mein' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance() # mein

        iterable = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti("Iterable khaan poe '{' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance() # {

        body = self.parse_block()

        return ForNode(iterator_name, iterable, body).set_pos(token.line, token.column)

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
            return UnaryOpNode(op, value).set_pos(op.line, op.column)
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
            return UnaryOpNode(op, value).set_pos(op.line, op.column)
        if self.peek().type == TokenType.NOT:
            op = self.advance()
            value = self.parse_unary()
            return UnaryOpNode(op, value).set_pos(op.line, op.column)

        return self.parse_postfix()

    def _parse_method_chain(self, node):
        dot = self.advance()
        if self.peek().type not in (TokenType.IDENTIFIER, TokenType.GHALTI, TokenType.OK):
            raise LikhaiJeGhalti("'.' khaan poe method jo naalo lazmi aahe.", self.peek().line, self.peek().column, self.code)
        method_name = self.advance().value
        
        if method_name in ("bachao", "lazmi"):
            if not self.peek() or self.peek().type != TokenType.LPAREN:
                raise LikhaiJeGhalti(f"Method {method_name} khaan poe '(' lazmi aahe.", dot.line, dot.column, self.code)
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                raise LikhaiJeGhalti(f"{method_name} khe sirf 1 argument khapay.", dot.line, dot.column, self.code)
            return ResultMethodCallNode(node, method_name, args[0]).set_pos(dot.line, dot.column)
        
        if self.peek() and self.peek().type == TokenType.LPAREN:
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            return MethodCallNode(node, method_name, args, keywords, star_args, kw_args).set_pos(dot.line, dot.column)
            
        return GetAttrNode(node, method_name).set_pos(dot.line, dot.column)

    def parse_postfix(self):
        node = self.parse_primary()
        
        while True:
            if self.peek().type == TokenType.QMARK:
                op = self.advance()
                node = PostfixOpNode(node, op).set_pos(op.line, op.column)
            elif self.peek().type == TokenType.BANGBANG:
                op = self.advance()
                node = PostfixOpNode(node, op).set_pos(op.line, op.column)
            elif self.peek().type == TokenType.DOT:
                node = self._parse_method_chain(node)
            else:
                break
        return node

    def parse_list(self):
        token = self.peek()
        self.advance()  # [
        elements = []

        if self.peek().type != TokenType.RBRACKET:
            self.skip_newlines()
            elements.append(self.parse_expression())
            self.skip_newlines()
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                self.skip_newlines()
                elements.append(self.parse_expression())
                self.skip_newlines()

        if self.peek().type != TokenType.RBRACKET:
            raise LikhaiJeGhalti("Fehrist je aakhir mein ']' lazmi aahe.", self.peek().line, self.peek().column, self.code)
        self.advance()  # ]

        return ListNode(elements).set_pos(token.line, token.column)

    def parse_call_arguments(self):
        token = self.peek()
        self.advance()  # (
        args = []
        keywords = []
        star_args = None
        kw_args = None

        if self.peek().type != TokenType.RPAREN:
            while True:
                if self.peek().type == TokenType.MUL:
                    self.advance()
                    if star_args is not None:
                        raise LikhaiJeGhalti("Sirf hikro *args istamal kare saghjay tho.", token.line, token.column, self.code)
                    star_args = self.parse_expression()
                elif self.peek().type == TokenType.DBLSTAR:
                    self.advance()
                    if kw_args is not None:
                        raise LikhaiJeGhalti("Sirf hikro **kwargs istamal kare saghjay tho.", token.line, token.column, self.code)
                    kw_args = self.parse_expression()
                elif self.peek().type == TokenType.IDENTIFIER and self.peek_ahead() and self.peek_ahead().type == TokenType.EQ:
                    name = self.advance().value
                    self.advance() # =
                    val = self.parse_expression()
                    keywords.append((name, val))
                else:
                    args.append(self.parse_expression())

                if self.peek().type == TokenType.COMMA:
                    self.advance()
                    if self.peek().type == TokenType.RPAREN:
                        break
                else:
                    break

        if self.peek().type != TokenType.RPAREN:
            raise LikhaiJeGhalti("Arguments khaan poe ')' lazmi aahe.", token.line, token.column, self.code)
        self.advance()  # )
        return args, keywords, star_args, kw_args

    def parse_dict_set(self, expected_type=None):
        token = self.peek()
        self.advance()  # {

        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.advance()
            if expected_type == TokenType.MAJMUO:
                return SetNode([]).set_pos(token.line, token.column)
            return DictNode([]).set_pos(token.line, token.column)

        first_expr = self.parse_expression()
        self.skip_newlines()

        if self.peek() and self.peek().type == TokenType.COLON:
            self.advance()  # :
            self.skip_newlines()
            first_val = self.parse_expression()
            self.skip_newlines()
            pairs = [(first_expr, first_val)]

            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                self.skip_newlines()
                key = self.parse_expression()
                self.skip_newlines()
                if self.peek().type != TokenType.COLON:
                    raise LikhaiJeGhalti("Lughat ji ghalti: Key khaan poe ':' lazmi aahe.", self.peek().line, self.peek().column, self.code)
                self.advance()
                self.skip_newlines()
                val = self.parse_expression()
                self.skip_newlines()
                pairs.append((key, val))

            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti("Lughat je aakhir mein '}' lazmi aahe.", self.peek().line, self.peek().column, self.code)
            self.advance()
            return DictNode(pairs).set_pos(token.line, token.column)
        else:
            elements = [first_expr]
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                self.skip_newlines()
                elements.append(self.parse_expression())
                self.skip_newlines()

            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti("Majmuo je aakhir mein '}' lazmi aahe.", self.peek().line, self.peek().column, self.code)
            self.advance()  # }
            return SetNode(elements).set_pos(token.line, token.column)
