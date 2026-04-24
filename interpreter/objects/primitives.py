from .base import SdObject, SdType
from ..tokens import TokenType
from ..errors import QisamJeGhalti, ZeroVindJeGhalti

ADAD_TYPE = SdType("ADAD", TokenType.ADAD)
DAHAI_TYPE = SdType("DAHAI", TokenType.DAHAI)
LAFZ_TYPE = SdType("LAFZ", TokenType.LAFZ)
FAISLO_TYPE = SdType("FAISLO", TokenType.FAISLO)
FEHRIST_TYPE = SdType("FEHRIST", TokenType.FEHRIST)
LUGHAT_TYPE = SdType("LUGHAT", TokenType.LUGHAT)
MAJMUO_TYPE = SdType("MAJMUO", TokenType.MAJMUO)
KHALI_TYPE = SdType("KHALI", TokenType.KHALI)

class SdNumber(SdObject):
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
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho jore saghjay.")
        return SdNumber(self.value + other.value)
    
    def __sub__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' natho ghaat kare saghjay.")
        return SdNumber(self.value - other.value)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho zarab kare saghjay.")
        return SdNumber(self.value * other.value)
    
    def __truediv__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho vindaae saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san vindaae natho saghjay.")
        return SdNumber(self.value / other.value)
    
    def __div__(self, other):
        return self.__truediv__(other)
    
    def __floordiv__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho pura vindaae saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san vindaae natho saghjay.")
        return SdNumber(self.value // other.value)
    
    def __mod__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho baqi nikalne saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san baqi natho nikalne saghjay.")
        return SdNumber(self.value % other.value)
    
    def __pow__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho kuwat kare saghjay.")
        return SdNumber(self.value ** other.value)
    
    # Numeric protocol - Comparison
    def __gt__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value > other.value)
    
    def __lt__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value < other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value >= other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value <= other.value)
    
    # Numeric protocol - Bitwise
    def __and__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho AND kar saghjay.")
        return SdNumber(int(self.value) & int(other.value))
    
    def __or__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho OR kar saghjay.")
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
    
class SdString(SdObject):
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
            raise QisamJeGhalti(f"Lafz khe sirf biye Lafz (nan \"{other.type.name}\") sa jore saghjay tho.")
        return SdString(self.value + other.value)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz ko keenly Adad se zarab kar sakte ho.")
        return SdString(self.value * int(other.value))
    
    def __rmul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz ko keenly Adad se zarab kar sakte ho.")
        return SdString(other.value * self.value)
    
    # Sequence protocol - Comparison
    def __lt__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value < other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value <= other.value)
    
    def __gt__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value > other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value >= other.value)
    
    # Sequence protocol
    def __len__(self):
        return len(self.value)
    
    def __getitem__(self, index):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("String index keenly Adad hona chaheye.")
        try:
            return SdString(self.value[int(index.value)])
        except IndexError:
            raise QisamJeGhalti(f"String index {int(index.value)} range se bahar hai.")
    
    def __contains__(self, item):
        if not isinstance(item, SdString):
            raise QisamJeGhalti("Sirf Lafz search kar sakte ho.")
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
    
class SdBool(SdObject):
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
            raise QisamJeGhalti("Faislo ko sirf Faislo se AND kar sakte ho.")
        return SdBool(self.value and other.value)
    
    def __or__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti("Faislo ko sirf Faislo se OR kar sakte ho.")
        return SdBool(self.value or other.value)
    
    def __invert__(self):
        return SdBool(not self.value)
    
    # Comparison protocol
    def __lt__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value < other.value)
    
    def __le__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value <= other.value)
    
    def __gt__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value > other.value)
    
    def __ge__(self, other):
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value >= other.value)
    
    def __str__(self):
        return "such" if self.value else "koorh"

    def __hash__(self):
        return hash(self.value)
    
    def __bool__(self):
        return bool(self.value)
    
class SdList(SdObject):
    __slots__ = ('elements',)
    
    def __init__(self, elements):
        super().__init__(FEHRIST_TYPE)
        self.elements = elements

    # Sequence protocol - Concatenation/Repetition
    def __add__(self, other):
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist ko sirf Fehrist se jor sakte ho.")
        return SdList(self.elements + other.elements)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist ko sirf Adad se zarab kar sakte ho.")
        return SdList(self.elements * int(other.value))
    
    def __rmul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist ko sirf Adad se zarab kar sakte ho.")
        return SdList(self.elements * int(other.value))
    
    # Sequence protocol
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, index):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist index keenly Adad hona chaheye.")
        try:
            return self.elements[int(index.value)]
        except IndexError:
            raise QisamJeGhalti(f"Fehrist index {int(index.value)} range se bahar hai.")
    
    def __setitem__(self, index, value):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist index keenly Adad hona chaheye.")
        try:
            self.elements[int(index.value)] = value
            return SdNull()
        except IndexError:
            raise QisamJeGhalti(f"Fehrist index {int(index.value)} range se bahar hai.")
    
    def __contains__(self, item):
        return SdBool(item in self.elements)
    
    # Container protocol
    def __iter__(self):
        return iter(self.elements)
    
    # Non-protocol methods (keep in _attributes)
    def append(self, item):
        self.elements.append(item)
        return SdNull()
    
    def extend(self, other):
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist ko sirf Fehrist se extend kar sakte ho.")
        self.elements.extend(other.elements)
        return SdNull()
    
    def remove(self, item):
        try:
            self.elements.remove(item)
            return SdNull()
        except ValueError:
            raise QisamJeGhalti("Yeh item Fehrist mein nahi hai.")
    
    def pop(self, index=None):
        if index is not None and isinstance(index, SdNumber):
            idx = int(index.value)
            try:
                return self.elements.pop(idx)
            except IndexError:
                raise QisamJeGhalti(f"Fehrist index {idx} range se bahar hai.")
        else:
            if len(self.elements) == 0:
                raise QisamJeGhalti("Khali Fehrist se pop natho kar sakte.")
            return self.elements.pop()
    
    def clear(self):
        self.elements.clear()
        return SdNull()
    
    def index(self, item):
        try:
            return SdNumber(self.elements.index(item))
        except ValueError:
            raise QisamJeGhalti("Yeh item Fehrist mein nahi hai.")
    
    def count(self, item):
        return SdNumber(self.elements.count(item))
    
    def reverse(self):
        self.elements.reverse()
        return SdNull()
    
    def __str__(self):
        return "[" + ", ".join(str(el) for el in self.elements) + "]"
    
    def __bool__(self):
        return bool(self.elements)
    
    def __hash__(self):
        raise TypeError(f"unhashable type: '{self.type.name}'")
    
