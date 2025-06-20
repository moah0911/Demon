"""
Exception handling implementation for the Demon programming language.
"""

class DemonException:
    """Base class for all Demon exceptions."""
    
    def __init__(self, message, token=None):
        self.message = message
        self.token = token
        self.traceback = []
    
    def add_traceback_entry(self, function_name, line_number, file_name=None):
        """Add an entry to the exception traceback."""
        self.traceback.append({
            "function": function_name,
            "line": line_number,
            "file": file_name
        })
    
    def get_traceback(self):
        """Get the formatted traceback."""
        result = [f"Exception: {self.message}"]
        
        if self.token:
            result.append(f"  at line {self.token.line}")
        
        if self.traceback:
            result.append("Traceback:")
            for entry in reversed(self.traceback):
                location = f"line {entry['line']}"
                if entry['file']:
                    location += f" in {entry['file']}"
                result.append(f"  in {entry['function']} at {location}")
        
        return "\n".join(result)
    
    def __str__(self):
        return self.message

class ValueError(DemonException):
    """Exception raised for errors in value types or ranges."""
    pass

class TypeError(DemonException):
    """Exception raised for errors in types."""
    pass

class NameError(DemonException):
    """Exception raised when a name is not found."""
    pass

class IndexError(DemonException):
    """Exception raised for errors in sequence subscripts."""
    pass

class KeyError(DemonException):
    """Exception raised when a mapping key is not found."""
    pass

class DivisionByZeroError(DemonException):
    """Exception raised when division by zero occurs."""
    pass

class FileError(DemonException):
    """Exception raised for file-related errors."""
    pass

class ImportError(DemonException):
    """Exception raised when an import statement fails."""
    pass

class AssertionError(DemonException):
    """Exception raised when an assertion fails."""
    pass

class NotImplementedError(DemonException):
    """Exception raised when a feature is not implemented."""
    pass

# Map Python exceptions to Demon exceptions
EXCEPTION_MAP = {
    ZeroDivisionError: DivisionByZeroError,
    IndexError: IndexError,
    KeyError: KeyError,
    ValueError: ValueError,
    TypeError: TypeError,
    FileNotFoundError: FileError,
    PermissionError: FileError,
    NotImplementedError: NotImplementedError,
    AssertionError: AssertionError
}

def convert_python_exception(py_exception):
    """Convert a Python exception to a Demon exception."""
    exception_type = type(py_exception)
    demon_exception_class = EXCEPTION_MAP.get(exception_type, DemonException)
    
    return demon_exception_class(str(py_exception))