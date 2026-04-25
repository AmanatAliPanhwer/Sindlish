import os
import sys
import re

# Ensure the interpreter modules are in the python path
# 1. Check if we are running in the bundled extension (server/interpreter)
# 2. Check if we are running in the development workspace (../../interpreter)
current_dir = os.path.dirname(__file__)
bundled_path = current_dir
dev_path = os.path.abspath(os.path.join(current_dir, "..", ".."))

if os.path.exists(os.path.join(bundled_path, "interpreter")):
    sys.path.insert(0, bundled_path)
else:
    sys.path.insert(0, dev_path)

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

from interpreter import Lexer, Parser, Resolver, Compiler, VM, TokenType
from interpreter.runtime.env import Environment
from interpreter.frontend.keywords import KEYWORDS
from interpreter.runtime.builtins import SimpleBuiltins
from interpreter.objects.collections import SdList, SdDict, SdSet

server = LanguageServer("sindlish-lsp", "v1.0")

def create_globals_env():
    globals_env = Environment()
    simple_handler = SimpleBuiltins()
    for name, func in simple_handler.get_all().items():
        globals_env.define(name, value=func, var_type=TokenType.KAAM, is_const=True)
    return globals_env

from interpreter.errors import SindhiBaseError

def _report_diagnostic(ls, uri, e, diagnostics, source):
    if isinstance(e, SindhiBaseError) and e.line is not None:
        line = e.line
        col = e.column if e.column is not None else 1
        
        # Calculate range: find the word at the position
        start_char = col - 1
        end_char = col
        
        lines = source.split('\n')
        if 0 < line <= len(lines):
            error_line = lines[line - 1]
            # Try to find the extent of the word/token
            match = re.search(r'[a-zA-Z0-9_]+', error_line[start_char:])
            if match:
                end_char = start_char + match.end()
            else:
                end_char = len(error_line)
        
        d = Diagnostic(
            range=Range(
                start=Position(line=line - 1, character=start_char),
                end=Position(line=line - 1, character=max(start_char + 1, end_char)),
            ),
            message=e.details,
            source="Sindlish",
            severity=DiagnosticSeverity.Error,
        )
        diagnostics.append(d)
        return

    # Fallback for generic exceptions
    msg = str(e)
    msg = re.sub(r"\x1b\[[0-9;]*m", "", msg)
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
    
    # Store state for completions/hover
    ls.current_ast = None
    ls.current_resolver = None
    ls.current_source = source

    try:
        lexer = Lexer(source)
        tokens = lexer.generate_tokens()

        parser = Parser(tokens, source)
        ast = parser.parse()

        resolver = Resolver(source)
        resolver.resolve(ast)

        compiler = Compiler(source)
        instructions, constants, line_col_map = compiler.compile(ast)

        #globals_env = create_globals_env()
        #vm = VM(
        #    source,
        #    instructions,
        #    constants,
        #    globals_env,
        #    getattr(ast, "slot_count", 0),
        #    getattr(resolver, "slot_metadata", {}),
        #    line_col_map,
        #)
        #vm.run()
        
        # Save successful state for hover/completion
        ls.current_ast = ast
        ls.current_resolver = resolver
    except Exception as e:
        _report_diagnostic(ls, text_doc.uri, e, diagnostics, source)
    
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
def completions(ls: LanguageServer, params: CompletionParams):
    items = []
    
    # 1. Keywords
    for k in KEYWORDS:
        items.append(CompletionItem(label=k, kind=CompletionItemKind.Keyword))
    
    # 2. Built-ins
    simple = SimpleBuiltins().get_all()
    for f in simple:
        items.append(CompletionItem(label=f, kind=CompletionItemKind.Function, detail="Built-in Function"))
        
    # 3. Local Symbols (from Resolver)
    if hasattr(ls, 'current_resolver') and ls.current_resolver:
        for sym in ls.current_resolver.symbols:
            kind = CompletionItemKind.Function if sym["kind"] == "function" else CompletionItemKind.Variable
            items.append(CompletionItem(
                label=sym["name"], 
                kind=kind, 
                detail=f"Local {sym['kind']} (line {sym['line']})"
            ))

    # 4. Method Completion (after dot)
    text_doc = ls.workspace.get_text_document(params.text_document.uri)
    lines = text_doc.source.splitlines()
    if params.position.line < len(lines):
        line = lines[params.position.line]
        before_cursor = line[:params.position.character]
        
        if before_cursor.endswith('.'):
            # We are completing a method.
            # Only suggest methods in this case.
            method_items = []
            
            # Map of common methods to help the user
            # In a full LSP we'd check the type of the object before '.', 
            # but here we'll provide all native methods for better UX.
            native_methods = {
                # Strings
                "vada": "Convert to uppercase",
                "nanda": "Convert to lowercase",
                "hata": "Remove whitespace",
                "badla": "Replace text",
                "shamil": "Check if contains",
                # Lists
                "wadha": "Add element to list",
                "kadh": "Remove and return element",
                "saaf": "Clear all elements",
                "ulat": "Reverse the list",
                "tartib": "Sort the list",
                # Sets
                "mela": "Union of sets",
                "farq": "Difference of sets",
                # Results
                "lazmi": "Unwrap value or panic",
                "bachao": "Provide fallback for error",
                "ok": "Check if success",
                "ghalti": "Check if error",
            }
            
            for m_name, doc in native_methods.items():
                method_items.append(CompletionItem(
                    label=m_name,
                    kind=CompletionItemKind.Method,
                    detail=f"Native Method: {doc}"
                ))
            return CompletionList(is_incomplete=False, items=method_items)
            
    return CompletionList(is_incomplete=False, items=items)

from lsprotocol.types import TEXT_DOCUMENT_HOVER, Hover, TEXT_DOCUMENT_DEFINITION, Location

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params):
    uri = params.text_document.uri
    pos = params.position
    
    if not hasattr(ls, 'current_resolver') or not ls.current_resolver:
        return None
        
    # Find symbol at position
    for sym in ls.current_resolver.symbols:
        if sym["line"] == pos.line + 1:
            # Check if cursor is within the name
            start = sym["col"] - 1
            end = start + len(sym["name"])
            if start <= pos.character <= end:
                type_info = sym["type"].name.lower() if sym["type"] else "any"
                content = f"**{sym['name']}** ({sym['kind']})\n\nType: `{type_info}`"
                return Hover(contents=content)
    return None

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: LanguageServer, params):
    uri = params.text_document.uri
    pos = params.position
    
    if not hasattr(ls, 'current_resolver') or not ls.current_resolver:
        return None
        
    # This is a bit tricky without a full reference map, but we can check if 
    # the cursor is on an identifier and then find its definition in the symbols list.
    text_doc = ls.workspace.get_text_document(uri)
    line_content = text_doc.source.splitlines()[pos.line]
    
    # Simple regex to find word under cursor
    match = re.search(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line_content[max(0, pos.character-20):pos.character+20])
    if not match:
        return None
        
    # Find word under cursor more precisely
    word = None
    for m in re.finditer(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', line_content):
        if m.start() <= pos.character <= m.end():
            word = m.group()
            break
            
    if word:
        for sym in ls.current_resolver.symbols:
            if sym["name"] == word:
                return Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=sym["line"] - 1, character=sym["col"] - 1),
                        end=Position(line=sym["line"] - 1, character=sym["col"] - 1 + len(sym["name"]))
                    )
                )
    return None

if __name__ == "__main__":
    server.start_io()
