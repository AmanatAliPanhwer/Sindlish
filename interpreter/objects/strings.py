from .base import SdShey, SdType
from ..frontend.tokens import TokenType
from ..errors import QisamJeGhalti
from .numbers import SdBool, SdNumber

LAFZ_TYPE = SdType("LAFZ", TokenType.LAFZ)

class SdString(SdShey):
    __slots__ = ('value',)
    
    def __init__(self, value):
        super().__init__(LAFZ_TYPE)
        self.value = value

    # Sequence protocol - Equality
    def __eq__(self, other):
        if not isinstance(other, SdString):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def __ne__(self, other):
        if not isinstance(other, SdString):
            return SdBool(True)
        return SdBool(self.value != other.value)

    # Sequence protocol - Concatenation/Repetition
    def __add__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ke '{other.type.name}' saan bhet (compare) natho kare saghjay.")
        return SdString(self.value + other.value)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz khe sirf Adad saan zarab kare saghjay tho.")
        return SdString(self.value * int(other.value))
    
    def __rmul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz khe sirf Adad saan zarab kare saghjay tho.")
        return SdString(other.value * self.value)
    
    # Sequence protocol - Comparison
    def __lt__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ke '{other.type.name}' saan bhet (compare) natho kare saghjay.")
        return SdBool(self.value < other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ke '{other.type.name}' saan bhet (compare) natho kare saghjay.")
        return SdBool(self.value <= other.value)
    
    def __gt__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ke '{other.type.name}' saan bhet (compare) natho kare saghjay.")
        return SdBool(self.value > other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ke '{other.type.name}' saan bhet (compare) natho kare saghjay.")
        return SdBool(self.value >= other.value)
    
    # Sequence protocol
    def __len__(self):
        return len(self.value)
    
    def __getitem__(self, index):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Lafz jo index Adad hujjhan lazmi aahe.")
        try:
            return SdString(self.value[int(index.value)])
        except IndexError:
            raise QisamJeGhalti(f"Lafz jo index {int(index.value)} hadd khaan bahar aahe.")
    
    def __contains__(self, item):
        if not isinstance(item, SdString):
            raise QisamJeGhalti("Sirf Lafz gholi saghjan tha.")
        return SdBool(item.value in self.value)
    
    # Container protocol
    def __iter__(self):
        return iter(self.value)
    
    def __str__(self):
        return self.value
    
    def __hash__(self):
        return hash(self.value)
    
    def __bool__(self):
        return bool(self.value)
