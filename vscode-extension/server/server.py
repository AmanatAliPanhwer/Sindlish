import os
import sys

# Add parent to path to find `interpreter` module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    Position,
    Range,
    DiagnosticSeverity
)
import urllib.parse
from pygls.workspace import Document

from interpreter.lexer import Lexer
from interpreter.parser import Parser
from interpreter.keywords import KEYWORDS, DATATYPES
from interpreter.builtins import SimpleBuiltins, MethodBuiltins

server = LanguageServer("sindlish-lsp", "v1.0")

def _validate(ls: LanguageServer, params):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    source = text_doc.source
    diagnostics = []
    
    # Run Lexer
    try:
        lexer = Lexer(source)
        tokens = lexer.generate_tokens()
        
        # Run Parser
        parser = Parser(tokens)
        _ = parser.parse()
    except Exception as e:
        msg = str(e)
        # We try to extract line from standard interpreter errors
        line = 1
        import re
        m = re.search(r'line (\d+)', msg)
        if m:
            line = int(m.group(1))
            
        d = Diagnostic(
            range=Range(
                start=Position(line=line-1, character=0),
                end=Position(line=line-1, character=100)
            ),
            message=msg,
            source="Sindlish",
            severity=DiagnosticSeverity.Error
        )
        diagnostics.append(d)

    ls.publish_diagnostics(text_doc.uri, diagnostics)

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls, params):
    _validate(ls, params)

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params):
    _validate(ls, params)

@server.feature("textDocument/completion")
def completions(ls, params: CompletionParams):
    items = []
    
    # Keywords
    for k in KEYWORDS:
        items.append(CompletionItem(
            label=k,
            kind=CompletionItemKind.Keyword
        ))
        
    # Simple Builtins
    simple = SimpleBuiltins().get_all()
    for f in simple:
        items.append(CompletionItem(
            label=f,
            kind=CompletionItemKind.Function
        ))
        
    # Method Builtins
    methods = MethodBuiltins().get_all()
    for m in methods:
        items.append(CompletionItem(
            label=m,
            kind=CompletionItemKind.Method
        ))

    return CompletionList(
        is_incomplete=False,
        items=items
    )

if __name__ == "__main__":
    server.start_io()
