from .base import SdShey, SdType
from ..frontend.tokens import TokenType
from ..errors import QisamJeGhalti, ZeroVindJeGhalti

ADAD_TYPE = SdType("ADAD", TokenType.ADAD)
DAHAI_TYPE = SdType("DAHAI", TokenType.DAHAI)
FAISLO_TYPE = SdType("FAISLO", TokenType.FAISLO)

class SdNumber(SdShey):
    __slots__ = ('value',)
    
    def __init__(self, value):
        super().__init__(DAHAI_TYPE if isinstance(value, float) else ADAD_TYPE)
        self.value = value

    # Numeric protocol - Equality
    def __eq__(self, other):
        if not isinstance(other, SdNumber):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def __ne__(self, other):
        if not isinstance(other, SdNumber):
            return SdBool(True)
        return SdBool(self.value != other.value)

    # Numeric protocol - Arithmetic
    def __add__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' saan natho jore saghjay.")
        return SdNumber(self.value + other.value)
    
    def __sub__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad maan '{other.type.name}' natho kaat kare saghjay.")
        return SdNumber(self.value - other.value)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' saan natho zarab kare saghjay.")
        return SdNumber(self.value * other.value)
    
    def __truediv__(self, other):
        from .core import SdResult
        from .strings import SdString
        if not isinstance(other, SdNumber):
            return SdResult(SdResult.GHALTI, SdString(f"Adad khe '{other.type.name}' saan natho vand (divide) kare saghjay."), "QisamJeGhalti")
        if other.value == 0:
            return SdResult(SdResult.GHALTI, SdString("Zero (0) saan vand natho kare saghjay."), "ZeroVindJeGhalti")
        return SdResult(SdResult.OK, SdNumber(self.value / other.value))
    
    def __div__(self, other):
        return self.__truediv__(other)
    
    def __floordiv__(self, other):
        from .core import SdResult
        from .strings import SdString
        if not isinstance(other, SdNumber):
            return SdResult(SdResult.GHALTI, SdString(f"Adad khe '{other.type.name}' saan puro vand natho kare saghjay."))
        if other.value == 0:
            return SdResult(SdResult.GHALTI, SdString("Zero (0) saan vand natho kare saghjay."))
        return SdResult(SdResult.OK, SdNumber(self.value // other.value))
    
    def __mod__(self, other):
        from .core import SdResult
        from .strings import SdString
        if not isinstance(other, SdNumber):
            return SdResult(SdResult.GHALTI, SdString(f"'{other.type.name}' saan pachi (remainder) natho kadhi saghjay."))
        if other.value == 0:
            return SdResult(SdResult.GHALTI, SdString("Zero (0) saan pachi natho kadhi saghjay."))
        return SdResult(SdResult.OK, SdNumber(self.value % other.value))
    
    def __pow__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"'{other.type.name}' saan power nathi kare saghjay.")
        return SdNumber(self.value ** other.value)
    
    # Numeric protocol - Comparison
    def __gt__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value > other.value)
    
    def __lt__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value < other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value >= other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value <= other.value)
    
    # Numeric protocol - Bitwise
    def __and__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad aen '{other.type.name}' je vich mein 'aen' operation natho kare saghjay.")
        return SdNumber(int(self.value) & int(other.value))
    
    def __or__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad aen '{other.type.name}' je vich mein 'ya' operation natho kare saghjay.")
        return SdNumber(int(self.value) | int(other.value))
    
    # Numeric protocol - Unary
    def __neg__(self):
        return SdNumber(-self.value)
    
    def __pos__(self):
        return SdNumber(+self.value)
    
    def __abs__(self):
        return SdNumber(abs(self.value))
    
    def __invert__(self):
        return SdNumber(~int(self.value))
    
    def __int__(self):
        return int(self.value)
    
    def __float__(self):
        return float(self.value)
    
    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)
    
class SdBool(SdShey):
    __slots__ = ('value',)
    
    def __init__(self, value):
        super().__init__(FAISLO_TYPE)
        self.value = value

    # Boolean protocol - Equality
    def __eq__(self, other):
        if not isinstance(other, SdBool):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def __ne__(self, other):
        if not isinstance(other, SdBool):
            return SdBool(True)
        return SdBool(self.value != other.value)
    
    # Boolean protocol - Logical operations
    def __and__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti("Faislo khe sirf biye Faislo saan 'aen' kare saghjay tho.")
        return SdBool(self.value and other.value)
    
    def __or__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti("Faislo khe sirf biye Faislo saan 'ya' kare saghjay tho.")
        return SdBool(self.value or other.value)
    
    def __invert__(self):
        return SdBool(not self.value)
    
    # Comparison protocol
    def __lt__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value < other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value <= other.value)
    
    def __gt__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value > other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ji '{other.type.name}' saan bhet nathi kare saghjay.")
        return SdBool(self.value >= other.value)
    
    def __str__(self):
        return "such" if self.value else "koorh"

    def __hash__(self):
        return hash(self.value)
    
    def __bool__(self):
        return bool(self.value)
