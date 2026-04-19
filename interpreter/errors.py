class Colors:
    """Standard ANSI escape codes for terminal formatting."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class SindhiBaseError(Exception):
    def __init__(self, error_name, details, line, column, code_string):
        self.error_name = error_name
        self.details = details
        self.line = max(1, line)
        self.column = max(1, column)
        self.code_string = code_string
        super().__init__(self.generate_message())

    def generate_message(self):
        lines = self.code_string.split('\n')
        
        error_header = f"\n{Colors.BOLD}{Colors.RED}{self.error_name}:{Colors.RESET} {self.details}"
        location_info = f"{Colors.CYAN}  --> Line {self.line}, Column {self.column}{Colors.RESET}\n"
        
        if 0 < self.line <= len(lines):
            error_line = lines[self.line - 1]
            
            tab_spaces = "    "
            clean_line = error_line.replace('\t', tab_spaces)
            
            original_prefix = error_line[:self.column - 1]
            tab_count = original_prefix.count('\t')
            space_count = len(original_prefix) - tab_count + (tab_count * len(tab_spaces))
            
            pointer = " " * space_count + f"{Colors.BOLD}{Colors.YELLOW}^{Colors.RESET}"
            
            line_prefix = f" {self.line} | "
            empty_prefix = " " * len(f" {self.line} |")
            
            return (
                f"{error_header}\n"
                f"{location_info}\n"
                f"{line_prefix}{clean_line}\n"
                f"{empty_prefix}{pointer}\n"
            )
            
        return f"{error_header}\n{location_info}"

class LikhaiJeGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("LikhaiJeGhalti (SyntaxError)", details, line, column, code_string)

class NaleJeGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("NaleJeGhalti (NameError)", details, line, column, code_string)

class QisamJeGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("QisamJeGhalti (TypeError)", details, line, column, code_string)

class HalndeVaktGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("HalndeVaktGhalti (RuntimeError)", details, line, column, code_string)

# --- Specific Math/Logic Errors ---

class ZeroVindJeGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("ZeroVindJeGhalti (ZeroDivisionError)", details, line, column, code_string)

class IndexJeGhalti(SindhiBaseError):
    def __init__(self, details, line, column, code_string):
        super().__init__("IndexJeGhalti (IndexError)", details, line, column, code_string)