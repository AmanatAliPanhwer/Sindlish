from ..errors import QisamJeGhalti, HalndeVaktGhalti, NaleJeGhalti, ZeroVindJeGhalti, IndexJeGhalti, LikhaiJeGhalti
from ..tokens import TokenType


class SdType:
    """
    Type objects in Sindlish.
    Acts as metaclass for SdObject subclasses.
    Mirrors Python's 'type' - types are objects too.
    
    Like CPython's PyTypeObject, SdType defines:
    - Name and token type
    - Type-level methods
    - Base classes for MRO
    - Instance creation protocol
    """
    __slots__ = ('name', 'token_type', '_methods', '_bases', '_mro_cache', '_instance_class')
    
    def __init__(self, name: str, token_type: TokenType, instance_class=None):
        self.name = name
        self.token_type = token_type
        self._methods = {}
        self._bases = ()
        self._mro_cache = None
        self._instance_class = instance_class  # Don't use default - handle in _new()
    
    def __repr__(self):
        return f"<SdType '{self.name}'>"
    
    @property
    def __dict__(self) -> dict:
        """Type's namespace - like Python's type.__dict__"""
        return self._methods
    
    def __call__(self, *args, **kwargs):
        """Calling a type creates an instance - mirrors type.__call__"""
        return self._new(*args, **kwargs)
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, SdType):
            return False
        return self.name == other.name and self.token_type == other.token_type
    
    def __ne__(self, other) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.name, self.token_type))
    
    @property
    def bases(self) -> tuple:
        """Parent types for MRO"""
        return self._bases
    
    @bases.setter
    def bases(self, value: tuple):
        self._bases = value
        self._mro_cache = None
    
    @property
    def mro(self) -> tuple:
        """Method Resolution Order - like Python's type.mro"""
        if self._mro_cache is None:
            self._mro_cache = self._compute_mro()
        return self._mro_cache
    
    def _compute_mro(self) -> tuple:
        """
        Compute MRO using C3 linearization algorithm.
        Mirrors CPython's type resolution order computation.
        """
        if not self._bases:
            return (self,)
        
        # C3 linearization algorithm
        merge_seq = []
        for base in self._bases:
            if isinstance(base, SdType):
                merge_seq.append(base.mro)
            else:
                merge_seq.append((base,))
        
        result = self._c3_merge(merge_seq)
        return tuple(result) + (self,)
    
    def _c3_merge(self, sequences: list) -> list:
        """
        C3 merge step - merge head elements from sequences.
        """
        result = []
        while True:
            merged = False
            
            for seq in sequences:
                if not seq:
                    continue
                
                head = seq[0]
                
                # Check if head appears in any tail
                appears_in_tail = False
                for other_seq in sequences:
                    if other_seq is seq or not other_seq:
                        continue
                    if head in other_seq[1:]:
                        appears_in_tail = True
                        break
                
                if not appears_in_tail:
                    result.append(head)
                    for seq in sequences:
                        if seq and seq[0] == head:
                            sequences[sequences.index(seq)] = seq[1:]
                    merged = True
                    break
            
            if not merged:
                break
            
            # Check if all sequences are empty
            if all(not seq for seq in sequences):
                break
        
        return result
    
    def _new(self, *args, **kwargs):
        """Instance creation - mirrors tp_new"""
        if self._instance_class is None:
            # Fallback to using object.__new__ on the class that created this type
            # Subclasses should override this properly
            obj = object.__new__(self.__class__.__bases__[0] if self.__class__.__bases__ else SdObject)
        else:
            obj = object.__new__(self._instance_class)
        if hasattr(obj, '__init__'):
            obj.__init__(*args, **kwargs)
        return obj
    
    def register_method(self, name: str, method):
        """Register a type-level method"""
        self._methods[name] = method
    
    def get_method(self, name: str):
        """Get a type-level method"""
        return self._methods.get(name)
    
    def lookup_method(self, name: str):
        """
        Look up method by name using MRO.
        Like Python's attribute lookup on types.
        """
        for type_obj in self.mro:
            if isinstance(type_obj, SdType):
                method = type_obj._methods.get(name)
                if method is not None:
                    return method
        return None


