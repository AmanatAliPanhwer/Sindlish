from .objects.primitives import SdNumber, SdNull, SdBool, SdDict, SdList, SdSet, SdString
from .errors import QisamJeGhalti, HalndeVaktGhalti

def register(registry_dict):
    """A decorator to automatically add functions to a dictionary."""

    def decorator(func):
        registry_dict[func.__name__] = func
        return func

    return decorator


class SimpleBuiltins:
    functions = {}

    def __init__(self):
        pass

    @register(functions)
    def majmuo(self, args):
        if len(args) == 0:
            return SdSet(set())
        if len(args) == 1:
            return SdSet(set(args[0]))
        raise HalndeVaktGhalti("lambi() khe sirf 1 ya 0 argument khapay.")

    @register(functions)
    def lambi(self, args):
        if len(args) != 1:
            raise HalndeVaktGhalti("lambi() khe sirf 1 argument khapay.")

        obj = args[0]

        # We check the internal storage of our SdObjects
        if hasattr(obj, 'elements'): # For SdList, SdSet
            return SdNumber(len(obj.elements))
        if hasattr(obj, 'value') and isinstance(obj.value, (str, dict)):
            return SdNumber(len(obj.value))

        raise QisamJeGhalti(f"'{obj.type.name}' ji lambi nathi kashi saghjay.")

    @register(functions)
    def likh(self, args):
        print(*(str(arg) for arg in args))
        return SdNull()

    def get_all(self):
        return self.functions


