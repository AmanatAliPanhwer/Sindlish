from .base import SdShey, SdType
from ..frontend.tokens import TokenType
from ..errors import QisamJeGhalti
from .numbers import SdNumber, SdBool
from .core import SdNull

FEHRIST_TYPE = SdType("FEHRIST", TokenType.FEHRIST)
LUGHAT_TYPE = SdType("LUGHAT", TokenType.LUGHAT)
MAJMUO_TYPE = SdType("MAJMUO", TokenType.MAJMUO)

class SdList(SdShey):
    __slots__ = ('elements',)
    
    def __init__(self, elements):
        super().__init__(FEHRIST_TYPE)
        self.elements = elements

    def __add__(self, other):
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist khe sirf biye Fehrist saan jore saghjay tho.")
        return SdList(self.elements + other.elements)
    
    def __mul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist khe sirf Adad saan zarab kare saghjay tho.")
        return SdList(self.elements * int(other.value))
    
    def __rmul__(self, other):
        if not isinstance(other, SdNumber):
            raise QisamJeGhalti("Fehrist khe sirf Adad saan zarab kare saghjay tho.")
        return SdList(self.elements * int(other.value))
    
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, index):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist jo index Adad hujjhan lazmi aahe.")
        try:
            return self.elements[int(index.value)]
        except IndexError:
            raise QisamJeGhalti(f"Fehrist jo index {int(index.value)} hadd khaan bahar aahe.")
    
    def __setitem__(self, index, value):
        if not isinstance(index, SdNumber):
            raise QisamJeGhalti("Fehrist jo index Adad hujjhan lazmi aahe.")
        try:
            self.elements[int(index.value)] = value
            return SdNull()
        except IndexError:
            raise QisamJeGhalti(f"Fehrist jo index {int(index.value)} hadd khaan bahar aahe.")
    
    def __contains__(self, item):
        return SdBool(item in self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    def __str__(self):
        return "[" + ", ".join(str(el) for el in self.elements) + "]"
    
    def __bool__(self):
        return bool(self.elements)
    
    def __hash__(self):
        raise TypeError(f"Unhashable qisam: '{self.type.name}'.")

    # Non-protocol methods
    def append(self, item):
        self.elements.append(item)
        return SdNull()
    
    def extend(self, other):
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Fehrist khe sirf biye Fehrist saan wadhaye (extend) kare saghjay tho.")
        self.elements.extend(other.elements)
        return SdNull()
    
    def remove(self, item):
        try:
            self.elements.remove(item)
            return SdNull()
        except ValueError:
            raise QisamJeGhalti("He item Fehrist mein na aahe.")
            
    def pop(self, index=None):
        if index is not None and isinstance(index, SdNumber):
            idx = int(index.value)
            try:
                return self.elements.pop(idx)
            except IndexError:
                raise QisamJeGhalti(f"Fehrist jo index {idx} hadd khaan bahar aahe.")
        else:
            if len(self.elements) == 0:
                raise QisamJeGhalti("Khaali Fehrist maan natho kadhi (pop) saghjay.")
            return self.elements.pop()
    
    def clear(self):
        self.elements.clear()
        return SdNull()
    
    def index(self, item):
        try:
            return SdNumber(self.elements.index(item))
        except ValueError:
            raise QisamJeGhalti("He item Fehrist mein na aahe.")
    
    def count(self, item):
        return SdNumber(self.elements.count(item))
    
    def reverse(self):
        self.elements.reverse()
        return SdNull()

class SdDict(SdShey):
    __slots__ = ('pairs',)
    
    def __init__(self, pairs):
        super().__init__(LUGHAT_TYPE)
        self.pairs = pairs

    def __len__(self):
        return len(self.pairs)
    
    def __getitem__(self, key):
        if key in self.pairs:
            return self.pairs[key]
        raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein na mili.")
    
    def __setitem__(self, key, value):
        self.pairs[key] = value
        return SdNull()
    
    def __contains__(self, key):
        return SdBool(key in self.pairs)
    
    def __iter__(self):
        return iter(self.pairs)
    
    def __str__(self):
        return "{" + ", ".join(f"{k}: {v}" for k, v in self.pairs.items()) + "}"
    
    def __hash__(self):
        raise TypeError(f"Unhashable qisam: '{self.type.name}'.")

    # Non-protocol methods
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
            raise QisamJeGhalti(f"Key '{str(key)}' Lughat mein na mili.")
    
    def update(self, other):
        if not isinstance(other, SdDict):
            raise QisamJeGhalti("Sirf biye Lughat saan update kare saghjay tho.")
        self.pairs.update(other.pairs)
        return SdNull()
    
    def clear(self):
        self.pairs.clear()
        return SdNull()

class SdSet(SdShey):
    __slots__ = ('elements',)
    
    def __init__(self, elements):
        super().__init__(MAJMUO_TYPE)
        self.elements = set(elements) if not isinstance(elements, set) else elements

    def __add__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan milap (union) kare saghjay tho.")
        return SdSet(self.elements | other.elements)
    
    def __sub__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan farq (difference) kadhi saghjay tho.")
        return SdSet(self.elements - other.elements)
    
    def __mul__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan intersection kare saghjay tho.")
        return SdSet(self.elements & other.elements)
    
    def __le__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ji sirf biye Majmuo saan bheta kare saghjay thi.")
        return SdBool(self.elements <= other.elements)
    
    def __lt__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ji sirf biye Majmuo saan bheta kare saghjay thi.")
        return SdBool(self.elements < other.elements)
    
    def __ge__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ji sirf biye Majmuo saan bheta kare saghjay thi.")
        return SdBool(self.elements >= other.elements)
    
    def __gt__(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo ji sirf biye Majmuo saan bheta kare saghjay thi.")
        return SdBool(self.elements > other.elements)
    
    def __len__(self):
        return len(self.elements)
    
    def __contains__(self, item):
        return SdBool(item in self.elements)
    
    def __iter__(self):
        return iter(self.elements)
    
    def __str__(self):
        return "{" + ", ".join(str(el) for el in self.elements) + "}"
    
    def __hash__(self):
        raise TypeError(f"Unhashable qisam: '{self.type.name}'.")

    # Non-protocol methods
    def add(self, item):
        if isinstance(item, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(f"{item.type.name} Majmuo jo hisso natho thi saghjay (he mutable aahe).")
        self.elements.add(item)
        return SdNull()
    
    def remove(self, item):
        try:
            self.elements.remove(item)
            return SdNull()
        except KeyError:
            raise QisamJeGhalti("He item Majmuo mein na aahe.")
    
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
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan milap (union) kare saghjay tho.")
        return SdSet(self.elements | other.elements)
    
    def difference(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan farq (difference) kadhi saghjay tho.")
        return SdSet(self.elements - other.elements)
    
    def intersection(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan intersection kare saghjay tho.")
        return SdSet(self.elements & other.elements)
    
    def symmetric_difference(self, other):
        if not isinstance(other, SdSet):
            raise QisamJeGhalti("Majmuo jo sirf biye Majmuo saan symmetric farq kadhi saghjay tho.")
        return SdSet(self.elements ^ other.elements)

# --- NATIVE METHODS REGISTRATION ---

# Fehrist (List) Methods
def fehrist_wadha(obj, args):
    obj.elements.append(args[0])
    return obj

def fehrist_wadhayo(obj, args):
    other = args[0]
    if not isinstance(other, SdList):
        raise QisamJeGhalti("Wadhayo laai argument Fehrist hujjhan lazmi aahe.")
    obj.elements.extend(other.elements)
    return obj

def fehrist_wajh(obj, args):
    if len(args) < 2:
        raise QisamJeGhalti("Wajh khe 2 arguments khapan: index aen value.")
    idx = args[0].value if hasattr(args[0], 'value') else args[0]
    obj.elements.insert(idx, args[1])
    return obj

def fehrist_hata(obj, args):
    target = args[0]
    for i, item in enumerate(obj.elements):
        eq_result = item.call_method("__eq__", [target])
        if isinstance(eq_result, SdBool) and eq_result.value:
            obj.elements.pop(i)
            return obj
    raise QisamJeGhalti(f"{target} Fehrist mein na milyo.")

def fehrist_kadh(obj, args):
    index = args[0].value if args and hasattr(args[0], 'value') else -1
    return obj.elements.pop(index) if args else obj.elements.pop()

def fehrist_saf(obj, args):
    obj.elements.clear()
    return obj

def fehrist_index(obj, args):
    target = args[0]
    for i, item in enumerate(obj.elements):
        eq_result = item.call_method("__eq__", [target])
        if isinstance(eq_result, SdBool) and eq_result.value:
            return SdNumber(i)
    raise QisamJeGhalti(f"{target} Fehrist mein na milyo.")

def fehrist_garn(obj, args):
    target = args[0]
    count = 0
    for item in obj.elements:
        eq_result = item.call_method("__eq__", [target])
        if isinstance(eq_result, SdBool) and eq_result.value:
            count += 1
    return SdNumber(count)

def fehrist_tarteeb(obj, args):
    def compare_key(x):
        return x.value if hasattr(x, 'value') else str(x)
    try:
        obj.elements.sort(key=compare_key)
    except Exception as e:
        raise QisamJeGhalti(f"Tarteeb mein ghalti: {str(e)}.")
    return obj

def fehrist_ulto(obj, args):
    obj.elements.reverse()
    return obj

def fehrist_nakal(obj, args):
    return SdList(obj.elements.copy())

FEHRIST_TYPE.register_method("wadha", fehrist_wadha)
FEHRIST_TYPE.register_method("wadhayo", fehrist_wadhayo)
FEHRIST_TYPE.register_method("wajh", fehrist_wajh)
FEHRIST_TYPE.register_method("hata", fehrist_hata)
FEHRIST_TYPE.register_method("kadh", fehrist_kadh)
FEHRIST_TYPE.register_method("saf", fehrist_saf)
FEHRIST_TYPE.register_method("index", fehrist_index)
FEHRIST_TYPE.register_method("garn", fehrist_garn)
FEHRIST_TYPE.register_method("tarteeb", fehrist_tarteeb)
FEHRIST_TYPE.register_method("ulto", fehrist_ulto)
FEHRIST_TYPE.register_method("nakal", fehrist_nakal)

# Lughat (Dict) Methods
def lughat_hasil(obj, args):
    key = args[0]
    default = args[1] if len(args) > 1 else SdNull()
    return obj.pairs.get(key, default)

def lughat_syon(obj, args):
    return SdList([SdList([k, v]) for k, v in obj.pairs.items()])

def lughat_cabeyon(obj, args):
    return SdList(list(obj.pairs.keys()))

def lughat_raqamon(obj, args):
    return SdList(list(obj.pairs.values()))

def lughat_syonkadh(obj, args):
    if not obj.pairs:
        raise QisamJeGhalti("Lughat khaali aahe.")
    k, v = obj.pairs.popitem()
    return SdList([k, v])

def lughat_defaultrakh(obj, args):
    key = args[0]
    default = args[1] if len(args) > 1 else SdNull()
    return obj.pairs.setdefault(key, default)

def lughat_update(obj, args):
    if not isinstance(args[0], SdDict):
        raise QisamJeGhalti("Update sirf Lughat je saath hi kare saghjay tho.")
    obj.pairs.update(args[0].pairs)
    return obj

def lughat_kadh(obj, args):
    if not args:
        raise QisamJeGhalti("Lughat laai 'kadh()' mein key khapay.")
    key = args[0]
    return obj.pairs.pop(key, SdNull())

def lughat_saf(obj, args):
    obj.pairs.clear()
    return obj

def lughat_nakal(obj, args):
    return SdDict({k: v for k, v in obj.pairs.items()})

LUGHAT_TYPE.register_method("hasil", lughat_hasil)
LUGHAT_TYPE.register_method("syon", lughat_syon)
LUGHAT_TYPE.register_method("cabeyon", lughat_cabeyon)
LUGHAT_TYPE.register_method("raqamon", lughat_raqamon)
LUGHAT_TYPE.register_method("syonkadh", lughat_syonkadh)
LUGHAT_TYPE.register_method("defaultrakh", lughat_defaultrakh)
LUGHAT_TYPE.register_method("update", lughat_update)
LUGHAT_TYPE.register_method("kadh", lughat_kadh)
LUGHAT_TYPE.register_method("saf", lughat_saf)
LUGHAT_TYPE.register_method("nakal", lughat_nakal)

# Majmuo (Set) Methods
def majmuo_addkar(obj, args):
    item = args[0]
    if isinstance(item, (SdList, SdDict, SdSet)):
        raise QisamJeGhalti(f"{item.type.name} Majmuo jo hisso natho thi saghjay (he mutable aahe).")
    obj.elements.add(item)
    return obj

def majmuo_chad(obj, args):
    obj.elements.discard(args[0])
    return obj

def majmuo_bade(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Bade sirf Majmuo laai aahe.")
    return SdSet(obj.elements.union(args[0].elements))

def majmuo_milap(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Milap sirf Majmuo laai aahe.")
    return SdSet(obj.elements.intersection(args[0].elements))

def majmuo_farq(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Farq sirf Majmuo laai aahe.")
    return SdSet(obj.elements.difference(args[0].elements))

def majmuo_symmetric_farq(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Symmetric farq sirf Majmuo laai aahe.")
    return SdSet(obj.elements.symmetric_difference(args[0].elements))

def majmuo_nandohisoahe(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Nandohisoahe sirf Majmuo laai aahe.")
    return SdBool(obj.elements.issubset(args[0].elements))

def majmuo_wadohisoahe(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Wadohisoahe sirf Majmuo laai aahe.")
    return SdBool(obj.elements.issuperset(args[0].elements))

def majmuo_alaghahe(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Alaghahe sirf Majmuo laai aahe.")
    return SdBool(obj.elements.isdisjoint(args[0].elements))

def majmuo_hata(obj, args):
    target = args[0]
    for item in obj.elements:
        eq_result = item.call_method("__eq__", [target])
        if isinstance(eq_result, SdBool) and eq_result.value:
            obj.elements.discard(item)
            return obj
    raise QisamJeGhalti(f"{target} Majmuo mein na milyo.")

def majmuo_kadh(obj, args):
    if args:
        raise QisamJeGhalti("Majmuo laai 'kadh()' mein koi argument na khapay.")
    return obj.elements.pop() if obj.elements else SdNull()

def majmuo_saf(obj, args):
    obj.elements.clear()
    return obj

def majmuo_nakal(obj, args):
    return SdSet(obj.elements.copy())

def majmuo_update(obj, args):
    if not isinstance(args[0], SdSet):
        raise QisamJeGhalti("Update laai banhay objects jo qisam same hujjhan lazmi aahe.")
    for el in args[0].elements:
        if isinstance(el, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(f"{el.type.name} Majmuo jo hisso natho thi saghjay (he mutable aahe).")
    obj.elements.update(args[0].elements)
    return obj

MAJMUO_TYPE.register_method("addkar", majmuo_addkar)
MAJMUO_TYPE.register_method("chad", majmuo_chad)
MAJMUO_TYPE.register_method("bade", majmuo_bade)
MAJMUO_TYPE.register_method("milap", majmuo_milap)
MAJMUO_TYPE.register_method("farq", majmuo_farq)
MAJMUO_TYPE.register_method("symmetric_farq", majmuo_symmetric_farq)
MAJMUO_TYPE.register_method("nandohisoahe", majmuo_nandohisoahe)
MAJMUO_TYPE.register_method("wadohisoahe", majmuo_wadohisoahe)
MAJMUO_TYPE.register_method("alaghahe", majmuo_alaghahe)
MAJMUO_TYPE.register_method("hata", majmuo_hata)
MAJMUO_TYPE.register_method("kadh", majmuo_kadh)
MAJMUO_TYPE.register_method("saf", majmuo_saf)
MAJMUO_TYPE.register_method("nakal", majmuo_nakal)
MAJMUO_TYPE.register_method("update", majmuo_update)