# Base SdType for base object - uses None since it doesn't map to a token
OBJECT_TYPE = SdType("OBJECT", None)


class SdObject:
    """
    Base for ALL Sindlish objects.
    Mirrors CPython's PyObject structure.
    
    __slots__ defines fixed attributes - like CPython's 
    fixed-layout objects. Subclasses MUST extend __slots__.
    
    Attributes:
    - _type: reference to type object
    - _ref_count: reference count for memory management
    """
    __slots__ = ('_type', '_ref_count')
    
    def __init__(self, type_obj: SdType):
        self._type = type_obj
        self._ref_count = 1
    
    @property
    def type(self) -> SdType:
        """Object's type - mirrors Python's obj.__class__"""
        return self._type
    
    @type.setter
    def type(self, value: SdType):
        self._type = value
    
    @property
    def ref_count(self) -> int:
        """Reference count"""
        return self._ref_count
    
    # Python special methods - default implementations
    def __eq__(self, other) -> bool:
        """Identity-based equality - like Python's 'is'"""
        if not isinstance(other, SdObject):
            return False
        return id(self) == id(other)
    
    def __ne__(self, other) -> bool:
        """Inequality"""
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        """
        Hash based on identity for mutable objects.
        Immutable subclasses should override with value-based hash.
        """
        return id(self)
    
    def __repr__(self) -> str:
        return f"<{self.type.name} object at 0x{id(self):x}>"
    
    def __str__(self) -> str:
        return f"<{self.type.name} object>"
    
    def __bool__(self) -> bool:
        """Default truthiness - like Python"""
        return True
    
    def __len__(self) -> int:
        """Default length - subclasses should override"""
        raise TypeError(f"object of type '{self.type.name}' has no len()")
    
    def __iter__(self):
        """Default iteration - raise TypeError"""
        raise TypeError(f"'{self.type.name}' object is not iterable")
    
    def __getitem__(self, key):
        """Subscription - raise TypeError"""
        raise TypeError(f"'{self.type.name}' object is not subscriptable")
    
    def __setitem__(self, key, value):
        """Subscription assignment - raise TypeError"""
        raise TypeError(f"'{self.type.name}' object does not support item assignment")
    
    def __contains__(self, item) -> bool:
        """Container membership test"""
        raise TypeError(f"'{self.type.name}' object is not a container")
    
    # Object protocol methods
    def call_method(self, name: str, args: list, node=None, code=""):
        """
        Dispatch method calls.
        1. First checks for protocol method (Python dunder methods)
        2. Falls back to type's method lookup via MRO
        Maps Python exceptions to Sindlish-specific error classes.
        """
        line = node.line if node else 1
        column = node.column if node else 1
        
        # First: Check for actual protocol method (Python dunder methods)
        protocol_method = getattr(self, name, None)
        if protocol_method and callable(protocol_method):
            try:
                return protocol_method(*args)
            except (QisamJeGhalti, HalndeVaktGhalti, NaleJeGhalti, ZeroVindJeGhalti, IndexJeGhalti, LikhaiJeGhalti):
                raise
            except TypeError as e:
                raise QisamJeGhalti(str(e), line, column, code)
            except Exception as e:
                raise HalndeVaktGhalti(str(e), line, column, code)
        
        # Second: Fallback to type's method lookup via MRO
        method = self._type.lookup_method(name)
        
        if not method:
            raise QisamJeGhalti(
                details=f"'{self.type.name}' object mein '{name}' nale jo ko bh method na aahe.",
                line=line,
                column=column,
                code_string=code
            )
        
        try:
            return method(*args)
        except (QisamJeGhalti, HalndeVaktGhalti, NaleJeGhalti, ZeroVindJeGhalti, IndexJeGhalti, LikhaiJeGhalti):
            raise
        except TypeError as e:
            raise QisamJeGhalti(str(e), line, column, code)
        except Exception as e:
            raise HalndeVaktGhalti(str(e), line, column, code)
    
    # Reference counting
    def incref(self):
        """Increment reference count"""
        self._ref_count += 1
    
    def decref(self):
        """Decrement reference count"""
        self._ref_count -= 1
        if self._ref_count <= 0:
            self._dealloc()
    
    def _dealloc(self):
        """Deallocate object - override for cleanup"""
        pass