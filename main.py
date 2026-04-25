"""Sindlish language interpreter — CLI entry point."""

import argparse
from interpreter import Interpreter


def main():
    parser = argparse.ArgumentParser(description="Sindlish interptater")
    parser.add_argument("input", help="The .sd file to process")
    args = parser.parse_args()

    if not args.input.endswith(".sd"):
        raise Exception("file must have .sd extension.")

    with open(args.input, "r", encoding="utf-8") as f:
        code = f.read()

    interp = Interpreter()
    interp.run_source(code)


if __name__ == "__main__":
    main()
