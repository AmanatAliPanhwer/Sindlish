import os
import sys
import re

# Ensure the interpreter modules are in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_COMPLETION,
    PublishDiagnosticsParams,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    Position,
    Range,
    DiagnosticSeverity,
)

from pygls.workspace import TextDocument

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.resolver import Resolver
from interpreter.compiler import Compiler
from interpreter.vm import VM
from interpreter.env import Environment
from interpreter.tokens import TokenType
from interpreter.keywords import KEYWORDS
from interpreter.builtins import SimpleBuiltins, MethodBuiltins

server = LanguageServer("sindlish-lsp", "v1.0")

def create_globals_env():
    globals_env = Environment()
    simple_handler = SimpleBuiltins()
    for name, func in simple_handler.get_all().items():
        globals_env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return globals_env

def _report_diagnostic(ls, uri, e, diagnostics):
    msg = str(e)
    # Strip ANSI escape codes
    msg = re.sub(r"\x1b\[[0-9;]*m", "", msg)
    
    # Extract core error message
    lines = [l.strip() for l in msg.split('\n') if l.strip()]
    core_msg = lines[0] if lines else "Unknown Error"
    
    line = 1
    m = re.search(r"Line (\d+)", msg, re.IGNORECASE)
    if m:
        line = int(m.group(1))

    d = Diagnostic(
        range=Range(
            start=Position(line=line - 1, character=0),
            end=Position(line=line - 1, character=100),
        ),
        message=core_msg,
        source="Sindlish",
        severity=DiagnosticSeverity.Error,
    )
    diagnostics.append(d)

def _validate(ls: LanguageServer, params):
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    source = text_doc.source.replace('\r\n', '\n')
    diagnostics = []

    try:
        lexer = Lexer(source)
        tokens = lexer.generate_tokens()

        parser = Parser(tokens, source)
        ast = parser.parse()

        resolver = Resolver(source)
        resolver.resolve(ast)

        compiler = Compiler(source)
        instructions, constants, line_col_map = compiler.compile(ast)

        globals_env = create_globals_env()
        vm = VM(
            source,
            instructions,
            constants,
            globals_env,
            getattr(ast, "slot_count", 0),
            getattr(resolver, "slot_metadata", {}),
            line_col_map,
        )
        vm.run()
    except Exception as e:
        _report_diagnostic(ls, text_doc.uri, e, diagnostics)
    
    ls.text_document_publish_diagnostics(
        PublishDiagnosticsParams(uri=text_doc.uri, diagnostics=diagnostics)
    )

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls, params):
    _validate(ls, params)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params):
    _validate(ls, params)

@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(ls, params: CompletionParams):
    items = []
    for k in KEYWORDS:
        items.append(CompletionItem(label=k, kind=CompletionItemKind.Keyword))
    simple = SimpleBuiltins().get_all()
    for f in simple:
        items.append(CompletionItem(label=f, kind=CompletionItemKind.Function))
    methods = MethodBuiltins().get_all()
    for m in methods:
        items.append(CompletionItem(label=m, kind=CompletionItemKind.Method))
    return CompletionList(is_incomplete=False, items=items)

if __name__ == "__main__":
    server.start_io()
