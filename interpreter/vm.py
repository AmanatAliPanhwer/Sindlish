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

class VM:
    def __init__(self, code_string, instructions, constants, globals_env, slot_count, slot_metadata, line_col_map=None):
        self.code_string = code_string
        self.instructions = instructions
        self.constants = constants
        self.globals = globals_env
        self.slots = [None] * slot_count
        self.stack = []
        self.ip = 0
        self.slot_metadata = slot_metadata
        self.line_col_map = line_col_map or {}
        
        self.simple_handler = SimpleBuiltins()
        self.method_handler = MethodBuiltins()

    def _get_line_column(self):
        return self.line_col_map.get(self.ip, (0, 0))

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()
    
    def _get_line_column(self):
        return self.line_col_map.get(self.ip, (0, 0))

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
        if hasattr(self, 'slot_names'):
            for name, slot_idx in self.slot_names.items():
                if slot_idx < len(self.slots) and self.slots[slot_idx] is not None:
                    metadata = self.slot_metadata.get(slot_idx, {})
                    result[name] = {"value": self.slots[slot_idx], "is_const": metadata.get("is_const", False)}
        return result

    def run(self):
        while self.ip < len(self.instructions):
            self.step()

    def step(self):
        line, column = self._get_line_column()  # Get line/col BEFORE incrementing ip
        opcode, arg = self.instructions[self.ip]
        self.ip += 1

        if opcode == OpCode.LOAD_CONST:
            self.push(self.constants[arg])
        
        elif opcode == OpCode.LOAD_FAST:
            val = self.slots[arg]
            self.push(val)
            
        elif opcode == OpCode.STORE_FAST:
            value = self.pop()
            metadata = self.slot_metadata.get(arg, {})
            if metadata.get("is_const") and self.slots[arg] is not None:
                raise HalndeVaktGhalti("pakko (const) variable badli natho saghjay.", line, column, self.code_string)
            expected_type = metadata.get("type")
            has_explicit = metadata.get("has_explicit_type", False)
            if has_explicit and expected_type is not None:
                self._check_type(value, expected_type, metadata.get("element_type"), line=line, column=column)
            self.slots[arg] = value
            
        elif opcode == OpCode.LOAD_GLOBAL:
            name = self.constants[arg].value
            record = self.globals.lookup_record(name, None, self.code_string)
            self.push(record.value)
            
        elif opcode == OpCode.STORE_GLOBAL:
            name = self.constants[arg].value
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
            self.ip = arg
        elif opcode == OpCode.JUMP_IF_FALSE:
            condition = self.pop()
            if not condition.value:
                self.ip = arg

        elif opcode == OpCode.PRINT_ITEM:
            val = self.pop()
            print(val)

        elif opcode == OpCode.CALL_FUNCTION:
            const_idx, num_args = arg
            name = self.constants[const_idx].value
            args = [self.pop() for _ in range(num_args)]
            args.reverse()
            
            # For now, only builtins
            record = self.globals.lookup_record(name, None, self.code_string)
            func = record.value
            result = func(self.simple_handler, args)
            if result is not None:
                self.push(result)
            else:
                self.push(SdNull())

        elif opcode == OpCode.CALL_METHOD:
            const_idx, num_args = arg
            method_name = self.constants[const_idx].value
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

        elif opcode == OpCode.HALT:
            self.ip = len(self.instructions)

