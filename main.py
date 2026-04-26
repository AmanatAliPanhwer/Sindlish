"""Sindlish language interpreter — CLI entry point."""

import argparse
from interpreter import Interpreter
from interpreter.repl import start_repl


def main():
    parser = argparse.ArgumentParser(description="Sindlish interptater")
    parser.add_argument("input", nargs="?", help="The .sd file to process")
    args = parser.parse_args()

    if args.input:
        if not args.input.endswith(".sd"):
            raise Exception("file must have .sd extension.")

        with open(args.input, "r", encoding="utf-8") as f:
            code = f.read()

        interp = Interpreter()
        interp.run_source(code)
    else:
        start_repl()


if __name__ == "__main__":
    main()
