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
    def lambi(self, args):
        if len(args) != 1:
            raise RuntimeError("lambi() needs 1 argument")
        return len(args[0])

    @register(functions)
    def likh(self, args):
        print(*args)
        return None

    def get_all(self):
        return self.functions


class MethodBuiltins:
    methods = {}

    def __init__(self):
        pass

    @register(methods)
    def wadha(self, obj, args):  # append
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        obj.append(args[0])
        return obj

    @register(methods)
    def wadhayo(self, obj, args):  # extend
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        obj.extend(args[0])
        return obj

    @register(methods)
    def wajh(self, obj, args):  # insert
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        obj.insert(args[0], args[1])
        return obj

    @register(methods)
    def hata(self, obj, args):  # remove
        if isinstance(obj, (list, set)):
            obj.remove(args[0])
            return obj
        raise TypeError(f"Method hata not supported for {type(obj).__name__}")

    @register(methods)
    def kadh(self, obj, args):  # pop (Used by List, Dict, and Set)
        if isinstance(obj, list):
            return obj.pop(args[0]) if args else obj.pop()
        elif isinstance(obj, dict):
            if not args:
                raise RuntimeError("kadh() for lughat (dict) requires a key")
            return obj.pop(args[0])
        elif isinstance(obj, set):
            # Set: pop() - takes NO arguments
            if args:
                raise RuntimeError("kadh() for majmuo (set) takes no arguments")
            return obj.pop()
        raise TypeError(f"Method kadh not supported for {type(obj).__name__}")

    @register(methods)
    def saf(self, obj, args):  # clear (Common)
        obj.clear()
        return obj

    @register(methods)
    def index(self, obj, args):  # index
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        return obj.index(args[0])

    @register(methods)
    def garn(self, obj, args):  # count
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        return obj.count(args[0])

    @register(methods)
    def tarteeb(self, obj, args):  # sort
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        obj.sort()
        return obj

    @register(methods)
    def ulto(self, obj, args):  # reverse
        if not isinstance(obj, list):
            raise TypeError("Needs a fehrist")
        obj.reverse()
        return obj

    @register(methods)
    def nakal(self, obj, args):  # copy (Common)
        return obj.copy()

    @register(methods)
    def hasil(self, obj, args):  # get
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return obj.get(args[0], args[1] if len(args) > 1 else None)

    @register(methods)
    def syon(self, obj, args):  # items
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return list(obj.items())

    @register(methods)
    def cabeyon(self, obj, args):
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return list(obj.keys())

    @register(methods)
    def raqamon(self, obj, args):  # values
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return list(obj.values())

    @register(methods)
    def syonkadh(self, obj, args):  # popitem
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return obj.popitem()

    @register(methods)
    def defaultrakh(self, obj, args):  # setdefault
        if not isinstance(obj, dict):
            raise TypeError("Needs a lughat")
        return obj.setdefault(args[0], args[1] if len(args) > 1 else None)

    @register(methods)
    def update(self, obj, args):  # update (Used by Dict and Set)
        obj.update(args[0])
        return obj

    @register(methods)
    def addkar(self, obj, args):  # add
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        obj.add(args[0])
        return obj

    @register(methods)
    def chad(self, obj, args):  # discard
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        obj.discard(args[0])
        return obj

    @register(methods)
    def bade(self, obj, args):  # union
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.union(args[0])

    @register(methods)
    def milap(self, obj, args):  # intersection
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.intersection(args[0])

    @register(methods)
    def farq(self, obj, args):  # difference
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.difference(args[0])

    @register(methods)
    def symmetric_farq(self, obj, args):  # symmetric_difference
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.symmetric_difference(args[0])

    @register(methods)
    def nandohisoahe(self, obj, args):  # issubset
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.issubset(args[0])

    @register(methods)
    def wadohisoahe(self, obj, args):  # issuperset
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.issuperset(args[0])

    @register(methods)
    def alaghahe(self, obj, args):  # isdisjoint
        if not isinstance(obj, set):
            raise TypeError("Needs a majmuo")
        return obj.isdisjoint(args[0])

    def get_all(self):
        return self.methods
