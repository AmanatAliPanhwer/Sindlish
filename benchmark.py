import time
import io
import sys
from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.resolver import Resolver
from interpreter.executor import Interpreter

def run_test(filename, iterations=10):
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.generate_tokens()
    parser = Parser(tokens, code)
    ast = parser.parse()

    # Case 1: With Resolver (O(1) Slots)
    resolver = Resolver(code)
    resolver.resolve(ast)
    
    start_fast = time.time()
    for _ in range(iterations):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        interpreter = Interpreter(code)
        interpreter.visit(ast)
        sys.stdout = old_stdout
    end_fast = time.time()
    
    # Case 2: Without Resolver (O(D) Dicts)
    parser = Parser(tokens, code)
    ast_slow = parser.parse()
    
    start_slow = time.time()
    for _ in range(iterations):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        interpreter = Interpreter(code)
        interpreter.visit(ast_slow)
        sys.stdout = old_stdout
    end_slow = time.time()

    return (end_fast - start_fast), (end_slow - start_slow)

if __name__ == "__main__":
    print("Running Benchmarks...")
    
    # Hello.sd (I/O Heavy)
    fast, slow = run_test("hello.sd", iterations=20)
    print(f"\n[hello.sd - General script]")
    print(f"Slot-Based: {fast:.4f}s")
    print(f"Dict-Based: {slow:.4f}s")
    print(f"Speedup: {slow/fast:.2f}x")

    # Stress_test.sd (CPU/Variable Heavy)
    fast, slow = run_test("stress_test.sd", iterations=5)
    print(f"\n[stress_test.sd - 10,000 iterations loop]")
    print(f"Slot-Based: {fast:.4f}s")
    print(f"Dict-Based: {slow:.4f}s")
    print(f"Speedup: {slow/fast:.2f}x")
