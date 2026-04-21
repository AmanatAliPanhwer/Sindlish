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
    def __init__(self, value):
        super().__init__(DAHAI_TYPE if isinstance(value, float) else ADAD_TYPE)
        self.value = value
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # Arithmetic operations
        self.attributes["__add__"] = self._add
        self.attributes["__sub__"] = self._sub
        self.attributes["__mul__"] = self._mul
        self.attributes["__truediv__"] = self._truediv
        self.attributes["__floordiv__"] = self._floordiv
        self.attributes["__div__"] = self._div
        self.attributes["__mod__"] = self._mod
        self.attributes["__pow__"] = self._pow
        
        # Comparison operations
        self.attributes["__gt__"] = self._gt
        self.attributes["__lt__"] = self._lt
        self.attributes["__ge__"] = self._ge
        self.attributes["__le__"] = self._le
        
        # Logical operations
        self.attributes["__and__"] = self._and
        self.attributes["__or__"] = self._or
        
        # Unary operations
        self.attributes["__neg__"] = self._neg
        self.attributes["__pos__"] = self._pos
        self.attributes["__abs__"] = self._abs
        self.attributes["__invert__"] = self._invert
        self.attributes["__dec__"] = self._dec

    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def _ne(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            return SdBool(True)
        return SdBool(self.value != other.value)

    def _add(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho jore saghjay.")
        return SdNumber(self.value + other.value)
    
    def _sub(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' natho ghaat kare saghjay.")
        return SdNumber(self.value - other.value)
    
    def _mul(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho zarab kare saghjay.")
        return SdNumber(self.value * other.value)
    
    def _truediv(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho vindaae saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san vindaae natho saghjay.")
        return SdNumber(self.value / other.value)
    
    def _floordiv(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho pura vindaae saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san vindaae natho saghjay.")
        return SdNumber(self.value // other.value)
    
    def _div(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho vindaae saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san vindaae natho saghjay.")
        return SdNumber(self.value / other.value)
    
    def _mod(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho baqi nikalne saghjay.")
        if other.value == 0:
            raise ZeroVindJeGhalti("Zero (0) san baqi natho nikalne saghjay.")
        return SdNumber(self.value % other.value)
    
    def _pow(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho kuwat kare saghjay.")
        return SdNumber(self.value ** other.value)
    
    def _gt(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value > other.value)
    
    def _lt(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value < other.value)
    
    def _ge(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value >= other.value)
    
    def _le(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' sa moqabala natho kar saghjay.")
        return SdBool(self.value <= other.value)
    
    def _and(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho AND kar saghjay.")
        return SdNumber(int(self.value) & int(other.value))
    
    def _or(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti(f"Adad khe '{other.type.name}' san natho OR kar saghjay.")
        return SdNumber(int(self.value) | int(other.value))
    
    def _neg(self, args):
        return SdNumber(-self.value)
    
    def _pos(self, args):
        return SdNumber(+self.value)
    
    def _abs(self, args):
        return SdNumber(abs(self.value))
    
    def _invert(self, args):
        return SdNumber(~int(self.value))
    
    def _inc(self, args):
        return SdNumber(self.value + 1)
    
    def _dec(self, args):
        return SdNumber(self.value - 1)
    
    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)
    
    def __eq__(self, other):
        if not isinstance(other, SdNumber):
            return False
        return self.value == other.value
    
class SdString(SdObject):
    def __init__(self, value):
        super().__init__(LAFZ_TYPE)
        self.value = value
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # String operations
        self.attributes["__add__"] = self._add
        self.attributes["__mul__"] = self._mul
        self.attributes["__rmul__"] = self._rmul
        self.attributes["__lt__"] = self._lt
        self.attributes["__le__"] = self._le
        self.attributes["__gt__"] = self._gt
        self.attributes["__ge__"] = self._ge
        self.attributes["__len__"] = self._len
        self.attributes["__getitem__"] = self._getitem
        self.attributes["__contains__"] = self._contains

    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def _ne(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            return SdBool(True)
        return SdBool(self.value != other.value)

    def _add(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz khe sirf biye Lafz (nan \"{other.type.name}\") sa jore saghjay tho.")
        return SdString(self.value + other.value)
    
    def _mul(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz ko keenly Adad se zarab kar sakte ho.")
        return SdString(self.value * int(other.value))
    
    def _rmul(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Lafz ko keenly Adad se zarab kar sakte ho.")
        return SdString(other.value * self.value)
    
    def _lt(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value < other.value)
    
    def _le(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value <= other.value)
    
    def _gt(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value > other.value)
    
    def _ge(self, args):
        other = args[0]
        if not isinstance(other, SdString):
            raise QisamJeGhalti(f"Lafz ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value >= other.value)
    
    def _len(self, args):
        return SdNumber(len(self.value))
    
    def _getitem(self, args):
        index = args[0]
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("String index keenly Adad hona chaheye.")
        try:
            return SdString(self.value[int(index.value)])
        except IndexError:
            raise QisamJeGhalti(f"String index {int(index.value)} range se bahar hai.")
    
    def _contains(self, args):
        substr = args[0]
        if not isinstance(substr, SdString):
            raise QisamJeGhalti("Sirf Lafz search kar sakte ho.")
        return SdBool(substr.value in self.value)
    
    def __str__(self):
        return self.value
    
    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, SdString):
            return False
        return self.value == other.value
    
    def __bool__(self):
        return bool(self.value)
    
class SdBool(SdObject):
    def __init__(self, value):
        super().__init__(FAISLO_TYPE)
        self.value = value
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # Boolean operations
        self.attributes["__and__"] = self._and
        self.attributes["__or__"] = self._or
        self.attributes["__invert__"] = self._invert
        self.attributes["__lt__"] = self._lt
        self.attributes["__le__"] = self._le
        self.attributes["__gt__"] = self._gt
        self.attributes["__ge__"] = self._ge
    
    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            return SdBool(False)
        return SdBool(self.value == other.value)
    
    def _ne(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            return SdBool(True)
        return SdBool(self.value != other.value)
    
    def _and(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti("Faislo ko sirf Faislo se AND kar sakte ho.")
        return SdBool(self.value and other.value)
    
    def _or(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti("Faislo ko sirf Faislo se OR kar sakte ho.")
        return SdBool(self.value or other.value)
    
    def _invert(self, args):
        return SdBool(not self.value)
    
    def _lt(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value < other.value)
    
    def _le(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value <= other.value)
    
    def _gt(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value > other.value)
    
    def _ge(self, args):
        other = args[0]
        if not isinstance(other, SdBool):
            raise QisamJeGhalti(f"Faislo ko '{other.type.name}' sa compare natho kar sakte.")
        return SdBool(self.value >= other.value)
    
    def __str__(self):
        return "such" if self.value else "koorh"

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, SdBool):
            return False
        return self.value == other.value

    def __bool__(self):
        return bool(self.value)
    
class SdList(SdObject):
    def __init__(self, elements):
        super().__init__(FEHRIST_TYPE)
        self.elements = elements
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # List operations
        self.attributes["__add__"] = self._add
        self.attributes["__mul__"] = self._mul
        self.attributes["__rmul__"] = self._rmul
        self.attributes["__len__"] = self._len
        self.attributes["__getitem__"] = self._getitem
        self.attributes["__setitem__"] = self._setitem
        self.attributes["__contains__"] = self._contains
        self.attributes["__iter__"] = self._iter
        self.attributes["append"] = self._append
        self.attributes["extend"] = self._extend
        self.attributes["remove"] = self._remove
        self.attributes["pop"] = self._pop
        self.attributes["clear"] = self._clear
        self.attributes["index"] = self._index
        self.attributes["count"] = self._count
        self.attributes["reverse"] = self._reverse

    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdList):
            return SdBool(False)
        if len(self.elements) != len(other.elements):
            return SdBool(False)
        for a, b in zip(self.elements, other.elements):
            result = a.call_method("__eq__", [b])
            if not (isinstance(result, SdBool) and result.value):
                return SdBool(False)
        return SdBool(True)
    
    def _ne(self, args):
        eq_result = self._eq(args)
        return SdBool(not eq_result.value)

    def _add(self, args):
        other = args[0]
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist ko sirf Fehrist se jor sakte ho.")
        return SdList(self.elements + other.elements)
    
    def _mul(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist ko sirf Adad se zarab kar sakte ho.")
        return SdList(self.elements * int(other.value))
    
    def _rmul(self, args):
        other = args[0]
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist ko sirf Adad se zarab kar sakte ho.")
        return SdList(self.elements * int(other.value))
    
    def _len(self, args):
        return SdNumber(len(self.elements))
    
    def _getitem(self, args):
        index = args[0]
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist index keenly Adad hona chaheye.")
        try:
            return self.elements[int(index.value)]
        except IndexError:
            raise QisamJeGhalti(f"Fehrist index {int(index.value)} range se bahar hai.")
    
    def _setitem(self, args):
        index = args[0]
        value = args[1]
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist index keenly Adad hona chaheye.")
        try:
            self.elements[int(index.value)] = value
            return SdNull()
        except IndexError:
            raise QisamJeGhalti(f"Fehrist index {int(index.value)} range se bahar hai.")
    
    def _contains(self, args):
        item = args[0]
        return SdBool(item in self.elements)
    
    def _iter(self, args):
        return iter(self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, index):
        return self.elements[index]
    
    def _append(self, args):
        item = args[0]
        self.elements.append(item)
        return SdNull()
    
    def _extend(self, args):
        other = args[0]
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist ko sirf Fehrist se extend kar sakte ho.")
        self.elements.extend(other.elements)
        return SdNull()
    
    def _remove(self, args):
        item = args[0]
        try:
            self.elements.remove(item)
            return SdNull()
        except ValueError:
            raise QisamJeGhalti("Yeh item Fehrist mein nahi hai.")
    
    def _pop(self, args):
        if len(args) > 0 and isinstance(args[0], SdNumber):
            index = int(args[0].value)
            try:
                return self.elements.pop(index)
            except IndexError:
                raise QisamJeGhalti(f"Fehrist index {index} range se bahar hai.")
        else:
            if len(self.elements) == 0:
                raise QisamJeGhalti("Khali Fehrist se pop natho kar sakte.")
            return self.elements.pop()
    
    def _clear(self, args):
        self.elements.clear()
        return SdNull()
    
    def _index(self, args):
        item = args[0]
        try:
            return SdNumber(self.elements.index(item))
        except ValueError:
            raise QisamJeGhalti("Yeh item Fehrist mein nahi hai.")
    
    def _count(self, args):
        item = args[0]
        return SdNumber(self.elements.count(item))
    
    def _reverse(self, args):
        self.elements.reverse()
        return SdNull()

    def __str__(self):
        return "[" + ", ".join(str(el) for el in self.elements) + "]"

    def __bool__(self):
        return bool(self.elements)
    
    def __len__(self):
        return len(self.elements)
    
class SdDict(SdObject):
    def __init__(self, pairs):
        super().__init__(LUGHAT_TYPE)
        self.pairs = pairs
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # Dict operations
        self.attributes["__len__"] = self._len
        self.attributes["__getitem__"] = self._getitem
        self.attributes["__setitem__"] = self._setitem
        self.attributes["__contains__"] = self._contains
        self.attributes["keys"] = self._keys
        self.attributes["values"] = self._values
        self.attributes["items"] = self._items
        self.attributes["get"] = self._get
        self.attributes["pop"] = self._pop
        self.attributes["update"] = self._update
        self.attributes["clear"] = self._clear

    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdDict):
            return SdBool(False)
        if len(self.pairs) != len(other.pairs):
            return SdBool(False)
        for k, v in self.pairs.items():
            if k not in other.pairs:
                return SdBool(False)
            result = v.call_method("__eq__", [other.pairs[k]])
            if not (isinstance(result, SdBool) and result.value):
                return SdBool(False)
        return SdBool(True)
    
    def _ne(self, args):
        eq_result = self._eq(args)
        return SdBool(not eq_result.value)

    def _len(self, args):
        return SdNumber(len(self.pairs))
    
    def _getitem(self, args):
        key = args[0]
        if key in self.pairs:
            return self.pairs[key]
        raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein nahi hai.")
    
    def _setitem(self, args):
        key = args[0]
        value = args[1]
        self.pairs[key] = value
        return SdNull()
    
    def _contains(self, args):
        key = args[0]
        return SdBool(key in self.pairs)
    
    def _keys(self, args):
        return SdList(list(self.pairs.keys()))
    
    def _values(self, args):
        return SdList(list(self.pairs.values()))
    
    def _items(self, args):
        items = []
        for k, v in self.pairs.items():
            items.append(SdList([k, v]))
        return SdList(items)
    
    def _get(self, args):
        key = args[0]
        default = args[1] if len(args) > 1 else SdNull()
        return self.pairs.get(key, default)
    
    def _pop(self, args):
        key = args[0]
        default = args[1] if len(args) > 1 else None
        if key in self.pairs:
            return self.pairs.pop(key)
        elif default is not None:
            return default
        else:
            raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein nahi hai.")
    
    def _update(self, args):
        other = args[0]
        if not isinstance(other, SdDict):
            raise QisamJeGhalti("Sirf Lughat se update kar sakte ho.")
        self.pairs.update(other.pairs)
        return SdNull()
    
    def _clear(self, args):
        self.pairs.clear()
        return SdNull()

    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.pairs.items()) + "}"
    
    def __len__(self):
        return len(self.pairs)
    
    def __iter__(self):
        return iter(self.pairs)
    
    def items(self):
        return self.pairs.items()
    
class SdSet(SdObject):
    def __init__(self, elements):
        super().__init__(MAJMUO_TYPE)
        self.elements = set(elements) if not isinstance(elements, set) else elements
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne
        
        # Set operations
        self.attributes["__add__"] = self._union
        self.attributes["__sub__"] = self._difference
        self.attributes["__mul__"] = self._intersection
        self.attributes["__le__"] = self._issubset
        self.attributes["__lt__"] = self._ispropersubset
        self.attributes["__ge__"] = self._issuperset
        self.attributes["__gt__"] = self._ispropers
        self.attributes["__len__"] = self._len
        self.attributes["__contains__"] = self._contains
        self.attributes["add"] = self._add
        self.attributes["remove"] = self._remove
        self.attributes["discard"] = self._discard
        self.attributes["clear"] = self._clear
        self.attributes["union"] = self._union
        self.attributes["difference"] = self._difference
        self.attributes["intersection"] = self._intersection
        self.attributes["symmetric_difference"] = self._symdiff
        self.attributes["copy"] = self._copy

    def _eq(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            return SdBool(False)
        if len(self.elements) != len(other.elements):
            return SdBool(False)
        # Check if all elements in self are in other
        for elem_a in self.elements:
            found = False
            for elem_b in other.elements:
                result = elem_a.call_method("__eq__", [elem_b])
                if isinstance(result, SdBool) and result.value:
                    found = True
                    break
            if not found:
                return SdBool(False)
        return SdBool(True)
    
    def _ne(self, args):
        eq_result = self._eq(args)
        return SdBool(not eq_result.value)

    def _union(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se union kar sakte ho.")
        return SdSet(self.elements | other.elements)
    
    def _difference(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se difference kar sakte ho.")
        return SdSet(self.elements - other.elements)
    
    def _intersection(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se intersection kar sakte ho.")
        return SdSet(self.elements & other.elements)
    
    def _symdiff(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se symmetric difference kar sakte ho.")
        return SdSet(self.elements ^ other.elements)
    
    def _issubset(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements <= other.elements)
    
    def _ispropersubset(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements < other.elements)
    
    def _issuperset(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements >= other.elements)
    
    def _ispropers(self, args):
        other = args[0]
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ko sirf Majmuo se compare kar sakte ho.")
        return SdBool(self.elements > other.elements)
    
    def _len(self, args):
        return SdNumber(len(self.elements))
    
    def _contains(self, args):
        item = args[0]
        return SdBool(item in self.elements)
    
    def _add(self, args):
        item = args[0]
        if isinstance(item, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(f"`{item.type.name}` kahan majmuo ji member natho bani sakhay (he mutable aahe).")
        self.elements.add(item)
        return SdNull()
    
    def _remove(self, args):
        item = args[0]
        try:
            self.elements.remove(item)
            return SdNull()
        except KeyError:
            raise QisamJeGhalti("Yeh item Majmuo mein nahi hai.")
    
    def _discard(self, args):
        item = args[0]
        self.elements.discard(item)
        return SdNull()
    
    def _clear(self, args):
        self.elements.clear()
        return SdNull()
    
    def _copy(self, args):
        return SdSet(self.elements.copy())

    def __str__(self):
        return "{" + ", ".join(str(el) for el in self.elements) + "}"
    
    def __len__(self):
        return len(self.elements)
    
    def __iter__(self):
        return iter(self.elements)

class SdNull(SdObject):
    def __init__(self):
        super().__init__(KHALI_TYPE)
        self.value = None
        
        # Equality operations
        self.attributes["__eq__"] = self._eq
        self.attributes["__ne__"] = self._ne

    def _eq(self, args):
        other = args[0]
        return SdBool(isinstance(other, SdNull))
    
    def _ne(self, args):
        other = args[0]
        return SdBool(not isinstance(other, SdNull))

    def __str__(self):
        return "khali"
    
    def __hash__(self):
        return hash(None)

    def __eq__(self, other):
        return isinstance(other, SdNull)
    
    def __bool__(self):
        return False