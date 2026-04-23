from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.resolver import Resolver
from interpreter.compiler import Compiler
from interpreter.vm import VM
from interpreter.env import Environment
from interpreter.tokens import TokenType
from interpreter.builtins import SimpleBuiltins
import argparse

# Create and populate the global environment with built-in functions
def create_globals_env():
    globals_env = Environment()
    simple_handler = SimpleBuiltins()
    for name, func in simple_handler.get_all().items():
        globals_env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return globals_env

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

compiler = Compiler(code)
instructions, constants, line_col_map = compiler.compile(ast)

globals_env = create_globals_env()

vm = VM(code, instructions, constants, globals_env, getattr(ast, "slot_count", 0), resolver.slot_metadata, line_col_map)
vm.run()
