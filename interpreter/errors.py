import sys
import re

class Colors:
    """Standard ANSI escape codes for terminal formatting."""
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    GRAY = '\033[90m'

class TracebackEntry:
    """A single entry in the Sindlish call stack."""
    def __init__(self, context_name, line, column, source_line=None):
        self.context_name = context_name
        self.line = line
        self.column = column
        self.source_line = source_line

class SindhiBaseError(Exception):
    """Base class for all Sindlish errors."""
    def __init__(self, error_name, details, line=None, column=None, code_string=None, traceback=None):
        self.error_name = error_name
        self.details = details
        self.line = line
        self.column = column
        self.code_string = code_string
        self.traceback = traceback or []
        # We don't generate the message in __init__ anymore
        super().__init__(self.details)

    def add_traceback(self, context_name, line, column, source_line=None):
        self.traceback.append(TracebackEntry(context_name, line, column, source_line))

class ErrorReporter:
    """Beautifully renders Sindlish errors with tracebacks and code snippets."""
    
    @staticmethod
    def report(error: SindhiBaseError):
        """Prints a professional error report to stderr."""
        # 1. Header
        sys.stderr.write(f"\n{Colors.BOLD}{Colors.RED}{error.error_name}:{Colors.RESET} {error.details}\n")
        
        # 2. Traceback
        if error.traceback:
            sys.stderr.write(f"\n{Colors.GRAY}Call Stack (most recent call last):{Colors.RESET}\n")
            for entry in error.traceback:
                sys.stderr.write(f"  {Colors.CYAN}-->{Colors.RESET} Line {entry.line}, in {Colors.BLUE}{entry.context_name}{Colors.RESET}\n")
                if entry.source_line:
                    sys.stderr.write(f"    {entry.source_line.strip()}\n")
        
        # 3. Main Error Location
        if error.line and error.column and error.code_string:
            sys.stderr.write(f"\n{Colors.BOLD}At Location:{Colors.RESET}\n")
            lines = error.code_string.split('\n')
            if 0 < error.line <= len(lines):
                # Show context (previous and next line if available)
                start_line = max(1, error.line - 1)
                end_line = min(len(lines), error.line + 1)
                
                for i in range(start_line, end_line + 1):
                    line_content = lines[i-1]
                    prefix = f"{Colors.GRAY}{i:4} | {Colors.RESET}"
                    
                    if i == error.line:
                        # Highlight current line
                        sys.stderr.write(f"{prefix}{line_content}\n")
                        
                        # Pointer
                        tab_spaces = "    "
                        clean_line = line_content.replace('\t', tab_spaces)
                        original_prefix = line_content[:error.column - 1]
                        tab_count = original_prefix.count('\t')
                        space_count = len(original_prefix) - tab_count + (tab_count * len(tab_spaces))
                        
                        pointer = " " * (space_count + 7) + f"{Colors.BOLD}{Colors.YELLOW}^{Colors.RESET}"
                        sys.stderr.write(f"{pointer}\n")
                    else:
                        sys.stderr.write(f"{prefix}{line_content}\n")
        
        sys.stderr.write("\n")

# --- Specific Error Subclasses ---

class LikhaiJeGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("LikhaiJeGhalti", details, line, column, code_string, traceback)

class NaleJeGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("NaleJeGhalti", details, line, column, code_string, traceback)

class QisamJeGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("QisamJeGhalti", details, line, column, code_string, traceback)

class HalndeVaktGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("HalndeVaktGhalti", details, line, column, code_string, traceback)

class ZeroVindJeGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("ZeroVindJeGhalti", details, line, column, code_string, traceback)

class IndexJeGhalti(SindhiBaseError):
    def __init__(self, details, line=None, column=None, code_string=None, traceback=None):
        super().__init__("IndexJeGhalti", details, line, column, code_string, traceback)

# Registry for dynamic error lookup
ERROR_MAP = {
    "LikhaiJeGhalti": LikhaiJeGhalti,
    "NaleJeGhalti": NaleJeGhalti,
    "QisamJeGhalti": QisamJeGhalti,
    "HalndeVaktGhalti": HalndeVaktGhalti,
    "ZeroVindJeGhalti": ZeroVindJeGhalti,
    "IndexJeGhalti": IndexJeGhalti,
}