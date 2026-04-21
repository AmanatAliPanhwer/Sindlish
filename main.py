from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.resolver import Resolver
from interpreter.executor import Interpreter
import argparse

parser = argparse.ArgumentParser(description="Sindlish interptater")
parser.add_argument("input", help="The .sd file to process")
args = parser.parse_args()

if not args.input.endswith(".sd"):
    raise Exception("file must have .sd extension.")

with open(args.input, "r", encoding="utf-8") as f:
    code = f.read()

lexer = Lexer(code)
tokens = lexer.generate_tokens()

parser = Parser(tokens, code)
ast = parser.parse()

resolver = Resolver(code)
resolver.resolve(ast)

interpreter = Interpreter(code)
interpreter.visit(ast)
