import os
import time
import subprocess

# Configuration
TESTS = [
    {"name": "Fibonacci (20)", "type": "fib", "arg": "20"},
    {"name": "Fibonacci (25)", "type": "fib", "arg": "25"},
    {"name": "Fibonacci (30)", "type": "fib", "arg": "30"},
    {"name": "Loop (100k)", "type": "loop", "arg": None},
    {"name": "Primes (5k)", "type": "primes", "arg": None},
]

LANGS = ["Rust", "Python", "Sindlish"]

def run_cmd(cmd, cwd=None):
    start = time.perf_counter()
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, check=True)
        return f"{time.perf_counter() - start:.3f}s"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("=== Sindlish Performance Benchmark (Standard Mode) ===")
    
    print("\n[1/3] Compiling Rust (Release)...")
    subprocess.run(["cargo", "build", "--release"], cwd="bench/rust", capture_output=True)
    
    results = {}
    
    for test in TESTS:
        print(f"\n--- Running: {test['name']} ---")
        results[test['name']] = {}
        for lang in LANGS:
            print(f"  > {lang}...", end="", flush=True)
            
            if lang == "Sindlish":
                with open(f"bench/sindlish/{test['type']}.sd", "r") as f:
                    code = f.read()
                temp_file = "bench/temp.sd"
                with open(temp_file, "w") as f:
                    f.write(code)
                    if test["type"] == "fib":
                        f.write(f"\nlikh(fib({test['arg']}))\n")
                cmd = ["uv", "run", "python", "main.py", "bench/temp.sd"]
                
            elif lang == "Python":
                cmd = ["uv", "run", "python", f"bench/python/{test['type']}.py"]
                if test["arg"]: cmd.append(test["arg"])
                
            elif lang == "Rust":
                cmd = [os.path.join("bench", "rust", "target", "release", "sindlish-bench"), test["type"]]
                if test["arg"]: cmd.append(test["arg"])
            
            res = run_cmd(cmd)
            results[test['name']][lang] = res
            print(f" {res}")

    print("\n\n" + "="*50)
    print("FINAL RESULTS COMPARISON")
    print("="*50)
    header = f"{'Benchmark':<20} | {'Rust':<10} | {'Python':<10} | {'Sindlish':<10}"
    print(header)
    print("-" * len(header))
    for test_name in results:
        res = results[test_name]
        print(f"{test_name:<20} | {res['Rust']:<10} | {res['Python']:<10} | {res['Sindlish']:<10}")
    print("="*50)
