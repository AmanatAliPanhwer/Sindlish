"""
Frontend sub-package: Source code → Abstract Syntax Tree.

Responsible for lexical analysis (tokenization), parsing (AST construction),
and all token/keyword definitions used throughout the interpreter.
"""

from .tokens import Token, TokenType
from .keywords import KEYWORDS, DATATYPES
from .lexer import Lexer
from .parser import Parser
from .ast_nodes import (
    Node, ProgramNode, BlockNode,
    NumberNode, StringNode, BoolNode, NullNode,
    VariableNode, AssignNode,
    BinaryOpNode, UnaryOpNode, PostfixOpNode,
    PrintNode, IfNode, WhileNode,
    ListNode, DictNode, SetNode, IndexNode,
    FunctionNode, ParamNode, CallNode, ReturnNode,
    MethodCallNode, GetAttrNode,
    GlobalNode, NonLocalNode,
    MatchNode, MatchCaseNode,
    ResultConstructorNode, ResultMethodCallNode, KharabiNode,
)

__all__ = [
    "Token", "TokenType",
    "KEYWORDS", "DATATYPES",
    "Lexer", "Parser",
    # AST nodes
    "Node", "ProgramNode", "BlockNode",
    "NumberNode", "StringNode", "BoolNode", "NullNode",
    "VariableNode", "AssignNode",
    "BinaryOpNode", "UnaryOpNode", "PostfixOpNode",
    "PrintNode", "IfNode", "WhileNode",
    "ListNode", "DictNode", "SetNode", "IndexNode",
    "FunctionNode", "ParamNode", "CallNode", "ReturnNode",
    "MethodCallNode", "GetAttrNode",
    "GlobalNode", "NonLocalNode",
    "MatchNode", "MatchCaseNode",
    "ResultConstructorNode", "ResultMethodCallNode", "KharabiNode",
]
