from dataclasses import dataclass
from typing import Any, Optional
from ..frontend.tokens import TokenType
from ..errors import NaleJeGhalti, HalndeVaktGhalti

@dataclass(slots=True)
class VariableRecord:
    value: Any
    type: Optional[TokenType]
    element_type: Optional[list[TokenType]] | Optional[TokenType] = None
    is_const: bool = False

class Environment:
    def __init__(self, parent: Optional['Environment'] = None):
        self.records: dict[str, VariableRecord] = {}
        self.parent = parent
        self.global_names = set()
        self.nonlocal_names = set()
    
    def define(self, name: str, value: Any, var_type: Optional[TokenType] = None, is_const: bool = False, element_type: Optional[list[TokenType]] | Optional[TokenType] = None):
        """Register a new variable in the CURRENT scope."""
        record = VariableRecord(value=value, type=var_type, is_const=is_const, element_type=element_type)
        self.records[name] = record
        return value
    
    def lookup_record(self, name: str, node, code: str) -> VariableRecord:
        """Helper to find the actual Record object in the chain."""
        if name in self.records:
            return self.records[name]
        
        if self.parent:
            return self.parent.lookup_record(name, node, code)
        if node:
            raise NaleJeGhalti(
                details=f"Nalo '{name}' na milio. Cha tawaan sahi likhyo aahe?",
                line=node.line, column=node.column, code_string=code
            )
        else:
            raise NaleJeGhalti(
                details=f"Nalo '{name}' na milio. Cha tawaan sahi likhyo aahe?",
                line=1, column=1, code_string=code
            )
    
    def get_value(self, name: str, node, code: str) -> Any:
        """Returns just the value of a variable."""
        return self.lookup_record(name, node, code).value
    
    def assign(self, name: str, value: Any, node, code: str):
        """Updates an existing record's value."""
        record = self.lookup_record(name, node, code)

        if record.is_const:
            raise HalndeVaktGhalti(
                details=f"'{name}' pakko (const) aahe, eho badli natho saghjay.",
                line=node.line, column=node.column, code_string=code
            )
        record.value = value
        return value
    
    def resolve_scope(self, name):
        if name in self.records:
            return self
        if self.parent:
            return self.parent.resolve_scope(name)
        return None

    def lookup(self, name):
        if name in self.records:
            return self
        return None
