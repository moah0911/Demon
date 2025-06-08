#!/usr/bin/env python3
"""
Demon Programming Language Interpreter
A Python-based interpreter for the Demon language.
"""

import sys
import os
import math
import random
import time
from typing import List, Dict, Optional, Any, Union, Callable, Tuple, TypeVar, Generic
from collections import defaultdict, deque
import heapq
import dataclasses
from dataclasses import dataclass

# Import local modules
from .tokens import Token, TokenType
from .ast import *
from .parser import Parser, ParseError
from .resolver import Resolver
from .interpreter import Interpreter, RuntimeError, Return, Break, Continue, Environment
from .type_checker import TypeChecker
from .bytecode import BytecodeCompiler
from .vm import VM

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Built-in DSA Types and Algorithms
class Graph:
    def __init__(self):
        self.adjacency = defaultdict(dict)
    
    def add_node(self, node: Any) -> None:
        if node not in self.adjacency:
            self.adjacency[node] = {}
    
    def add_edge(self, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
        self.adjacency[from_node][to_node] = weight
        # For undirected graph, uncomment:
        # self.adjacency[to_node][from_node] = weight
    
    def depth_first_search(self, start: Any) -> List[Any]:
        visited = set()
        result = []
        
        def dfs(node):
            if node not in visited:
                visited.add(node)
                result.append(node)
                for neighbor in self.adjacency[node]:
                    dfs(neighbor)
        
        dfs(start)
        return result
    
    def breadth_first_search(self, start: Any) -> List[Any]:
        visited = {start}
        queue = deque([start])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in self.adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return result
    
    def shortest_path(self, start: Any, end: Any) -> Tuple[float, List[Any]]:
        # Dijkstra's algorithm
        heap = [(0, start, [])]
        visited = set()
        
        while heap:
            (cost, node, path) = heapq.heappop(heap)
            if node not in visited:
                visited.add(node)
                path = path + [node]
                
                if node == end:
                    return (cost, path)
                
                for neighbor, weight in self.adjacency[node].items():
                    if neighbor not in visited:
                        heapq.heappush(heap, (cost + weight, neighbor, path))
        
        return (float('inf'), [])

class TreeNode(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.left: Optional['TreeNode[T]'] = None
        self.right: Optional['TreeNode[T]'] = None
        self.children: List['TreeNode[T]'] = []
    
    def add_child(self, node: 'TreeNode[T]') -> None:
        self.children.append(node)

class LinkedListNode(Generic[T]):
    def __init__(self, value: T):
        self.value = value
        self.next: Optional['LinkedListNode[T]'] = None

class Stack(Generic[T]):
    def __init__(self):
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        return self._items.pop()
    
    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)

class Queue(Generic[T]):
    def __init__(self):
        self._items: deque[T] = deque()
    
    def enqueue(self, item: T) -> None:
        self._items.append(item)
    
    def dequeue(self) -> T:
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        return self._items.popleft()
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def size(self) -> int:
        return len(self._items)

# Built-in functions
def demon_print(*args, **kwargs):
    print(*args, **kwargs)

def demon_input(prompt: str = "") -> str:
    return input(prompt)

def demon_range(*args):
    return list(range(*args))

def demon_len(iterable) -> int:
    return len(iterable)

def demon_type(obj) -> str:
    return type(obj).__name__

# Built-in DSA functions
def demon_graph_create() -> Graph:
    return Graph()

def demon_graph_add_node(graph: Graph, node: Any) -> None:
    graph.add_node(node)

def demon_graph_add_edge(graph: Graph, from_node: Any, to_node: Any, weight: float = 1.0) -> None:
    graph.add_edge(from_node, to_node, weight)

def demon_graph_dfs(graph: Graph, start: Any) -> List[Any]:
    return graph.depth_first_search(start)

def demon_graph_bfs(graph: Graph, start: Any) -> List[Any]:
    return graph.breadth_first_search(start)

def demon_graph_shortest_path(graph: Graph, start: Any, end: Any) -> Tuple[float, List[Any]]:
    return graph.shortest_path(start, end)

def demon_tree_create(value: Any) -> TreeNode:
    return TreeNode(value)

def demon_tree_insert(root: TreeNode, value: Any) -> None:
    if value < root.value:
        if root.left is None:
            root.left = TreeNode(value)
        else:
            demon_tree_insert(root.left, value)
    else:
        if root.right is None:
            root.right = TreeNode(value)
        else:
            demon_tree_insert(root.right, value)

def demon_sort_quick(arr: List[Any]) -> List[Any]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return demon_sort_quick(left) + middle + demon_sort_quick(right)

def demon_sort_merge(arr: List[Any]) -> List[Any]:
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = demon_sort_merge(arr[:mid])
    right = demon_sort_merge(arr[mid:])
    
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def demon_binary_search(arr: List[Any], target: Any) -> int:
    low = 0
    high = len(arr) - 1
    
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] < target:
            low = mid + 1
        elif arr[mid] > target:
            high = mid - 1
        else:
            return mid
    
    return -1

