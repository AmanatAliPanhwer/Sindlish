from lexer.tokenizer import Lexer
from parser.parser import Parser
from interpreter.executor import Interpreter
import argparse

parser = argparse.ArgumentParser(description="Sindlish interptater")
parser.add_argument("input", help="The .sind file to process")
args = parser.parse_args()

if not args.input.endswith(".sind"):
    raise Exception("file must have .sind extension.")
    
with open(args.input, 'r', encoding="utf-8") as f:
    code = f.read()

lexer = Lexer(code)
tokens = lexer.generate_tokens()

parser = Parser(tokens)
ast = parser.parse()

interpreter = Interpreter()

interpreter.visit(ast)