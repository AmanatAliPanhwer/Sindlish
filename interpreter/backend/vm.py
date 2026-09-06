"""Stack-machine VM for Sindlish bytecode.

The VM consumes the flat instruction list emitted by :mod:`.compiler` and
executes it against a single shared operand stack (``self.stack``) plus one
:class:`.frame.BytecodeFrame` per active call (each with its own local
slots / closure cells / instruction pointer).

Dispatch contract (see :meth:`VM.step`): every handler takes
``(frame, arg, line, column)``; handlers ``pop`` their operands from the
top of ``self.stack`` in evaluation order and ``append`` their result, so
the stack depth is unchanged. ``line``/``column`` point at the executing
instruction for error messages and are unused by the fast instruction
paths.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ..errors import (
    ERROR_MAP,
    HalndeVaktGhalti,
    LikhaiJeGhalti,
    NaleJeGhalti,
    QisamJeGhalti,
    SindhiBaseError,
)
from ..frontend.tokens import TokenType
from ..objects import (
    ADAD_TYPE,
    DAHAI_TYPE,
    FAISLO_TYPE,
    FEHRIST_TYPE,
    KHALI_TYPE,
    LAFZ_TYPE,
    LUGHAT_TYPE,
    MAJMUO_TYPE,
    SdBool,
    SdDict,
    SdFunction,
    SdList,
    SdNull,
    SdNumber,
    SdResult,
    SdSet,
    SdString,
)
from ..objects.base import sd_truthy
from ..objects.core import CallPlan
from ..runtime.builtins import SimpleBuiltins
from .frame import BytecodeFrame
from .markers import KwargMarker, KwargsDictMarker, StarArgsMarker
from .opcodes import OpCode

OpcodeHandler = Callable[["VM", BytecodeFrame, object, int, int], None]
DispatchTable = dict[OpCode, OpcodeHandler]
StoreGlobalArg = object | tuple[object, bool, object | None, object | None]

TYPE_MAP = {
    TokenType.ADAD: ADAD_TYPE,
    TokenType.DAHAI: DAHAI_TYPE,
    TokenType.LAFZ: LAFZ_TYPE,
    TokenType.FAISLO: FAISLO_TYPE,
    TokenType.FEHRIST: FEHRIST_TYPE,
    TokenType.LUGHAT: LUGHAT_TYPE,
    TokenType.MAJMUO: MAJMUO_TYPE,
    TokenType.KHALI: KHALI_TYPE,
}


@dataclass(frozen=True)
class LocationProxy:
    """Minimal ``node``-shaped object used to hand the VM position into
    :meth:`.objects.base.SdShey.call_method` without allocating a token."""

    line: int
    column: int


def _get_expected_type(type_hint):
    if type_hint is None:
        return None
    return TYPE_MAP.get(type_hint)


def _type_label(type_hint):
    """Human-readable name matching pre-refactor messages ('adad', 'MyClass')."""
    return type_hint.name.lower() if isinstance(type_hint, TokenType) else type_hint


class VM:
    def __init__(
        self,
        code_string: str,
        instructions: list[tuple[object, object]],
        constants: list[object],
        globals_env: object,
        slot_count: int,
        slot_metadata: dict,
        line_col_map: list[tuple[int, int]] | None = None,
    ):
        self.code_string = code_string
        self.globals = globals_env
        self.stack: list[object] = []
        self.line_col_map = line_col_map or []

        self.simple_handler = SimpleBuiltins()

        main_frame = BytecodeFrame(
            "main",
            instructions,
            constants,
            self.line_col_map,
            slot_count,
            slot_metadata,
        )
        self.frames = [main_frame]

        # Dispatch table is generated from handler names: every opcode's
        # handler must be named ``_op_<name.lower()>``. A missing handler is
        # a programming error surfaced immediately at construction.
        self.dispatch_table: DispatchTable = {
            opcode: getattr(self, f"_op_{opcode.name.lower()}")
            for opcode in OpCode
        }

        self._dispatch: list[OpcodeHandler | None] = [
            None
        ] * (int(max(OpCode)) + 1)
        for opcode, handler in self.dispatch_table.items():
            self._dispatch[int(opcode)] = handler

    def push(self, value: object) -> None:
        self.stack.append(value)

    def pop(self) -> object:
        return self.stack.pop()

    def _raise_from_result(self, val: SdResult, line: int, column: int) -> None:
        """Raise the error a Ghalti parcel remembers, with its frozen traceback."""
        error_cls = ERROR_MAP.get(val._error_cls, HalndeVaktGhalti)
        raise error_cls(
            str(val.value),
            line,
            column,
            self.code_string,
            traceback=val._captured_traceback,
        )

    def _unwrap_val(self, val: object, line: int, column: int) -> object:
        """Extracts the value from an Ok result, or panics on a Ghalti result."""
        if isinstance(val, SdResult):
            if val.is_ok():
                return val.value
            self._raise_from_result(val, line, column)
        return val

    def _check_type(
        self,
        value: object,
        expected_type: object | None,
        element_type: object | None = None,
        line: int = 0,
        column: int = 0,
    ) -> None:
        if isinstance(value, SdResult):
            if value.is_ok():
                value = value.value
            else:
                return
        match expected_type:
            case TokenType.ADAD:
                if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                    raise QisamJeGhalti(
                        f"'adad' qisam laai adad khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.DAHAI:
                if not isinstance(value, SdNumber) or not isinstance(
                    value.value, float
                ):
                    raise QisamJeGhalti(
                        f"'dahai' qisam laai dahai khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.LAFZ:
                if not isinstance(value, SdString):
                    raise QisamJeGhalti(
                        f"'lafz' qisam laai lafz khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.FAISLO:
                if not isinstance(value, SdBool):
                    raise QisamJeGhalti(
                        f"'faislo' qisam laai faislo khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.FEHRIST:
                if not isinstance(value, SdList):
                    raise QisamJeGhalti(
                        f"'fehrist' qisam laai fehrist khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
                if element_type is not None:
                    for elem in value.elements:
                        self._check_element_type(elem, element_type, line, column)

            case TokenType.MAJMUO:
                if not isinstance(value, SdSet):
                    raise QisamJeGhalti(
                        f"'majmuo' qisam laai majmuo khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
                if element_type is not None:
                    for elem in value.elements:
                        self._check_element_type(
                            elem, element_type, line, column, container_name="Majmuo"
                        )
            case TokenType.LUGHAT:
                if not isinstance(value, SdDict):
                    raise QisamJeGhalti(
                        f"'lughat' qisam laai lughat khapyo paye, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
                if element_type is not None and isinstance(element_type, list):
                    key_type, val_type = element_type
                    for k, v in value.pairs.items():
                        self._check_element_type(
                            k, key_type, line, column, container_name="Lughat"
                        )
                        self._check_element_type(
                            v, val_type, line, column, container_name="Lughat"
                        )

    def _check_element_type(
        self, value: object, element_type: object, line: int = 0, column: int = 0, container_name: str = "Fehrist"
    ) -> None:
        if isinstance(value, SdResult) and value.is_ok():
            value = value.value
        match element_type:
            case TokenType.ADAD:
                if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                    raise QisamJeGhalti(
                        f"{container_name} je elements jo qisam 'adad' hujjhan lazmi aahe, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.DAHAI:
                if not isinstance(value, SdNumber) or not isinstance(
                    value.value, float
                ):
                    raise QisamJeGhalti(
                        f"{container_name} je element jo qisam 'dahai' hujjhan lazmi aahe, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.LAFZ:
                if not isinstance(value, SdString):
                    raise QisamJeGhalti(
                        f"{container_name} je element jo qisam 'lafz' hujjhan lazmi aahe, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
            case TokenType.FAISLO:
                if not isinstance(value, SdBool):
                    raise QisamJeGhalti(
                        f"{container_name} je element jo qisam 'faislo' hujjhan lazmi aahe, par '{value.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )

    @property
    def variables(self) -> dict:
        result = {}
        for name, record in self.globals.records.items():
            result[name] = {
                "value": record.value,
                "is_const": getattr(record, "is_const", False),
            }
        return result

    def run(self) -> None:
        try:
            while self.frames:
                frame = self.frames[-1]
                if frame.ip < len(frame.instructions):
                    self.step()
                else:
                    if len(self.frames) == 1:
                        break
                    self.frames.pop()
        except SindhiBaseError as e:
            self._build_traceback(e)
            raise
        except Exception as e:
            print(f"Internal VM Error: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _build_traceback(self, error: SindhiBaseError) -> None:
        if error.traceback:
            return

        source_lines = self.code_string.split("\n")
        for frame in self.frames:
            line_col_map = frame.line_col_map
            pc = frame.ip - 1
            line, col = line_col_map[pc] if 0 <= pc < len(line_col_map) else (0, 0)
            if line == 0:
                continue

            source_line = (
                source_lines[line - 1] if 0 < line <= len(source_lines) else None
            )
            error.add_traceback(frame.name, line, col, source_line)

    def _handle_result(self, result: object) -> object:
        if isinstance(result, SdResult) and result.is_error() and not result._captured_traceback:
            result.capture_traceback(self.frames, self.code_string)
        return result

    def step(self) -> None:
        frame = self.frames[-1]
        instructions = frame.instructions
        pc = frame.ip
        opcode, arg = instructions[pc]
        frame.ip = pc + 1

        line_col = frame.line_col_map
        line, column = line_col[pc] if 0 <= pc < len(line_col) else (0, 0)

        handler = self._dispatch[opcode]
        if handler:
            handler(frame, arg, line, column)
        else:
            raise HalndeVaktGhalti(
                f"Na-maloom opcode: {opcode}.", line, column, self.code_string
            )

    # ===== OpCode Handlers =====

    def _op_load_const(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push the pooled constant ``result`` (``< -- result``)."""
        self.stack.append(frame.constants[arg])

    def _op_load_fast(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push the local slot ``arg`` (``< -- slot``)."""
        self.stack.append(frame.slots[arg])

    def _op_store_fast(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value into local slot ``arg``, after const/type checks (``value -- >``)."""
        value = self.stack.pop()
        metadata = frame.slot_metadata.get(arg, {})
        if metadata.get("is_const") and frame.slots[arg] is not None:
            raise HalndeVaktGhalti(
                "pakko (constant) variable badlaye natho saghjay.",
                line,
                column,
                self.code_string,
            )
        expected_type = metadata.get("type")
        if metadata.get("has_explicit_type", False) and expected_type is not None:
            self._check_type(
                value,
                expected_type,
                metadata.get("element_type"),
                line=line,
                column=column,
            )
        frame.slots[arg] = value

    def _op_load_global(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push the named global's value (``< -- global``)."""
        name = frame.constants[arg].value
        record = self.globals.lookup_record(name, None, self.code_string)
        self.push(record.value)

    def _op_store_global(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value into the named global, after const/type checks (``value -- >``)."""
        if not isinstance(arg, tuple):
            name = frame.constants[arg].value
            val = self.pop()
            if name in self.globals.records:
                self.globals.assign(name, val, None, self.code_string)
            else:
                self.globals.define(name, val)
            return

        const_idx, is_const, expected_type, element_type = arg
        name = frame.constants[const_idx].value
        val = self.pop()
        if name in self.globals.records:
            record = self.globals.records[name]
            if record.is_const and record.value is not None:
                raise HalndeVaktGhalti(
                    f"'{name}' pakko (const) aahe, eho badli natho saghjay.",
                    line,
                    column,
                    self.code_string,
                )
            if expected_type is None:
                expected_type = record.type
                element_type = (
                    element_type if expected_type is None else record.element_type
                )
            if expected_type is not None:
                self._check_type(
                    val, expected_type, element_type, line=line, column=column
                )
            record.value = val
        else:
            if expected_type is not None:
                self._check_type(
                    val, expected_type, element_type, line=line, column=column
                )
            self.globals.define(
                name, val, var_type=expected_type, is_const=is_const
            )

    def _op_push_null(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push ``SdNull()`` (``< -- null``)."""
        self.stack.append(SdNull())

    def _op_push_true(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push ``SdBool(True)`` (``< -- true``)."""
        self.stack.append(SdBool(True))

    def _op_push_false(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push ``SdBool(False)`` (``< -- false``)."""
        self.stack.append(SdBool(False))

    def _op_load_deref(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Push closure cell ``arg``'s value (``< -- cell``)."""
        cell = frame.cells[arg]
        if cell.value is None:
            name = getattr(cell, "name", None) or f"cell[{arg}]"
            raise HalndeVaktGhalti(
                f"'{name}' khe value likhwan khaan pehrioan read natho thyo sendho (khali cell).",
                line,
                column,
                self.code_string,
            )
        self.push(cell.value)

    def _op_store_deref(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value into closure cell ``arg``, after const/type checks (``value -- >``)."""
        value = self.pop()
        cell = frame.cells[arg]
        metadata = getattr(cell, "metadata", {})
        if metadata.get("is_const") and cell.value is not None:
            raise HalndeVaktGhalti(
                "pakko (constant) variable badlaye natho saghjay.",
                line,
                column,
                self.code_string,
            )
        expected_type = metadata.get("type")
        if metadata.get("has_explicit_type", False) and expected_type is not None:
            self._check_type(
                value,
                expected_type,
                metadata.get("element_type"),
                line=line,
                column=column,
            )
        cell.value = value

    def _binary_op_result(
        self, left: object, right: object, dunder: str, line: int, column: int
    ) -> object:
        try:
            out = left.call_method(
                dunder, [right], LocationProxy(line, column), self.code_string
            )
        except SindhiBaseError as e:
            if e.line is None:
                e.line, e.column, e.code_string = line, column, self.code_string
            err = SdResult(SdResult.GHALTI, SdString(str(e)), type(e).__name__)
            err.capture_traceback(self.frames, self.code_string)
            return err
        if isinstance(out, SdResult):
            if out.is_error():
                return self._handle_result(out)
            return out.value
        return out

    def _op_binary_add(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left + right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdNumber(left.value + right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__add__", line, column)
            )

    def _op_binary_sub(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left - right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdNumber(left.value - right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__sub__", line, column)
            )

    def _op_binary_mul(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left * right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdNumber(left.value * right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__mul__", line, column)
            )

    def _op_binary_div(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left / right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if (
            isinstance(left, SdNumber)
            and isinstance(right, SdNumber)
            and right.value != 0
        ):
            self.stack.append(SdNumber(left.value / right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__truediv__", line, column)
            )

    def _op_binary_pow(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left ** right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdNumber(left.value**right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__pow__", line, column)
            )

    def _op_binary_mod(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left % right`` (others: see dunder)."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if (
            isinstance(left, SdNumber)
            and isinstance(right, SdNumber)
            and right.value != 0
        ):
            self.stack.append(SdNumber(left.value % right.value))
        else:
            self.stack.append(
                self._binary_op_result(left, right, "__mod__", line, column)
            )

    def _op_compare_eq(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left == right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value == right.value))
        else:
            self.stack.append(
                left.call_method("__eq__", [right], None, self.code_string)
            )

    def _op_compare_ne(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left != right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value != right.value))
        else:
            self.stack.append(
                left.call_method("__ne__", [right], None, self.code_string)
            )

    def _op_compare_lt(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left < right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value < right.value))
        else:
            self.stack.append(
                left.call_method("__lt__", [right], None, self.code_string)
            )

    def _op_compare_le(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left <= right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value <= right.value))
        else:
            self.stack.append(
                left.call_method("__le__", [right], None, self.code_string)
            )

    def _op_compare_gt(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left > right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value > right.value))
        else:
            self.stack.append(
                left.call_method("__gt__", [right], None, self.code_string)
            )

    def _op_compare_ge(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``left`` and ``right``; push ``left >= right``."""
        right = self._unwrap_val(self.stack.pop(), line, column)
        left = self._unwrap_val(self.stack.pop(), line, column)
        if isinstance(left, SdNumber) and isinstance(right, SdNumber):
            self.stack.append(SdBool(left.value >= right.value))
        else:
            self.stack.append(
                left.call_method("__ge__", [right], None, self.code_string)
            )

    def _op_logical_not(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value; push its truthy negation (``value -- > not value``)."""
        val = self._unwrap_val(self.stack.pop(), line, column)
        self.stack.append(SdBool(not sd_truthy(val)))

    def _op_jump_absolute(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Set the instruction pointer to ``arg``."""
        frame.ip = arg

    def _op_jump_if_false(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value; jump to ``arg`` if it is falsy."""
        condition = self._unwrap_val(self.stack.pop(), line, column)
        if not sd_truthy(condition):
            frame.ip = arg

    def _op_jump_if_false_or_pop(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Peek top value; pop it if truthy, else jump to ``arg``."""
        condition = self._unwrap_val(self.stack[-1], line, column)
        if sd_truthy(condition):
            self.stack.pop()
        else:
            frame.ip = arg

    def _op_jump_if_true_or_pop(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Peek top value; jump to ``arg`` if truthy, else pop it."""
        condition = self._unwrap_val(self.stack[-1], line, column)
        if sd_truthy(condition):
            frame.ip = arg
        else:
            self.stack.pop()

    def _op_get_iter(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop an object; push its iterator (``< -- iterator``)."""
        obj = self._unwrap_val(self.pop(), line, column)
        try:
            it = iter(obj)
            self.push(it)
        except TypeError:
            raise QisamJeGhalti(
                f"'{obj.type.name}' object iterable na aahe.",
                line,
                column,
                self.code_string,
            )

    def _op_for_iter(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Advance the top iterator; push next value, or pop and jump at end."""
        it = self.stack[-1]  # Peek at the iterator
        try:
            val = next(it)
            self.push(val)
        except StopIteration:
            self.pop()  # Pop the iterator
            frame.ip = arg  # Jump to end

    def _op_call_function(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop call args; invoke the named global function (``args -- > result``)."""
        const_idx, num_args, has_markers = arg
        name = frame.constants[const_idx].value
        args_list = [self.pop() for _ in range(num_args)]
        args_list.reverse()

        if has_markers:
            positional, kwargs = self._expand_call_args(args_list, line, column)
        else:
            positional, kwargs = args_list, {}

        record = self.globals.lookup_record(name, None, self.code_string)
        self._invoke(record.value, positional, kwargs, name, line, column)

    def _op_call_value(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Call a function value from the stack (chained calls like f()())."""
        num_args, has_markers = arg
        args_list = [self.pop() for _ in range(num_args)]
        args_list.reverse()
        callee = self.pop()

        if has_markers:
            positional, kwargs = self._expand_call_args(args_list, line, column)
        else:
            positional, kwargs = args_list, {}
        name = getattr(callee, "name", None) or "<expression>"
        self._invoke(callee, positional, kwargs, name, line, column)

    def _invoke(self, func: object, positional: list, kwargs: dict, name: str, line: int, column: int) -> None:
        if isinstance(func, SdFunction):
            self._call_sd_function(func, positional, kwargs, line, column)
        else:
            if kwargs:
                raise QisamJeGhalti(
                    f"'{name}' keyword arguments support natho kando.",
                    line,
                    column,
                    self.code_string,
                )
            try:
                result = func(self.simple_handler, positional)
                self.push(result if result is not None else SdNull())
            except SindhiBaseError as e:
                if e.line is None:
                    e.line, e.column = line, column
                    e.code_string = self.code_string
                raise

    def _expand_call_args(self, args_list: list, line: int, column: int) -> tuple[list, dict]:
        """Split raw stack slots into positional values and kwargs.

        Markers precede their payload: KwargMarker+value pairs, then
        StarArgsMarker/KwargsDictMarker followed by the expression value.
        """
        positional = []
        kwargs = {}
        i = 0
        n = len(args_list)
        while i < n:
            val = args_list[i]
            if isinstance(val, KwargMarker):
                if i + 1 >= n:
                    raise HalndeVaktGhalti(
                        "Keyword argument jaani maalu na thi.",
                        line,
                        column,
                        self.code_string,
                    )
                kwargs[val.value] = args_list[i + 1]
                i += 2
            elif isinstance(val, StarArgsMarker):
                if i + 1 >= n:
                    raise HalndeVaktGhalti(
                        "Star argument jaani maalu na thyo.",
                        line,
                        column,
                        self.code_string,
                    )
                seq = self._unwrap_val(args_list[i + 1], line, column)
                try:
                    positional.extend(list(seq))
                except TypeError:
                    raise QisamJeGhalti(
                        f"'{seq.type.name}' khe '*' saan kholi (unpack) natho kare saghjay.",
                        line,
                        column,
                        self.code_string,
                    )
                i += 2
            elif isinstance(val, KwargsDictMarker):
                if i + 1 >= n:
                    raise HalndeVaktGhalti(
                        "Kwargs lughat jaani maalu na thi.",
                        line,
                        column,
                        self.code_string,
                    )
                d = self._unwrap_val(args_list[i + 1], line, column)
                if not isinstance(d, SdDict):
                    raise QisamJeGhalti(
                        f"'**' laai lughat khapyo paye, par '{d.type.name}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )
                for k, v in d.pairs.items():
                    key = k.value if isinstance(k, SdString) else str(k)
                    kwargs[key] = v
                i += 2
            else:
                positional.append(val)
                i += 1
        return positional, kwargs

    def _call_sd_function(self, func, positional: list, kwargs: dict, line: int, column: int) -> object:
        plan = func.call_plan
        if plan is None:
            plan = CallPlan(func.params, func.defaults, func.cell_names)
            func.call_plan = plan
        params = plan.params
        expected_types = plan.expected_types

        if plan.simple and not kwargs:
            return self._call_simple_function(
                func, plan, params, expected_types, positional, line, column
            )

        has_star_param = plan.has_star
        has_kw_param = plan.has_kw
        defaults_map = plan.defaults_map

        if plan.known_names is not None:
            for key in kwargs:
                if key not in plan.known_names:
                    raise LikhaiJeGhalti(
                        f"Achanak keyword argument '{key}' milo.",
                        line,
                        column,
                        self.code_string,
                    )

        bound = {}
        pos_idx = 0
        for i, param in enumerate(params):
            if param.is_star or param.is_kw:
                continue
            if param.name in kwargs:
                val = kwargs.pop(param.name)
            elif pos_idx < len(positional):
                val = positional[pos_idx]
                pos_idx += 1
            elif param.name in defaults_map:
                val = defaults_map[param.name]
            else:
                raise LikhaiJeGhalti(
                    f"Parameter '{param.name}' laai value lazmi aahe.",
                    line,
                    column,
                    self.code_string,
                )

            if isinstance(val, SdResult) and val.is_ok():
                val = val.value

            if isinstance(val, SdResult) and val.is_error():
                # Ghalti survives the boundary like a value; the type check
                # applies only to real values (mirrors _check_type).
                bound[param.name] = val
                continue

            expected = expected_types[i]
            if expected is not None and val.type != expected:
                raise QisamJeGhalti(
                    f"Parameter '{param.name}' khe '{_type_label(param.type)}' khapyo paye par '{val.type.name.lower()}' milyo.",
                    line,
                    column,
                    self.code_string,
                )
            # Element-typed params (fehrist[adad], lughat[k,v], ...) validate the
            # container's members too. _check_type re-verifies the top-level type
            # (which already passed above, so it is idempotent here) and then
            # walks the elements via _check_element_type.
            if param.type and param.element_type is not None:
                self._check_type(val, param.type, param.element_type, line, column)
            bound[param.name] = val

        extra_positional = positional[pos_idx:]
        if extra_positional and not has_star_param:
            raise LikhaiJeGhalti(
                f"{len(extra_positional)} wadhoo arguments mile; kaam khe itna khapay na tha.",
                line,
                column,
                self.code_string,
            )

        if kwargs and not has_kw_param:
            unknown = next(iter(kwargs))
            raise LikhaiJeGhalti(
                f"Achanak keyword argument '{unknown}' milo.",
                line,
                column,
                self.code_string,
            )

        new_frame = BytecodeFrame(
            func.name,
            func.instructions,
            func.constants,
            func.line_col_map,
            func.slot_count,
            func.slot_metadata,
            func=func,
        )

        for frame_idx, param in enumerate(params):
            if param.is_star:
                val = SdList(list(extra_positional))
            elif param.is_kw:
                val = SdDict(dict(kwargs))
            else:
                val = bound[param.name]
            # Captured params live in cells, not raw slots
            cell_idx = new_frame.cell_map.get(param.name)
            if cell_idx is not None and cell_idx < len(new_frame.cells):
                new_frame.cells[cell_idx].value = val
            else:
                new_frame.slots[frame_idx] = val

        new_frame.return_type = func.return_type
        new_frame.function_name = func.name
        self.frames.append(new_frame)

    def _call_simple_function(
        self,
        func: object,
        plan,
        params,
        expected_types,
        positional,
        line,
        column,
    ) -> object:
        """Single-pass call for closure-free, default-free, exact-arity functions.

        Mirrors the general binding path exactly (arity errors, Ok-unwrapping,
        type checks) but skips the ``bound`` dict, kwargs/defaults machinery,
        and the second frame-fill loop.
        """
        n = plan.arity
        supplied = len(positional)
        if supplied != n:
            if supplied < n:
                raise LikhaiJeGhalti(
                    f"Parameter '{params[supplied].name}' laai value lazmi aahe.",
                    line,
                    column,
                    self.code_string,
                )
            raise LikhaiJeGhalti(
                f"{supplied - n} wadhoo arguments mile; kaam khe itna khapay na tha.",
                line,
                column,
                self.code_string,
            )

        new_frame = BytecodeFrame(
            func.name,
            func.instructions,
            func.constants,
            func.line_col_map,
            func.slot_count,
            func.slot_metadata,
            func=func,
        )

        for i in range(n):
            val = positional[i]
            if isinstance(val, SdResult) and val.is_ok():
                val = val.value
            if isinstance(val, SdResult) and val.is_error():
                # Ghalti survives the boundary like a value.
                new_frame.slots[i] = val
                continue
            expected = expected_types[i]
            if expected is not None and val.type != expected:
                raise QisamJeGhalti(
                    f"Parameter '{params[i].name}' khe '{_type_label(params[i].type)}' khapyo paye par '{val.type.name.lower()}' milyo.",
                    line,
                    column,
                    self.code_string,
                )
            new_frame.slots[i] = val

        if func.return_type is not None:
            new_frame.return_type = func.return_type
            new_frame.function_name = func.name
        self.frames.append(new_frame)

    def _op_make_function(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a function and optional defaults; push it bound to cells/defs."""
        func = self.pop()
        if arg:
            defaults = tuple(self.pop() for _ in range(arg))
            defaults = tuple(reversed(defaults))
        else:
            defaults = ()
        if isinstance(func, SdFunction):
            func = func.bind_defaults(defaults)
            if func.free_specs:
                # Link each free variable via the defining frame's cell table.
                # Intermediate functions forward the owner's Cell into their
                # own tables, so depth never requires walking past frame[-1].
                defining = self.frames[-1]
                bound_cells = []
                for depth, name in func.free_specs:
                    idx = defining.cell_map.get(name)
                    if (
                        idx is None
                        or idx >= len(defining.cells)
                        or defining.cells[idx] is None
                    ):
                        raise HalndeVaktGhalti(
                            f"'{name}' laai baharli kaam je cell natho milio.",
                            line,
                            column,
                            self.code_string,
                        )
                    bound_cells.append(defining.cells[idx])
                func.cells = tuple(bound_cells)
        self.push(func)

    def _op_call_method(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop method args and object; push the method call result (``< -- result``)."""
        const_idx, num_args, has_markers = arg
        method_name = frame.constants[const_idx].value
        args = [self.pop() for _ in range(num_args)]
        args.reverse()
        obj = self.pop()

        if has_markers:
            positional, kwargs = self._expand_call_args(args, line, column)
        else:
            positional, kwargs = args, {}
        if kwargs:
            raise QisamJeGhalti(
                f"Method '{method_name}' keyword arguments support natho kando.",
                line,
                column,
                self.code_string,
            )
        args = positional

        if method_name in ("ok", "ghalti"):
            # Result inspection: works on Results, and on raw values
            # (raw = success path after boundary unwrapping)
            if isinstance(obj, SdResult):
                self.push(getattr(obj, method_name))
            elif method_name == "ok":
                self.push(SdBool(True))
            else:
                self.push(SdNull())
            return

        method = obj.type.lookup_method(method_name)
        if method:
            try:
                result = method(obj, args)
                self.push(result if result is not None else SdNull())
            except SindhiBaseError as e:
                if e.line is None:
                    e.line, e.column = line, column
                    e.code_string = self.code_string
                raise
        else:
            raise NaleJeGhalti(
                f"Method '{method_name}' ji wazahat na milyo.",
                line,
                column,
                self.code_string,
            )

    def _op_get_attr(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop an object; push its ``arg`` attribute/result (``< -- attr``)."""
        attr_name = frame.constants[arg].value
        obj = self.pop()
        if isinstance(obj, SdResult) and attr_name in ("ok", "ghalti"):
            self.push(getattr(obj, attr_name))
        elif attr_name == "ok":
            # Raw value at an inspection site = success path
            self.push(SdBool(True))
        elif attr_name == "ghalti":
            self.push(SdNull())
        else:
            raise NaleJeGhalti(
                f"Attribute {attr_name} na milyo.", line, column, self.code_string
            )

    def _op_make_ok(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value; push it wrapped as an Ok result (``< -- Ok``)."""
        val = self.pop()
        self.push(val if isinstance(val, SdResult) else SdResult(SdResult.OK, val))

    def _op_make_error(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value; push it wrapped as a Ghalti result (``< -- Ghalti``)."""
        val = self.pop()
        self.push(
            val
            if isinstance(val, SdResult) and val.is_error()
            else SdResult(SdResult.GHALTI, val)
        )

    def _op_call_bachao(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop result and fallback; push Ok value or fallback on Ghalti."""
        fallback = self.pop()
        result = self.pop()
        if not isinstance(result, SdResult):
            # Raw value = success path; keep it as-is
            self.push(result)
            return
        self.push(result.value if result.is_ok() else fallback)

    def _op_call_lazmi(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop result and message; push Ok value or unwrap/raise the Ghalti."""
        message = self.pop()
        result = self.pop()
        if not isinstance(result, SdResult):
            self.push(result)
            return
        if result.is_ok():
            self.push(result.value)
        else:
            msg_val = (
                message.value
                if isinstance(message, (SdString, SdNumber, SdBool))
                else str(message)
            )
            error_cls = ERROR_MAP.get(result._error_cls, HalndeVaktGhalti)
            raise error_cls(
                msg_val,
                line,
                column,
                self.code_string,
                traceback=result._captured_traceback,
            )

    def _op_postfix_qmark(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a result; push its Ok value or keep the Ghalti result unchanged."""
        result = self.pop()
        if not isinstance(result, SdResult):
            self.push(result)
            return
        self.push(result.value if result.is_ok() else result)

    def _op_postfix_bangbang(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a result; push its Ok value or raise the Ghalti error."""
        result = self.pop()
        if not isinstance(result, SdResult):
            self.push(result)
            return
        if result.is_ok():
            self.push(result.value)
        else:
            err_msg = str(result.value)
            error_cls = ERROR_MAP.get(result._error_cls, HalndeVaktGhalti)
            raise error_cls(
                err_msg,
                line,
                column,
                self.code_string,
                traceback=result._captured_traceback,
            )

    def _op_panic(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a message and raise a runtime error (``message -- >``)."""
        message = self.pop()
        msg_val = (
            message.value
            if isinstance(message, (SdString, SdNumber, SdBool))
            else str(message)
        )
        raise HalndeVaktGhalti(msg_val, line, column, self.code_string)

    def _op_typecast(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop a value; push it cast to ``arg``'s target type (``< -- cast``)."""
        target_type = arg
        value = self.pop()

        # Auto-unwrap successful Results for typecasting
        if isinstance(value, SdResult):
            if value.is_ok():
                value = value.value
            else:
                # If it's an error, we panic because you can't cast an error to a value
                error_cls = ERROR_MAP.get(value._error_cls, HalndeVaktGhalti)
                raise error_cls(
                    str(value.value),
                    line,
                    column,
                    self.code_string,
                    traceback=value._captured_traceback,
                )

        try:
            if target_type == TokenType.ADAD:
                if isinstance(value, SdNumber):
                    self.push(SdNumber(int(value.value)))
                elif isinstance(value, SdString):
                    # Allow float-like strings to be cast to int (e.g. "12.5" -> 12)
                    self.push(SdNumber(int(float(value.value))))
                elif isinstance(value, SdBool):
                    self.push(SdNumber(1 if value.value else 0))
                else:
                    raise QisamJeGhalti(
                        f"'{value.type.name}' khe 'adad' mein badli natho kare saghjay.",
                        line,
                        column,
                        self.code_string,
                    )

            elif target_type == TokenType.DAHAI:
                if isinstance(value, (SdNumber, SdString)):
                    self.push(SdNumber(float(value.value)))
                elif isinstance(value, SdBool):
                    self.push(SdNumber(1.0 if value.value else 0.0))
                else:
                    raise QisamJeGhalti(
                        f"'{value.type.name}' khe 'dahai' mein badli natho kare saghjay.",
                        line,
                        column,
                        self.code_string,
                    )

            elif target_type == TokenType.LAFZ:
                self.push(SdString(str(value)))

            elif target_type == TokenType.FAISLO:
                # Booleans are already truthy/falsy in Python
                self.push(
                    SdBool(bool(value.value if hasattr(value, "value") else value))
                )

            elif target_type == TokenType.FEHRIST:
                if isinstance(value, (SdList, SdSet)):
                    self.push(SdList(list(value.elements)))
                elif isinstance(value, SdString):
                    self.push(SdList([SdString(c) for c in value.value]))
                else:
                    raise QisamJeGhalti(
                        f"'{value.type.name}' khe 'fehrist' mein badli natho kare saghjay.",
                        line,
                        column,
                        self.code_string,
                    )

            elif target_type == TokenType.MAJMUO:
                if isinstance(value, (SdList, SdSet)):
                    self.push(SdSet(set(value.elements)))
                elif isinstance(value, SdString):
                    self.push(SdSet({SdString(c) for c in value.value}))
                else:
                    raise QisamJeGhalti(
                        f"'{value.type.name}' khe 'majmuo' mein badli natho kare saghjay.",
                        line,
                        column,
                        self.code_string,
                    )

            else:
                raise HalndeVaktGhalti(
                    f"Na-maloom typecast target: {target_type}.",
                    line,
                    column,
                    self.code_string,
                )

        except ValueError:
            raise HalndeVaktGhalti(
                f"Value '{value!s}' khe {_type_label(target_type)} mein badli natho kare saghjay.",
                line,
                column,
                self.code_string,
            )

    def _op_build_list(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``arg`` elements; push a list (``< -- list``)."""
        elements = [self._unwrap_val(self.pop(), line, column) for _ in range(arg)]
        elements.reverse()
        self.push(SdList(elements))

    def _op_build_dict(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``arg`` key/value pairs; push a dict (``< -- dict``)."""
        pairs = {}
        for _ in range(arg):
            v = self._unwrap_val(self.pop(), line, column)
            k = self._unwrap_val(self.pop(), line, column)
            try:
                pairs[k] = v
            except TypeError:
                raise QisamJeGhalti(
                    f"Lughat ji key hashable hujjhan lazmi aahe, par '{k.type.name}' milyo.",
                    line,
                    column,
                    self.code_string,
                )
        self.push(SdDict(pairs))

    def _op_build_set(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop ``arg`` elements; push a set (``< -- set``)."""
        elements = set()
        for _ in range(arg):
            el = self._unwrap_val(self.pop(), line, column)
            try:
                elements.add(el)
            except TypeError:
                raise QisamJeGhalti(
                    f"Majmuo jo hisso hashable hujjhan lazmi aahe, par '{el.type.name}' milyo.",
                    line,
                    column,
                    self.code_string,
                )
        self.push(SdSet(elements))

    def _op_binary_subscript(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop index and object; push ``obj[idx]`` (``< -- element``)."""
        idx = self._unwrap_val(self.pop(), line, column)
        obj = self._unwrap_val(self.pop(), line, column)
        self.push(obj.call_method("__getitem__", [idx], None, self.code_string))

    def _op_store_subscript(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop value, index, and object; store ``obj[idx] = val`` and push ``val``."""
        val = self._unwrap_val(self.pop(), line, column)
        idx = self._unwrap_val(self.pop(), line, column)
        obj = self._unwrap_val(self.pop(), line, column)
        obj.call_method("__setitem__", [idx, val], None, self.code_string)
        self.push(val)

    def _op_pop_top(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Discard the top value (``value -- >``).

        Discarding a Ghalti parcel raises it: errors demand acknowledgment.
        Storing, printing, or inspecting a Ghalti never reaches this opcode.
        """
        val = self.stack.pop()
        if isinstance(val, SdResult) and val.is_error():
            self._raise_from_result(val, line, column)

    def _op_return_value(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Pop the return value, pop the frame, and push it onto the caller's stack."""
        val = self.stack.pop()
        frame = self.frames.pop()

        if isinstance(val, SdResult) and val.is_ok():
            val = val.value

        return_type = frame.return_type
        if return_type:
            expected = _get_expected_type(return_type)
            if expected:
                check_val = val
                if isinstance(val, SdResult):
                    if val.is_error():
                        self.stack.append(val)
                        return
                    check_val = val.value

                if check_val.type != expected:
                    func_name = frame.function_name or "unknown"
                    raise QisamJeGhalti(
                        f"Wapas khe '{_type_label(return_type)}' khapyo paye, par {func_name} mein '{check_val.type.name.lower()}' milyo.",
                        line,
                        column,
                        self.code_string,
                    )

        self.stack.append(val)

    def _op_halt(self, frame: BytecodeFrame, arg: object, line: int, column: int) -> None:
        """Set the instruction pointer past the end to stop execution."""
        frame.ip = len(frame.instructions)
