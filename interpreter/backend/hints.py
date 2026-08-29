"""Per-node storage decisions resolved before compilation."""

from dataclasses import dataclass, field

from ..frontend.tokens import TokenType


@dataclass(slots=True, eq=False)
class CompilerHints:
    """Storage/closure decisions the Resolver stamps for the Compiler.

    The resolver fills one per name-bearing node; the compiler reads only
    this object (never raw resolver fields) to emit FAST/GLOBAL/DEREF
    access. Fields the resolver leaves untouched keep their defaults.
    """

    scope_level: int | None = None
    slot_index: int | None = None
    deref_depth: int | None = None
    deref_name: str | None = None
    is_const: bool = False
    type: TokenType | None = None
    element_type: object = None
    has_explicit_type: bool = False
    iterator_slot: int | None = None              # ForNode
    callee_variable: object = None                # CallNode
    slot_count: int = 0                           # FunctionNode
    slot_metadata: dict = field(default_factory=dict)
    cell_slots: tuple = ()
    free_slots: tuple = ()
    cell_metadata: dict = field(default_factory=dict)