class MethodBuiltins:
    methods = {}

    def __init__(self):
        pass

    @register(methods)
    def wadha(self, obj, args):  # append
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Wadha (append) sirf Fehrist (List) laye aahe.")
        
        # We modify the internal 'elements' list
        obj.elements.append(args[0])
        return obj

    @register(methods)
    def wadhayo(self, obj, args):  # extend
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Wadhayo sirf Fehrist (List) laye aahe.")
        other = args[0]
        if not isinstance(other, SdList):
            raise QisamJeGhalti("Wadhayo argument Fehrist (List) honu chahida.")
        obj.elements.extend(other.elements)
        return obj

    @register(methods)
    def wajh(self, obj, args):  # insert
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Wajh sirf Fehrist (List) laye aahe.")
        if len(args) < 2:
            raise QisamJeGhalti("Wajh khe 2 arguments khapay: index ane value.")
        idx = args[0].value if hasattr(args[0], 'value') else args[0]
        obj.elements.insert(idx, args[1])
        return obj

    @register(methods)
    def hata(self, obj, args):  # remove
        if isinstance(obj, SdList):
            target = args[0]
            for i, item in enumerate(obj.elements):
                eq_result = item.call_method("__eq__", [target])
                if isinstance(eq_result, SdBool) and eq_result.value:
                    obj.elements.pop(i)
                    return obj
            raise QisamJeGhalti(f"Fehrist mein {target} na milyo.")
        elif isinstance(obj, SdSet):
            target = args[0]
            for item in obj.elements:
                eq_result = item.call_method("__eq__", [target])
                if isinstance(eq_result, SdBool) and eq_result.value:
                    obj.elements.discard(item)
                    return obj
            raise QisamJeGhalti(f"Majmuo mein {target} na milyo.")
        raise QisamJeGhalti("Hata sirf Fehrist ya Majmuo laye aahe.")

    @register(methods)
    def kadh(self, obj, args):  # pop (Used by List, Dict, and Set)
        if isinstance(obj, SdList):
            index = args[0].value if args and hasattr(args[0], 'value') else -1
            return obj.elements.pop(index) if args else obj.elements.pop()
        elif isinstance(obj, SdDict):
            if not args:
                raise QisamJeGhalti("kadh() for lughat (dict) needs a key.")
            key = args[0]
            return obj.pairs.pop(key, SdNull())
        elif isinstance(obj, SdSet):
            if args:
                raise QisamJeGhalti("kadh() for majmuo (set) requires no arguments.")
            return obj.elements.pop() if obj.elements else SdNull()
        raise QisamJeGhalti(f"Kadh '{obj.type.name}' laye support nathi.")

    @register(methods)
    def saf(self, obj, args):  # clear (Common)
        if isinstance(obj, SdList):
            obj.elements.clear()
        elif isinstance(obj, SdDict):
            obj.pairs.clear()
        elif isinstance(obj, SdSet):
            obj.elements.clear()
        else:
            raise QisamJeGhalti(f"Saf '{obj.type.name}' laye support nathi.")
        return obj

    @register(methods)
    def index(self, obj, args):  # index
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Index sirf Fehrist (List) laye aahe.")
        target = args[0]
        for i, item in enumerate(obj.elements):
            eq_result = item.call_method("__eq__", [target])
            if isinstance(eq_result, SdBool) and eq_result.value:
                return SdNumber(i)
        raise QisamJeGhalti(f"Fehrist mein {target} na milyo.")

    @register(methods)
    def garn(self, obj, args):  # count
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Garn sirf Fehrist (List) laye aahe.")
        target = args[0]
        count = 0
        for item in obj.elements:
            eq_result = item.call_method("__eq__", [target])
            if isinstance(eq_result, SdBool) and eq_result.value:
                count += 1
        return SdNumber(count)

    @register(methods)
    def tarteeb(self, obj, args):  # sort
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Tarteeb sirf Fehrist (List) laye aahe.")
        # Sort using comparison methods
        def compare_key(x):
            if hasattr(x, 'value'):
                return x.value
            return str(x)
        try:
            obj.elements.sort(key=compare_key)
        except Exception as e:
            raise QisamJeGhalti(f"Tarteeb mein error: {str(e)}")
        return obj

    @register(methods)
    def ulto(self, obj, args):  # reverse
        if not isinstance(obj, SdList):
            raise QisamJeGhalti("Ulto sirf Fehrist (List) laye aahe.")
        obj.elements.reverse()
        return obj

    @register(methods)
    def nakal(self, obj, args):  # copy (Common)
        if isinstance(obj, SdList):
            return SdList(obj.elements.copy())
        elif isinstance(obj, SdDict):
            return SdDict({k: v for k, v in obj.pairs.items()})
        elif isinstance(obj, SdSet):
            return SdSet(obj.elements.copy())
        else:
            raise QisamJeGhalti(f"Nakal '{obj.type.name}' laye support nathi.")

    @register(methods)
    def hasil(self, obj, args):  # get
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Hasil sirf Lughat (Dict) laye aahe.")
        key = args[0]
        default = args[1] if len(args) > 1 else SdNull()
        return obj.pairs.get(key, default)

    @register(methods)
    def syon(self, obj, args):  # items
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Syon sirf Lughat (Dict) laye aahe.")
        return SdList([SdList([k, v]) for k, v in obj.pairs.items()])

    @register(methods)
    def cabeyon(self, obj, args):
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Cabeyon sirf Lughat (Dict) laye aahe.")
        return SdList(list(obj.pairs.keys()))

    @register(methods)
    def raqamon(self, obj, args):  # values
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Raqamon sirf Lughat (Dict) laye aahe.")
        return SdList(list(obj.pairs.values()))

    @register(methods)
    def syonkadh(self, obj, args):  # popitem
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Syonkadh sirf Lughat (Dict) laye aahe.")
        if not obj.pairs:
            raise QisamJeGhalti("Lughat khaali aahe.")
        k, v = obj.pairs.popitem()
        return SdList([k, v])

    @register(methods)
    def defaultrakh(self, obj, args):  # setdefault
        if not isinstance(obj, SdDict):
            raise QisamJeGhalti("Defaultrakh sirf Lughat (Dict) laye aahe.")
        key = args[0]
        default = args[1] if len(args) > 1 else SdNull()
        return obj.pairs.setdefault(key, default)

    @register(methods)
    def update(self, obj, args):  # update (Used by Dict and Set)
        if isinstance(obj, SdDict) and isinstance(args[0], SdDict):
            obj.pairs.update(args[0].pairs)
        elif isinstance(obj, SdSet) and isinstance(args[0], SdSet):
            for el in args[0].elements:
                if isinstance(el, (SdList, SdDict, SdSet)):
                     raise QisamJeGhalti(f"`{el.type.name}` kahan majmuo ji member natho bani sakhay (he mutable aahe).")
            obj.elements.update(args[0].elements)
        else:
            raise QisamJeGhalti("Update dono objects same type ke hone chahiye.")
        return obj

    @register(methods)
    def addkar(self, obj, args):  # add
        if not isinstance(obj, SdSet):
            raise QisamJeGhalti("addkar sirf Majmuo laye aahe.")
        item = args[0]
        if isinstance(item, (SdList, SdDict, SdSet)):
            raise QisamJeGhalti(f"`{item.type.name}` kahan majmuo ji member natho bani sakhay (he mutable aahe).")
        obj.elements.add(item)
        return obj

    @register(methods)
    def chad(self, obj, args):  # discard
        if not isinstance(obj, SdSet):
            raise QisamJeGhalti("Chad sirf Majmuo (Set) laye aahe.")
        obj.elements.discard(args[0])
        return obj

    @register(methods)
    def bade(self, obj, args):  # union
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Bade sirf Majmuo (Set) laye aahe.")
        return SdSet(obj.elements.union(args[0].elements))

    @register(methods)
    def milap(self, obj, args):  # intersection
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Milap sirf Majmuo (Set) laye aahe.")
        return SdSet(obj.elements.intersection(args[0].elements))

    @register(methods)
    def farq(self, obj, args):  # difference
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Farq sirf Majmuo (Set) laye aahe.")
        return SdSet(obj.elements.difference(args[0].elements))

    @register(methods)
    def symmetric_farq(self, obj, args):  # symmetric_difference
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Symmetric_farq sirf Majmuo (Set) laye aahe.")
        return SdSet(obj.elements.symmetric_difference(args[0].elements))

    @register(methods)
    def nandohisoahe(self, obj, args):  # issubset
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Nandohisoahe sirf Majmuo (Set) laye aahe.")
        return SdBool(obj.elements.issubset(args[0].elements))

    @register(methods)
    def wadohisoahe(self, obj, args):  # issuperset
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Wadohisoahe sirf Majmuo (Set) laye aahe.")
        return SdBool(obj.elements.issuperset(args[0].elements))

    @register(methods)
    def alaghahe(self, obj, args):  # isdisjoint
        if not isinstance(obj, SdSet) or not isinstance(args[0], SdSet):
            raise QisamJeGhalti("Alaghahe sirf Majmuo (Set) laye aahe.")
        return SdBool(obj.elements.isdisjoint(args[0].elements))

    def get_all(self):
        return self.methods
