import sys
import os

# Ensure we can import the interpreter package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interpreter.lexer import Lexer
from interpreter.parser import Parser

def lint(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
    except Exception as e:
        print(f"1:Error reading file {e}")
        return

    try:
        lexer = Lexer(code)
        tokens = lexer.generate_tokens()
        
        parser = Parser(tokens)
        parser.parse()
        print("OK")
    except Exception as e:
        msg = str(e)
        import re
        line = 1
        m = re.search(r'line (\d+)', msg)
        if m:
            line = int(m.group(1))
            
        print(f"{line}:{msg}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lint(sys.argv[1])
