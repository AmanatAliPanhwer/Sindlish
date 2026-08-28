"""
Name resolution: slots, scopes, and closures.

Walks the parsed AST once, before compilation, and answers "where does every
name live". Local variables are assigned numbered frame slots; references and
assignments are stamped onto the AST nodes so the Compiler can emit
FAST/GLOBAL/DEREF access without re-deriving scope information.

Scope levels stamped onto nodes:

    0  local slot in the current frame       -> LOAD_FAST  / STORE_FAST
    1  program-global environment            -> LOAD_GLOBAL / STORE_GLOBAL
    2  closure Cell shared with an enclosing -> LOAD_DEREF / STORE_DEREF
       function

The resolver also enforces static type annotations (typed declarations and
collection element types) and feeds ``symbols`` to the LSP server.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ..errors import QisamJeGhalti
from ..frontend.ast_nodes import (
    AssignNode,
    BinaryOpNode,
    BlockNode,
    BoolNode,
    BreakNode,
    CallNode,
    ContinueNode,
    DictNode,
    ForNode,
    FunctionNode,
    GetAttrNode,
    GhaltiNode,
    GlobalNode,
    IfNode,
    IndexNode,
    ListNode,
    MethodCallNode,
    Node,
    NonLocalNode,
    NullNode,
    NumberNode,
    PostfixOpNode,
    ProgramNode,
    ResultConstructorNode,
    ResultMethodCallNode,
    ReturnNode,
    SetNode,
    StringNode,
    VariableNode,
    WhileNode,
)
from ..frontend.tokens import TokenType

_TYPE_NAME_MAP: dict[str, TokenType] = {
    "adad": TokenType.ADAD,
    "dahai": TokenType.DAHAI,
    "lafz": TokenType.LAFZ,
    "faislo": TokenType.FAISLO,
    "fehrist": TokenType.FEHRIST,
    "silsilo": TokenType.FEHRIST,
    "lughat": TokenType.LUGHAT,
    "majmuo": TokenType.MAJMUO,
    "khali": TokenType.KHALI,
    "kaam": TokenType.KAAM,
}


@dataclass(slots=True, eq=False)
class _FnRec:
    """Per-function resolution state for closure analysis.

    ``captured`` lists this function's own locals that inner functions
    capture (they become Cells). ``free``/``free_keys`` list the upvalues
    inherited from enclosing functions as ``(depth, name)`` pairs.
    ``nonlocal_names`` are the names declared via ``bahari``.
    """

    captured: list[str] = field(default_factory=list)
    free: list[tuple[int, str]] = field(default_factory=list)
    free_keys: set[tuple[int, str]] = field(default_factory=set)
    nonlocal_names: set[str] = field(default_factory=set)


def _infer_type(
    node: Node,
    find: Callable[[str], tuple | None],
    slot_metadata: dict,
) -> TokenType | None:
    """Infer a literal's TokenType, or a resolved slot's declared type.

    Returns ``None`` when the type cannot be proven yet; callers treat
    ``None`` as "unknown", never as a mismatch.
    """
    match node:
        case NumberNode(value=int()):
            return TokenType.ADAD
        case NumberNode(value=float()):
            return TokenType.DAHAI
        case StringNode():
            return TokenType.LAFZ
        case BoolNode():
            return TokenType.FAISLO
        case NullNode():
            return TokenType.KHALI
        case ListNode():
            return TokenType.FEHRIST
        case DictNode():
            return TokenType.LUGHAT
        case SetNode():
            return TokenType.MAJMUO
        case VariableNode():
            found = find(node.name)
            if found and found[0] == "slot" and found[2] > 0:
                return slot_metadata.get(found[1], {}).get("type")
            return None
        case _:
            return None


class Resolver:
    """Resolve names to storage locations before compilation.

    Assigns slot indices to locals, stamps ``scope_level``/``slot_index``/
    ``deref_*`` onto AST nodes, tracks closure cells, and verifies explicit
    type annotations. ``symbols`` feeds the VS Code LSP server.
    """

    def __init__(self, code: str):
        """Set up the scope stacks and closure bookkeeping for one walk.

        ``fn_records`` holds one ``_FnRec`` per function (index 0 is the
        program-level sentinel); ``scope_rec`` maps each scope to the
        function record that owns it.
        """
        self.code = code
        self.scopes: list[dict[str, int]] = [{}]
        self.function_scopes: list[set[str]] = [set()]
        self.fn_records: list[_FnRec] = [_FnRec()]
        self.scope_rec: list[_FnRec] = [self.fn_records[0]]
        self.declared_globals: set[str] = set()
        self.global_var_names: set[str] = set()
        self.next_slot: int = 0
        self.slot_metadata: dict[int, dict] = {}
        self.symbols: list[dict] = []

    def infer_type(self, node: Node) -> TokenType | None:
        """Infer the type of a literal or resolved reference (see ``_infer_type``)."""
        return _infer_type(node, self._find, self.slot_metadata)

    def resolve(self, node: Node | None) -> None:
        """Dispatch ``node`` to its ``resolve_<TypeName>`` visitor.

        Falls back to the generic recursive visitor (``no_resolve_method``)
        when no dedicated method exists.
        """
        if node is None:
            return
        method_name = f"resolve_{type(node).__name__}"
        method = getattr(self, method_name, self.no_resolve_method)
        return method(node)

    def no_resolve_method(self, node: Node) -> None:
        """Default visitor: recurse into every Node-typed attribute.

        Skips ``line``/``column``, then resolves all list/tuple/Node values
        found in the node's slots, so new node types resolve without a
        dedicated method.
        """
        if not hasattr(node, "__slots__"):
            return

        for attr in node.__slots__:
            if attr in ("line", "column"):
                continue

            val = getattr(node, attr)
            self._resolve_recursive(val)

    def _resolve_recursive(self, val) -> None:
        """Resolve ``val`` if it is a Node, or each element if list/tuple."""
        if isinstance(val, Node):
            self.resolve(val)
        elif isinstance(val, (list, tuple)):
            for item in val:
                self._resolve_recursive(item)

    def resolve_ProgramNode(self, node: ProgramNode) -> None:
        """Resolve every top-level statement; size the main frame."""
        for stmt in node.statements:
            self.resolve(stmt)
        node.slot_count = self.next_slot

    def resolve_BlockNode(self, node: BlockNode) -> None:
        """Resolve a block inside the current scope.

        Blocks never create a scope (Python semantics): a name bound inside a
        block belongs to the enclosing function, or to the program globals at
        top level, so it stays visible after the block closes.
        """
        for stmt in node.statements:
            self.resolve(stmt)

    def _verify_assignment_types(self, node: AssignNode) -> None:
        """Statically reject typed declarations that clearly mismatch.

        Only literal values are provable at resolve time; variables and call
        results return ``None`` from ``infer_type`` and defer to runtime
        checks. Collection element types are verified for fehrist/majmuo/lughat
        literals.
        """
        inferred_type = self.infer_type(node.value)

        # Typed collection literals: verify every statically knowable element
        # before the whole-literal match short-circuits.
        if (
            node.type in (TokenType.FEHRIST, TokenType.MAJMUO, TokenType.LUGHAT)
            and node.element_type is not None
            and isinstance(node.value, (ListNode, SetNode, DictNode))
        ):
            self._verify_collection_elements(node)
            return

        if inferred_type is None or inferred_type == node.type:
            return

        line = getattr(node, "line", 0)
        column = getattr(node, "column", 0)
        raise QisamJeGhalti(
            f"Qisam natho mile: {node.type.name.lower()} khapyo paye, par {inferred_type.name.lower()} milyo.",
            line,
            column,
            self.code,
        )

    def _verify_collection_elements(self, node: AssignNode) -> None:
        """Verify statically inferable element types of a typed collection literal.

        Unprovable elements (``infer_type`` returns ``None``) are deferred; the
        runtime check still enforces them on execution.
        """
        if node.type == TokenType.LUGHAT and isinstance(node.value, DictNode):
            key_type, val_type = node.element_type
            for key, value in node.value.pairs:
                self._check_element_types(key, key_type, "Lughat")
                self._check_element_types(value, val_type, "Lughat")
            return

        container = "Fehrist" if isinstance(node.value, ListNode) else "Majmuo"
        for elem in node.value.elements:
            self._check_element_types(elem, node.element_type, container)

    def _check_element_types(
        self, elem: Node, expected: TokenType, container: str
    ) -> None:
        """Raise when ``elem``'s static type provably differs from ``expected``.

        Nested/compound element types are not provable statically and are
        deferred to the runtime check.
        """
        elem_type = self.infer_type(elem)
        if not isinstance(elem_type, TokenType) or not isinstance(
            expected, TokenType
        ):
            return
        if elem_type == expected:
            return
        line = getattr(elem, "line", 0)
        column = getattr(elem, "column", 0)
        raise QisamJeGhalti(
            f"{container} je elements jo qisam {expected.name.lower()} hujjhan lazmi aahe, par {elem_type.name.lower()} milyo.",
            line,
            column,
            self.code,
        )

    def _normalize_annotation(
        self, ann: str | TokenType | None, line: int, column: int
    ) -> TokenType | None:
        """STRICT policy: string annotations must name a known type.

        Builtin spellings upgrade to TokenType; a declared variable/function
        name gets a targeted error; anything else is unknown.
        """
        if not isinstance(ann, str):
            return ann
        tok = _TYPE_NAME_MAP.get(ann.lower())
        if tok is not None:
            return tok
        if ann in self.global_var_names:
            raise QisamJeGhalti(
                f"'{ann}' hik variable ya kaam jo naalo aahe; qisam natho thiyen saghjay.",
                line,
                column,
                self.code,
            )
        raise QisamJeGhalti(
            f"Qisam '{ann}' natho mile.",
            line,
            column,
            self.code,
        )

    def _normalize_element(
        self, elem: list | str | TokenType | None, line: int, column: int
    ) -> list | TokenType | None:
        """Normalize ``[key, val]`` pairs or single element annotations."""
        if isinstance(elem, list):
            return [self._normalize_annotation(e, line, column) for e in elem]
        return self._normalize_annotation(elem, line, column)

    def resolve_AssignNode(self, node: AssignNode) -> None:
        """Resolve an assignment/declaration and stamp its storage location.

        The value is resolved first. Nonlocal (``bahari``) writes route to a
        closure Cell; program-level, ``aalmi``, and unknown names go to the
        globals environment (``scope_level`` 1). Local writes reuse the nearest
        slot or allocate a fresh one, recording const/type metadata for
        runtime enforcement.
        """
        self.resolve(node.value)

        if node.type is not None:
            node.type = self._normalize_annotation(node.type, node.line, node.column)
        if node.element_type is not None:
            node.element_type = self._normalize_element(
                node.element_type, node.line, node.column
            )

        if node.has_explicit_type and node.type is not None:
            self._verify_assignment_types(node)

        found = self._find(node.name)

        # Assignment through a 'bahari' declaration targets the outer cell
        top_rec = self.fn_records[-1]
        if node.name in top_rec.nonlocal_names:
            depth, _ = next(e for e in top_rec.free if e[1] == node.name)
            node.scope_level = 2
            node.deref_depth = depth
            node.deref_name = node.name
            return

        goes_global = (
            node.name in self.declared_globals
            or len(self.scopes) == 1
            or (found is not None and found[2] == 0)
        )

        if goes_global:
            # Program-level variables live in the globals environment;
            # const/type enforcement happens at runtime via STORE_GLOBAL.
            self.global_var_names.add(node.name)
            node.scope_level = 1
            node.slot_index = -1
            return

        if found is None or found[0] == "function":
            slot = self.define(node.name, node)
        elif found[3] is not None and found[3] is not top_rec:
            # Name belongs to an enclosing function's local scope.
            # Writes require an explicit 'bahari' declaration.
            line = getattr(node, "line", 0)
            column = getattr(node, "column", 0)
            raise QisamJeGhalti(
                f"'{node.name}' baharli kaam jo variable aahe; us khe badhayn laai 'bahari {node.name}' likho.",
                line,
                column,
                self.code,
            )
        else:
            slot = found[1]

        node.slot_index = slot
        node.scope_level = 0

        existing = self.slot_metadata.get(slot)
        if node.has_explicit_type and node.type is not None:
            if existing is not None and existing["has_explicit_type"]:
                old_type = existing["type"]
                old_elem = existing["element_type"]
                if (
                    old_type != node.type
                    or old_elem != node.element_type
                    or bool(existing["is_const"]) != bool(node.is_const)
                ):
                    line = getattr(node, "line", 0)
                    column = getattr(node, "column", 0)
                    old_name = old_type.name.lower() if old_type else "undefined"
                    raise QisamJeGhalti(
                        f"Qisam natho badlo sendho: '{node.name}' pehryoan '{old_name}' khapyo paye, par '{node.type.name.lower()}' milyo.",
                        line,
                        column,
                        self.code,
                    )
            self.slot_metadata[slot] = {
                "is_const": node.is_const,
                "type": node.type,
                "element_type": node.element_type,
                "has_explicit_type": True,
            }
        elif slot not in self.slot_metadata:
            self.slot_metadata[slot] = {
                "is_const": node.is_const,
                "type": None,
                "element_type": node.element_type,
                "has_explicit_type": False,
            }

    def push_scope(self) -> None:
        """Push a scope bucket: name map, function names, and owner record."""
        self.scopes.append({})
        self.function_scopes.append(set())
        self.scope_rec.append(self.fn_records[-1])

    def pop_scope(self) -> None:
        """Pop the innermost scope bucket."""
        self.scopes.pop()
        self.function_scopes.pop()
        self.scope_rec.pop()

    def define(self, name: str, node: Node | None = None) -> int:
        """Allocate a fresh slot for ``name`` unless already bound here.

        Returns the existing slot when ``name`` is already in the innermost
        scope; otherwise allocates ``next_slot``, records the name in the
        current scope, and feeds the LSP symbol table.
        """
        if name in self.scopes[-1]:
            return self.scopes[-1][name]

        slot = self.next_slot
        self.next_slot += 1

        self.scopes[-1][name] = slot

        # Track symbol for LSP
        if node:
            self.symbols.append(
                {
                    "name": name,
                    "type": getattr(node, "type", None),
                    "line": getattr(node, "line", 0),
                    "col": getattr(node, "column", 0),
                    "kind": "variable" if isinstance(node, AssignNode) else "function",
                }
            )

        return slot

    def define_function(self, name: str, node: Node | None = None) -> None:
        """Register ``name`` as a function in this scope without a slot.

        Function values live in the globals environment, so references
        compile to ``LOAD_GLOBAL`` instead of reading an empty local slot.
        """
        self.function_scopes[-1].add(name)
        if node:
            self.symbols.append(
                {
                    "name": name,
                    "type": getattr(node, "type", None),
                    "line": getattr(node, "line", 0),
                    "col": getattr(node, "column", 0),
                    "kind": "function",
                }
            )

    def _find(self, name: str) -> tuple | None:
        """Find a name across scopes.

        Returns ``("slot", slot_index, owner_scope_index, owner_record)``,
        ``("function", None, owner_scope_index, None)``,
        ``("global", -1, 0, None)`` for program-level variables, or ``None``
        when the name is unknown. Scope indices >= 1 hold frame-local slots;
        scope 0 is the program-global scope whose variables live in the
        globals environment.
        """
        for i in range(len(self.scopes) - 1, 0, -1):
            if name in self.function_scopes[i]:
                return ("function", None, i, None)
            if name in self.scopes[i]:
                return ("slot", self.scopes[i][name], i, self.scope_rec[i])
        if name in self.function_scopes[0]:
            return ("function", None, 0, None)
        if name in self.global_var_names:
            return ("global", -1, 0, None)
        return None

    def _register_capture(self, name: str, owner: _FnRec) -> int:
        """Mark ``name`` (a local of ``owner``) as captured by the current function.

        Registers a cell on the owning function and pass-through free
        entries on every intermediate function. Returns the upvalue depth
        from the current (innermost) function.
        """
        top_idx = len(self.fn_records) - 1
        own_idx = self.fn_records.index(owner)
        if name not in owner.captured:
            owner.captured.append(name)
        for lvl in range(own_idx + 1, top_idx + 1):
            rec = self.fn_records[lvl]
            entry = (lvl - own_idx, name)
            if entry not in rec.free_keys:
                rec.free_keys.add(entry)
                rec.free.append(entry)
        return top_idx - own_idx

    def get_slot_metadata(self) -> dict[int, dict]:
        """Return the slot -> metadata ledger for the main (program) frame."""
        return self.slot_metadata

    def resolve_VariableNode(self, node: VariableNode) -> None:
        """Stamp a variable reference's storage: slot, global, or closure Cell.

        References to an enclosing function's local auto-register a closure
        capture (``scope_level`` 2); references to globals, functions, and
        unknown names fall back to ``scope_level`` 1.
        """
        found = self._find(node.name)
        if (
            found is not None
            and found[0] == "slot"
            and found[2] > 0
            and node.name not in self.declared_globals
        ):
            owner = found[3]
            if owner is not None and owner is not self.fn_records[-1]:
                # Reference to an enclosing function's local: closure capture
                node.scope_level = 2
                node.deref_depth = self._register_capture(node.name, owner)
                node.deref_name = node.name
            else:
                node.slot_index = found[1]
                node.scope_level = 0
        else:
            node.scope_level = 1

    def resolve_IfNode(self, node: IfNode) -> None:
        """Resolve an if/else-if/else chain (bodies resolve in the current scope)."""
        self.resolve(node.condition)
        self.resolve(node.body)
        if node.else_if_bodies:
            for else_if_condition, else_if_body in node.else_if_bodies:
                self.resolve(else_if_condition)
                self.resolve(else_if_body)
        if node.else_body:
            self.resolve(node.else_body)

    def resolve_WhileNode(self, node: WhileNode) -> None:
        """Resolve a while loop's condition and body."""
        self.resolve(node.condition)
        self.resolve(node.body)

    def resolve_ForNode(self, node: ForNode) -> None:
        """Bind the iterator in the current scope (flat, Python-style).

        Inside a function the iterator is an ordinary local slot; at program
        level it is a global (``iterator_slot`` -1), so it leaks its last
        value after the loop like a module-level Python loop variable.
        """
        self.resolve(node.iterable)

        if len(self.scopes) == 1:
            self.global_var_names.add(node.iterator)
            node.iterator_slot = -1
        else:
            node.iterator_slot = self.define(node.iterator, node)

        self.resolve(node.body)

    def resolve_BreakNode(self, node: BreakNode) -> None:
        """Break is a control-flow marker; nothing to resolve."""
        return

    def resolve_ContinueNode(self, node: ContinueNode) -> None:
        """Continue is a control-flow marker; nothing to resolve."""
        return

    def resolve_CallNode(self, node: CallNode) -> None:
        """Resolve a call's callee (when computed) and its arguments.

        For computed callees (``f()()``, factory results) ``CallNode.name`` is
        a Node and is resolved just like MethodCallNode resolves its instance;
        for named calls it is a str and needs no resolution. Named calls to a
        function-local or captured variable get a ``callee_variable`` stamp so
        the compiler routes them through CALL_VALUE instead of a globals-only
        name lookup (issue #30 2.6).
        """
        if isinstance(node.name, Node):
            self.resolve(node.name)
        elif isinstance(node.name, str):
            found = self._find(node.name)
            if (
                found is not None
                and found[0] == "slot"
                and found[2] > 0
                and node.name not in self.declared_globals
            ):
                owner = found[3]
                callee = VariableNode(node.name)
                if owner is not None and owner is not self.fn_records[-1]:
                    callee.scope_level = 2
                    callee.deref_depth = self._register_capture(node.name, owner)
                    callee.deref_name = node.name
                else:
                    callee.scope_level = 0
                    callee.slot_index = found[1]
                node.callee_variable = callee
        for arg in node.args:
            self.resolve(arg)

    def resolve_MethodCallNode(self, node: MethodCallNode) -> None:
        """Resolve a method call's instance and arguments."""
        self.resolve(node.instance)
        for arg in node.args:
            self.resolve(arg)

    def resolve_GetAttrNode(self, node: GetAttrNode) -> None:
        """Resolve the instance an attribute is read from."""
        self.resolve(node.instance)

    def resolve_BinaryOpNode(self, node: BinaryOpNode) -> None:
        """Resolve both operands of a binary expression."""
        self.resolve(node.left)
        self.resolve(node.right)

    def resolve_ListNode(self, node: ListNode) -> None:
        """Resolve every element of a list literal."""
        for el in node.elements:
            self.resolve(el)

    def resolve_DictNode(self, node: DictNode) -> None:
        """Resolve every key/value pair of a dict literal."""
        for k, v in node.pairs:
            self.resolve(k)
            self.resolve(v)

    def resolve_SetNode(self, node: SetNode) -> None:
        """Resolve every element of a set literal."""
        for el in node.elements:
            self.resolve(el)

    def resolve_IndexNode(self, node: IndexNode) -> None:
        """Resolve a subscript read/write (target, index, optional value)."""
        self.resolve(node.left)
        self.resolve(node.index)
        if node.value:
            self.resolve(node.value)

    def resolve_FunctionNode(self, node: FunctionNode) -> None:
        """Resolve params and body, snapshoting per-function closure state.

        Slot numbering restarts per function; ``slot_count``, ``slot_metadata``,
        ``cell_slots`` (own locals captured by inner functions) and
        ``free_slots`` (inherited upvalues) are recorded for the compiler to
        build the ``SdFunction`` and its frame.
        """
        # Function names live in the globals environment, not in frame slots
        self.define_function(node.name, node)

        node.return_type = self._normalize_annotation(
            node.return_type, node.line, node.column
        )

        # Then we push a new scope for params and body
        old_next_slot = self.next_slot
        old_slot_metadata = self.slot_metadata
        self.next_slot = 0
        self.slot_metadata = {}

        rec = _FnRec()
        self.fn_records.append(rec)
        self.push_scope()
        for param in node.params:
            param.type = self._normalize_annotation(param.type, node.line, node.column)
            if param.element_type is not None:
                param.element_type = self._normalize_element(
                    param.element_type, node.line, node.column
                )
            param_slot = self.define(param.name, param)
            param.slot_index = param_slot
        self.resolve(node.body)
        node.slot_count = self.next_slot
        node.slot_metadata = self.slot_metadata
        node.cell_slots = tuple(rec.captured)
        node.free_slots = tuple(rec.free)
        node.cell_metadata = {
            name: self.slot_metadata[slot]
            for name in rec.captured
            if name in self.scopes[-1]
            and (slot := self.scopes[-1][name]) in self.slot_metadata
        }
        self.pop_scope()
        self.fn_records.pop()

        self.next_slot = old_next_slot
        self.slot_metadata = old_slot_metadata

    def resolve_GlobalNode(self, node: GlobalNode) -> None:
        """Record an ``aalmi`` declaration: the name now routes to globals."""
        self.declared_globals.add(node.name)
        self.global_var_names.add(node.name)

    def resolve_NonLocalNode(self, node: NonLocalNode) -> None:
        """Record a ``bahari`` declaration targeting an enclosing function's local.

        The nearest enclosing scope owned by an enclosing ``_FnRec`` that
        binds the name becomes its owner; the name is registered as a capture
        and added to the current function's ``nonlocal_names``. Program-level
        use and unknown targets raise ``QisamJeGhalti``.
        """
        name = node.name
        line = getattr(node, "line", 0)
        column = getattr(node, "column", 0)
        if len(self.fn_records) == 1:
            raise QisamJeGhalti(
                "'bahari' sirf kaam ke andar istemaal thyo sendho.",
                line,
                column,
                self.code,
            )
        owner = None
        for lvl in range(len(self.fn_records) - 2, -1, -1):
            rec = self.fn_records[lvl]
            for i in range(len(self.scopes) - 1, 0, -1):
                if self.scope_rec[i] is rec and name in self.scopes[i]:
                    owner = rec
                    break
            if owner is not None:
                break
        if owner is None:
            raise QisamJeGhalti(
                f"'bahari {name}' laai baharli kaam mein '{name}' naatho milio.",
                line,
                column,
                self.code,
            )
        self._register_capture(name, owner)
        self.fn_records[-1].nonlocal_names.add(name)

    def resolve_ReturnNode(self, node: ReturnNode) -> None:
        """Resolve the returned expression, if any."""
        if node.value:
            self.resolve(node.value)

    def resolve_ResultMethodCallNode(self, node: ResultMethodCallNode) -> None:
        """Resolve a Result method call (receiver + single argument)."""
        self.resolve(node.receiver)
        self.resolve(node.arg)

    def resolve_PostfixOpNode(self, node: PostfixOpNode) -> None:
        """Resolve the expression a postfix operator (``?``/``!!``) applies to."""
        self.resolve(node.expr)

    def resolve_GhaltiNode(self, node: GhaltiNode) -> None:
        """Resolve a statement-level ``ghalti`` panic argument."""
        self.resolve(node.message)

    def resolve_ResultConstructorNode(self, node: ResultConstructorNode) -> None:
        """Resolve the value wrapped by ``ok()`` / ``ghalti()``."""
        self.resolve(node.value)