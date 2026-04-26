import sys
import os
from typing import Iterable

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import AnyFormattedText

from . import Interpreter
from .frontend.lexer import Lexer as SindlishLexerRaw
from .frontend.tokens import TokenType
from .frontend.keywords import KEYWORDS
from .runtime.builtins import SimpleBuiltins
from .errors import SindhiBaseError

# Define the style for syntax highlighting
sindlish_style = Style.from_dict({
    'keyword': '#ff79c6 bold',      # Pink
    'datatype': '#8be9fd italic',    # Cyan
    'string': '#f1fa8c',            # Yellow
    'number': '#bd93f9',            # Purple
    'comment': '#6272a4',           # Blue-ish gray
    'operator': '#ffb86c',          # Orange
    'identifier': '#f8f8f2',        # White
    'builtin': '#50fa7b',           # Green
})

class SindlishLexer(Lexer):
    def lex_document(self, document):
        def get_line(lineno):
            line = document.lines[lineno]
            tokens = []
            
            import re
            # Regex to match strings, comments, numbers, keywords, and other characters
            # Order matters: comments and strings first
            pattern = re.compile(r"""
                (?P<comment>\#.*) |
                (?P<string>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*') |
                (?P<number>\b\d+(?:\.\d+)?\b) |
                (?P<keyword>\b(?:agar|yawari|warna|jistain|aen|ya|nah|bahari|aalmi|wapas|match|ok|ghalti|kharabi|har|tor|jari|mein)\b) |
                (?P<datatype>\b(?:adad|lafz|dahai|faislo|sach|koorh|khali|pakko|fehrist|lughat|majmuo|kaam)\b) |
                (?P<builtin>\b(?:majmuo|lambi|likh|puch|range)\b) |
                (?P<operator>[+\-*/%^=><!?]+) |
                (?P<identifier>\b[a-zA-Z_]\w*\b) |
                (?P<space>\s+) |
                (?P<other>.)
            """, re.VERBOSE)

            for match in pattern.finditer(line):
                kind = match.lastgroup
                value = match.group()
                
                if kind == 'keyword':
                    tokens.append(('class:keyword', value))
                elif kind == 'datatype':
                    tokens.append(('class:datatype', value))
                elif kind == 'builtin':
                    tokens.append(('class:builtin', value))
                elif kind == 'string':
                    tokens.append(('class:string', value))
                elif kind == 'number':
                    tokens.append(('class:number', value))
                elif kind == 'comment':
                    tokens.append(('class:comment', value))
                elif kind == 'operator':
                    tokens.append(('class:operator', value))
                elif kind == 'identifier':
                    tokens.append(('class:identifier', value))
                else:
                    tokens.append(('', value))
                
            return tokens
        return get_line

class SindlishCompleter(Completer):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.keywords = list(KEYWORDS.keys())
        self.builtins = list(SimpleBuiltins.functions.keys())

    def get_completions(self, document, complete_event) -> Iterable[Completion]:
        word_before_cursor = document.get_word_before_cursor()
        
        # Suggest keywords
        for keyword in self.keywords:
            if keyword.startswith(word_before_cursor):
                yield Completion(keyword, -len(word_before_cursor))
        
        # Suggest builtins
        for builtin in self.builtins:
            if builtin.startswith(word_before_cursor):
                yield Completion(builtin, -len(word_before_cursor))
                
        # Suggest variables from global environment
        for var_name in self.interpreter._globals_env.records.keys():
            if var_name.startswith(word_before_cursor):
                yield Completion(var_name, -len(word_before_cursor))

def is_complete(text: str) -> bool:
    # Check for unclosed braces or parentheses
    braces = 0
    parens = 0
    brackets = 0
    
    # Simple check for strings to avoid counting braces inside them
    # This is a bit naive but works for common cases
    in_string = False
    quote_char = ''
    i = 0
    while i < len(text):
        char = text[i]
        if not in_string:
            if char in ('"', "'"):
                in_string = True
                quote_char = char
            elif char == '{': braces += 1
            elif char == '}': braces -= 1
            elif char == '(': parens += 1
            elif char == ')': parens -= 1
            elif char == '[': brackets += 1
            elif char == ']': brackets -= 1
        else:
            if char == quote_char and (i == 0 or text[i-1] != '\\'):
                in_string = False
        i += 1
        
    if braces > 0 or parens > 0 or brackets > 0:
        return False
        
    # Check if last line ends with a colon
    lines = text.strip().split('\n')
    if lines and lines[-1].strip().endswith(':'):
        return False
        
    return True

def start_repl():
    interpreter = Interpreter()
    session = PromptSession(
        lexer=SindlishLexer(),
        completer=SindlishCompleter(interpreter),
        style=sindlish_style
    )

    print("Sindlish Playground (v0.7.0)")
    print("Type 'exit' or press Ctrl+D to exit.")

    while True:
        try:
            # For multiline, we use a loop or prompt(multiline=True)
            # prompt(multiline=True) is cleaner but behaves differently (need Meta+Enter to submit)
            # Custom logic to continue until complete is more "REPL-like"
            buffer = []
            while True:
                prompt_text = 'sd> ' if not buffer else '... '
                line = session.prompt(prompt_text)
                
                if not buffer and line.strip() == 'exit':
                    return

                buffer.append(line)
                full_text = '\n'.join(buffer)
                
                if is_complete(full_text):
                    text = full_text
                    break
            
            if not text.strip():
                continue
            
            try:
                interpreter.run_source(text, is_repl=True)
            except SindhiBaseError:
                pass
            except Exception as e:
                print(f"Error: {e}")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == '__main__':
    start_repl()
