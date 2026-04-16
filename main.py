from lexer.tokenizer import Lexer
from parser.parser import Parser
from interpreter.executor import Interpreter

code = """
x = 10
agar x > 5:
    likh("Zabardast!")
"""

lexer = Lexer(code)
tokens = lexer.generate_tokens()

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()

interpreter.visit(ast)