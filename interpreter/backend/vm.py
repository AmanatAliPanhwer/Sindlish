from .opcodes import OpCode
from .frame import BytecodeFrame
from ..objects import (
    SdNumber, SdString, SdBool, SdNull, SdList, SdDict, SdSet, SdResult, SdFunction,
    ADAD_TYPE, DAHAI_TYPE, LAFZ_TYPE, FAISLO_TYPE, FEHRIST_TYPE, LUGHAT_TYPE, MAJMUO_TYPE, KHALI_TYPE,
)
from ..runtime.builtins import SimpleBuiltins
from ..frontend.tokens import TokenType
from ..errors import (
    NaleJeGhalti,
    QisamJeGhalti,
    HalndeVaktGhalti,
    ZeroVindJeGhalti,
    IndexJeGhalti,
    LikhaiJeGhalti,
    SindhiBaseError,
    ErrorReporter,
    ERROR_MAP
)
import sys

TYPE_MAP = {
    "adad": ADAD_TYPE,
    "dahai": DAHAI_TYPE,
    "lafz": LAFZ_TYPE,
    "faislo": FAISLO_TYPE,
    "fehrist": FEHRIST_TYPE,
    "lughat": LUGHAT_TYPE,
    "majmuo": MAJMUO_TYPE,
    "khali": KHALI_TYPE,
}

class LocationProxy:
    def __init__(self, line, column):
        self.line = line
        self.column = column

def _get_expected_type(type_name):
    if type_name is None:
        return None
    return TYPE_MAP.get(type_name.lower())