# Built-in modules
builtin_modules = {
    'math': math,
    'random': random,
    'time': time,
}

# Built-in functions
builtin_functions = {
    'print': demon_print,
    'input': demon_input,
    'range': demon_range,
    'len': demon_len,
    'type': demon_type,
    # DSA functions
    'Graph': demon_graph_create,
    'TreeNode': demon_tree_create,
    'Stack': Stack,
    'Queue': Queue,
    'LinkedListNode': LinkedListNode,
}

class Scanner:
    keywords = {
        # Control flow
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'for': TokenType.FOR,
        'while': TokenType.WHILE,
        'do': TokenType.DO,
        'switch': TokenType.SWITCH,
        'case': TokenType.CASE,
        'default': TokenType.DEFAULT,
        'break': TokenType.BREAK,
        'continue': TokenType.CONTINUE,
        'return': TokenType.RETURN,
        'yield': TokenType.YIELD,
        'throw': TokenType.THROW,
        'try': TokenType.TRY,
        'catch': TokenType.CATCH,
        'finally': TokenType.FINALLY,
        
        # Pattern matching
        'match': TokenType.MATCH,
        'when': TokenType.WHEN,
        'is': TokenType.IS,
        'as': TokenType.AS,
        'of': TokenType.OF,
        'where': TokenType.WHERE,
        
        # Functions and types
        'func': TokenType.FUNC,
        'class': TokenType.CLASS,
        'interface': TokenType.INTERFACE,
        'trait': TokenType.TRAIT,
        'enum': TokenType.ENUM,
        'type': TokenType.TYPE,
        'typeof': TokenType.TYPEOF,
        'new': TokenType.NEW,
        'this': TokenType.THIS,
        'super': TokenType.SUPER,
        'self': TokenType.SELF,
        
        # Variables and constants
        'var': TokenType.VAR,
        'let': TokenType.LET,
        'const': TokenType.CONST,
        'static': TokenType.STATIC,
        'readonly': TokenType.READONLY,
        'volatile': TokenType.VOLATILE,
        
        # I/O
        'print': TokenType.PRINT,
        
        # Access modifiers
        'public': TokenType.PUBLIC,
        'private': TokenType.PRIVATE,
        'protected': TokenType.PROTECTED,
        'internal': TokenType.INTERNAL,
        'export': TokenType.EXPORT,
        
        # OOP
        'extends': TokenType.EXTENDS,
        'implements': TokenType.IMPLEMENTS,
        'virtual': TokenType.VIRTUAL,
        'true': TokenType.TRUE,
        'false': TokenType.FALSE,
        'nil': TokenType.NIL,
        
        # Logic
        'and': TokenType.AND,
        'or': TokenType.OR,
        'not': TokenType.BANG,
        
        # DSA types
        'graph': TokenType.GRAPH,
        'node': TokenType.NODE,
        'edge': TokenType.EDGE,
        'tree': TokenType.TREE,
        'binary_tree': TokenType.BINARY_TREE,
        'bst': TokenType.BINARY_SEARCH_TREE,
        'heap': TokenType.HEAP,
        'min_heap': TokenType.MIN_HEAP,
        'max_heap': TokenType.MAX_HEAP,
        'stack': TokenType.STACK,
        'queue': TokenType.QUEUE,
        'linked_list': TokenType.LINKED_LIST,
        'hash_map': TokenType.HASH_MAP,
        'hash_set': TokenType.HASH_SET,
        
        # Type annotations
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'str': TokenType.STR,
        'bool': TokenType.BOOL,
        'list': TokenType.LIST,
        'dict': TokenType.DICT,
        'tuple': TokenType.TUPLE,
        'set': TokenType.SET,
        'any': TokenType.ANY,
        'void': TokenType.VOID,
        
        # For-each loop
        'in': TokenType.IN,
    }
    
    def __init__(self, source: str, file_path: str = "<stdin>"):
        self.source = source
        self.file_path = file_path
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.had_error = False
    
    def scan_tokens(self) -> List[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def scan_token(self):
        c = self.advance()
        
        # Handle multi-character operators first
        if c == '|' and self.match('>', '|'):  # |>|
            self.add_token(TokenType.PIPE_FIRST)
        elif c == '|' and self.match('>'):  # |>
            self.add_token(TokenType.PIPE_GT)
        elif c == '?' and self.match('?'):  # ??
            self.add_token(TokenType.NULL_COALESCE)
        elif c == '.' and self.match('.'):  # .. or ..<
            if self.match('<'):
                self.add_token(TokenType.RANGE_EXCL)  # ..<
            else:
                self.add_token(TokenType.RANGE_INCL)  # ..
        elif c == '=' and self.match('>'):  # =>
            self.add_token(TokenType.FAT_ARROW)
        elif c == '-' and self.match('>'):  # ->
            self.add_token(TokenType.DOUBLE_ARROW)
        elif c == '$' and self.match('{'):  # ${
            self.add_token(TokenType.INTERPOLATE)
            
        # Single character tokens
        elif c == '(': self.add_token(TokenType.LEFT_PAREN)
        elif c == ')': self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{': self.add_token(TokenType.LEFT_BRACE)
        elif c == '}': self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[': self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']': self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',': self.add_token(TokenType.COMMA)
        elif c == '.': self.add_token(TokenType.DOT)
        elif c == '-': self.add_token(TokenType.MINUS)
        elif c == '+': self.add_token(TokenType.PLUS)
        elif c == ';': self.add_token(TokenType.SEMICOLON)
        elif c == '*': self.add_token(TokenType.STAR)
        elif c == '@': self.add_token(TokenType.AT)
        elif c == '|': self.add_token(TokenType.PIPE)
        elif c == '?': self.add_token(TokenType.QUESTION)
        elif c == ':': self.add_token(TokenType.COLON)
        elif c == '%': self.add_token(TokenType.PERCENT)
        # Two character operators
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            if self.match('='):
                self.add_token(TokenType.LESS_EQUAL)
            else:
                self.add_token(TokenType.LESS)
        elif c == '>':
            if self.match('='):
                self.add_token(TokenType.GREATER_EQUAL)
            else:
                self.add_token(TokenType.GREATER)
        # Comments and division
        elif c == '/':
            if self.match('/'):
                # Line comment
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                # Block comment
                while not (self.peek() == '*' and self.peek_next() == '/') and not self.is_at_end():
                    if self.peek() == '\n':
                        self.line += 1
                    self.advance()
                if self.is_at_end():
                    self.error(self.line, "Unterminated block comment")
                # Skip the closing */
                self.advance()  # *
                self.advance()  # /
            else:
                self.add_token(TokenType.SLASH)
        # Whitespace
        elif c in [' ', '\r', '\t']:
            pass  # Ignore whitespace
        elif c == '\n':
            self.line += 1
        # String literals
        elif c == '"' or c == '\'':
            self.string(c)
        # Number literals
        elif c.isdigit():
            self.number()
        # Identifiers and keywords
        elif c.isalpha() or c == '_':
            self.identifier()
        # Unknown character
        else:
            self.error(self.line, f"Unexpected character: {c}")
    
    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)
    
    def number(self):
        is_float = False
        
        # Integer part
        while self.peek().isdigit():
            self.advance()
        
        # Fractional part
        if self.peek() == '.':
            is_float = True
            self.advance()  # Consume the "."
            
            while self.peek().isdigit():
                self.advance()
        
        # Exponent part
        if self.peek().lower() in ['e', 'E']:
            is_float = True
            self.advance()  # Consume 'e' or 'E'
            
            if self.peek() in ['+', '-']:
                self.advance()  # Consume sign
            
            while self.peek().isdigit():
                self.advance()
        
        # Parse the number
        number_str = self.source[self.start:self.current]
        if is_float or '.' in number_str or 'e' in number_str.lower():
            self.add_token(TokenType.NUMBER, float(number_str))
        else:
            self.add_token(TokenType.NUMBER, int(number_str))
    
    def string(self, quote_type):
        # Handle string literals with both single and double quotes
        while (self.peek() != quote_type or (self.peek() == quote_type and self.previous() == '\\')) and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            self.error(self.line, "Unterminated string")
            return
        
        # The closing quote
        self.advance()
        
        # Get the string value (without quotes)
        value = self.source[self.start + 1:self.current - 1]
        
        # Handle escape sequences
        value = (
            value
            .replace('\\n', '\n')
            .replace('\\t', '\t')
            .replace('\\r', '\r')
            .replace('\\\\', '\\')
            .replace(f'\\{quote_type}', quote_type)
        )
        
        self.add_token(TokenType.STRING, value)
    
    def match(self, *expected: str) -> bool:
        """Check if the next character(s) match any of the expected characters."""
        for exp in expected:
            if self.check_next(exp):
                self.advance()
                return True
        return False
    
    def check_next(self, expected: str) -> bool:
        """Check if the next len(expected) characters match the expected string."""
        if self.current + len(expected) > len(self.source):
            return False
        
        for i in range(len(expected)):
            if self.source[self.current + i] != expected[i]:
                return False
        return True
    
    def peek(self, offset: int = 0) -> str:
        """Look ahead 'offset' characters without consuming them."""
        if self.current + offset >= len(self.source):
            return '\0'
        return self.source[self.current + offset]
    
    def peek_next(self) -> str:
        """Look at the next character without consuming it."""
        return self.peek(1)
    
    def previous(self) -> str:
        """Get the last consumed character."""
        if self.current == 0:
            return '\0'
        return self.source[self.current - 1]
    
    def is_at_end(self) -> bool:
        """Check if we've consumed all characters."""
        return self.current >= len(self.source)
    
    def advance(self) -> str:
        """Consume and return the current character."""
        if not self.is_at_end():
            self.current += 1
        return self.source[self.current - 1] if self.current > 0 else '\0'
        
    def is_digit(self, c: str) -> bool:
        """Check if a character is a digit."""
        return c.isdigit()
    
    def is_alpha(self, c: str) -> bool:
        """Check if a character is alphabetic or underscore."""
        return c.isalpha() or c == '_'
    
    def is_alphanumeric(self, c: str) -> bool:
        """Check if a character is alphanumeric or underscore."""
        return c.isalnum() or c == '_'
    
    def add_token(self, type: TokenType, literal: Any = None):
        """Add a new token with the current lexeme."""
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
    
    def error(self, line: int, message: str):
        """Report a scanning error and set the error flag."""
        print(f"[{self.file_path}:{line}] Error: {message}")
        self.had_error = True
    
    def is_digit(self, c: str) -> bool:
        """Check if a character is a digit."""
        return c.isdigit()
    

class ParseError(RuntimeError):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message


# AST Nodes
class Expr:
    pass

class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"

class Grouping(Expr):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def __str__(self):
        return f"(group {self.expression})"

class Literal(Expr):
    def __init__(self, value: Any):
        self.value = value
    
    def __str__(self):
        return str(self.value) if self.value is not None else "nil"

class Unary(Expr):
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

class Demon:
    """Main Demon interpreter class."""
    
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)
        self.resolver = Resolver(self.interpreter)
        self.enable_type_checking = False  # Type checking is disabled by default
        self.use_bytecode = False  # Use bytecode VM instead of AST interpreter
        self.vm = VM(self)
    
    def run_file(self, path: str) -> None:
        """Run a Demon script from a file."""
        print(f"Attempting to run file: {path}")
        try:
            print(f"Opening file: {os.path.abspath(path)}")
            with open(path, 'r', encoding='utf-8') as f:
                source = f.read()
            print(f"File content length: {len(source)} characters")
            print("File content:")
            print("-" * 40)
            print(source)
            print("-" * 40)
            self.run(source, path)
            if self.had_error:
                print("Errors encountered during execution")
                sys.exit(65)
            if self.had_runtime_error:
                print("Runtime errors encountered")
                sys.exit(70)
        except IOError as e:
            print(f"Error reading file {path}: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"File exists: {os.path.exists(path)}")
            sys.exit(74)
    
    def run_prompt(self) -> None:
        """Start the Demon REPL."""
        print("Demon REPL (type 'exit' or 'quit' to exit)")
        while True:
            try:
                line = input("> ")
                if line.strip().lower() in ('exit', 'quit'):
                    break
                self.run(line)
                self.had_error = False  # Reset error flag for REPL
            except EOFError:
                print("\nExiting...")
                break
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")
    
    def run(self, source: str, file_path: str = "<stdin>") -> None:
        """Run Demon source code."""
        # Lexical analysis
        scanner = Scanner(source, file_path)
        tokens = scanner.scan_tokens()
        
        # Stop if there were scanning errors
        if scanner.had_error:
            self.had_error = True
            return
            
        # Parsing
        parser = Parser(tokens, self)
        statements = parser.parse()
        
        # Stop if there were parsing errors
        if self.had_error:
            return
            
        # Filter out None statements
        if statements is not None:
            statements = [stmt for stmt in statements if stmt is not None]
        
        # Type checking (optional, can be enabled/disabled)
        if self.enable_type_checking and statements:
            type_checker = TypeChecker(self)
            type_errors = type_checker.check(statements)
            
            # Report type errors
            for error in type_errors:
                print(error)
            
            # Stop if there were type errors
            if type_errors:
                self.had_error = True
                return
        
        # Resolve variables
        self.resolver.resolve(statements)
        
        # Stop if there were resolution errors
        if self.had_error:
            return
            
        # Interpret the program
        if statements:  # Only interpret if there are statements
            if self.use_bytecode:
                # Compile to bytecode and run in VM
                compiler = BytecodeCompiler(self)
                chunk = compiler.compile(statements)
                self.vm.interpret(chunk)
            else:
                # Use AST interpreter
                self.interpreter.interpret(statements)
    
    def error(self, token: Token, message: str) -> None:
        """Report a syntax error."""
        if isinstance(token, int):
            # Handle old-style error calls
            line = token
            file_path = "<stdin>"
            print(f"[{file_path}:{line}] Error: {message}")
        else:
            # Handle new-style error calls with token
            print(f"[line {token.line}] Error at '{token.lexeme}': {message}")
        self.had_error = True
    
    def runtime_error(self, error: RuntimeError) -> None:
        """Report a runtime error."""
        print(f"[line {error.token.line}] {error.message}")
        self.had_runtime_error = True


def main() -> None:
    """Entry point for the Demon interpreter."""
    demon = Demon()
    
    if len(sys.argv) > 2:
        print("Usage: demon [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        demon.run_file(sys.argv[1])
    else:
        demon.run_prompt()


if __name__ == "__main__":
    main()