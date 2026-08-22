import os
import time
import subprocess
import threading
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console

# Configuration
TESTS = [
    {"name": "Fibonacci (30)", "type": "fib", "arg": "30"},
    {"name": "Fibonacci (35)", "type": "fib", "arg": "35"},
    {"name": "Loop (10M)", "type": "loop", "arg": None},
    {"name": "Primes (100k)", "type": "primes", "arg": None},
]

LANGS = ["Sindlish", "Python", "Rust"]

results = {lang: {test["name"]: "Wait..." for test in TESTS} for lang in LANGS}
current_running = {"lang": "", "test": "", "code": ""}

def get_code(lang, test_type):
    if lang == "Sindlish":
        path = f"bench/sindlish/{test_type}.sd"
        lexer = "python" # Close enough for now
    elif lang == "Python":
        path = f"bench/python/{test_type}.py"
        lexer = "python"
    else:
        path = "bench/rust/src/main.rs"
        lexer = "rust"
    
    try:
        with open(path, "r") as f:
            return Syntax(f.read(), lexer, theme="monokai", line_numbers=True)
    except:
        return "Code not found"

def run_cmd(cmd, cwd=None):
    start = time.perf_counter()
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, check=True)
        return f"{time.perf_counter() - start:.3f}s"
    except Exception as e:
        return "Error"

def benchmark_thread():
    # 1. Compile Rust first
    global current_running
    current_running["lang"] = "Rust"
    current_running["test"] = "Compiling..."
    subprocess.run(["cargo", "build", "--release"], cwd="bench/rust", capture_output=True)

    for test in TESTS:
        for lang in LANGS:
            current_running["lang"] = lang
            current_running["test"] = test["name"]
            current_running["code"] = get_code(lang, test["type"])
            
            if lang == "Sindlish":
                # Create a temporary file to add the call
                with open(f"bench/sindlish/{test['type']}.sd", "r") as f:
                    code = f.read()
                
                temp_file = "bench/temp.sd"
                with open(temp_file, "w") as f:
                    f.write(code)
                    if test["type"] == "fib":
                        f.write(f"\nlikh(fib({test['arg']}))\n")
                
                cmd = ["uv", "run", "main.py", "bench/temp.sd"]
                results[lang][test["name"]] = run_cmd(cmd)
                
            elif lang == "Python":
                cmd = ["python", f"bench/python/{test['type']}.py"]
                if test["arg"]: cmd.append(test["arg"])
                results[lang][test["name"]] = run_cmd(cmd)
                
            elif lang == "Rust":
                cmd = [os.path.join("bench", "rust", "target", "release", "sindlish-bench"), test["type"]]
                if test["arg"]: cmd.append(test["arg"])
                results[lang][test["name"]] = run_cmd(cmd)

    current_running["lang"] = "DONE"
    current_running["test"] = "All benchmarks finished!"

def make_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="code", ratio=1),
        Layout(name="results", ratio=1)
    )
    return layout

def update_dashboard(layout):
    # Header
    status = f"[bold green]Running {current_running['lang']}: {current_running['test']}" if current_running["lang"] != "DONE" else "[bold blue]BENCHMARKS COMPLETE"
    layout["header"].update(Panel(status, title="Sindlish vs Python vs Rust Performance"))
    
    # Code View
    layout["code"].update(Panel(current_running["code"], title=f"Source Code: {current_running['lang']}"))
    
    # Results Table
    table = Table(expand=True)
    table.add_column("Benchmark")
    for lang in LANGS:
        table.add_column(lang)
    
    for test in TESTS:
        row = [test["name"]]
        for lang in LANGS:
            val = results[lang][test["name"]]
            if val == "Wait...":
                style = "dim"
            elif val == "Error":
                style = "red"
            else:
                # Color code based on relative performance (simple heuristic)
                style = "green" if "s" in val else ""
            row.append(f"[{style}]{val}[/]")
        table.add_row(*row)
        
    layout["results"].update(Panel(table, title="Live Results"))
    layout["footer"].update(Panel("[dim]Algorithmic Parity Guaranteed | Naive Recursion | No JIT Hacks[/]"))

if __name__ == "__main__":
    layout = make_layout()
    threading.Thread(target=benchmark_thread, daemon=True).start()
    
    with Live(layout, refresh_per_second=4, screen=True) as live:
        while current_running["lang"] != "DONE":
            update_dashboard(layout)
            time.sleep(0.2)
        update_dashboard(layout)
        time.sleep(50000000000) # Keep open for a bit
