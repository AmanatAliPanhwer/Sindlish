"""
Built-in functions for the Sindlish language.

Standalone functions available in the global scope: lambi, likh, majmuo.
"""

from ..objects import SdNumber, SdNull, SdBool, SdDict, SdList, SdSet, SdString
from ..errors import QisamJeGhalti, HalndeVaktGhalti


def _register(registry_dict):
    """Decorator to auto-register functions into a dictionary."""
    def decorator(func):
        registry_dict[func.__name__] = func
        return func
    return decorator


class SimpleBuiltins:
    """Built-in standalone functions available in the global scope."""

    functions = {}

    @_register(functions)
    def majmuo(self, args):
        """Create a new set from arguments."""
        if len(args) == 0:
            return SdSet(set())
        if len(args) == 1:
            return SdSet(set(args[0]))
        raise HalndeVaktGhalti("lambi() khe 0 ya 1 argument khapay.")

    @_register(functions)
    def lambi(self, args):
        """Return the length of a collection or string."""
        if len(args) != 1:
            raise HalndeVaktGhalti("lambi() khe sirf 1 argument khapay.")
        obj = args[0]
        if hasattr(obj, 'elements'):
            return SdNumber(len(obj.elements))
        if hasattr(obj, 'value') and isinstance(obj.value, (str, dict)):
            return SdNumber(len(obj.value))
        raise QisamJeGhalti(f"'{obj.type.name}' ji lambai nathi mapay saghjay.")

    @_register(functions)
    def likh(self, args):
        """Print values to stdout."""
        print(*(str(arg) for arg in args))
        return SdNull()

    def get_all(self):
        """Return all registered built-in functions."""
        return self.functions
