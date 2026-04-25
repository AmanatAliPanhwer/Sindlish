"""
Sindlish Interpreter — Public API.

Provides the Interpreter facade class that encapsulates the full
pipeline: lex → parse → resolve → compile → execute.
"""

from .frontend.lexer import Lexer
from .frontend.parser import Parser
from .frontend.tokens import TokenType
from .analysis.resolver import Resolver
from .backend.compiler import Compiler
from .backend.vm import VM
from .runtime.env import Environment
from .runtime.builtins import SimpleBuiltins
from .errors import ErrorReporter, SindhiBaseError
import sys


class Interpreter:
    """
    High-level facade for running Sindlish source code.

    Usage:
        interp = Interpreter()
        interp.run_source(code_string)
    """

    def __init__(self):
        self._globals_env = self._create_globals_env()

    @staticmethod
    def _create_globals_env() -> Environment:
        """Create and populate the global environment with built-in functions."""
        globals_env = Environment()
        simple_handler = SimpleBuiltins()
        for name, func in simple_handler.get_all().items():
            globals_env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
        return globals_env

    def run_source(self, code: str) -> VM:
        """
        Run Sindlish source code through the full pipeline.

        Returns the VM instance after execution (for inspection/testing).
        """
        # 1. Lex
        lexer = Lexer(code)
        tokens = lexer.generate_tokens()

        # 2. Parse
        parser = Parser(tokens, code)
        ast = parser.parse()

        # 3. Resolve
        resolver = Resolver(code)
        resolver.resolve(ast)

        # 4. Compile
        compiler = Compiler(code)
        instructions, constants, line_col_map = compiler.compile(ast)

        # 5. Execute
        vm = VM(
            code, instructions, constants,
            self._globals_env,
            getattr(ast, "slot_count", 0),
            resolver.slot_metadata,
            line_col_map,
        )
        try:
            vm.run()
        except SindhiBaseError as e:
            ErrorReporter.report(e)
            sys.exit(1)
        except Exception as e:
            print(f"Internal Error: {e}")
            sys.exit(1)
        return vm


__all__ = ["Interpreter"]
