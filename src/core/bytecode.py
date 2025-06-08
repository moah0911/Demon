"""
Bytecode compiler for the Demon programming language.
This module converts Demon AST to bytecode instructions.
"""

from enum import Enum, auto
from typing import List, Dict, Any, Optional, Union, Tuple
import demon_ast as ast
from tokens import Token, TokenType

class OpCode(Enum):
    """Bytecode operation codes."""
    CONSTANT = auto()      # Push constant onto stack
    NIL = auto()           # Push nil onto stack
    TRUE = auto()          # Push true onto stack
    FALSE = auto()         # Push false onto stack
    POP = auto()           # Pop value from stack
    GET_LOCAL = auto()     # Get local variable
    SET_LOCAL = auto()     # Set local variable
    GET_GLOBAL = auto()    # Get global variable
    SET_GLOBAL = auto()    # Set global variable
    DEFINE_GLOBAL = auto() # Define global variable
    GET_UPVALUE = auto()   # Get upvalue (closure)
    SET_UPVALUE = auto()   # Set upvalue (closure)
    EQUAL = auto()         # Check if two values are equal
    GREATER = auto()       # Check if first value is greater than second
    LESS = auto()          # Check if first value is less than second
    ADD = auto()           # Add two values
    SUBTRACT = auto()      # Subtract second value from first
    MULTIPLY = auto()      # Multiply two values
    DIVIDE = auto()        # Divide first value by second
    MODULO = auto()        # Modulo operation
    NOT = auto()           # Logical NOT
    NEGATE = auto()        # Arithmetic negation
    PRINT = auto()         # Print value
    JUMP = auto()          # Jump to offset
    JUMP_IF_FALSE = auto() # Jump to offset if condition is false
    LOOP = auto()          # Jump backward to start of loop
    CALL = auto()          # Call function
    RETURN = auto()        # Return from function
    CLOSURE = auto()       # Create closure
    CLOSE_UPVALUE = auto() # Close upvalue
    LIST = auto()          # Create list
    GET_INDEX = auto()     # Get item at index
    SET_INDEX = auto()     # Set item at index
    IMPORT = auto()        # Import module

class Chunk:
    """A chunk of bytecode."""
    
    def __init__(self):
        self.code: List[int] = []  # Bytecode instructions
        self.constants: List[Any] = []  # Constants pool
        self.lines: List[int] = []  # Line information for debugging
    
    def write(self, byte: int, line: int):
        """Write a byte to the chunk."""
        self.code.append(byte)
        self.lines.append(line)
    
    def add_constant(self, value: Any) -> int:
        """Add a constant to the chunk and return its index."""
        self.constants.append(value)
        return len(self.constants) - 1

class Local:
    """Represents a local variable during compilation."""
    
    def __init__(self, name: str, depth: int, is_captured: bool = False):
        self.name = name
        self.depth = depth
        self.is_captured = is_captured

class Upvalue:
    """Represents an upvalue during compilation."""
    
    def __init__(self, index: int, is_local: bool):
        self.index = index
        self.is_local = is_local

class CompilerFunction:
    """Represents a function being compiled."""
    
    def __init__(self, name: str, function_type: str):
        self.name = name
        self.function_type = function_type  # "script", "function", "method"
        self.chunk = Chunk()
        self.locals: List[Local] = []
        self.upvalues: List[Upvalue] = []
        self.scope_depth = 0
        self.arity = 0

