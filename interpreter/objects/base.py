from ..errors import QisamJeGhalti, HalndeVaktGhalti, NaleJeGhalti, ZeroVindJeGhalti, IndexJeGhalti, LikhaiJeGhalti
from ..tokens import TokenType

class SdType:
    """
    Represents the Type Object (e.g., ADAD, LAFZ).
    Acts as the 'class' for Sindlish objects.
    """
    def __init__(self, name: str, token_type: TokenType):
        self.name = name
        self.token_type = token_type
    
    def __repr__(self):
        return f"<SdType '{self.name}'>"
    
class SdObject:
    """
    The root of the Sindlish Object hierarchy.
    Every variable, number, string, and function in Sindlish will inherit from this.
    """
    def __init__(self, type_obj: SdType):
        self.ref_count = 1
        self.type = type_obj

        self.attributes = {}
        
        # Register default operations for all types
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        self.attributes["__inc__"] = self._inc
    
    def __hash__(self):
        # Default to id-based hashing for mutable objects
        return id(self)
    
    # Default operation implementations
    def _eq(self, args):
        from .primitives import SdBool
        other = args[0]
        if not isinstance(other, self.__class__):
            return SdBool(False)
        # Use id comparison to avoid infinite recursion
        return SdBool(id(self) == id(other))
    
    def _ne(self, args):
        from .primitives import SdBool
        other = args[0]
        if not isinstance(other, self.__class__):
            return SdBool(True)
        # Use id comparison to avoid infinite recursion
        return SdBool(id(self) != id(other))
    
    def _inc(self, args):
        """Default increment returns a copy of the object"""
        import copy
        return copy.copy(self)
    
    def call_method(self, name: str, args: list, node=None, code = ""):
        """
        Dispatches method calls and maps Python exceptions 
        to Sindlish-specific error classes.
        """
        method = self.attributes.get(name)
        
        # Safe defaults when node is None
        line = node.line if node else 1
        column = node.column if node else 1

        if not method:
            # Fallback: check if the type object has the method (Day 5 Roadmap)
            raise QisamJeGhalti(
                details=f"'{self.type.name}' object mein '{name}' nale jo ko bh method na aahe.",
                line=line,
                column=column,
                code_string=code
            )
        
        try:
            return method(args)
        except (QisamJeGhalti, HalndeVaktGhalti, NaleJeGhalti, ZeroVindJeGhalti, IndexJeGhalti, LikhaiJeGhalti):
            raise
        except TypeError as e:
            raise QisamJeGhalti(str(e), line, column, code)
        except Exception as e:
            raise HalndeVaktGhalti(str(e), line, column, code)
        
    def __str__(self):
        return f"<{self.type.name} object>"
