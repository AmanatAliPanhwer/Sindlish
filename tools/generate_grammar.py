import os
import json
import sys

# Ensure we can import the interpreter package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interpreter.keywords import KEYWORDS, DATATYPES
from interpreter.builtins import SimpleBuiltins, MethodBuiltins
from interpreter.tokens import TokenType

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
    methods = list(MethodBuiltins().get_all().keys())
    
    # Add other logical keywords like aen (and), ya (or), nah (not)
    logical = ["aen", "ya", "nah"]
    
    # Other control or functional words
    control_pattern = "(?:" + "|".join([k for k in all_kw if k not in types_list and k not in logical]) + ")\\b"
    logical_pattern = "(?:" + "|".join(logical) + ")\\b"
    functions_pattern = "\\b(?:" + "|".join(simple) + ")\\b"
    methods_pattern = "\\.\\s*(?:" + "|".join(methods) + ")\\b"

    grammar = {
        "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
        "name": "Sindlish",
        "patterns": [
            {"include": "#comments"},
            {"include": "#strings"},
            {"include": "#numbers"},
            {"include": "#keywords"},
            {"include": "#types"},
            {"include": "#builtins"}
        ],
        "repository": {
            "comments": {
                "patterns": [
                    {
                        "begin": "/\\*",
                        "end": "\\*/",
                        "name": "comment.block.sindlish"
                    },
                    {
                        "match": "#.*$",
                        "name": "comment.line.number-sign.sindlish"
                    }
                ]
            },
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
        "methods": methods
    }
    defs_path = os.path.join(os.path.dirname(__file__), '..', 'vscode-extension', 'syntaxes', 'sindlish-definitions.json')
    with open(defs_path, 'w', encoding='utf-8') as f:
        json.dump(defs, f, indent=4)
        
    print(f"Definitions successfully written to {defs_path}")

if __name__ == "__main__":
    generate_grammar()