class BytecodeCompiler(ast.Visitor):
    """Compiles Demon AST to bytecode."""
    
    def __init__(self, demon):
        self.demon = demon
        self.current = None  # Current function being compiled
        self.functions: List[CompilerFunction] = []
        self.locals: List[Local] = []
        self.upvalues: List[Upvalue] = []
        self.scope_depth = 0
        
        # Initialize with script function
        self.init_compiler("script", "script")
    
    def init_compiler(self, name: str, function_type: str):
        """Initialize a new compiler for a function."""
        function = CompilerFunction(name, function_type)
        self.functions.append(function)
        self.current = function
        
        # Add "this" as first local if it's a method
        if function_type == "method":
            self.add_local("this")
    
    def add_local(self, name: str):
        """Add a local variable."""
        local = Local(name, self.scope_depth)
        self.current.locals.append(local)
    
    def compile(self, statements: List[ast.Stmt]) -> Chunk:
        """Compile statements to bytecode."""
        for statement in statements:
            self.compile_stmt(statement)
        
        # Add implicit return at the end
        self.emit(OpCode.NIL)
        self.emit(OpCode.RETURN)
        
        return self.current.chunk
    
    def compile_stmt(self, stmt: ast.Stmt):
        """Compile a statement."""
        stmt.accept(self)
    
    def compile_expr(self, expr: ast.Expr):
        """Compile an expression."""
        expr.accept(self)
    
    def emit(self, op: OpCode, *args):
        """Emit a bytecode instruction."""
        self.current.chunk.write(op.value, 0)  # Line info is placeholder
        for arg in args:
            self.current.chunk.write(arg, 0)  # Line info is placeholder
    
    def emit_constant(self, value: Any):
        """Emit a constant."""
        constant_idx = self.current.chunk.add_constant(value)
        self.emit(OpCode.CONSTANT, constant_idx)
    
    def begin_scope(self):
        """Begin a new scope."""
        self.current.scope_depth += 1
    
    def end_scope(self):
        """End the current scope."""
        self.current.scope_depth -= 1
        
        # Pop locals that are going out of scope
        while (self.current.locals and 
               self.current.locals[-1].depth > self.current.scope_depth):
            if self.current.locals[-1].is_captured:
                self.emit(OpCode.CLOSE_UPVALUE)
            else:
                self.emit(OpCode.POP)
            self.current.locals.pop()
    
    # Statement visitors
    
    def visit_expression_stmt(self, stmt: ast.Expression):
        self.compile_expr(stmt.expression)
        self.emit(OpCode.POP)  # Discard the result
    
    def visit_print(self, stmt: ast.Print):
        for expr in stmt.expressions:
            self.compile_expr(expr)
        self.emit(OpCode.PRINT, len(stmt.expressions))
    
    def visit_var_stmt(self, stmt: ast.Var):
        # Compile initializer if present
        if stmt.initializer:
            self.compile_expr(stmt.initializer)
        else:
            self.emit(OpCode.NIL)  # Default to nil
        
        # Define the variable
        name = stmt.name.lexeme
        if self.current.scope_depth == 0:
            # Global variable
            global_idx = self.current.chunk.add_constant(name)
            self.emit(OpCode.DEFINE_GLOBAL, global_idx)
        else:
            # Local variable
            self.add_local(name)
    
    def visit_block_stmt(self, stmt: ast.Block):
        self.begin_scope()
        for statement in stmt.statements:
            self.compile_stmt(statement)
        self.end_scope()
    
    def visit_if_stmt(self, stmt: ast.If):
        # Compile condition
        self.compile_expr(stmt.condition)
        
        # Emit jump if false
        then_jump = len(self.current.chunk.code)
        self.emit(OpCode.JUMP_IF_FALSE, 0)  # Placeholder jump offset
        
        # Compile then branch
        self.emit(OpCode.POP)  # Pop condition
        self.compile_stmt(stmt.then_branch)
        
        # Emit jump over else branch
        else_jump = len(self.current.chunk.code)
        self.emit(OpCode.JUMP, 0)  # Placeholder jump offset
        
        # Patch then jump
        self.current.chunk.code[then_jump + 1] = len(self.current.chunk.code) - then_jump - 2
        
        # Compile else branch if present
        if stmt.else_branch:
            self.compile_stmt(stmt.else_branch)
        
        # Patch else jump
        self.current.chunk.code[else_jump + 1] = len(self.current.chunk.code) - else_jump - 2
    
    def visit_while_stmt(self, stmt: ast.While):
        loop_start = len(self.current.chunk.code)
        
        # Compile condition
        self.compile_expr(stmt.condition)
        
        # Emit jump if false
        exit_jump = len(self.current.chunk.code)
        self.emit(OpCode.JUMP_IF_FALSE, 0)  # Placeholder jump offset
        
        # Compile body
        self.emit(OpCode.POP)  # Pop condition
        self.compile_stmt(stmt.body)
        
        # Emit loop back
        self.emit(OpCode.LOOP, len(self.current.chunk.code) - loop_start + 2)
        
        # Patch exit jump
        self.current.chunk.code[exit_jump + 1] = len(self.current.chunk.code) - exit_jump - 2
        
        self.emit(OpCode.POP)  # Pop condition
    
    def visit_function_stmt(self, stmt: ast.Function):
        # Create function object
        function_name = stmt.name.lexeme
        self.init_compiler(function_name, "function")
        
        # Compile parameters
        self.begin_scope()
        self.current.arity = len(stmt.params)
        for param, _ in stmt.params:
            self.add_local(param.lexeme)
        
        # Compile body
        for statement in stmt.body:
            self.compile_stmt(statement)
        
        # Add implicit return if needed
        if not stmt.body or not isinstance(stmt.body[-1], ast.Return):
            self.emit(OpCode.NIL)
            self.emit(OpCode.RETURN)
        
        # Finalize function
        function = self.functions.pop()
        self.current = self.functions[-1]
        
        # Create closure
        function_idx = self.current.chunk.add_constant(function)
        self.emit(OpCode.CLOSURE, function_idx)
        
        # Define the function
        if self.current.scope_depth == 0:
            # Global function
            global_idx = self.current.chunk.add_constant(function_name)
            self.emit(OpCode.DEFINE_GLOBAL, global_idx)
        else:
            # Local function
            self.add_local(function_name)
    
    def visit_return_stmt(self, stmt: ast.Return):
        if stmt.value:
            self.compile_expr(stmt.value)
        else:
            self.emit(OpCode.NIL)
        
        self.emit(OpCode.RETURN)
    
    # Expression visitors
    
    def visit_binary_expr(self, expr: ast.Binary):
        # Compile operands
        self.compile_expr(expr.left)
        self.compile_expr(expr.right)
        
        # Emit operator
        if expr.operator.type == TokenType.PLUS:
            self.emit(OpCode.ADD)
        elif expr.operator.type == TokenType.MINUS:
            self.emit(OpCode.SUBTRACT)
        elif expr.operator.type == TokenType.STAR:
            self.emit(OpCode.MULTIPLY)
        elif expr.operator.type == TokenType.SLASH:
            self.emit(OpCode.DIVIDE)
        elif expr.operator.type == TokenType.PERCENT:
            self.emit(OpCode.MODULO)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            self.emit(OpCode.EQUAL)
        elif expr.operator.type == TokenType.BANG_EQUAL:
            self.emit(OpCode.EQUAL)
            self.emit(OpCode.NOT)
        elif expr.operator.type == TokenType.GREATER:
            self.emit(OpCode.GREATER)
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.emit(OpCode.LESS)
            self.emit(OpCode.NOT)
        elif expr.operator.type == TokenType.LESS:
            self.emit(OpCode.LESS)
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.emit(OpCode.GREATER)
            self.emit(OpCode.NOT)
    
    def visit_unary_expr(self, expr: ast.Unary):
        # Compile operand
        self.compile_expr(expr.right)
        
        # Emit operator
        if expr.operator.type == TokenType.MINUS:
            self.emit(OpCode.NEGATE)
        elif expr.operator.type == TokenType.BANG:
            self.emit(OpCode.NOT)
    
    def visit_literal_expr(self, expr: ast.Literal):
        if expr.value is None:
            self.emit(OpCode.NIL)
        elif expr.value is True:
            self.emit(OpCode.TRUE)
        elif expr.value is False:
            self.emit(OpCode.FALSE)
        else:
            self.emit_constant(expr.value)
    
    def visit_variable_expr(self, expr: ast.Variable):
        name = expr.name.lexeme
        
        # Look for local variable
        for i, local in enumerate(reversed(self.current.locals)):
            if local.name == name:
                self.emit(OpCode.GET_LOCAL, len(self.current.locals) - 1 - i)
                return
        
        # Global variable
        global_idx = self.current.chunk.add_constant(name)
        self.emit(OpCode.GET_GLOBAL, global_idx)
    
    def visit_assign_expr(self, expr: ast.Assign):
        # Compile value
        self.compile_expr(expr.value)
        
        name = expr.name.lexeme
        
        # Look for local variable
        for i, local in enumerate(reversed(self.current.locals)):
            if local.name == name:
                self.emit(OpCode.SET_LOCAL, len(self.current.locals) - 1 - i)
                return
        
        # Global variable
        global_idx = self.current.chunk.add_constant(name)
        self.emit(OpCode.SET_GLOBAL, global_idx)
    
    def visit_logical_expr(self, expr: ast.Logical):
        # Compile left operand
        self.compile_expr(expr.left)
        
        # Short-circuit evaluation
        if expr.operator.type == TokenType.OR:
            # Jump if true (short-circuit)
            jump = len(self.current.chunk.code)
            self.emit(OpCode.JUMP_IF_FALSE, 0)  # Placeholder jump offset
            
            # Pop the condition and return true
            self.emit(OpCode.POP)
            self.compile_expr(expr.right)
            
            # Patch jump
            self.current.chunk.code[jump + 1] = len(self.current.chunk.code) - jump - 2
        else:  # AND
            # Jump if false (short-circuit)
            jump = len(self.current.chunk.code)
            self.emit(OpCode.JUMP_IF_FALSE, 0)  # Placeholder jump offset
            
            # Pop the condition and evaluate right operand
            self.emit(OpCode.POP)
            self.compile_expr(expr.right)
            
            # Patch jump
            self.current.chunk.code[jump + 1] = len(self.current.chunk.code) - jump - 2
    
    def visit_call_expr(self, expr: ast.Call):
        # Compile callee
        self.compile_expr(expr.callee)
        
        # Compile arguments
        for arg in expr.arguments:
            self.compile_expr(arg)
        
        # Emit call instruction with argument count
        self.emit(OpCode.CALL, len(expr.arguments))
    
    def visit_grouping_expr(self, expr: ast.Grouping):
        self.compile_expr(expr.expression)
    
    def visit_listliteral(self, expr: ast.ListLiteral):
        # Compile elements
        for element in expr.elements:
            self.compile_expr(element)
        
        # Emit list creation instruction with element count
        self.emit(OpCode.LIST, len(expr.elements))