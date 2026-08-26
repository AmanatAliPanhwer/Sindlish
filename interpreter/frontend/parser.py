from ..errors import LikhaiJeGhalti
from .ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolNode,
    BreakNode,
    CallNode,
    ContinueNode,
    DictNode,
    ForNode,
    FunctionNode,
    GetAttrNode,
    GhaltiNode,
    GlobalNode,
    IfNode,
    IndexNode,
    ListNode,
    MethodCallNode,
    Node,
    NonLocalNode,
    NullNode,
    NumberNode,
    ParamNode,
    PostfixOpNode,
    ProgramNode,
    ResultConstructorNode,
    ResultMethodCallNode,
    ReturnNode,
    SetNode,
    StringNode,
    TypeCastNode,
    UnaryOpNode,
    VariableNode,
    WhileNode,
)
from .keywords import DATATYPES
from .tokens import Token, TokenType

COLLECTION_TYPES: tuple[TokenType, ...] = (
    TokenType.FEHRIST,
    TokenType.LUGHAT,
    TokenType.MAJMUO,
)

CallArgs = tuple[list[Node], list[tuple[str, Node]], Node | None, Node | None]


class Parser:
    def __init__(self, tokens: list[Token], code: str) -> None:
        self.tokens = tokens
        self.code = code
        self.pos = 0

    _COMPARISON_OPS = (
        TokenType.GT,
        TokenType.LT,
        TokenType.EQEQ,
        TokenType.NOTEQ,
        TokenType.GTEQ,
        TokenType.LTEQ,
    )

    def previous(self) -> Token | None:
        """Return the most recently consumed token, or None at the start."""
        return self.tokens[self.pos - 1] if self.pos > 0 else None

    def _at_pos(self, node: Node, token: Token | None = None) -> Node:
        """Stamp *node* with source position from *token* (or previous) and return it."""
        t = token or self.previous()
        if t:
            node.set_pos(t.line, t.column)
        return node

    def _is_typed_declaration(self, token: Token) -> bool:
        """True if the current token starts a declaration like
        `pakko x = ...`, `adad y`, or `fehrist<adad> z = ...`."""
        if token.type == TokenType.PAKKO:
            return True

        nxt = self.peek_ahead()
        if token.type not in DATATYPES or nxt is None:
            return False

        return nxt.type == TokenType.IDENTIFIER or (
            token.type in COLLECTION_TYPES and nxt.type == TokenType.LBRACKET
        )

    def peek(self) -> Token | None:
        """Return the current token without consuming it, or None at EOF."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Token:
        """Consume and return the current token, advancing position by one."""
        token = self.peek()
        self.pos += 1
        return token

    def peek_ahead(self) -> Token | None:
        """Return the token after current without consuming, or None if at/ near EOF."""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None

    def _skip_newlines(self) -> None:
        """Consume consecutive NEWLINE tokens."""
        while self.peek() and self.peek().type == TokenType.NEWLINE:
            self.advance()

    def get_default_value_node(self, var_type: TokenType | None, token: Token | None = None) -> Node:
        """Return a zero-value AST node for the given *var_type*.

        Consume nothing.  Returns a sensible default (0, 0.0, "", False, etc.)
        for each built-in datatype.  Returns NullNode for unknown types.
        """
        # TODO: Use match case statements or a dictionary look up whatever you want.
        if var_type == TokenType.ADAD:
            return self._at_pos(NumberNode(0), token)
        if var_type == TokenType.DAHAI:
            return self._at_pos(NumberNode(0.0), token)
        if var_type == TokenType.LAFZ:
            return self._at_pos(StringNode(""), token)
        if var_type == TokenType.FAISLO:
            return self._at_pos(BoolNode(False), token)
        return self._at_pos(NullNode(), token)

    def parse(self) -> ProgramNode:
        """Consume all tokens and return the root ProgramNode.

        Raises LikhaiJeGhalti on syntax errors.
        """
        statements = []

        while self.peek() and self.peek().type != TokenType.EOF:
            self._skip_newlines()
            if self.peek().type == TokenType.EOF:
                break

            stmt = self.parse_statement()
            statements.append(stmt)
            self._skip_newlines()

        return self._at_pos(
            ProgramNode(statements), self.tokens[0] if self.tokens else None
        )

    def parse_statement(self) -> Node:
        """Consume and return one statement (keyword, assignment, or expression).

        Dispatches on the current token to the appropriate parse_* method.
        Raises LikhaiJeGhalti on unexpected tokens.
        """
        token = self.peek()

        match token.type:
            case TokenType.AGAR:
                return self.parse_if().set_pos(token.line, token.column)

            case TokenType.JISTAIN:
                return self.parse_while().set_pos(token.line, token.column)

            case TokenType.KAAM:
                return self.parse_function_def().set_pos(token.line, token.column)

            case TokenType.WAPAS:
                return self.parse_return().set_pos(token.line, token.column)

            case TokenType.HAR:
                return self.parse_for().set_pos(token.line, token.column)

            case TokenType.TOR:
                self.advance()  # tor
                return BreakNode().set_pos(token.line, token.column)

            case TokenType.JARI:
                self.advance()  # jari
                return ContinueNode().set_pos(token.line, token.column)

            case TokenType.LBRACE:
                self.advance()  # {
                statements = self.parse_block()
                return statements

            case TokenType.AALMI:
                self.advance()  # aalmi
                if self.peek() and self.peek().type != TokenType.IDENTIFIER:
                    raise LikhaiJeGhalti(
                        "'aalmi' khaan poe variable jo naalo lazmi aahe.",
                        token.line,
                        token.column,
                        self.code,
                    )
                name = self.advance().value
                return GlobalNode(name).set_pos(token.line, token.column)

            case TokenType.MATCH:
                raise LikhaiJeGhalti(
                    "'match' abhi support natho tho; hale roadmap mein aahe.",
                    token.line,
                    token.column,
                    self.code,
                )

            case TokenType.BAHARI:
                self.advance()  # bahari
                if self.peek() and self.peek().type != TokenType.IDENTIFIER:
                    raise LikhaiJeGhalti(
                        "'bahari' khaan poe variable jo naalo lazmi aahe.",
                        token.line,
                        token.column,
                        self.code,
                    )
                name = self.advance().value
                return NonLocalNode(name).set_pos(token.line, token.column)

        # ===== Lookahead-dependent statements =====
        # PAKKO / DATATYPE / IDENTIFIER cannot be plain `case` labels above:
        # recognizing them requires peek_ahead() context (e.g. IDENTIFIER)
        # only starts an assignment when followed by '=' or ':'). Keep them
        # OUT of the match; adding a wildcard case would silently swallow
        # this whole section.

        if token.type == TokenType.PAKKO or (
            token.type in DATATYPES
            and self.peek_ahead()
            and (
                self.peek_ahead().type == TokenType.IDENTIFIER
                or (
                    token.type
                    in (TokenType.FEHRIST, TokenType.LUGHAT, TokenType.MAJMUO)
                    and self.peek_ahead().type == TokenType.LBRACKET
                )
            )
        ):
            return self.parse_assignment().set_pos(token.line, token.column)

        if token.type == TokenType.IDENTIFIER:
            nxt = self.peek_ahead()
            if nxt and nxt.type in (TokenType.EQ, TokenType.COLON):
                return self.parse_assignment().set_pos(token.line, token.column)
            if nxt and nxt.type == TokenType.IDENTIFIER:
                return self.parse_assignment().set_pos(token.line, token.column)
            expr = self.parse_expression()

            if self.peek() and self.peek().type == TokenType.EQ:
                self.advance()  # =
                value_node = self.parse_expression()

                if isinstance(expr, IndexNode):
                    return IndexNode(expr.left, expr.index, value_node).set_pos(
                        token.line, token.column
                    )
                else:
                    raise LikhaiJeGhalti(
                        "Ghalat assignment target.", token.line, token.column, self.code
                    )

            return expr

        # Catch-all for expression statements
        try:
            expr = self.parse_expression()
            # If it's a standalone ghalti(...) call, it should panic (Trigger Panic)
            if isinstance(expr, ResultConstructorNode) and expr.variant == "GHALTI":
                return GhaltiNode(expr.value).set_pos(token.line, token.column)
            return expr
        except LikhaiJeGhalti:
            raise
        except Exception as exc:
            raise LikhaiJeGhalti(
                f"Achanak {token.value} milyo.", token.line, token.column, self.code
            ) from exc

    def parse_block(self) -> BlockNode:
        """Consume statements until `}` or `warna` and return a BlockNode.

        Expects to be called after the opening `{` has already been consumed.
        Consumes the closing `}`. Raises LikhaiJeGhalti on unterminated blocks.
        """
        statements = []
        open_line, open_col = self.peek().line, self.peek().column

        while True:
            self._skip_newlines()
            token = self.peek()

            match token.type:
                case TokenType.EOF:
                    raise LikhaiJeGhalti(
                        "Block band natho thayo; '}' na milyo.",
                        open_line,
                        open_col,
                        self.code,
                    )

                case TokenType.WARNA:
                    break

                case TokenType.RBRACE:
                    self.advance()  # }
                    break

            statements.append(self.parse_statement())

        return BlockNode(statements).set_pos(token.line, token.column)

    def _parse_type_name(self) -> TokenType | str | None:
        """Consume one type token: builtin datatype -> TokenType,
        custom class name -> str, otherwise None."""
        if self.peek().type in DATATYPES:
            return self.advance().type
        if self.peek().type == TokenType.IDENTIFIER:
            return self.advance().value
        return None

    def _parse_element_type(self) -> TokenType | str:
        """Consume a type token inside brackets (fehrist[], lughat[], etc.).
        Raises on malformed element types — never returns None."""
        result = self._parse_type_name()
        if result is None:
            raise LikhaiJeGhalti(
                "Bracket je ander type annotation lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        return result

    def _try_prefix_type(self) -> tuple[TokenType | str | None, TokenType | None]:
        """Consume `[Type]` before a name, if present.
        Returns (TokenType|str|None, element_type|None)."""
        t = self.peek()
        if t.type in DATATYPES:
            return self._parse_type_annotation()
        if (
            t.type == TokenType.IDENTIFIER
            and self.peek_ahead()
            and self.peek_ahead().type == TokenType.IDENTIFIER
        ):
            return self.advance().value, None
        return None, None

    def _parse_param(self) -> ParamNode:
        """Consume one parameter and return a ParamNode.

        Handles optional `*`/`**` prefix, type prefix form (`[Type] name`),
        colon form (`name : Type`), and default value (`name = expr`).
        Raises LikhaiJeGhalti on missing name or malformed annotation.
        """
        is_star, is_kw = False, False
        if self.peek().type == TokenType.MUL:
            self.advance()  # *
            is_star = True
        elif self.peek().type == TokenType.DBLSTAR:
            self.advance()  # **
            is_kw = True

        # Prefix form: "adad x"
        param_type, param_element = self._try_prefix_type()
        if param_element is not None:
            # TODO: Make them Supported
            raise LikhaiJeGhalti(
                "Parameters laai `[]` element types barwakat supported nah aahin.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(
                "Parameter jo naalo lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        name = self.advance().value

        if param_type is None and self.peek().type == TokenType.COLON:
            self.advance()  # :
            param_type = self._parse_type_name()
            if param_type is None:
                raise LikhaiJeGhalti(
                    "Colon `:` khaan poe type annotation lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )

        default = None
        if self.peek().type == TokenType.EQ:
            self.advance()  # =
            default = self.parse_expression()

        return ParamNode(name, param_type, default, is_star, is_kw)

    def _parse_function_params(self) -> list[ParamNode]:
        """Consume `( ... )` and return a list of ParamNodes.

        Grammar per param: `[*|**] [datatype] name [: type] [= default]`
        Trailing commas allowed. Consumes the closing `)`.
        Raises LikhaiJeGhalti on missing `)`.
        """
        params = []
        self._skip_newlines()

        if self.peek().type == TokenType.RPAREN:
            self.advance()
            return params

        while True:
            params.append(self._parse_param())

            self._skip_newlines()
            if self.peek().type != TokenType.COMMA:
                break
            self.advance()  # ,
            self._skip_newlines()
            if self.peek().type == TokenType.RPAREN:
                break
        self._skip_newlines()
        if self.peek().type != TokenType.RPAREN:
            raise LikhaiJeGhalti(
                "Parameters khaan poe ')' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # )
        return params

    def _parse_return_type(self) -> TokenType | str | None:
        """Consume an optional `-> Type` and return the type, or None.

        Consumes `->` plus the type token if present.
        Returns a TokenType for builtins, str for custom names, None if absent.
        """
        if (
            self.peek().type == TokenType.MINUS
            and self.peek_ahead()
            and self.peek_ahead().type == TokenType.GT
        ):
            self.advance()  # -
            self.advance()  # >
            return self._parse_type_name()
        return None

    def parse_function_def(self) -> FunctionNode:
        """Consume `kaam name(params) [: ReturnType] { body }` and return a FunctionNode.

        Advances past `kaam`, name, `(`, params, optional return type, and body block.
        Raises LikhaiJeGhalti on missing name, `(`, or `{`.
        """
        self.advance()  # kaam
        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(
                "'kaam' khaan poe kaam jo naalo lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        name = self.advance().value

        if self.peek().type != TokenType.LPAREN:
            raise LikhaiJeGhalti(
                "Function je naale khaan poe '(' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # (

        params = self._parse_function_params()
        return_type = self._parse_return_type()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti(
                "Function body khaan pehriyan '{' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # {

        body = self.parse_block()
        return FunctionNode(name, params, body, return_type)

    def parse_return(self) -> ReturnNode:
        """Consume `wapas [expr]` and return a ReturnNode.

        Advances past `wapas`. The expression is optional — omitted if the next
        token is a newline, EOF, or `}`.
        """
        self.advance()  # wapas
        value = None
        if self.peek().type not in (TokenType.NEWLINE, TokenType.EOF, TokenType.RBRACE):
            value = self.parse_expression()
        return ReturnNode(value)

    def parse_if(self) -> IfNode:
        """Consume `agar cond { body } [yawari cond { body }]* [warna { body }]`.

        Returns an IfNode with condition, body, else-if branches, and optional else.
        Raises LikhaiJeGhalti on missing `{`.
        """
        token = self.peek()
        self.advance()  # agar

        condition = self.parse_expression()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti(
                "Shart (condition) khaan poe '{' lazmi aahe.",
                token.line,
                token.column,
                self.code,
            )
        self.advance()  # {

        body = self.parse_block()

        self._skip_newlines()

        else_if_bodies = []

        while self.peek().type == TokenType.YAWARI:
            self.advance()  # yawari
            else_if_condition = self.parse_expression()
            if self.peek().type != TokenType.LBRACE:
                raise LikhaiJeGhalti(
                    "'yawari' je shart khaan poe '{' lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            self.advance()  # {
            else_if_body = self.parse_block()
            else_if_bodies.append((else_if_condition, else_if_body))
            self._skip_newlines()

        else_body = None

        if self.peek().type == TokenType.WARNA:
            self.advance()  # warna
            if self.peek().type != TokenType.LBRACE:
                raise LikhaiJeGhalti(
                    "'warna' khaan poe '{' lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            self.advance()  # {

            else_body = self.parse_block()

        return IfNode(condition, body, else_body, else_if_bodies).set_pos(
            token.line, token.column
        )

    def parse_expression(self) -> Node:
        """Entry point for the expression precedence chain. Alias for parse_or()."""
        return self.parse_or()

    def parse_or(self) -> Node:
        """Parse `and ("ya" and)*` and return a BinaryOpNode or passthrough."""
        left = self.parse_and()

        while self.peek().type == TokenType.OR:
            op = self.advance()
            self._skip_newlines()
            right = self.parse_and()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_and(self) -> Node:
        """Parse `not ("aen" not)*` and return a BinaryOpNode or passthrough."""
        left = self.parse_not()

        while self.peek().type == TokenType.AND:
            op = self.advance()
            self._skip_newlines()
            right = self.parse_not()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_not(self) -> Node:
        """Parse `"nah" not | comparison` and return a UnaryOpNode or passthrough."""
        self._skip_newlines()
        if self.peek().type == TokenType.NOT:
            op = self.advance()
            self._skip_newlines()
            value = self.parse_not()
            return UnaryOpNode(op, value).set_pos(op.line, op.column)
        return self.parse_comparison()

    def parse_comparison(self) -> Node:
        """Parse `term (comp_op term)?` and return a BinaryOpNode or passthrough.

        Raises LikhaiJeGhalti on chained comparisons.
        """
        left = self.parse_term()

        if self.peek().type in self._COMPARISON_OPS:
            op = self.advance()
            self._skip_newlines()
            right = self.parse_term()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

            nxt = self.peek()
            if nxt.type in self._COMPARISON_OPS:
                raise LikhaiJeGhalti(
                    "Chained comparisons supported na aahin; likho (a < b) aen (b < c).",
                    nxt.line,
                    nxt.column,
                    self.code,
                )

        return left

    def parse_term(self) -> Node:
        """Parse `factor (("+" | "-") factor)*` and return a BinaryOpNode or passthrough."""
        left = self.parse_factor()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance()
            self._skip_newlines()
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_factor(self) -> Node:
        """Parse `power (("*" | "/" | "%") power)*` and return a BinaryOpNode or passthrough."""
        left = self.parse_power()

        while self.peek().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op = self.advance()
            self._skip_newlines()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_power(self) -> Node:
        """Parse `unary ("^" power)?` and return a BinaryOpNode or passthrough (right-associative)."""
        left = self.parse_unary()

        if self.peek().type == TokenType.POW:
            op = self.advance()
            self._skip_newlines()
            right = self.parse_power()
            left = BinaryOpNode(left, op, right).set_pos(op.line, op.column)

        return left

    def parse_unary(self) -> Node:
        """Parse `("-" | "nah") unary | postfix` and return a UnaryOpNode or passthrough."""
        self._skip_newlines()
        if self.peek().type == TokenType.MINUS:
            op = self.advance()
            self._skip_newlines()
            value = self.parse_unary()
            return UnaryOpNode(op, value).set_pos(op.line, op.column)
        if self.peek().type == TokenType.NOT:
            op = self.advance()
            self._skip_newlines()
            value = self.parse_unary()
            return UnaryOpNode(op, value).set_pos(op.line, op.column)

        return self.parse_postfix()

    def parse_postfix(self) -> Node:
        """Parse primary followed by postfix operators (?, !!, ., [], ()).

        Loops consuming postfix ops until none remain. Returns the final Node.
        """
        node = self.parse_primary()

        while True:
            match self.peek().type:
                case TokenType.QMARK | TokenType.BANGBANG:
                    op = self.advance()
                    node = PostfixOpNode(node, op).set_pos(op.line, op.column)
                case TokenType.DOT:
                    node = self._parse_method_chain(node)
                case TokenType.LBRACKET:
                    self.advance()  # [
                    self._skip_newlines()
                    index = self.parse_expression()
                    self._skip_newlines()
                    if self.peek().type != TokenType.RBRACKET:
                        raise LikhaiJeGhalti(
                            "Index khaan poe ']' lazmi aahe.",
                            self.peek().line,
                            self.peek().column,
                            self.code,
                        )
                    self.advance()  # ]
                    node = IndexNode(node, index).set_pos(node.line, node.column)
                case TokenType.LPAREN:
                    args, keywords, star_args, kw_args = self.parse_call_arguments()
                    if isinstance(node, VariableNode):
                        node = CallNode(
                            node.name, args, keywords, star_args, kw_args
                        ).set_pos(node.line, node.column)
                    else:
                        # Support calling results of expressions if compiler allows
                        # For now, we'll keep the CallNode(name, ...) structure
                        # but we might need to wrap the node if it's not a VariableNode.
                        # Since CallNode expects a name: str, we have a problem here for f()().
                        # But a[0][1] will work fine because IndexNode takes a node.
                        node = CallNode(
                            node, args, keywords, star_args, kw_args
                        ).set_pos(node.line, node.column)
                case _:
                    break
        return node

    def _parse_method_chain(self, node: Node) -> Node:
        """Consume `.method_name[(args)]` or `.attr_name` after a dot.

        Returns a MethodCallNode, ResultMethodCallNode, or GetAttrNode.
        Raises LikhaiJeGhalti on missing method name or `(` for result methods.
        """
        dot = self.advance()
        if self.peek().type not in (
            TokenType.IDENTIFIER,
            TokenType.GHALTI,
            TokenType.OK,
        ):
            raise LikhaiJeGhalti(
                "'.' khaan poe method jo naalo lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        method_name = self.advance().value

        if method_name in ("bachao", "lazmi"):
            if not self.peek() or self.peek().type != TokenType.LPAREN:
                raise LikhaiJeGhalti(
                    f"Method {method_name} khaan poe '(' lazmi aahe.",
                    dot.line,
                    dot.column,
                    self.code,
                )
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                raise LikhaiJeGhalti(
                    f"{method_name} khe sirf 1 argument khapay.",
                    dot.line,
                    dot.column,
                    self.code,
                )
            return ResultMethodCallNode(node, method_name, args[0]).set_pos(
                dot.line, dot.column
            )

        if self.peek() and self.peek().type == TokenType.LPAREN:
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            return MethodCallNode(
                node, method_name, args, keywords, star_args, kw_args
            ).set_pos(dot.line, dot.column)

        return GetAttrNode(node, method_name).set_pos(dot.line, dot.column)

    def parse_primary(self) -> Node:
        """Consume a literal, typecast, variable, parenthesised expression, or collection.

        Returns the corresponding AST node. Raises LikhaiJeGhalti on unexpected tokens.
        """
        token = self.peek()

        if (
            token.type in DATATYPES
            and self.peek_ahead()
            and self.peek_ahead().type == TokenType.LPAREN
        ):
            target_type = self.advance().type
            args, keywords, star_args, kw_args = self.parse_call_arguments()
            if len(args) != 1 or keywords or star_args or kw_args:
                # Special case: allow majmuo() with 0 args for empty set
                if target_type == TokenType.MAJMUO and len(args) == 0:
                    return SetNode([]).set_pos(token.line, token.column)
                raise LikhaiJeGhalti(
                    f"Typecasting '{token.value}' khe sirf hikro argument khapay.",
                    token.line,
                    token.column,
                    self.code,
                )
            return TypeCastNode(target_type, args[0]).set_pos(token.line, token.column)

        match token.type:
            case TokenType.ADAD:
                self.advance()
                return NumberNode(token.value).set_pos(token.line, token.column)
            case TokenType.DAHAI:
                self.advance()
                return NumberNode(token.value).set_pos(token.line, token.column)
            case TokenType.LAFZ:
                self.advance()
                return StringNode(token.value).set_pos(token.line, token.column)
            case TokenType.SACH:
                self.advance()
                return BoolNode(True).set_pos(token.line, token.column)
            case TokenType.KOORE:
                self.advance()
                return BoolNode(False).set_pos(token.line, token.column)
            case TokenType.KHALI:
                self.advance()
                return NullNode().set_pos(token.line, token.column)
            case TokenType.OK:
                self.advance()
                if self.peek().type != TokenType.LPAREN:
                    raise LikhaiJeGhalti(
                        "'ok' khaan poe '(' lazmi aahe.",
                        token.line,
                        token.column,
                        self.code,
                    )
                args, keywords, star_args, kw_args = self.parse_call_arguments()
                if len(args) != 1 or keywords or star_args or kw_args:
                    raise LikhaiJeGhalti(
                        "'ok' khe sirf 1 argument khapay.",
                        token.line,
                        token.column,
                        self.code,
                    )
                return ResultConstructorNode("OK", args[0]).set_pos(
                    token.line, token.column
                )
            case TokenType.GHALTI:
                self.advance()
                if self.peek().type != TokenType.LPAREN:
                    raise LikhaiJeGhalti(
                        "'ghalti' khaan poe '(' lazmi aahe.",
                        token.line,
                        token.column,
                        self.code,
                    )
                args, keywords, star_args, kw_args = self.parse_call_arguments()
                if len(args) != 1 or keywords or star_args or kw_args:
                    raise LikhaiJeGhalti(
                        "'ghalti' khe sirf 1 argument khapay.",
                        token.line,
                        token.column,
                        self.code,
                    )
                return ResultConstructorNode("GHALTI", args[0]).set_pos(
                    token.line, token.column
                )
            case TokenType.LBRACKET:
                return self.parse_list().set_pos(token.line, token.column)
            case TokenType.LBRACE:
                return self.parse_dict_set().set_pos(token.line, token.column)
            case TokenType.LPAREN:
                self.advance()
                self._skip_newlines()
                expr = self.parse_expression().set_pos(token.line, token.column)
                self._skip_newlines()
                if self.peek().type != TokenType.RPAREN:
                    raise LikhaiJeGhalti(
                        "'(' khaan poe ')' lazmi aahe.",
                        self.peek().line,
                        self.peek().column,
                        self.code,
                    )
                self.advance()  # )
                return expr
            case TokenType.IDENTIFIER:
                name = self.advance().value
                return VariableNode(name).set_pos(token.line, token.column)

        raise LikhaiJeGhalti(
            f"Achanak {token} milyo.", token.line, token.column, self.code
        )

    def parse_call_arguments(self) -> CallArgs:
        """Consume `( ... )` and return (args, keywords, star_args, kw_args).

        Handles positional, keyword, *args, and **kwargs arguments.
        Trailing commas allowed. Consumes the closing `)`.
        Raises LikhaiJeGhalti on missing `)` or duplicate *args/**kwargs.
        """
        token = self.peek()
        self.advance()  # (
        args = []
        keywords = []
        star_args = None
        kw_args = None

        self._skip_newlines()

        if self.peek().type == TokenType.RPAREN:
            self.advance()  # )
            return args, keywords, star_args, kw_args

        while True:
            self._skip_newlines()
            if self.peek().type == TokenType.MUL:
                self.advance()
                self._skip_newlines()
                if star_args is not None:
                    raise LikhaiJeGhalti(
                        "Sirf hikro *args istamal kare saghjay tho.",
                        token.line,
                        token.column,
                        self.code,
                    )
                star_args = self.parse_expression()
            elif self.peek().type == TokenType.DBLSTAR:
                self.advance()
                self._skip_newlines()
                if kw_args is not None:
                    raise LikhaiJeGhalti(
                        "Sirf hikro **kwargs istamal kare saghjay tho.",
                        token.line,
                        token.column,
                        self.code,
                    )
                kw_args = self.parse_expression()
            elif (
                self.peek().type == TokenType.IDENTIFIER
                and self.peek_ahead()
                and self.peek_ahead().type == TokenType.EQ
            ):
                name = self.advance().value
                self.advance()  # =
                self._skip_newlines()
                val = self.parse_expression()
                keywords.append((name, val))
            else:
                args.append(self.parse_expression())

            self._skip_newlines()
            if self.peek().type != TokenType.COMMA:
                break
            self.advance()
            self._skip_newlines()
            if self.peek().type == TokenType.RPAREN:
                break
        self._skip_newlines()
        if self.peek().type != TokenType.RPAREN:
            raise LikhaiJeGhalti(
                "Arguments khaan poe ')' lazmi aahe.",
                token.line,
                token.column,
                self.code,
            )
        self.advance()  # )
        return args, keywords, star_args, kw_args

    def _parse_type_annotation(self) -> tuple[TokenType | str, list | TokenType | None]:
        """Consume a full type annotation (with optional `[Element]` brackets).

        Handles bare type names, `fehrist[T]` / `majmuo[T]` (single element),
        and `lughat[K, V]` (key-value pair). Returns a tuple of
        (base_type, element_type) where element_type is None, a TokenType/str,
        or a [key_type, val_type] list for lughat.
        Raises LikhaiJeGhalti on malformed bracket annotations.
        """
        if self.peek().type == TokenType.IDENTIFIER:
            return self.advance().value, None
        _type = self.advance().type
        element_type = None

        if (
            _type in (TokenType.FEHRIST, TokenType.MAJMUO)
            and self.peek()
            and self.peek().type == TokenType.LBRACKET
        ):
            self.advance()  # [
            if self.peek() and (
                self.peek().type in DATATYPES
                or self.peek().type == TokenType.IDENTIFIER
            ):
                element_type = self._parse_element_type()
            else:
                raise LikhaiJeGhalti(
                    f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} laai [] jhay ander data type jo hovan lazmi aahe",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            if self.peek() and self.peek().type != TokenType.RBRACKET:
                raise LikhaiJeGhalti(
                    f"{'fehrist' if _type == TokenType.FEHRIST else 'majmuo'} jhay element type khan poe ']' lazmi aahe",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            self.advance()  # ]

        elif (
            _type == TokenType.LUGHAT
            and self.peek()
            and self.peek().type == TokenType.LBRACKET
        ):
            self.advance()  # [
            if self.peek() and (
                self.peek().type in DATATYPES
                or self.peek().type == TokenType.IDENTIFIER
            ):
                key_type = self._parse_element_type()
                if self.peek().type not in (TokenType.COMMA, TokenType.COLON):
                    raise LikhaiJeGhalti(
                        "Lughat je key type khaan poe ',' ya ':' lazmi aahe.",
                        self.peek().line,
                        self.peek().column,
                        self.code,
                    )
                self.advance()  # , or :
                if self.peek() and (
                    self.peek().type in DATATYPES
                    or self.peek().type == TokenType.IDENTIFIER
                ):
                    val_type = self._parse_element_type()
                    element_type = [key_type, val_type]
                if self.peek() and self.peek().type != TokenType.RBRACKET:
                    raise LikhaiJeGhalti(
                        "Lughat je element types khaan poe ']' lazmi aahe.",
                        self.peek().line,
                        self.peek().column,
                        self.code,
                    )
                self.advance()  # ]

        return _type, element_type

    def parse_assignment(self) -> AssignNode:
        """Consume a variable declaration/assignment and return an AssignNode.

        Handles: `pakko` const, prefix form (`[Type] name`), colon form (`name : Type`),
        and plain assignment (`name = expr`). Const declarations require an explicit value.
        Raises LikhaiJeGhalti on missing name, missing const value, or bad annotation.
        """
        is_const = False
        _type = None
        element_type = None
        token = self.peek()

        if self.peek().type == TokenType.PAKKO:
            self.advance()
            is_const = True

        if self.peek().type in DATATYPES or (
            self.peek().type == TokenType.IDENTIFIER
            and self.peek_ahead()
            and self.peek_ahead().type == TokenType.IDENTIFIER
        ):
            _type, element_type = self._try_prefix_type()

        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(
                f"Variable jo naalo khapyo paye, par {self.peek().type.name} milyo.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        name = self.advance().value

        if self.peek().type == TokenType.COLON:
            self.advance()  # :
            self._skip_newlines()
            if self.peek() and (
                self.peek().type in DATATYPES
                or self.peek().type == TokenType.IDENTIFIER
            ):
                _type, element_type = self._parse_type_annotation()
            else:
                raise LikhaiJeGhalti(
                    "Colon `:` khaan poe type annotation lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )

        if self.peek() and self.peek().type == TokenType.EQ:
            self.advance()  # =
            self._skip_newlines()
            value_node = self.parse_expression()
        else:
            if is_const:
                raise LikhaiJeGhalti(
                    f"Pakkey `{name}` laai value lazmi aahe.",
                    token.line,
                    token.column,
                    self.code,
                )

            value_node = self.get_default_value_node(_type)

        return AssignNode(
            name, value_node, _type, is_const, element_type, _type is not None
        ).set_pos(token.line, token.column)

    def parse_while(self) -> WhileNode:
        """Consume `jistain condition { body }` and return a WhileNode.

        Raises LikhaiJeGhalti on missing `{`.
        """
        token = self.peek()
        self.advance()  # jistain
        self._skip_newlines()

        condition = self.parse_expression()
        self._skip_newlines()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti(
                "Shart (condition) khaan poe '{' lazmi aahe.",
                token.line,
                token.column,
                self.code,
            )
        self.advance()  # {

        body = self.parse_block()

        return WhileNode(condition, body).set_pos(token.line, token.column)

    def parse_for(self) -> ForNode:
        """Consume `har name mein iterable { body }` and return a ForNode.

        Raises LikhaiJeGhalti on missing name, `mein`, or `{`.
        """
        token = self.peek()
        self.advance()  # har
        self._skip_newlines()

        if self.peek().type != TokenType.IDENTIFIER:
            raise LikhaiJeGhalti(
                "'har' khaan poe variable jo naalo lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )

        iterator_name = self.advance().value
        self._skip_newlines()

        if self.peek().type != TokenType.MEIN:
            raise LikhaiJeGhalti(
                "Variable khaan poe 'mein' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # mein
        self._skip_newlines()

        iterable = self.parse_expression()
        self._skip_newlines()

        if self.peek().type != TokenType.LBRACE:
            raise LikhaiJeGhalti(
                "Iterable khaan poe '{' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # {

        body = self.parse_block()

        return ForNode(iterator_name, iterable, body).set_pos(token.line, token.column)

    def parse_list(self) -> ListNode:
        """Consume `[expr, ...]` and return a ListNode.

        Expects `[` already consumed. Handles trailing commas and empty lists.
        Raises LikhaiJeGhalti on missing `]`.
        """
        token = self.peek()
        self.advance()  # [
        elements = []

        if self.peek().type == TokenType.RBRACKET:
            self.advance()
            return ListNode(elements).set_pos(token.line, token.column)

        self._skip_newlines()
        elements.append(self.parse_expression())
        self._skip_newlines()
        while self.peek().type == TokenType.COMMA:
            self.advance()  # ,
            self._skip_newlines()
            elements.append(self.parse_expression())
            self._skip_newlines()

        if self.peek().type != TokenType.RBRACKET:
            raise LikhaiJeGhalti(
                "Fehrist je aakhir mein ']' lazmi aahe.",
                self.peek().line,
                self.peek().column,
                self.code,
            )
        self.advance()  # ]

        return ListNode(elements).set_pos(token.line, token.column)

    def parse_dict_set(self, expected_type: TokenType | None = None) -> DictNode | SetNode:
        """Consume `{ ... }` and return a DictNode or SetNode.

        If *expected_type* is MAJMUO, empty `{}` is treated as a set.
        Otherwise the first element determines dict (if followed by `:`) vs set.
        Raises LikhaiJeGhalti on missing `}` or malformed dict entries.
        """
        token = self.peek()
        self.advance()  # {

        self._skip_newlines()
        if self.peek() and self.peek().type == TokenType.RBRACE:
            self.advance()
            if expected_type == TokenType.MAJMUO:
                return SetNode([]).set_pos(token.line, token.column)
            return DictNode([]).set_pos(token.line, token.column)

        self._skip_newlines()
        first_expr = self.parse_expression()
        self._skip_newlines()

        if self.peek() and self.peek().type == TokenType.COLON:
            self.advance()  # :
            self._skip_newlines()
            first_val = self.parse_expression()
            self._skip_newlines()
            pairs = [(first_expr, first_val)]

            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                self._skip_newlines()
                key = self.parse_expression()
                self._skip_newlines()
                if self.peek().type != TokenType.COLON:
                    raise LikhaiJeGhalti(
                        "Lughat ji ghalti: Key khaan poe ':' lazmi aahe.",
                        self.peek().line,
                        self.peek().column,
                        self.code,
                    )
                self.advance()
                self._skip_newlines()
                val = self.parse_expression()
                self._skip_newlines()
                pairs.append((key, val))

            self._skip_newlines()
            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti(
                    "Lughat je aakhir mein '}' lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            self.advance()
            return DictNode(pairs).set_pos(token.line, token.column)
        else:
            elements = [first_expr]
            self._skip_newlines()
            while self.peek().type == TokenType.COMMA:
                self.advance()  # ,
                self._skip_newlines()
                elements.append(self.parse_expression())
                self._skip_newlines()

            self._skip_newlines()
            if self.peek().type != TokenType.RBRACE:
                raise LikhaiJeGhalti(
                    "Majmuo je aakhir mein '}' lazmi aahe.",
                    self.peek().line,
                    self.peek().column,
                    self.code,
                )
            self.advance()  # }
            return SetNode(elements).set_pos(token.line, token.column)
