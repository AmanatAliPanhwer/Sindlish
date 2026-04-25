from .opcodes import OpCode
from .objects.primitives import *
from .builtins import SimpleBuiltins, MethodBuiltins
from .errors import (
    NaleJeGhalti,
    QisamJeGhalti,
    HalndeVaktGhalti,
    ZeroVindJeGhalti,
    IndexJeGhalti,
    LikhaiJeGhalti,
)
from .tokens import TokenType

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

def _get_expected_type(type_name):
    if type_name is None:
        return None
    return TYPE_MAP.get(type_name.lower())

def _check_type(value, expected_type_name, param_name):
    if expected_type_name is None:
        return True
    expected = _get_expected_type(expected_type_name)
    if expected is None:
        return True
    if value.type != expected:
        return False
    return True

class BytecodeFrame:
    def __init__(self, name, instructions, constants, line_col_map, slot_count, slot_metadata):
        self.name = name
        self.instructions = instructions
        self.constants = constants
        self.line_col_map = line_col_map
        self.slots = [None] * slot_count
        self.slot_metadata = slot_metadata
        self.ip = 0

class VM:
    def __init__(self, code_string, instructions, constants, globals_env, slot_count, slot_metadata, line_col_map=None):
        self.code_string = code_string
        
        self.globals = globals_env
        self.stack = []
        
        self.line_col_map = line_col_map or {}
        
        self.simple_handler = SimpleBuiltins()
        self.method_handler = MethodBuiltins()
        
        main_frame = BytecodeFrame("main", instructions, constants, self.line_col_map, slot_count, slot_metadata)
        self.frames = [main_frame]

    def _get_line_column(self):
        frame = self.frames[-1]
        return frame.line_col_map.get(frame.ip, (0, 0))

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()
    
    def _check_type(self, value, expected_type, element_type=None, line=0, column=0):
        if expected_type == TokenType.ADAD:
            if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                raise QisamJeGhalti(f"adad qisam laai adad lazmi aahe, '{value.type.name}' milyo.  variable likher vakt qisam khe haty try karyo.", line, column, self.code_string)
        elif expected_type == TokenType.DAHAI:
            if not isinstance(value, SdNumber) or not isinstance(value.value, float):
                raise QisamJeGhalti(f"dahai qisam laai dahai lazmi aahe, '{value.type.name}' milyo.  variable likher vakt qisam khe haty try karyo.", line, column, self.code_string)
        elif expected_type == TokenType.LAFZ:
            if not isinstance(value, SdString):
                raise QisamJeGhalti(f"lafz qisam laai lafz lazmi aahe, '{value.type.name}' milyo. variable likher vakt qisam khe haty try karyo.", line, column, self.code_string)
        elif expected_type == TokenType.FAISLO:
            if not isinstance(value, SdBool):
                raise QisamJeGhalti(f"faislo qisam laai faislo lazmi aahe, '{value.type.name}' milyo. variable likher vakt qisam khe haty try karyo", line, column, self.code_string)
        elif expected_type == TokenType.FEHRIST:
            if not isinstance(value, SdList):
                raise QisamJeGhalti(f"fehrist qisam laai fehrist lazmi aahe, '{value.type.name}' milyo. variable likher vakt qisam khe haty try karyo", line, column, self.code_string)
            if element_type is not None:
                for elem in value.elements:
                    self._check_element_type(elem, element_type)
        elif expected_type == TokenType.MAJMUO:
            if not isinstance(value, SdSet):
                raise QisamJeGhalti(f"majmuo qisam laai majmuo lazmi aahe, '{value.type.name}' milyo. variable likher vakt qisam khe haty try karyo", line, column, self.code_string)
            if element_type is not None:
                for elem in value.elements:
                    self._check_element_type(elem, element_type)
        elif expected_type == TokenType.LUGHAT:
            if not isinstance(value, SdDict):
                raise QisamJeGhalti(f"lughat qisam laai lughat lazmi aahe, '{value.type.name}' milyo. variable likher vakt qisam khe haty try karyo", line, column, self.code_string)
            if element_type is not None and isinstance(element_type, list):
                key_type, val_type = element_type
                for k, v in value.pairs.items():
                    self._check_element_type(k, key_type, line, column)
                    self._check_element_type(v, val_type, line, column)
    
    def _check_element_type(self, value, element_type, line=0, column=0):
        if element_type == TokenType.ADAD:
            if not isinstance(value, SdNumber) or not isinstance(value.value, int):
                raise QisamJeGhalti(f"fehrist je elements laai adad qisam lazmi aahe, '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.DAHAI:
            if not isinstance(value, SdNumber) or not isinstance(value.value, float):
                raise QisamJeGhalti(f"fehrist je element laai dahai qisam lazmi aahe, '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.LAFZ:
            if not isinstance(value, SdString):
                raise QisamJeGhalti(f"fehrist je element laai lafz qisam lazmi aahe, '{value.type.name}' milyo.", line, column, self.code_string)
        elif element_type == TokenType.FAISLO:
            if not isinstance(value, SdBool):
                raise QisamJeGhalti(f"fehrist je element laai faislo qisam lazmi aahe, '{value.type.name}' milyo.", line, column, self.code_string)

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
        while self.frames:
            frame = self.frames[-1]
            if frame.ip < len(frame.instructions):
                self.step()
            else:
                if len(self.frames) == 1:
                    # Don't pop the main frame so tests can access its slots
                    break
                self.frames.pop()

    def step(self):
        line, column = self._get_line_column()
        frame = self.frames[-1]
        opcode, arg = frame.instructions[frame.ip]
        frame.ip += 1

        if opcode == OpCode.LOAD_CONST:
            self.push(frame.constants[arg])
        
        elif opcode == OpCode.LOAD_FAST:
            val = frame.slots[arg]
            self.push(val)
            
        elif opcode == OpCode.STORE_FAST:
            value = self.pop()
            metadata = frame.slot_metadata.get(arg, {})
            if metadata.get("is_const") and frame.slots[arg] is not None:
                raise HalndeVaktGhalti("pakko (const) variable badli natho saghjay.", line, column, self.code_string)
            expected_type = metadata.get("type")
            has_explicit = metadata.get("has_explicit_type", False)
            if has_explicit and expected_type is not None:
                self._check_type(value, expected_type, metadata.get("element_type"), line=line, column=column)
            frame.slots[arg] = value
            
        elif opcode == OpCode.LOAD_GLOBAL:
            name = frame.constants[arg].value
            record = self.globals.lookup_record(name, None, self.code_string)
            self.push(record.value)
            
        elif opcode == OpCode.STORE_GLOBAL:
            name = frame.constants[arg].value
            val = self.pop()
            if name in self.globals.records:
                self.globals.assign(name, val, None, self.code_string)
            else:
                self.globals.define(name, val)

        elif opcode == OpCode.PUSH_NULL:
            self.push(SdNull())
        elif opcode == OpCode.PUSH_TRUE:
            self.push(SdBool(True))
        elif opcode == OpCode.PUSH_FALSE:
            self.push(SdBool(False))

        elif opcode == OpCode.BINARY_ADD:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__add__", [right], None, self.code_string))
        elif opcode == OpCode.BINARY_SUB:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__sub__", [right], None, self.code_string))
        elif opcode == OpCode.BINARY_MUL:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__mul__", [right], None, self.code_string))
        elif opcode == OpCode.BINARY_DIV:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__div__", [right], None, self.code_string))
        elif opcode == OpCode.BINARY_POW:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__pow__", [right], None, self.code_string))
        elif opcode == OpCode.BINARY_MOD:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__mod__", [right], None, self.code_string))

        elif opcode == OpCode.COMPARE_EQ:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__eq__", [right], None, self.code_string))
        elif opcode == OpCode.COMPARE_NE:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__ne__", [right], None, self.code_string))
        elif opcode == OpCode.COMPARE_LT:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__lt__", [right], None, self.code_string))
        elif opcode == OpCode.COMPARE_LE:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__le__", [right], None, self.code_string))
        elif opcode == OpCode.COMPARE_GT:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__gt__", [right], None, self.code_string))
        elif opcode == OpCode.COMPARE_GE:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__ge__", [right], None, self.code_string))

        elif opcode == OpCode.LOGICAL_AND:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__and__", [right], None, self.code_string))
        elif opcode == OpCode.LOGICAL_OR:
            right = self.pop()
            left = self.pop()
            self.push(left.call_method("__or__", [right], None, self.code_string))
        elif opcode == OpCode.LOGICAL_NOT:
            val = self.pop()
            self.push(val.call_method("__invert__", [], None, self.code_string))

        elif opcode == OpCode.JUMP_ABSOLUTE:
            frame.ip = arg
        elif opcode == OpCode.JUMP_IF_FALSE:
            condition = self.pop()
            if not condition.value:
                frame.ip = arg

        elif opcode == OpCode.PRINT_ITEM:
            val = self.pop()
            print(val)

        elif opcode == OpCode.CALL_FUNCTION:
            const_idx, num_args = arg
            name = frame.constants[const_idx].value
            args = [self.pop() for _ in range(num_args)]
            args.reverse()
            
            record = self.globals.lookup_record(name, None, self.code_string)
            func = record.value
            
            if isinstance(func, SdFunction):
                params = func.params
                
                args_to_pass = []
                star_args_list = []
                kwargs_dict = SdDict([])
                
                keyword_args = {}
                positional_args = []
                param_names = {p.name for p in params}
                i = 0
                while i < len(args):
                    arg_i = args[i]
                    # Check if this is a keyword: arg is a string, there's a next arg, and this matches a param name
                    if i + 1 < len(args) and hasattr(arg_i, 'type') and arg_i.type.name == 'LAFZ':
                        if arg_i.value in param_names:
                            keyword_args[arg_i.value] = args[i + 1]
                            i += 2
                            continue
                    positional_args.append(args[i])
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
                        expected_type = param.type
                        if expected_type and not _check_type(arg_val, expected_type, param.name):
                            line, column = self._get_line_column()
                            actual_type = arg_val.type.name.lower()
                            raise QisamJeGhalti(
                                f"parameter '{param.name}' khe '{expected_type}' khapyo te per '{actual_type}' milyo.",
                                line, column, self.code_string
                            )
                        args_to_pass.append(arg_val)
                    elif args_idx < len(positional_args):
                        arg_val = positional_args[args_idx]
                        expected_type = param.type
                        if expected_type and not _check_type(arg_val, expected_type, param.name):
                            line, column = self._get_line_column()
                            actual_type = arg_val.type.name.lower()
                            raise QisamJeGhalti(
                                f"parameter '{param.name}' khe '{expected_type}' khapyo te per '{actual_type}' milyo.",
                                line, column, self.code_string
                            )
                        args_to_pass.append(arg_val)
                        args_idx += 1
                    elif param.default is not None:
                        args_to_pass.append(param.default)
                    else:
                        line, column = self._get_line_column()
                        raise LikhaiJeGhalti(
                            f"parameter '{param.name}' laai qeemat lazmi aahe",
                            line, column, self.code_string
                        )
                
                slot_count = func.slot_count
                
                new_frame = BytecodeFrame(func.name, func.instructions, func.constants, func.line_col_map, slot_count, func.slot_metadata)
                
                frame_idx = 0
                args_passed_idx = 0
                for param in params:
                    if param.is_star:
                        new_frame.slots[frame_idx] = SdList(star_args_list)
                        frame_idx += 1
                    elif param.is_kw:
                        new_frame.slots[frame_idx] = kwargs_dict
                        frame_idx += 1
                    else:
                        new_frame.slots[frame_idx] = args_to_pass[args_passed_idx]
                        frame_idx += 1
                        args_passed_idx += 1
                
                new_frame.call_metadata = {
                    "return_type": func.return_type,
                    "function_name": func.name,
                }
                self.frames.append(new_frame)
            else:
                result = func(self.simple_handler, args)
                if result is not None:
                    self.push(result)
                else:
                    self.push(SdNull())

        elif opcode == OpCode.CALL_METHOD:
            const_idx, num_args = arg
            method_name = frame.constants[const_idx].value
            args = [self.pop() for _ in range(num_args)]
            args.reverse()
            obj = self.pop()
            
            method = MethodBuiltins.methods.get(method_name)
            if method:
                result = method(self.method_handler, obj, args)
                if result is not None:
                    self.push(result)
                else:
                    self.push(SdNull())
            else:
                line, column = self._get_line_column()
                raise NaleJeGhalti(f"Method `{method_name}` wazahat thayal", line, column, self.code_string)

        elif opcode == OpCode.GET_ATTR:
            attr_name = frame.constants[arg].value
            obj = self.pop()
            
            # Special handling for Result properties
            if isinstance(obj, SdResult) and attr_name in ('ok', 'ghalti'):
                self.push(getattr(obj, attr_name))
            else:
                line, column = self._get_line_column()
                raise NaleJeGhalti(f"Attribute `{attr_name}` na milio.", line, column, self.code_string)

        elif opcode == OpCode.MAKE_OK:
            val = self.pop()
            if isinstance(val, SdResult):
                self.push(val)
            else:
                self.push(SdResult(SdResult.OK, val))
        
        elif opcode == OpCode.MAKE_ERROR:
            val = self.pop()
            if isinstance(val, SdResult) and val.is_error():
                self.push(val)
            else:
                self.push(SdResult(SdResult.GHALTI, val))
            
        elif opcode == OpCode.CALL_BACHAO:
            fallback = self.pop()
            result = self.pop()
            if not isinstance(result, SdResult):
                 raise QisamJeGhalti(f"Result object expected, got '{result.type.name}'", line, column, self.code_string)
            if result.is_ok():
                self.push(result.value)
            else:
                self.push(fallback)
                
        elif opcode == OpCode.CALL_LAZMI:
            message = self.pop()
            result = self.pop()
            if not isinstance(result, SdResult):
                 raise QisamJeGhalti(f"Result object expected, got '{result.type.name}'", line, column, self.code_string)
            if result.is_ok():
                self.push(result.value)
            else:
                msg_val = message.value if isinstance(message, (SdString, SdNumber, SdBool)) else str(message)
                raise HalndeVaktGhalti(msg_val, line, column, self.code_string)
                
        elif opcode == OpCode.POSTFIX_QMARK:
            result = self.pop()
            if not isinstance(result, SdResult):
                 raise QisamJeGhalti(f"Result object expected, got '{result.type.name}'", line, column, self.code_string)
            if result.is_ok():
                self.push(result.value)
            else:
                self.push(result) # Keep wrapped Ghalti
                
        elif opcode == OpCode.POSTFIX_BANGBANG:
            result = self.pop()
            if not isinstance(result, SdResult):
                 raise QisamJeGhalti(f"Result object expected, got '{result.type.name}'", line, column, self.code_string)
            if result.is_ok():
                self.push(result.value)
            else:
                raise HalndeVaktGhalti(f"Panic! Ghalti: {str(result.value)}", line, column, self.code_string)
                
        elif opcode == OpCode.PANIC:
            message = self.pop()
            msg_val = message.value if isinstance(message, (SdString, SdNumber, SdBool)) else str(message)
            raise HalndeVaktGhalti(msg_val, line, column, self.code_string)

        elif opcode == OpCode.BUILD_LIST:
            elements = [self.pop() for _ in range(arg)]
            elements.reverse()
            self.push(SdList(elements))

        elif opcode == OpCode.BUILD_DICT:
            pairs = {}
            for _ in range(arg):
                v = self.pop()
                k = self.pop()
                pairs[k] = v
            self.push(SdDict(pairs))

        elif opcode == OpCode.BUILD_SET:
            elements = {self.pop() for _ in range(arg)}
            self.push(SdSet(elements))

        elif opcode == OpCode.BINARY_SUBSCRIPT:
            idx = self.pop()
            obj = self.pop()
            self.push(obj.call_method("__getitem__", [idx], None, self.code_string))

        elif opcode == OpCode.STORE_SUBSCRIPT:
            val = self.pop()
            idx = self.pop()
            obj = self.pop()
            obj.call_method("__setitem__", [idx, val], None, self.code_string)
            self.push(val)

        elif opcode == OpCode.POP_TOP:
            self.pop()
        elif opcode == OpCode.DUP_TOP:
            val = self.stack[-1]
            self.push(val)

        elif opcode == OpCode.RETURN_VALUE:
            val = self.pop()
            frame = self.frames.pop()
            
            return_type = getattr(frame, 'call_metadata', {}).get('return_type')
            function_name = getattr(frame, 'call_metadata', {}).get('function_name', 'unknown')
            
            if return_type:
                expected = _get_expected_type(return_type)
                is_result = isinstance(val, SdResult)
                ok_val = val.value if is_result else val
                actual_type = ok_val.type
                
                if actual_type != expected:
                    line, column = self._get_line_column()
                    actual_type_name = actual_type.name.lower()
                    raise QisamJeGhalti(
                        f"wapas khe '{return_type}' khapyo te per '{actual_type_name}' milyo. ({function_name} mein)",
                        line, column, self.code_string
                    )
            
            self.push(val)

        elif opcode == OpCode.HALT:
            frame.ip = len(frame.instructions)

