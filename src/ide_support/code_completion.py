"""
Code completion for the Demon programming language.
"""

import os
import re
from typing import Dict, List, Optional, Any, Union, Tuple

class CodeCompleter:
    """Code completion for the Demon language."""
    
    def __init__(self, language_server):
        self.language_server = language_server
        self.symbols_cache = {}
        self.definitions_cache = {}
    
    def complete(self, uri: str, position: Dict[str, int]) -> List[Dict[str, Any]]:
        """Provide code completions at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get line up to cursor
        lines = text.splitlines()
        if line >= len(lines):
            return []
        
        line_text = lines[line][:character]
        
        # Check for member access completion
        match = re.search(r'(\w+)\.$', line_text)
        if match:
            return self._complete_member(match.group(1), uri)
        
        # Check for variable/function completion
        return self._complete_symbol(line_text, uri)
    
    def hover(self, uri: str, position: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Provide hover information at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return None
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get word at cursor
        lines = text.splitlines()
        if line >= len(lines):
            return None
        
        line_text = lines[line]
        word_match = re.search(r'\b(\w+)\b', line_text[max(0, character - 20):character + 20])
        if not word_match:
            return None
        
        word = word_match.group(1)
        
        # Find symbol definition
        symbol_info = self._find_symbol_definition(word, uri)
        if not symbol_info:
            return None
        
        # Create hover content
        content = f"```demon\n{symbol_info['detail']}\n```\n\n{symbol_info.get('documentation', '')}"
        
        return {
            "contents": {
                "kind": "markdown",
                "value": content
            }
        }
    
    def signature_help(self, uri: str, position: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Provide signature help at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return None
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get line up to cursor
        lines = text.splitlines()
        if line >= len(lines):
            return None
        
        line_text = lines[line][:character]
        
        # Check for function call
        match = re.search(r'(\w+)\s*\(([^()]*)$', line_text)
        if not match:
            return None
        
        function_name = match.group(1)
        args_text = match.group(2)
        
        # Count commas to determine active parameter
        active_parameter = 0
        if args_text:
            active_parameter = args_text.count(',')
        
        # Find function definition
        function_info = self._find_symbol_definition(function_name, uri)
        if not function_info or function_info["kind"] != 3:  # Function
            return None
        
        # Create signature information
        parameters = function_info.get("parameters", [])
        parameter_infos = [{"label": param["name"]} for param in parameters]
        
        return {
            "signatures": [
                {
                    "label": f"{function_name}({', '.join(param['name'] for param in parameters)})",
                    "documentation": function_info.get("documentation", ""),
                    "parameters": parameter_infos
                }
            ],
            "activeSignature": 0,
            "activeParameter": min(active_parameter, len(parameter_infos) - 1) if parameter_infos else 0
        }
    
    def definition(self, uri: str, position: Dict[str, int]) -> Optional[Dict[str, Any]]:
        """Provide definition location for symbol at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return None
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get word at cursor
        lines = text.splitlines()
        if line >= len(lines):
            return None
        
        line_text = lines[line]
        word_match = re.search(r'\b(\w+)\b', line_text[max(0, character - 20):character + 20])
        if not word_match:
            return None
        
        word = word_match.group(1)
        
        # Find symbol definition
        symbol_info = self._find_symbol_definition(word, uri)
        if not symbol_info or "location" not in symbol_info:
            return None
        
        return symbol_info["location"]
    
    def references(self, uri: str, position: Dict[str, int], include_declaration: bool) -> List[Dict[str, Any]]:
        """Find references to the symbol at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get word at cursor
        lines = text.splitlines()
        if line >= len(lines):
            return []
        
        line_text = lines[line]
        word_match = re.search(r'\b(\w+)\b', line_text[max(0, character - 20):character + 20])
        if not word_match:
            return []
        
        word = word_match.group(1)
        
        # Find all references
        references = self._find_references(word, uri)
        
        # Include declaration if requested
        if include_declaration:
            symbol_info = self._find_symbol_definition(word, uri)
            if symbol_info and "location" in symbol_info:
                references.insert(0, symbol_info["location"])
        
        return references
    
    def document_symbols(self, uri: str) -> List[Dict[str, Any]]:
        """Provide document symbols."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        # Parse document and extract symbols
        return self._extract_symbols(uri, document["text"])
    
    def workspace_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Provide workspace symbols matching the query."""
        results = []
        
        # Search in all open documents
        for doc_uri, document in self.language_server.open_documents.items():
            symbols = self._extract_symbols(doc_uri, document["text"])
            
            # Filter symbols by query
            if query:
                symbols = [s for s in symbols if query.lower() in s["name"].lower()]
            
            results.extend(symbols)
        
        return results
    
    def rename(self, uri: str, position: Dict[str, int], new_name: str) -> Dict[str, Any]:
        """Rename the symbol at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return {"documentChanges": []}
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get word at cursor
        lines = text.splitlines()
        if line >= len(lines):
            return {"documentChanges": []}
        
        line_text = lines[line]
        word_match = re.search(r'\b(\w+)\b', line_text[max(0, character - 20):character + 20])
        if not word_match:
            return {"documentChanges": []}
        
        word = word_match.group(1)
        
        # Find all references
        references = self._find_references(word, uri)
        
        # Include declaration
        symbol_info = self._find_symbol_definition(word, uri)
        if symbol_info and "location" in symbol_info:
            references.insert(0, symbol_info["location"])
        
        # Create text edits
        changes = {}
        for ref in references:
            ref_uri = ref["uri"]
            if ref_uri not in changes:
                changes[ref_uri] = []
            
            changes[ref_uri].append({
                "range": ref["range"],
                "newText": new_name
            })
        
        # Create document changes
        document_changes = []
        for change_uri, edits in changes.items():
            document_changes.append({
                "textDocument": {
                    "uri": change_uri,
                    "version": self.language_server.open_documents.get(change_uri, {}).get("version", 0)
                },
                "edits": edits
            })
        
        return {"documentChanges": document_changes}
    
    def _complete_member(self, obj_name: str, uri: str) -> List[Dict[str, Any]]:
        """Complete member access."""
        # Find object type
        obj_info = self._find_symbol_definition(obj_name, uri)
        if not obj_info:
            return []
        
        # Get members based on type
        members = []
        
        # Add standard library members based on type
        if obj_info.get("detail", "").startswith("List"):
            members = [
                {"label": "append", "kind": 2, "detail": "append(item): Append item to list"},
                {"label": "pop", "kind": 2, "detail": "pop(index=-1): Remove and return item at index"},
                {"label": "insert", "kind": 2, "detail": "insert(index, item): Insert item at index"},
                {"label": "remove", "kind": 2, "detail": "remove(item): Remove first occurrence of item"},
                {"label": "clear", "kind": 2, "detail": "clear(): Remove all items"},
                {"label": "length", "kind": 7, "detail": "length: Number of items in list"}
            ]
        elif obj_info.get("detail", "").startswith("String"):
            members = [
                {"label": "length", "kind": 7, "detail": "length: Length of string"},
                {"label": "upper", "kind": 2, "detail": "upper(): Convert to uppercase"},
                {"label": "lower", "kind": 2, "detail": "lower(): Convert to lowercase"},
                {"label": "trim", "kind": 2, "detail": "trim(): Remove whitespace from both ends"},
                {"label": "split", "kind": 2, "detail": "split(separator=' '): Split string into list"}
            ]
        
        return members
    
    def _complete_symbol(self, line_text: str, uri: str) -> List[Dict[str, Any]]:
        """Complete variable or function name."""
        # Extract symbols from document
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        symbols = self._extract_symbols(uri, document["text"])
        
        # Add standard library functions
        stdlib_symbols = [
            {"label": "print", "kind": 3, "detail": "print(...): Print values to console"},
            {"label": "input", "kind": 3, "detail": "input(prompt=''): Read input from user"},
            {"label": "len", "kind": 3, "detail": "len(obj): Return length of object"},
            {"label": "str", "kind": 3, "detail": "str(obj): Convert object to string"},
            {"label": "int", "kind": 3, "detail": "int(obj): Convert object to integer"},
            {"label": "float", "kind": 3, "detail": "float(obj): Convert object to float"},
            {"label": "bool", "kind": 3, "detail": "bool(obj): Convert object to boolean"},
            {"label": "range", "kind": 3, "detail": "range(start, stop, step=1): Create range of numbers"},
            {"label": "list", "kind": 3, "detail": "list(iterable=None): Create a new list"},
            {"label": "map", "kind": 3, "detail": "map(func, iterable): Apply function to each item"},
            {"label": "filter", "kind": 3, "detail": "filter(func, iterable): Filter items by function"},
            {"label": "reduce", "kind": 3, "detail": "reduce(func, iterable, initial=None): Reduce iterable to single value"},
            {"label": "sum", "kind": 3, "detail": "sum(iterable): Sum of items in iterable"},
            {"label": "min", "kind": 3, "detail": "min(...): Return smallest item"},
            {"label": "max", "kind": 3, "detail": "max(...): Return largest item"},
            {"label": "abs", "kind": 3, "detail": "abs(x): Absolute value of x"},
            {"label": "round", "kind": 3, "detail": "round(x, n=0): Round x to n decimal places"},
            {"label": "floor", "kind": 3, "detail": "floor(x): Round down to nearest integer"},
            {"label": "ceil", "kind": 3, "detail": "ceil(x): Round up to nearest integer"},
            {"label": "sqrt", "kind": 3, "detail": "sqrt(x): Square root of x"},
            {"label": "pow", "kind": 3, "detail": "pow(x, y): x raised to power y"},
            {"label": "sin", "kind": 3, "detail": "sin(x): Sine of x"},
            {"label": "cos", "kind": 3, "detail": "cos(x): Cosine of x"},
            {"label": "tan", "kind": 3, "detail": "tan(x): Tangent of x"},
            {"label": "log", "kind": 3, "detail": "log(x, base=e): Logarithm of x to given base"},
            {"label": "random", "kind": 3, "detail": "random(): Random number between 0 and 1"},
            {"label": "randint", "kind": 3, "detail": "randint(a, b): Random integer between a and b"},
            {"label": "choice", "kind": 3, "detail": "choice(seq): Random element from sequence"},
            {"label": "shuffle", "kind": 3, "detail": "shuffle(seq): Shuffle sequence in place"},
            {"label": "time", "kind": 3, "detail": "time(): Current time in seconds since epoch"},
            {"label": "sleep", "kind": 3, "detail": "sleep(seconds): Sleep for given number of seconds"},
            {"label": "read_file", "kind": 3, "detail": "read_file(path): Read file contents"},
            {"label": "write_file", "kind": 3, "detail": "write_file(path, content): Write content to file"},
            {"label": "append_file", "kind": 3, "detail": "append_file(path, content): Append content to file"},
            {"label": "file_exists", "kind": 3, "detail": "file_exists(path): Check if file exists"},
            {"label": "list_dir", "kind": 3, "detail": "list_dir(path='.'): List directory contents"},
            {"label": "Stack", "kind": 3, "detail": "Stack(): Create a new stack"},
            {"label": "Queue", "kind": 3, "detail": "Queue(): Create a new queue"},
            {"label": "PriorityQueue", "kind": 3, "detail": "PriorityQueue(): Create a new priority queue"},
            {"label": "Set", "kind": 3, "detail": "Set(items=None): Create a new set"},
            {"label": "Graph", "kind": 3, "detail": "Graph(): Create a new graph"}
        ]
        
        # Add keywords
        keywords = [
            {"label": "if", "kind": 14, "detail": "if condition: Control flow statement"},
            {"label": "else", "kind": 14, "detail": "else: Control flow statement"},
            {"label": "for", "kind": 14, "detail": "for var in iterable: Loop statement"},
            {"label": "while", "kind": 14, "detail": "while condition: Loop statement"},
            {"label": "func", "kind": 14, "detail": "func name(params): Function definition"},
            {"label": "return", "kind": 14, "detail": "return value: Return from function"},
            {"label": "break", "kind": 14, "detail": "break: Exit loop"},
            {"label": "continue", "kind": 14, "detail": "continue: Skip to next iteration"},
            {"label": "let", "kind": 14, "detail": "let name = value: Variable declaration"},
            {"label": "true", "kind": 14, "detail": "true: Boolean literal"},
            {"label": "false", "kind": 14, "detail": "false: Boolean literal"},
            {"label": "nil", "kind": 14, "detail": "nil: Null value"}
        ]
        
        # Convert symbols to completion items
        completion_items = []
        
        for symbol in symbols:
            item = {
                "label": symbol["name"],
                "kind": symbol["kind"],
                "detail": symbol.get("detail", ""),
                "documentation": symbol.get("documentation", "")
            }
            completion_items.append(item)
        
        # Add standard library and keywords
        completion_items.extend(stdlib_symbols)
        completion_items.extend(keywords)
        
        # Filter by prefix if any
        prefix_match = re.search(r'(\w+)$', line_text)
        if prefix_match:
            prefix = prefix_match.group(1).lower()
            completion_items = [item for item in completion_items if item["label"].lower().startswith(prefix)]
        
        return completion_items
    
    def _extract_symbols(self, uri: str, text: str) -> List[Dict[str, Any]]:
        """Extract symbols from document text."""
        # Check cache
        if uri in self.symbols_cache:
            return self.symbols_cache[uri]
        
        symbols = []
        lines = text.splitlines()
        
        # Find variable declarations
        for i, line in enumerate(lines):
            # Variables
            for match in re.finditer(r'let\s+(\w+)\s*=\s*(.+?);', line):
                var_name = match.group(1)
                var_value = match.group(2).strip()
                
                # Determine variable type
                var_type = "any"
                if var_value.startswith('"') or var_value.startswith("'"):
                    var_type = "string"
                elif var_value.isdigit():
                    var_type = "int"
                elif re.match(r'^[0-9]+\.[0-9]+$', var_value):
                    var_type = "float"
                elif var_value in ["true", "false"]:
                    var_type = "boolean"
                elif var_value.startswith("["):
                    var_type = "List<any>"
                
                symbols.append({
                    "name": var_name,
                    "kind": 13,  # Variable
                    "detail": f"{var_type} {var_name}",
                    "location": {
                        "uri": uri,
                        "range": {
                            "start": {"line": i, "character": match.start(1)},
                            "end": {"line": i, "character": match.end(1)}
                        }
                    }
                })
            
            # Functions
            func_match = re.search(r'func\s+(\w+)\s*\(([^)]*)\)', line)
            if func_match:
                func_name = func_match.group(1)
                params_str = func_match.group(2)
                
                # Parse parameters
                params = []
                if params_str.strip():
                    for param in params_str.split(","):
                        param = param.strip()
                        params.append({"name": param})
                
                symbols.append({
                    "name": func_name,
                    "kind": 3,  # Function
                    "detail": f"func {func_name}({params_str})",
                    "parameters": params,
                    "location": {
                        "uri": uri,
                        "range": {
                            "start": {"line": i, "character": func_match.start(1)},
                            "end": {"line": i, "character": func_match.end(1)}
                        }
                    }
                })
        
        # Cache symbols
        self.symbols_cache[uri] = symbols
        
        return symbols
    
    def _find_symbol_definition(self, name: str, uri: str) -> Optional[Dict[str, Any]]:
        """Find symbol definition."""
        # Check cache
        cache_key = f"{uri}:{name}"
        if cache_key in self.definitions_cache:
            return self.definitions_cache[cache_key]
        
        # Extract symbols from document
        document = self.language_server.open_documents.get(uri)
        if not document:
            return None
        
        symbols = self._extract_symbols(uri, document["text"])
        
        # Find symbol by name
        for symbol in symbols:
            if symbol["name"] == name:
                self.definitions_cache[cache_key] = symbol
                return symbol
        
        return None
    
    def _find_references(self, name: str, uri: str) -> List[Dict[str, Any]]:
        """Find all references to a symbol."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        references = []
        
        # Find all occurrences of the name
        for i, line in enumerate(text.splitlines()):
            for match in re.finditer(r'\b' + re.escape(name) + r'\b', line):
                references.append({
                    "uri": uri,
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    }
                })
        
        return references