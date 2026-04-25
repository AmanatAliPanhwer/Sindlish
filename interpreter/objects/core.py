from .base import SdShey, SdType
from ..frontend.tokens import TokenType
from ..errors import QisamJeGhalti

KHALI_TYPE = SdType("KHALI", TokenType.KHALI)
KAAM_TYPE = SdType("KAAM", TokenType.KAAM)
RESULT_TYPE = SdType("RESULT", None)

class SdResult(SdShey):
    __slots__ = ('variant', 'value', 'ok', 'ghalti', '_captured_traceback', '_error_cls')
    
    OK = "OK"
    GHALTI = "GHALTI"
    
    def __init__(self, variant, value, error_cls=None):
        from .numbers import SdBool # Local import to prevent circular dependency
        super().__init__(RESULT_TYPE)
        self.variant = variant
        self.value = value
        self.ok = SdBool(self.variant == self.OK)
        self.ghalti = SdBool(self.variant == self.GHALTI)
        self._captured_traceback = []
        self._error_cls = error_cls or "HalndeVaktGhalti"

    def capture_traceback(self, frames, code_string):
        """Captures the current call stack for GHALTI results."""
        if self.variant != self.GHALTI:
            return
        
        from ..errors import TracebackEntry
        source_lines = code_string.split('\n')
        for frame in frames:
            line, col = frame.line_col_map.get(frame.ip, (0, 0))
            if line == 0: continue
            source_line = source_lines[line-1] if 0 < line <= len(source_lines) else None
            self._captured_traceback.append(TracebackEntry(frame.name, line, col, source_line))

    def is_ok(self):
        return self.variant == self.OK

    def is_error(self):
        return self.variant == self.GHALTI

    def __eq__(self, other):
        from .numbers import SdBool
        if not isinstance(other, SdResult):
            return SdBool(False)
        return SdBool(self.variant == other.variant and self.value == other.value)

    def __str__(self):
        return str(self.value)

    def __hash__(self):
        return hash((self.variant, self.value))

class SdFunction(SdShey):
    __slots__ = ('name', 'params', 'instructions', 'constants', 'line_col_map', 'slot_count', 'slot_metadata', 'return_type')
    
    def __init__(self, name, params, instructions, constants, line_col_map, slot_count, slot_metadata, return_type=None):
        super().__init__(KAAM_TYPE)
        self.name = name
        self.params = params
        self.instructions = instructions
        self.constants = constants
        self.line_col_map = line_col_map
        self.slot_count = slot_count
        self.slot_metadata = slot_metadata
        self.return_type = return_type

    def __str__(self):
        return f"<kaam {self.name}>"

    def __hash__(self):
        return id(self)

class SdNull(SdShey):
    __slots__ = ('value',)
    
    def __init__(self):
        super().__init__(KHALI_TYPE)
        self.value = None

    def __eq__(self, other):
        from .numbers import SdBool
        return SdBool(isinstance(other, SdNull))
    
    def __ne__(self, other):
        from .numbers import SdBool
        return SdBool(not isinstance(other, SdNull))
    
    def __str__(self):
        return "khali"
    
    def __hash__(self):
        return hash(None)
    
    def __bool__(self):
        return False