class SdDict(SdObject):
    __slots__ = ('pairs',)
    
    def __init__(self, pairs):
        super().__init__(LUGHAT_TYPE)
        self.pairs = pairs

    # Mapping protocol
    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, key):
        if key in self.pairs:
            return self.pairs[key]
        raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein nahi hai.")
    
    def __setitem__(self, key, value):
        self.pairs[key] = value
        return SdNull()
    
    def __contains__(self, key):
        return SdBool(key in self.pairs)
    
    # Container protocol
    def __iter__(self):
        return iter(self.pairs)
    
    # Non-protocol methods (keep in _attributes)
    def keys(self):
        return SdList(list(self.pairs.keys()))
    
    def values(self):
        return SdList(list(self.pairs.values()))
    
    def items(self):
        items = []
        for k, v in self.pairs.items():
            items.append(SdList([k, v]))
        return SdList(items)
    
    def get(self, key, default=None):
        default = default if default is not None else SdNull()
        return self.pairs.get(key, default)
    
    def pop(self, key, default=None):
        if key in self.pairs:
            return self.pairs.pop(key)
        elif default is not None:
            return default
        else:
            raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein nahi hai.")
    
    def update(self, other):
        if not isinstance(other, SdDict):
            raise QisamJeGhalti("Sirf Lughat se update kar sakte ho.")
        self.pairs.update(other.pairs)
        return SdNull()
    
    def clear(self):
        self.pairs.clear()
        return SdNull()
    
    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.pairs.items()) + "}"
    
    def __hash__(self):
        raise TypeError(f"unhashable type: '{self.type.name}'")
    
class SdSet(SdObject):
    __slots__ = ('elements',)
    
    def __init__(self, elements):
        super().__init__(MAJMUO_TYPE)
        self.elements = set(elements) if not isinstance(elements, set) else elements

    # Set protocol - Operations
    def __add__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se union kar sakte ho.")
        return SdSet(self.elements | other.elements)
    
    def __sub__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se difference kar sakte ho.")
        return SdSet(self.elements - other.elements)
    
    def __mul__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se intersection kar sakte ho.")
        return SdSet(self.elements & other.elements)
    
    # Set protocol - Comparison
    def __le__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements <= other.elements)
    
    def __lt__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements < other.elements)
    
    def __ge__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements >= other.elements)
    
    def __gt__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements > other.elements)
    
    # Container protocol
    def __len__(self):
        return len(self.elements)
    
    def __contains__(self, item):
        return SdBool(item in self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    # Non-protocol methods (keep in _attributes)
    def add(self, item):
        if isinstance(item, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(f"`{item.type.name}` kahan majmuo ji member natho bani sakhay (he mutable aahe).")
        self.elements.add(item)
        return SdNull()
    
    def remove(self, item):
        try:
            self.elements.remove(item)
            return SdNull()
        except KeyError:
            raise QisamJeGhalti("Yeh item Majmuo mein nahi hai.")
    
    def discard(self, item):
        self.elements.discard(item)
        return SdNull()
    
    def clear(self):
        self.elements.clear()
        return SdNull()
    
    def copy(self):
        return SdSet(self.elements.copy())
    
    def union(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se union kar sakte ho.")
        return SdSet(self.elements | other.elements)
    
    def difference(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se difference kar sakte ho.")
        return SdSet(self.elements - other.elements)
    
    def intersection(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se intersection kar sakte ho.")
        return SdSet(self.elements & other.elements)
    
    def symmetric_difference(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se symmetric difference kar sakte ho.")
        return SdSet(self.elements ^ other.elements)
    
    def __str__(self):
        return "{" + ", ".join(str(el) for el in self.elements) + "}"
    
    def __hash__(self):
        raise TypeError(f"unhashable type: '{self.type.name}'")

class SdNull(SdObject):
    __slots__ = ('value',)
    
    def __init__(self):
        super().__init__(KHALI_TYPE)
        self.value = None

    # Equality - identity based
    def __eq__(self, other):
        return SdBool(isinstance(other, SdNull))
    
    def __ne__(self, other):
        return SdBool(not isinstance(other, SdNull))
    
    def __str__(self):
        return "khali"
    
    def __hash__(self):
        return hash(None)
    
    def __bool__(self):
        return False