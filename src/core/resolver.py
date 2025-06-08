"""
Variable resolution pass for the Demon programming language.
Handles variable scoping and resolution.
"""

from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from collections import defaultdict, namedtuple

from . import ast
from .tokens import Token, TokenType

class RuntimeError(Exception):
    """Runtime error for the Demon interpreter."""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(self.message)

class Interpreter:
    """Dummy Interpreter class to satisfy type hints."""
    pass

class FunctionType(Enum):
    NONE = "none"
    FUNCTION = "function"
    METHOD = "method"
    INITIALIZER = "initializer"
    LAMBDA = "lambda"

class ClassType(Enum):
    NONE = "none"
    CLASS = "class"
    SUBCLASS = "subclass"

class Resolver(ast.Visitor):
    """Variable resolution pass for the Demon programming language."""
    
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.loop_depth = 0
    
    def resolve(self, statements: List[ast.Stmt]):
        """Resolve a list of statements."""
        if statements is None:
            return
            
        for statement in statements:
            if statement is None:
                continue
            try:
                self.visit_stmt(statement)
            except Exception as e:
                print(f"Error resolving statement: {e}")
                continue
    
    def begin_scope(self):
        """Begin a new scope."""
        self.scopes.append({})
    
    def end_scope(self):
        """End the current scope."""
        self.scopes.pop()
    
    def declare(self, name: Token):
        """Declare a variable in the current scope."""
        if not self.scopes:
            return
        
        if name.lexeme in self.scopes[-1]:
            raise RuntimeError(name, f"Variable '{name.lexeme}' already declared in this scope.")
        
        self.scopes[-1][name.lexeme] = False
    
    def define(self, name: Token):
        """Define a variable in the current scope."""
        if not self.scopes:
            return
        
        self.scopes[-1][name.lexeme] = True
    
    def resolve_local(self, expr: ast.Expr, name: Token):
        """Resolve a variable reference."""
        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
                return
    
    def resolve_function(self, function: ast.Function, type: FunctionType):
        """Resolve a function's body."""
        enclosing_function = self.current_function
        self.current_function = type
        
        self.begin_scope()
        for param, _ in function.params:
            self.declare(param)
            self.define(param)
        
        self.resolve(function.body)
        self.end_scope()
        
        self.current_function = enclosing_function
    
    # Statement visitors
    def visit_block_stmt(self, stmt: ast.Block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()
    
    def visit_var_stmt(self, stmt: ast.Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.visit_expr(stmt.initializer)
        self.define(stmt.name)
    
    def visit_variable_expr(self, expr: ast.Variable):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme, True) is False:
            raise RuntimeError(expr.name, "Can't read local variable in its own initializer.")
        
        self.resolve_local(expr, expr.name)
    
    def visit_assign_expr(self, expr: ast.Assign):
        self.visit_expr(expr.value)
        self.resolve_local(expr, expr.name)
    
    def visit_function_stmt(self, stmt: ast.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        
        self.resolve_function(stmt, 
            FunctionType.INITIALIZER if stmt.name.lexeme == "init" else FunctionType.FUNCTION)
    
    def visit_expression_stmt(self, stmt: ast.Expression):
        self.visit_expr(stmt.expression)
    
    def visit_if_stmt(self, stmt: ast.If):
        self.visit_expr(stmt.condition)
        self.visit_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.visit_stmt(stmt.else_branch)
    
    def visit_print_stmt(self, stmt: ast.Print):
        for expr in stmt.expressions:
            self.visit_expr(expr)
    
    def visit_return_stmt(self, stmt: ast.Return):
        if self.current_function == FunctionType.NONE:
            raise RuntimeError(stmt.keyword, "Can't return from top-level code.")
        
        if stmt.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                raise RuntimeError(stmt.keyword, "Can't return a value from an initializer.")
            self.visit_expr(stmt.value)
    
    def visit_while_stmt(self, stmt: ast.While):
        self.visit_expr(stmt.condition)
        
        self.loop_depth += 1
        self.visit_stmt(stmt.body)
        self.loop_depth -= 1
    
    def visit_foreach_stmt(self, stmt: ast.ForEach):
        # Resolve the iterable
        self.visit_expr(stmt.iterable)
        
        # Begin a new scope for the loop variable
        self.begin_scope()
        
        # Resolve the variable declaration
        if isinstance(stmt.variable, ast.Var):
            self.visit_stmt(stmt.variable)
        elif isinstance(stmt.variable, ast.Variable):
            # If it's just a variable reference, we need to declare and define it
            self.declare(stmt.variable.name)
            self.define(stmt.variable.name)
            self.resolve_local(stmt.variable, stmt.variable.name)
        
        # Resolve the loop body with the new scope
        self.loop_depth += 1
        self.visit_stmt(stmt.body)
        self.loop_depth -= 1
        
        # End the loop variable scope
        self.end_scope()
    
    def visit_break_stmt(self, stmt: ast.Break):
        if self.loop_depth == 0:
            raise RuntimeError(stmt.keyword, "'break' outside of loop.")
    
    def visit_continue_stmt(self, stmt: ast.Continue):
        if self.loop_depth == 0:
            raise RuntimeError(stmt.keyword, "'continue' outside of loop.")
    
    def visit_class_stmt(self, stmt: ast.Class):
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        
        self.declare(stmt.name)
        self.define(stmt.name)
        
        if stmt.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            if stmt.name.lexeme == stmt.superclass.name.lexeme:
                raise RuntimeError(stmt.superclass.name, "A class can't inherit from itself.")
            
            self.visit_expr(stmt.superclass)
            
            # Create a new scope for 'super'
            self.begin_scope()
            self.scopes[-1]["super"] = True
        
        # Create a new scope for 'this'
        self.begin_scope()
        self.scopes[-1]["this"] = True
        
        # Resolve methods
        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)
        
        # Resolve static methods
        for method in stmt.static_methods:
            self.resolve_function(method, FunctionType.METHOD)
        
        self.end_scope()  # End 'this' scope
        
        if stmt.superclass is not None:
            self.end_scope()  # End 'super' scope
        
        self.current_class = enclosing_class
    
    def visit_get_expr(self, expr: ast.Get):
        self.visit_expr(expr.obj)
    
    def visit_set_expr(self, expr: ast.Set):
        self.visit_expr(expr.value)
        self.visit_expr(expr.obj)
    
    def visit_this_expr(self, expr: ast.This):
        if self.current_class == ClassType.NONE:
            raise RuntimeError(expr.keyword, "Can't use 'this' outside of a class.")
        
        self.resolve_local(expr, expr.keyword)
    
    def visit_super_expr(self, expr: ast.Super):
        if self.current_class == ClassType.NONE:
            raise RuntimeError(expr.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            raise RuntimeError(expr.keyword, "Can't use 'super' in a class with no superclass.")
        
        self.resolve_local(expr, expr.keyword)
    
    # Expression visitors
    def visit_binary_expr(self, expr: ast.Binary):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)
    
    def visit_call_expr(self, expr: ast.Call):
        self.visit_expr(expr.callee)
        
        for argument in expr.arguments:
            self.visit_expr(argument)
    
    def visit_grouping_expr(self, expr: ast.Grouping):
        self.visit_expr(expr.expression)
    
    def visit_literal_expr(self, expr: ast.Literal):
        pass  # Literals don't contain expressions
    
    def visit_logical_expr(self, expr: ast.Logical):
        self.visit_expr(expr.left)
        self.visit_expr(expr.right)
    
    def visit_unary_expr(self, expr: ast.Unary):
        self.visit_expr(expr.right)
    
    def visit_lambda_expr(self, expr: ast.Lambda):
        self.resolve_function_like(expr.params, expr.body, FunctionType.LAMBDA)
    
    def visit_listliteral_expr(self, expr: ast.ListLiteral):
        for element in expr.elements:
            self.visit_expr(element)
    
    def visit_mapliteral_expr(self, expr: ast.MapLiteral):
        for key, value in expr.entries:
            self.visit_expr(value)  # Keys are always identifiers, no need to resolve
    
    def visit_blockexpr_expr(self, expr: ast.BlockExpr):
        self.begin_scope()
        self.resolve(expr.statements)
        self.end_scope()
    
    # Helper method for resolving function-like constructs
    def resolve_function_like(self, params, body, function_type):
        enclosing_function = self.current_function
        self.current_function = function_type
        
        self.begin_scope()
        for param, _ in params:
            self.declare(param)
            self.define(param)
        
        self.resolve(body)
        self.end_scope()
        
        self.current_function = enclosing_function