class VM:
    def __init__(self, code_string, instructions, constants, globals_env, slot_count, slot_metadata, line_col_map=None):
        self.code_string = code_string
        self.globals = globals_env
        self.stack = []
        self.line_col_map = line_col_map or {}
        
        self.simple_handler = SimpleBuiltins()
        
        main_frame = BytecodeFrame("main", instructions, constants, self.line_col_map, slot_count, slot_metadata)
        self.frames = [main_frame]
        
        self._setup_dispatch_table()

    def _setup_dispatch_table(self):
        self.dispatch_table = {
            OpCode.LOAD_CONST: self._op_load_const,
            OpCode.LOAD_FAST: self._op_load_fast,
            OpCode.STORE_FAST: self._op_store_fast,
            OpCode.LOAD_GLOBAL: self._op_load_global,
            OpCode.STORE_GLOBAL: self._op_store_global,
            OpCode.PUSH_NULL: self._op_push_null,
            OpCode.PUSH_TRUE: self._op_push_true,
            OpCode.PUSH_FALSE: self._op_push_false,
            OpCode.BINARY_ADD: self._op_binary_add,
            OpCode.BINARY_SUB: self._op_binary_sub,
            OpCode.BINARY_MUL: self._op_binary_mul,
            OpCode.BINARY_DIV: self._op_binary_div,
            OpCode.BINARY_POW: self._op_binary_pow,
            OpCode.BINARY_MOD: self._op_binary_mod,
            OpCode.COMPARE_EQ: self._op_compare_eq,
            OpCode.COMPARE_NE: self._op_compare_ne,
            OpCode.COMPARE_LT: self._op_compare_lt,
            OpCode.COMPARE_LE: self._op_compare_le,
            OpCode.COMPARE_GT: self._op_compare_gt,
            OpCode.COMPARE_GE: self._op_compare_ge,
            OpCode.LOGICAL_AND: self._op_logical_and,
            OpCode.LOGICAL_OR: self._op_logical_or,
            OpCode.LOGICAL_NOT: self._op_logical_not,
            OpCode.JUMP_ABSOLUTE: self._op_jump_absolute,
            OpCode.JUMP_IF_FALSE: self._op_jump_if_false,
            OpCode.JUMP_IF_FALSE: self._op_jump_if_false,
            OpCode.GET_ITER: self._op_get_iter,
            OpCode.FOR_ITER: self._op_for_iter,
            OpCode.PRINT_ITEM: self._op_print_item,
            OpCode.CALL_FUNCTION: self._op_call_function,
            OpCode.CALL_METHOD: self._op_call_method,
            OpCode.GET_ATTR: self._op_get_attr,
            OpCode.MAKE_OK: self._op_make_ok,
            OpCode.MAKE_ERROR: self._op_make_error,
            OpCode.CALL_BACHAO: self._op_call_bachao,
            OpCode.CALL_LAZMI: self._op_call_lazmi,
            OpCode.POSTFIX_QMARK: self._op_postfix_qmark,
            OpCode.POSTFIX_BANGBANG: self._op_postfix_bangbang,
            OpCode.PANIC: self._op_panic,
            OpCode.BUILD_LIST: self._op_build_list,
            OpCode.BUILD_DICT: self._op_build_dict,
            OpCode.BUILD_SET: self._op_build_set,
            OpCode.BINARY_SUBSCRIPT: self._op_binary_subscript,
            OpCode.STORE_SUBSCRIPT: self._op_store_subscript,
            OpCode.POP_TOP: self._op_pop_top,
            OpCode.TYPECAST: self._op_typecast,
            OpCode.DUP_TOP: self._op_dup_top,
            OpCode.RETURN_VALUE: self._op_return_value,
            OpCode.HALT: self._op_halt,
        }

    def _get_line_column(self):
        frame = self.frames[-1]
        return frame.line_col_map.get(frame.ip, (0, 0))

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()
    
    def _unwrap_val(self, val, line, column):
        """Extracts the value from an Ok result, or panics on a Ghalti result."""
        if isinstance(val, SdResult):
            if val.is_ok():
                return val.value
            else:
                error_cls = ERROR_MAP.get(val._error_cls, HalndeVaktGhalti)
                raise error_cls(str(val.value), line, column, self.code_string, traceback=val._captured_traceback)
        return val

    def _check_type(self, value, expected_type, element_type=None, line=0, column=0):
        if expected_type == TokenType.ADAD:
            if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                raise QisamJeGhalti(f"'adad' qisam laai adad khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif expected_type == TokenType.DAHAI:
            if not isinstance(value, SdNumber) or not isinstance(value.value, float):
                raise QisamJeGhalti(f"'dahai' qisam laai dahai khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif expected_type == TokenType.LAFZ:
            if not isinstance(value, SdString):
                raise QisamJeGhalti(f"'lafz' qisam laai lafz khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif expected_type == TokenType.FAISLO:
            if not isinstance(value, SdBool):
                raise QisamJeGhalti(f"'faislo' qisam laai faislo khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif expected_type == TokenType.FEHRIST:
            if not isinstance(value, SdList):
                raise QisamJeGhalti(f"'fehrist' qisam laai fehrist khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
            if element_type is not None:
                for elem in value.elements:
                    self._check_element_type(elem, element_type)
        elif expected_type == TokenType.MAJMUO:
            if not isinstance(value, SdSet):
                raise QisamJeGhalti(f"'majmuo' qisam laai majmuo khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
            if element_type is not None:
                for elem in value.elements:
                    self._check_element_type(elem, element_type)
        elif expected_type == TokenType.LUGHAT:
            if not isinstance(value, SdDict):
                raise QisamJeGhalti(f"'lughat' qisam laai lughat khapyo paye, par '{value.type.name}' milyo.", line, column, self.code_string)
            if element_type is not None and isinstance(element_type, list):
                key_type, val_type = element_type
                for k, v in value.pairs.items():
                    self._check_element_type(k, key_type, line, column)
                    self._check_element_type(v, val_type, line, column)
        return True
    
    def _check_element_type(self, value, element_type, line=0, column=0):
        if element_type == TokenType.ADAD:
            if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                raise QisamJeGhalti(f"Fehrist je elements jo qisam 'adad' hujjhan lazmi aahe, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.DAHAI:
            if not isinstance(value, SdNumber) or not isinstance(value.value, float):
                raise QisamJeGhalti(f"Fehrist je element jo qisam 'dahai' hujjhan lazmi aahe, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.LAFZ:
            if not isinstance(value, SdString):
                raise QisamJeGhalti(f"Fehrist je element jo qisam 'lafz' hujjhan lazmi aahe, par '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.FAISLO:
            if not isinstance(value, SdBool):
                raise QisamJeGhalti(f"Fehrist je element jo qisam 'faislo' hujjhan lazmi aahe, par '{value.type.name}' milyo.", line, column, self.code_string)

    @property
    def variables(self):
        result = {}
        for name, record in self.globals.records.items():
            result[name] = {"value": record.value, "is_const": getattr(record, 'is_const', False)}
        
        frame = self.frames[-1]
        if hasattr(self, 'slot_names'):
             for name, slot_idx in self.slot_names.items():
                if slot_idx < len(frame.slots) and frame.slots[slot_idx] is not None:
                    metadata = frame.slot_metadata.get(slot_idx, {})
                    result[name] = {"value": frame.slots[slot_idx], "is_const": metadata.get("is_const", False)}
        return result

    def run(self):
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
            raise e
        except Exception as e:
            print(f"Internal VM Error: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def _build_traceback(self, error: SindhiBaseError):
        # Only build new traceback if it's empty (didn't come from a Result)
        if error.traceback:
            return
            
        source_lines = self.code_string.split('\n')
        for frame in self.frames:
            line, col = frame.line_col_map.get(frame.ip, (0, 0))
            if line == 0:
                continue
            
            source_line = source_lines[line-1] if 0 < line <= len(source_lines) else None
            error.add_traceback(frame.name, line, col, source_line)

    def _handle_result(self, result):
        if isinstance(result, SdResult) and result.is_error():
            if not result._captured_traceback:
                result.capture_traceback(self.frames, self.code_string)
        return result

    def step(self):
        line, column = self._get_line_column()
        frame = self.frames[-1]
        opcode, arg = frame.instructions[frame.ip]
        frame.ip += 1

        handler = self.dispatch_table.get(opcode)
        if handler:
            handler(frame, arg, line, column)
        else:
            raise HalndeVaktGhalti(f"Na-maloom opcode: {opcode}.", line, column, self.code_string)

    # --- OpCode Handlers ---

    def _op_load_const(self, frame, arg, line, column):
        self.push(frame.constants[arg])
        
    def _op_load_fast(self, frame, arg, line, column):
        self.push(frame.slots[arg])
        
    def _op_store_fast(self, frame, arg, line, column):
        value = self.pop()
        metadata = frame.slot_metadata.get(arg, {})
        if metadata.get("is_const") and frame.slots[arg] is not None:
            raise HalndeVaktGhalti("pakko (constant) variable badlaye natho saghjay.", line, column, self.code_string)
        expected_type = metadata.get("type")
        if metadata.get("has_explicit_type", False) and expected_type is not None:
            self._check_type(value, expected_type, metadata.get("element_type"), line=line, column=column)
        frame.slots[arg] = value
        
    def _op_load_global(self, frame, arg, line, column):
        name = frame.constants[arg].value
        record = self.globals.lookup_record(name, None, self.code_string)
        self.push(record.value)
        
    def _op_store_global(self, frame, arg, line, column):
        name = frame.constants[arg].value
        val = self.pop()
        if name in self.globals.records:
            self.globals.assign(name, val, None, self.code_string)
        else:
            self.globals.define(name, val)

    def _op_push_null(self, frame, arg, line, column): self.push(SdNull())
    def _op_push_true(self, frame, arg, line, column): self.push(SdBool(True))
    def _op_push_false(self, frame, arg, line, column): self.push(SdBool(False))

    def _op_binary_add(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__add__", [right], loc, self.code_string)))
        
    def _op_binary_sub(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__sub__", [right], loc, self.code_string)))
        
    def _op_binary_mul(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__mul__", [right], loc, self.code_string)))
        
    def _op_binary_div(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__truediv__", [right], loc, self.code_string)))
        
    def _op_binary_pow(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__pow__", [right], loc, self.code_string)))
        
    def _op_binary_mod(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        loc = LocationProxy(line, column)
        self.push(self._handle_result(left.call_method("__mod__", [right], loc, self.code_string)))

    def _op_compare_eq(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__eq__", [right], None, self.code_string))
        
    def _op_compare_ne(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__ne__", [right], None, self.code_string))
        
    def _op_compare_lt(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__lt__", [right], None, self.code_string))
        
    def _op_compare_le(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__le__", [right], None, self.code_string))
        
    def _op_compare_gt(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__gt__", [right], None, self.code_string))
        
    def _op_compare_ge(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__ge__", [right], None, self.code_string))

    def _op_logical_and(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__and__", [right], None, self.code_string))
        
    def _op_logical_or(self, frame, arg, line, column):
        right = self._unwrap_val(self.pop(), line, column)
        left = self._unwrap_val(self.pop(), line, column)
        self.push(left.call_method("__or__", [right], None, self.code_string))
        
    def _op_logical_not(self, frame, arg, line, column):
        val = self._unwrap_val(self.pop(), line, column)
        self.push(val.call_method("__invert__", [], None, self.code_string))

    def _op_jump_absolute(self, frame, arg, line, column):
        frame.ip = arg
        
    def _op_jump_if_false(self, frame, arg, line, column):
        condition = self.pop()
        if not condition.value:
            frame.ip = arg

    def _op_get_iter(self, frame, arg, line, column):
        obj = self.pop()
        try:
            it = iter(obj)
            self.push(it)
        except TypeError:
            raise QisamJeGhalti(f"'{obj.type.name}' object iterable na aahe.", line, column, self.code_string)

    def _op_for_iter(self, frame, arg, line, column):
        it = self.stack[-1] # Peek at the iterator
        try:
            val = next(it)
            self.push(val)
        except StopIteration:
            self.pop() # Pop the iterator
            frame.ip = arg # Jump to end

    def _op_print_item(self, frame, arg, line, column):
        print(self.pop())

    def _op_call_function(self, frame, arg, line, column):
        const_idx, num_args = arg
        name = frame.constants[const_idx].value
        args_list = [self.pop() for _ in range(num_args)]
        args_list.reverse()
        
        record = self.globals.lookup_record(name, None, self.code_string)
        func = record.value
        
        if isinstance(func, SdFunction):
            self._call_sd_function(func, args_list, line, column)
        else:
            try:
                result = func(self.simple_handler, args_list)
                self.push(result if result is not None else SdNull())
            except SindhiBaseError as e:
                if e.line is None:
                    e.line, e.column = line, column
                    e.code_string = self.code_string
                raise e

    def _call_sd_function(self, func, args_list, line, column):
        params = func.params
        args_to_pass = []
        star_args_list = []
        kwargs_dict = SdDict({})
        
        keyword_args = {}
        positional_args = []
        param_names = {p.name for p in params}
        i = 0
        while i < len(args_list):
            arg_i = args_list[i]
            if i + 1 < len(args_list) and hasattr(arg_i, 'type') and arg_i.type.name == 'LAFZ':
                if arg_i.value in param_names:
                    keyword_args[arg_i.value] = args_list[i + 1]
                    i += 2
                    continue
            positional_args.append(args_list[i])
            i += 1
        
        args_idx = 0
        for param in params:
            if param.is_star:
                star_args_list = positional_args[args_idx:] if args_idx < len(positional_args) else []
                args_idx = len(positional_args)
            elif param.is_kw:
                pass
            elif param.name in keyword_args:
                arg_val = keyword_args[param.name]
                if param.type and not self._is_type_match(arg_val, param.type):
                    raise QisamJeGhalti(f"Parameter '{param.name}' khe '{param.type}' khapyo paye par '{arg_val.type.name.lower()}' milyo.", line, column, self.code_string)
                args_to_pass.append(arg_val)
            elif args_idx < len(positional_args):
                arg_val = positional_args[args_idx]
                if param.type and not self._is_type_match(arg_val, param.type):
                    raise QisamJeGhalti(f"Parameter '{param.name}' khe '{param.type}' khapyo paye par '{arg_val.type.name.lower()}' milyo.", line, column, self.code_string)
                args_to_pass.append(arg_val)
                args_idx += 1
            elif param.default is not None:
                args_to_pass.append(param.default)
            else:
                raise LikhaiJeGhalti(f"Parameter '{param.name}' laai value lazmi aahe.", line, column, self.code_string)
        
        new_frame = BytecodeFrame(func.name, func.instructions, func.constants, func.line_col_map, func.slot_count, func.slot_metadata)
        
        frame_idx, args_passed_idx = 0, 0
        for param in params:
            if param.is_star:
                new_frame.slots[frame_idx] = SdList(star_args_list)
            elif param.is_kw:
                new_frame.slots[frame_idx] = kwargs_dict
            else:
                new_frame.slots[frame_idx] = args_to_pass[args_passed_idx]
                args_passed_idx += 1
            frame_idx += 1
        
        new_frame.call_metadata = {"return_type": func.return_type, "function_name": func.name}
        self.frames.append(new_frame)

    def _is_type_match(self, value, expected_type_name):
        expected = _get_expected_type(expected_type_name)
        return expected is None or value.type == expected

    def _op_call_method(self, frame, arg, line, column):
        const_idx, num_args = arg
        method_name = frame.constants[const_idx].value
        args = [self.pop() for _ in range(num_args)]
        args.reverse()
        obj = self.pop()
        
        method = obj.type.lookup_method(method_name)
        if method:
            try:
                result = method(obj, args)
                self.push(result if result is not None else SdNull())
            except SindhiBaseError as e:
                if e.line is None:
                    e.line, e.column = line, column
                    e.code_string = self.code_string
                raise e
        else:
            raise NaleJeGhalti(f"Method '{method_name}' ji wazahat na milyo.", line, column, self.code_string)

    def _op_get_attr(self, frame, arg, line, column):
        attr_name = frame.constants[arg].value
        obj = self.pop()
        if isinstance(obj, SdResult) and attr_name in ('ok', 'ghalti'):
            self.push(getattr(obj, attr_name))
        else:
            raise NaleJeGhalti(f"Attribute {attr_name} na milyo.", line, column, self.code_string)

    def _op_make_ok(self, frame, arg, line, column):
        val = self.pop()
        self.push(val if isinstance(val, SdResult) else SdResult(SdResult.OK, val))
        
    def _op_make_error(self, frame, arg, line, column):
        val = self.pop()
        self.push(val if isinstance(val, SdResult) and val.is_error() else SdResult(SdResult.GHALTI, val))
        
    def _op_call_bachao(self, frame, arg, line, column):
        fallback = self.pop()
        result = self.pop()
        if not isinstance(result, SdResult):
            raise QisamJeGhalti(f"Result object khapyo paye, par '{result.type.name}' milyo.", line, column, self.code_string)
        self.push(result.value if result.is_ok() else fallback)
            
    def _op_call_lazmi(self, frame, arg, line, column):
        message = self.pop()
        result = self.pop()
        if not isinstance(result, SdResult):
            raise QisamJeGhalti(f"Result object khapyo paye, par '{result.type.name}' milyo.", line, column, self.code_string)
        if result.is_ok():
            self.push(result.value)
        else:
            msg_val = message.value if isinstance(message, (SdString, SdNumber, SdBool)) else str(message)
            error_cls = ERROR_MAP.get(result._error_cls, HalndeVaktGhalti)
            raise error_cls(msg_val, line, column, self.code_string, traceback=result._captured_traceback)
            
    def _op_postfix_qmark(self, frame, arg, line, column):
        result = self.pop()
        if not isinstance(result, SdResult):
            raise QisamJeGhalti(f"Result object khapyo paye, par '{result.type.name}' milyo.", line, column, self.code_string)
        self.push(result.value if result.is_ok() else result)
            
    def _op_postfix_bangbang(self, frame, arg, line, column):
        result = self.pop()
        if not isinstance(result, SdResult):
            raise QisamJeGhalti(f"Result object khapyo paye, par '{result.type.name}' milyo.", line, column, self.code_string)
        if result.is_ok():
            self.push(result.value)
        else:
            err_msg = str(result.value)
            error_cls = ERROR_MAP.get(result._error_cls, HalndeVaktGhalti)
            raise error_cls(err_msg, line, column, self.code_string, traceback=result._captured_traceback)
            
    def _op_panic(self, frame, arg, line, column):
        message = self.pop()
        msg_val = message.value if isinstance(message, (SdString, SdNumber, SdBool)) else str(message)
        raise HalndeVaktGhalti(msg_val, line, column, self.code_string)

    def _op_typecast(self, frame, arg, line, column):
        target_type_name = frame.constants[arg].value
        value = self.pop()
        
        # Auto-unwrap successful Results for typecasting
        if isinstance(value, SdResult):
            if value.is_ok():
                value = value.value
            else:
                # If it's an error, we panic because you can't cast an error to a value
                error_cls = ERROR_MAP.get(value._error_cls, HalndeVaktGhalti)
                raise error_cls(str(value.value), line, column, self.code_string, traceback=value._captured_traceback)

        try:
            if target_type_name == "ADAD":
                if isinstance(value, SdNumber):
                    self.push(SdNumber(int(value.value)))
                elif isinstance(value, SdString):
                    # Allow float-like strings to be cast to int (e.g. "12.5" -> 12)
                    self.push(SdNumber(int(float(value.value))))
                elif isinstance(value, SdBool):
                    self.push(SdNumber(1 if value.value else 0))
                else:
                    raise QisamJeGhalti(f"'{value.type.name}' khe 'adad' mein badli natho kare saghjay.", line, column, self.code_string)
            
            elif target_type_name == "DAHAI":
                if isinstance(value, SdNumber):
                    self.push(SdNumber(float(value.value)))
                elif isinstance(value, SdString):
                    self.push(SdNumber(float(value.value)))
                elif isinstance(value, SdBool):
                    self.push(SdNumber(1.0 if value.value else 0.0))
                else:
                    raise QisamJeGhalti(f"'{value.type.name}' khe 'dahai' mein badli natho kare saghjay.", line, column, self.code_string)
            
            elif target_type_name == "LAFZ":
                self.push(SdString(str(value)))
            
            elif target_type_name == "FAISLO":
                # Booleans are already truthy/falsy in Python
                self.push(SdBool(bool(value.value if hasattr(value, 'value') else value)))
                
            elif target_type_name == "FEHRIST":
                if isinstance(value, (SdList, SdSet)):
                    self.push(SdList(list(value.elements)))
                elif isinstance(value, SdString):
                    self.push(SdList([SdString(c) for c in value.value]))
                else:
                     raise QisamJeGhalti(f"'{value.type.name}' khe 'fehrist' mein badli natho kare saghjay.", line, column, self.code_string)

            elif target_type_name == "MAJMUO":
                if isinstance(value, (SdList, SdSet)):
                    self.push(SdSet(set(value.elements)))
                elif isinstance(value, SdString):
                    self.push(SdSet({SdString(c) for c in value.value}))
                else:
                     raise QisamJeGhalti(f"'{value.type.name}' khe 'majmuo' mein badli natho kare saghjay.", line, column, self.code_string)
            
            else:
                 raise HalndeVaktGhalti(f"Na-maloom typecast target: {target_type_name}.", line, column, self.code_string)
        
        except ValueError:
             raise HalndeVaktGhalti(f"Value '{str(value)}' khe {target_type_name.lower()} mein badli natho kare saghjay.", line, column, self.code_string)

    def _op_build_list(self, frame, arg, line, column):
        elements = [self._unwrap_val(self.pop(), line, column) for _ in range(arg)]
        elements.reverse()
        self.push(SdList(elements))

    def _op_build_dict(self, frame, arg, line, column):
        pairs = {}
        for _ in range(arg):
            v = self._unwrap_val(self.pop(), line, column)
            k = self._unwrap_val(self.pop(), line, column)
            pairs[k] = v
        self.push(SdDict(pairs))

    def _op_build_set(self, frame, arg, line, column):
        elements = {self._unwrap_val(self.pop(), line, column) for _ in range(arg)}
        self.push(SdSet(elements))

    def _op_binary_subscript(self, frame, arg, line, column):
        idx = self._unwrap_val(self.pop(), line, column)
        obj = self._unwrap_val(self.pop(), line, column)
        self.push(obj.call_method("__getitem__", [idx], None, self.code_string))

    def _op_store_subscript(self, frame, arg, line, column):
        val = self._unwrap_val(self.pop(), line, column)
        idx = self._unwrap_val(self.pop(), line, column)
        obj = self._unwrap_val(self.pop(), line, column)
        obj.call_method("__setitem__", [idx, val], None, self.code_string)
        self.push(val)

    def _op_pop_top(self, frame, arg, line, column): self.pop()
    def _op_dup_top(self, frame, arg, line, column): self.push(self.stack[-1])

    def _op_return_value(self, frame, arg, line, column):
        val = self.pop()
        frame = self.frames.pop()
        
        return_type = getattr(frame, 'call_metadata', {}).get('return_type')
        if return_type:
            expected = _get_expected_type(return_type)
            if expected:
                # If it's a Result, we only check the type if it's OK.
                # GHALTI variants are always allowed to propagate.
                check_val = val
                if isinstance(val, SdResult):
                    if val.is_error():
                        self.push(val)
                        return
                    check_val = val.value
                
                if check_val.type != expected:
                    func_name = getattr(frame, 'call_metadata', {}).get('function_name', 'unknown')
                    raise QisamJeGhalti(
                        f"Wapas khe '{return_type}' khapyo paye, par {func_name} mein '{check_val.type.name.lower()}' milyo.",
                        line, column, self.code_string
                    )
        
        self.push(val)

    def _op_halt(self, frame, arg, line, column):
        frame.ip = len(frame.instructions)
