"""
Code linter for the Demon programming language.
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple

class CodeLinter:
    """Code linter for the Demon language."""
    
    def __init__(self, language_server):
        self.language_server = language_server
    
    def lint(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Lint the document and return diagnostics."""
        diagnostics = []
        
        # Collect diagnostics from different linting passes
        diagnostics.extend(self._check_syntax(uri, text))
        diagnostics.extend(self._check_unused_variables(uri, text))
        diagnostics.extend(self._check_undefined_variables(uri, text))
        diagnostics.extend(self._check_style(uri, text))
        
        return diagnostics
    
    def type_check(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Type check the document and return diagnostics."""
        # Parse the document
        from scanner import Scanner
        from parser import Parser
        from type_checker import TypeChecker
        
        scanner = Scanner(text, uri)
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens, self.language_server.demon)
        statements = parser.parse()
        
        if not statements:
            return []
        
        # Type check
        type_checker = TypeChecker(self.language_server.demon)
        errors = type_checker.check(statements)
        
        # Convert errors to diagnostics
        diagnostics = []
        for error in errors:
            diagnostics.append({
                "range": {
                    "start": {"line": error.token.line - 1, "character": 0},
                    "end": {"line": error.token.line - 1, "character": 80}
                },
                "severity": 1,  # Error
                "source": "demon-type-checker",
                "message": error.message
            })
        
        return diagnostics
    
    def _check_syntax(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Check for syntax errors."""
        diagnostics = []
        lines = text.splitlines()
        
        # Check for unbalanced braces
        open_braces = 0
        open_brace_lines = []
        
        for i, line in enumerate(lines):
            for j, char in enumerate(line):
                if char == '{':
                    open_braces += 1
                    open_brace_lines.append(i)
                elif char == '}':
                    open_braces -= 1
                    if open_braces < 0:
                        diagnostics.append({
                            "range": {
                                "start": {"line": i, "character": j},
                                "end": {"line": i, "character": j + 1}
                            },
                            "severity": 1,  # Error
                            "source": "demon-linter",
                            "message": "Unmatched closing brace"
                        })
                        open_braces = 0  # Reset to avoid cascading errors
        
        if open_braces > 0:
            for line in open_brace_lines[-open_braces:]:
                diagnostics.append({
                    "range": {
                        "start": {"line": line, "character": lines[line].find('{')},
                        "end": {"line": line, "character": lines[line].find('{') + 1}
                    },
                    "severity": 1,  # Error
                    "source": "demon-linter",
                    "message": "Unmatched opening brace"
                })
        
        # Check for missing semicolons
        for i, line in enumerate(lines):
            # Skip comments and empty lines
            if line.strip().startswith("//") or not line.strip():
                continue
            
            # Skip lines that end with opening brace or closing brace
            if line.rstrip().endswith("{") or line.rstrip().endswith("}"):
                continue
            
            # Skip lines that are part of a multi-line statement
            if line.rstrip().endswith("\\"):
                continue
            
            # Check if line should end with semicolon but doesn't
            if not line.rstrip().endswith(";") and not re.search(r'^\s*(if|for|while|func)\b', line):
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": len(line.rstrip())},
                        "end": {"line": i, "character": len(line.rstrip())}
                    },
                    "severity": 2,  # Warning
                    "source": "demon-linter",
                    "message": "Missing semicolon"
                })
        
        # Check for unclosed strings
        for i, line in enumerate(lines):
            in_string = False
            string_start = 0
            quote_char = None
            
            for j, char in enumerate(line):
                if not in_string and char in ['"', "'"]:
                    in_string = True
                    string_start = j
                    quote_char = char
                elif in_string and char == quote_char and line[j-1] != '\\':
                    in_string = False
            
            if in_string:
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": string_start},
                        "end": {"line": i, "character": len(line)}
                    },
                    "severity": 1,  # Error
                    "source": "demon-linter",
                    "message": f"Unclosed string literal"
                })
        
        return diagnostics
    
    def _check_unused_variables(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Check for unused variables."""
        diagnostics = []
        lines = text.splitlines()
        
        # Find variable declarations
        declarations = {}
        for i, line in enumerate(lines):
            for match in re.finditer(r'let\s+(\w+)', line):
                var_name = match.group(1)
                declarations[var_name] = {
                    "line": i,
                    "character": match.start(1),
                    "used": False
                }
        
        # Check for variable usage
        for i, line in enumerate(lines):
            for var_name in declarations:
                # Skip the declaration line itself
                if i == declarations[var_name]["line"]:
                    continue
                
                # Check if variable is used
                if re.search(r'\b' + re.escape(var_name) + r'\b', line):
                    declarations[var_name]["used"] = True
        
        # Report unused variables
        for var_name, info in declarations.items():
            if not info["used"]:
                diagnostics.append({
                    "range": {
                        "start": {"line": info["line"], "character": info["character"]},
                        "end": {"line": info["line"], "character": info["character"] + len(var_name)}
                    },
                    "severity": 3,  # Information
                    "source": "demon-linter",
                    "message": f"Unused variable '{var_name}'"
                })
        
        return diagnostics
    
    def _check_undefined_variables(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Check for undefined variables."""
        diagnostics = []
        lines = text.splitlines()
        
        # Built-in functions and keywords
        builtins = [
            "print", "input", "len", "str", "int", "float", "bool", "range",
            "list", "map", "filter", "reduce", "sum", "min", "max", "abs",
            "round", "floor", "ceil", "sqrt", "pow", "sin", "cos", "tan",
            "log", "random", "randint", "choice", "shuffle", "time", "sleep",
            "read_file", "write_file", "append_file", "file_exists", "list_dir",
            "Stack", "Queue", "PriorityQueue", "Set", "Graph",
            "if", "else", "for", "while", "func", "return", "break", "continue",
            "let", "true", "false", "nil"
        ]
        
        # Find variable declarations
        declarations = set()
        for line in lines:
            for match in re.finditer(r'let\s+(\w+)', line):
                declarations.add(match.group(1))
            
            # Function declarations
            for match in re.finditer(r'func\s+(\w+)', line):
                declarations.add(match.group(1))
            
            # Function parameters
            for match in re.finditer(r'func\s+\w+\s*\(([^)]*)\)', line):
                params = match.group(1)
                for param in params.split(","):
                    param = param.strip()
                    if param:
                        declarations.add(param)
            
            # For loop variables
            for match in re.finditer(r'for\s*\(\s*let\s+(\w+)', line):
                declarations.add(match.group(1))
        
        # Check for variable usage
        for i, line in enumerate(lines):
            # Skip comments
            if line.strip().startswith("//"):
                continue
            
            # Find all identifiers
            for match in re.finditer(r'\b(\w+)\b', line):
                var_name = match.group(1)
                
                # Skip if it's a declaration
                if re.search(r'let\s+' + re.escape(var_name), line) or \
                   re.search(r'func\s+' + re.escape(var_name), line) or \
                   re.search(r'for\s*\(\s*let\s+' + re.escape(var_name), line):
                    continue
                
                # Skip if it's a built-in
                if var_name in builtins:
                    continue
                
                # Skip if it's a number
                if var_name.isdigit():
                    continue
                
                # Check if variable is declared
                if var_name not in declarations:
                    diagnostics.append({
                        "range": {
                            "start": {"line": i, "character": match.start(1)},
                            "end": {"line": i, "character": match.end(1)}
                        },
                        "severity": 1,  # Error
                        "source": "demon-linter",
                        "message": f"Undefined variable '{var_name}'"
                    })
        
        return diagnostics
    
    def _check_style(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Check for style issues."""
        diagnostics = []
        lines = text.splitlines()
        
        # Check line length
        max_line_length = 80
        for i, line in enumerate(lines):
            if len(line) > max_line_length:
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": max_line_length},
                        "end": {"line": i, "character": len(line)}
                    },
                    "severity": 3,  # Information
                    "source": "demon-linter",
                    "message": f"Line exceeds {max_line_length} characters"
                })
        
        # Check for trailing whitespace
        for i, line in enumerate(lines):
            match = re.search(r'\s+$', line)
            if match:
                diagnostics.append({
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    },
                    "severity": 3,  # Information
                    "source": "demon-linter",
                    "message": "Trailing whitespace"
                })
        
        # Check for inconsistent indentation
        indent_sizes = []
        for line in lines:
            if not line.strip():
                continue
            
            match = re.match(r'^(\s+)', line)
            if match:
                indent = match.group(1)
                indent_size = len(indent.replace('\t', ' ' * 4))
                if indent_size > 0:
                    indent_sizes.append(indent_size)
        
        if indent_sizes:
            # Find most common indent size
            from collections import Counter
            common_indent = Counter(indent_sizes).most_common(1)[0][0]
            
            # Check for inconsistent indentation
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                
                match = re.match(r'^(\s+)', line)
                if match:
                    indent = match.group(1)
                    indent_size = len(indent.replace('\t', ' ' * 4))
                    
                    if indent_size % common_indent != 0:
                        diagnostics.append({
                            "range": {
                                "start": {"line": i, "character": 0},
                                "end": {"line": i, "character": len(indent)}
                            },
                            "severity": 3,  # Information
                            "source": "demon-linter",
                            "message": f"Inconsistent indentation (expected multiple of {common_indent})"
                        })
        
        return diagnostics