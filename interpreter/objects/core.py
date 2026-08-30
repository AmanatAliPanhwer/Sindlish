from ..frontend.tokens import TokenType
from .base import SdShey, SdType

KHALI_TYPE = SdType("KHALI", TokenType.KHALI)
KAAM_TYPE = SdType("KAAM", TokenType.KAAM)
RESULT_TYPE = SdType("RESULT", None)


class SdResult(SdShey):
    __slots__ = (
        "_captured_traceback",
        "_error_cls",
        "ghalti",
        "ok",
        "value",
        "variant",
    )

    OK = "OK"
    GHALTI = "GHALTI"

    def __init__(self, variant, value, error_cls=None):
        from .numbers import SdBool  # Local import to prevent circular dependency

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

        source_lines = code_string.split("\n")
        for frame in frames:
            line_col_map = frame.line_col_map
            pc = frame.ip - 1
            line, col = (
                line_col_map[pc] if 0 <= pc < len(line_col_map) else (0, 0)
            )
            if line == 0:
                continue
            source_line = (
                source_lines[line - 1] if 0 < line <= len(source_lines) else None
            )
            self._captured_traceback.append(
                TracebackEntry(frame.name, line, col, source_line)
            )

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


class CallPlan:
    """Precomputed call-time metadata for a :class:`SdFunction`.

    Built once when a function is defined and refreshed when defaults are
    bound, eliminating the per-call scans of ``params`` and default-value
    lookups that previously happened on every invocation.
    """

    __slots__ = (
        "arity",
        "captured",
        "defaults_map",
        "expected_types",
        "has_defaults",
        "has_kw",
        "has_star",
        "known_names",
        "params",
        "simple",
    )

    def __init__(self, params, defaults=(), cell_names=()):
        from .collections import FEHRIST_TYPE, LUGHAT_TYPE, MAJMUO_TYPE
        from .numbers import ADAD_TYPE, DAHAI_TYPE, FAISLO_TYPE
        from .strings import LAFZ_TYPE

        params = tuple(params)
        self.params = params
        self.has_star = any(p.is_star for p in params)
        self.has_kw = any(p.is_kw for p in params)
        self.arity = sum(1 for p in params if not p.is_star and not p.is_kw)

        defaults_map = {}
        defaults = tuple(defaults)
        di = 0
        for p in params:
            if p.default is not None:
                defaults_map[p.name] = (
                    defaults[di] if di < len(defaults) else p.default
                )
                di += 1
        self.defaults_map = defaults_map
        self.has_defaults = bool(defaults_map)
        self.known_names = (
            None if self.has_kw else frozenset(p.name for p in params)
        )

        type_map = {
            TokenType.ADAD: ADAD_TYPE,
            TokenType.DAHAI: DAHAI_TYPE,
            TokenType.LAFZ: LAFZ_TYPE,
            TokenType.FAISLO: FAISLO_TYPE,
            TokenType.FEHRIST: FEHRIST_TYPE,
            TokenType.LUGHAT: LUGHAT_TYPE,
            TokenType.MAJMUO: MAJMUO_TYPE,
        }
        self.expected_types = tuple(type_map.get(p.type) for p in params)
        self.captured = tuple(name in cell_names for name in (p.name for p in params))

        self.simple = (
            not self.has_star
            and not self.has_kw
            and not self.has_defaults
            and not any(p.element_type is not None for p in params)
            and not cell_names
        )


class Cell:
    """Mutable box shared between a function frame and its closures."""

    __slots__ = ("metadata", "name", "value")

    def __init__(self, value=None, name=None, metadata=None):
        self.value = value
        self.name = name
        self.metadata = metadata if metadata is not None else {}


class SdFunction(SdShey):
    __slots__ = (
        "call_plan",
        "cell_metadata",
        "cell_names",
        "cells",
        "constants",
        "defaults",
        "free_specs",
        "instructions",
        "line_col_map",
        "name",
        "params",
        "return_type",
        "slot_count",
        "slot_metadata",
    )

    def __init__(
        self,
        name,
        params,
        instructions,
        constants,
        line_col_map,
        slot_count,
        slot_metadata,
        return_type=None,
        defaults=(),
        cell_names=(),
        free_specs=(),
        cells=(),
        cell_metadata=None,
    ):
        super().__init__(KAAM_TYPE)
        self.name = name
        self.params = params
        self.instructions = instructions
        self.constants = constants
        self.line_col_map = line_col_map
        self.slot_count = slot_count
        self.slot_metadata = slot_metadata
        self.return_type = return_type
        self.defaults = tuple(defaults)
        self.cell_names = tuple(cell_names)
        self.free_specs = tuple(free_specs)
        self.cells = tuple(cells)
        self.cell_metadata = dict(cell_metadata) if cell_metadata else {}
        self.call_plan = CallPlan(self.params, self.defaults, self.cell_names)

    def bind_defaults(self, defaults):
        """Return a copy of this function carrying evaluated default values."""
        return SdFunction(
            self.name,
            self.params,
            self.instructions,
            self.constants,
            self.line_col_map,
            self.slot_count,
            self.slot_metadata,
            self.return_type,
            defaults,
            self.cell_names,
            self.free_specs,
            self.cells,
            self.cell_metadata,
        )

    def __str__(self):
        return f"<kaam {self.name}>"

    def __hash__(self):
        return id(self)


class SdNull(SdShey):
    __slots__ = ("value",)

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
