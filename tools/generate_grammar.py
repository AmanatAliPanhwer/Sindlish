import os
import json
import sys

# Ensure we can import the interpreter package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interpreter.frontend.keywords import KEYWORDS, DATATYPES
from interpreter.runtime.builtins import SimpleBuiltins
from interpreter.frontend.tokens import TokenType
from interpreter.objects.numbers import ADAD_TYPE, DAHAI_TYPE, FAISLO_TYPE
from interpreter.objects.strings import LAFZ_TYPE
from interpreter.objects.collections import FEHRIST_TYPE, LUGHAT_TYPE, MAJMUO_TYPE
from interpreter.objects.core import KHALI_TYPE, RESULT_TYPE

def generate_grammar():
    # Keywords
    control_keywords = [
        "agar", "warna", "jistain", "halando", "tor", 
        "koshish", "bachao", "aakhir"
    ]
    # We pull from our KEYWORDS dict to ensure consistency, 
    # but manually categorize them for better TextMate scopes.
    all_kw = list(KEYWORDS.keys())
    
    # Types
    types_list = [k for k, v in KEYWORDS.items() if v in DATATYPES]
    types_pattern = "|".join(types_list)
    
    # Builtin functions and methods
    simple = list(SimpleBuiltins().get_all().keys())
    # Collect methods from all types
    all_types = [
        ADAD_TYPE, DAHAI_TYPE, FAISLO_TYPE, LAFZ_TYPE,
        FEHRIST_TYPE, LUGHAT_TYPE, MAJMUO_TYPE, KHALI_TYPE, RESULT_TYPE
    ]
    methods = set()
    for t in all_types:
        methods.update(t._methods.keys())
    
    # Add other logical keywords like aen (and), ya (or), nah (not)
    logical = ["aen", "ya", "nah"]
    
    # Other control or functional words
    control_pattern = "(?:" + "|".join([k for k in all_kw if k not in types_list and k not in logical]) + ")\\b"
    logical_pattern = "(?:" + "|".join(logical) + ")\\b"
    functions_pattern = "\\b(?:" + "|".join(simple) + ")\\b"
    methods_pattern = "\\.\\s*(?:" + "|".join(sorted(list(methods))) + ")\\b"

    grammar = {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "Sindlish",
        "patterns": [
            {"include": "#comments"},
            {"include": "#strings"},
            {"include": "#numbers"},
            {"include": "#keywords"},
            {"include": "#types"},
            {"include": "#builtins"},
            {"include": "#function-defs"},
            {"include": "#function-calls"},
            {"include": "#variables"}
        ],
        "repository": {
            "comments": {
                "patterns": [
                    # Change this if you change your multiline comments
                    {
                        "begin": "/\\*",
                        "end": "\\*/",
                        "name": "comment.block.sindlish"
                    },
                    # Change this if you change your single-line comment (#)
                    {
                        "match": "#.*$",
                        "name": "comment.line.number-sign.sindlish"
                    }
                ]
            },
            # Change these if you define new string modifiers like backticks (`)
            "strings": {
                "patterns": [
                    {
                        "begin": "\"\"\"",
                        "end": "\"\"\"",
                        "name": "string.quoted.triple.sindlish"
                    },
                    {
                        "begin": "\"",
                        "end": "\"",
                        "name": "string.quoted.double.sindlish",
                        "patterns": [
                            {
                                "match": "\\\\.",
                                "name": "constant.character.escape.sindlish"
                            }
                        ]
                    },
                    {
                        "begin": "'",
                        "end": "'",
                        "name": "string.quoted.single.sindlish",
                        "patterns": [
                            {
                                "match": "\\\\.",
                                "name": "constant.character.escape.sindlish"
                            }
                        ]
                    }
                ]
            },
            "numbers": {
                "match": "\\b[0-9]+(?:\\.[0-9]+)?\\b|\\B\\.[0-9]+\\b",
                "name": "constant.numeric.sindlish"
            },
            "types": {
                "match": f"\\b(?:{types_pattern})\\b",
                "name": "support.type.sindlish"
            },
            "keywords": {
                "patterns": [
                    {
                        "match": f"\\b{control_pattern}",
                        "name": "keyword.control.sindlish"
                    },
                    {
                        "match": f"\\b{logical_pattern}",
                        "name": "keyword.operator.logical.sindlish"
                    }
                ]
            },
            "builtins": {
                "patterns": [
                    {
                        "match": functions_pattern,
                        "name": "support.function.sindlish"
                    },
                    {
                        "match": methods_pattern,
                        "name": "entity.name.function.sindlish"
                    }
                ]
            },
            "function-defs": {
                "match": "\\b(kaam)\\s+([a-zA-Z_][a-zA-Z0-9_]*)\\b",
                "captures": {
                    "1": { "name": "keyword.control.sindlish" },
                    "2": { "name": "entity.name.function.sindlish" }
                }
            },
            "function-calls": {
                "match": "\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*(?=\\()",
                "name": "entity.name.function.sindlish"
            },
            "variables": {
                "patterns": [
                    {
                        "match": "\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*(?==)",
                        "name": "variable.other.sindlish"
                    }
                ]
            }
        },
        "scopeName": "source.sindlish"
    }

    out_path = os.path.join(os.path.dirname(__file__), '..', 'vscode-extension', 'syntaxes', 'sindlish.tmLanguage.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(grammar, f, indent=4)
        
    print(f"Grammar successfully written to {out_path}")

    # Generate the Completion Definitions JSON
    defs = {
        "keywords": all_kw,
        "functions": simple,
        "methods": sorted(list(methods))
    }
    defs_path = os.path.join(os.path.dirname(__file__), '..', 'vscode-extension', 'syntaxes', 'sindlish-definitions.json')
    with open(defs_path, 'w', encoding='utf-8') as f:
        json.dump(defs, f, indent=4)
        
    print(f"Definitions successfully written to {defs_path}")

    # Generate VS Code Native Language Configuration
    # This controls editor behavior like Ctrl+/ and auto-closing brackets!
    lang_config = {
        "comments": {
            "lineComment": "#",               # If you change this, Ctrl+/ will still work!
            "blockComment": ["/*", "*/"]      # Same with Shift+Alt+A
        },
        "brackets": [
            ["{", "}"],  # Add custom block wrappers here if you invent them
            ["[", "]"],
            ["(", ")"]
        ],
        "autoClosingPairs": [
            {"open": "{", "close": "}"},
            {"open": "[", "close": "]"},
            {"open": "(", "close": ")"},
            {"open": "\"", "close": "\"", "notIn": ["string"]},
            {"open": "'", "close": "'", "notIn": ["string", "comment"]}
        ],
        "surroundingPairs": [
            ["{", "}"],
            ["[", "]"],
            ["(", ")"],
            ["\"", "\""],
            ["'", "'"]
        ]
    }
    lang_path = os.path.join(os.path.dirname(__file__), '..', 'vscode-extension', 'language-configuration.json')
    with open(lang_path, 'w', encoding='utf-8') as f:
        json.dump(lang_config, f, indent=4)
        
    print(f"Language configuration successfully written to {lang_path}")

if __name__ == "__main__":
    generate_grammar()
