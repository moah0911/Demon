"""
Type checker for the Demon programming language.
This implements static type checking for Demon code.
"""

from typing import Dict, List, Optional, Set, Any, Union
from . import ast
from .tokens import Token, TokenType

class TypeError:
    """Represents a type error in the Demon language."""
    
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
    
    def __str__(self) -> str:
        return f"[line {self.token.line}] Type Error: {self.message}"

class Type:
    """Base class for all types in the Demon language."""
    pass

class PrimitiveType(Type):
    """Represents a primitive type like int, float, string, or boolean."""
    
    def __init__(self, name: str):
        self.name = name
    
    def __eq__(self, other):
        if not isinstance(other, PrimitiveType):
            return False
        return self.name == other.name
    
    def __str__(self) -> str:
        return self.name

class ListType(Type):
    """Represents a list type with element type."""
    
    def __init__(self, element_type: Type):
        self.element_type = element_type
    
    def __eq__(self, other):
        if not isinstance(other, ListType):
            return False
        return self.element_type == other.element_type
    
    def __str__(self) -> str:
        return f"List<{self.element_type}>"

class FunctionType(Type):
    """Represents a function type with parameter and return types."""
    
    def __init__(self, param_types: List[Type], return_type: Type):
        self.param_types = param_types
        self.return_type = return_type
    
    def __eq__(self, other):
        if not isinstance(other, FunctionType):
            return False
        if len(self.param_types) != len(other.param_types):
            return False
        for i in range(len(self.param_types)):
            if self.param_types[i] != other.param_types[i]:
                return False
        return self.return_type == other.return_type
    
    def __str__(self) -> str:
        params = ", ".join(str(t) for t in self.param_types)
        return f"({params}) -> {self.return_type}"

class AnyType(Type):
    """Represents the 'any' type which is compatible with all types."""
    
    def __eq__(self, other):
        return True  # Any type is compatible with any other type
    
    def __str__(self) -> str:
        return "any"

# Define common types
INT_TYPE = PrimitiveType("int")
FLOAT_TYPE = PrimitiveType("float")
STRING_TYPE = PrimitiveType("string")
BOOLEAN_TYPE = PrimitiveType("boolean")
NIL_TYPE = PrimitiveType("nil")
ANY_TYPE = AnyType()

class TypeEnvironment:
    """Environment for storing variable types."""
    
    def __init__(self, enclosing=None):
        self.types: Dict[str, Type] = {}
        self.enclosing = enclosing
    
    def define(self, name: str, type: Type):
        """Define a variable with its type."""
        self.types[name] = type
    
    def get(self, name: Token) -> Type:
        """Get a variable's type."""
        if name.lexeme in self.types:
            return self.types[name.lexeme]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        # If not found, return ANY_TYPE to avoid cascading errors
        return ANY_TYPE

class TypeChecker(ast.Visitor):
    """Type checker for the Demon language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.environment = TypeEnvironment()
        self.errors: List[TypeError] = []
        self.current_function_return_type = NIL_TYPE
    
    def check(self, statements: List[ast.Stmt]) -> List[TypeError]:
        """Check types in a list of statements."""
        self.errors = []
        
        # Add built-in functions to environment
        self.define_native_functions()
        
        # Check each statement
        for statement in statements:
            if statement is not None:
                self.check_stmt(statement)
        
        return self.errors
    
    def define_native_functions(self):
        """Define types for native functions."""
        # print function
        self.environment.define("print", FunctionType([ANY_TYPE], NIL_TYPE))
        
        # Other native functions can be added here
        self.environment.define("clock", FunctionType([], FLOAT_TYPE))
    
    def check_stmt(self, stmt: ast.Stmt):
        """Check types in a statement."""
        return self.visit_stmt(stmt)
    
    def check_expr(self, expr: ast.Expr) -> Type:
        """Check types in an expression and return its type."""
        return self.visit_expr(expr)
    
    def error(self, token: Token, message: str):
        """Report a type error."""
        self.errors.append(TypeError(token, message))
    
    # Statement visitors
    
    def visit_expression_stmt(self, stmt: ast.Expression):
        self.check_expr(stmt.expression)
    
    def visit_print(self, stmt: ast.Print):
        for expr in stmt.expressions:
            self.check_expr(expr)
    
    def visit_var_stmt(self, stmt: ast.Var):
        if stmt.initializer is not None:
            init_type = self.check_expr(stmt.initializer)
            self.environment.define(stmt.name.lexeme, init_type)
        else:
            # If no initializer, assume ANY_TYPE
            self.environment.define(stmt.name.lexeme, ANY_TYPE)
    
    def visit_block_stmt(self, stmt: ast.Block):
        previous_env = self.environment
        self.environment = TypeEnvironment(previous_env)
        
        for statement in stmt.statements:
            self.check_stmt(statement)
        
        self.environment = previous_env
    
    def visit_if_stmt(self, stmt: ast.If):
        condition_type = self.check_expr(stmt.condition)
        if condition_type != BOOLEAN_TYPE and condition_type != ANY_TYPE:
            self.error(stmt.condition.operator if hasattr(stmt.condition, 'operator') else stmt.condition.name, 
                      f"Condition must be a boolean, got {condition_type}")
        
        self.check_stmt(stmt.then_branch)
        if stmt.else_branch is not None:
            self.check_stmt(stmt.else_branch)
    
    def visit_while_stmt(self, stmt: ast.While):
        condition_type = self.check_expr(stmt.condition)
        if condition_type != BOOLEAN_TYPE and condition_type != ANY_TYPE:
            self.error(stmt.condition.operator if hasattr(stmt.condition, 'operator') else stmt.condition.name,
                      f"Condition must be a boolean, got {condition_type}")
        
        self.check_stmt(stmt.body)
    
    def visit_function_stmt(self, stmt: ast.Function):
        # Create function type with parameter types (initially ANY_TYPE)
        param_types = [ANY_TYPE for _ in stmt.params]
        return_type = ANY_TYPE  # Initially assume ANY_TYPE for return
        
        function_type = FunctionType(param_types, return_type)
        self.environment.define(stmt.name.lexeme, function_type)
        
        # Save current return type and set new one
        previous_return_type = self.current_function_return_type
        self.current_function_return_type = return_type
        
        # Check function body in new environment
        previous_env = self.environment
        self.environment = TypeEnvironment(previous_env)
        
        # Define parameters in the new environment
        for (param, _) in stmt.params:
            self.environment.define(param.lexeme, ANY_TYPE)
        
        # Check function body
        for statement in stmt.body:
            self.check_stmt(statement)
        
        # Restore environment and return type
        self.environment = previous_env
        self.current_function_return_type = previous_return_type
    
    def visit_return_stmt(self, stmt: ast.Return):
        value_type = NIL_TYPE
        if stmt.value is not None:
            value_type = self.check_expr(stmt.value)
        
        # Check if return type matches function return type
        if self.current_function_return_type != ANY_TYPE and value_type != self.current_function_return_type:
            self.error(stmt.keyword, 
                      f"Return type mismatch: expected {self.current_function_return_type}, got {value_type}")
    
    # Expression visitors
    
    def visit_binary_expr(self, expr: ast.Binary) -> Type:
        left_type = self.check_expr(expr.left)
        right_type = self.check_expr(expr.right)
        
        # Handle different operators
        if expr.operator.type in [TokenType.PLUS, TokenType.MINUS, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT]:
            # Arithmetic operators
            if left_type in [INT_TYPE, FLOAT_TYPE] and right_type in [INT_TYPE, FLOAT_TYPE]:
                # If either is float, result is float, otherwise int
                if left_type == FLOAT_TYPE or right_type == FLOAT_TYPE:
                    return FLOAT_TYPE
                return INT_TYPE
            
            # Special case for string concatenation with +
            if expr.operator.type == TokenType.PLUS and left_type == STRING_TYPE and right_type == STRING_TYPE:
                return STRING_TYPE
            
            self.error(expr.operator, 
                      f"Operator {expr.operator.lexeme} cannot be applied to types {left_type} and {right_type}")
            return ANY_TYPE
        
        elif expr.operator.type in [TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL]:
            # Comparison operators
            if left_type in [INT_TYPE, FLOAT_TYPE] and right_type in [INT_TYPE, FLOAT_TYPE]:
                return BOOLEAN_TYPE
            
            self.error(expr.operator, 
                      f"Operator {expr.operator.lexeme} cannot be applied to types {left_type} and {right_type}")
            return BOOLEAN_TYPE  # Return boolean anyway to avoid cascading errors
        
        elif expr.operator.type in [TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL]:
            # Equality operators can be applied to any types
            return BOOLEAN_TYPE
        
        # Default case
        return ANY_TYPE
    
    def visit_unary_expr(self, expr: ast.Unary) -> Type:
        right_type = self.check_expr(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            if right_type in [INT_TYPE, FLOAT_TYPE]:
                return right_type
            self.error(expr.operator, f"Unary minus cannot be applied to type {right_type}")
            return ANY_TYPE
        
        elif expr.operator.type == TokenType.BANG:
            return BOOLEAN_TYPE
        
        return ANY_TYPE
    
    def visit_literal_expr(self, expr: ast.Literal) -> Type:
        if expr.value is None:
            return NIL_TYPE
        elif isinstance(expr.value, bool):
            return BOOLEAN_TYPE
        elif isinstance(expr.value, int):
            return INT_TYPE
        elif isinstance(expr.value, float):
            return FLOAT_TYPE
        elif isinstance(expr.value, str):
            return STRING_TYPE
        
        return ANY_TYPE
    
    def visit_variable_expr(self, expr: ast.Variable) -> Type:
        return self.environment.get(expr.name)
    
    def visit_assign_expr(self, expr: ast.Assign) -> Type:
        value_type = self.check_expr(expr.value)
        var_type = self.environment.get(expr.name)
        
        if var_type != ANY_TYPE and value_type != ANY_TYPE and var_type != value_type:
            self.error(expr.name, f"Cannot assign {value_type} to variable of type {var_type}")
        
        return value_type
    
    def visit_logical_expr(self, expr: ast.Logical) -> Type:
        left_type = self.check_expr(expr.left)
        right_type = self.check_expr(expr.right)
        
        if left_type != BOOLEAN_TYPE and left_type != ANY_TYPE:
            self.error(expr.operator, f"Left operand of logical operator must be boolean, got {left_type}")
        
        if right_type != BOOLEAN_TYPE and right_type != ANY_TYPE:
            self.error(expr.operator, f"Right operand of logical operator must be boolean, got {right_type}")
        
        return BOOLEAN_TYPE
    
    def visit_call_expr(self, expr: ast.Call) -> Type:
        callee_type = self.check_expr(expr.callee)
        
        # Check if callee is a function
        if not isinstance(callee_type, FunctionType):
            if callee_type != ANY_TYPE:  # Skip error for ANY_TYPE to avoid cascading errors
                self.error(expr.paren, f"Can only call functions, got {callee_type}")
            return ANY_TYPE
        
        # Check argument count
        if len(expr.arguments) != len(callee_type.param_types):
            self.error(expr.paren, 
                      f"Expected {len(callee_type.param_types)} arguments but got {len(expr.arguments)}")
        
        # Check argument types
        for i, argument in enumerate(expr.arguments):
            if i < len(callee_type.param_types):
                arg_type = self.check_expr(argument)
                param_type = callee_type.param_types[i]
                
                if param_type != ANY_TYPE and arg_type != ANY_TYPE and param_type != arg_type:
                    self.error(expr.paren, 
                              f"Argument {i+1} type mismatch: expected {param_type}, got {arg_type}")
        
        return callee_type.return_type
    
    def visit_grouping_expr(self, expr: ast.Grouping) -> Type:
        return self.check_expr(expr.expression)
    
    def visit_listliteral(self, expr: ast.ListLiteral) -> Type:
        if not expr.elements:
            # Empty list, assume ANY_TYPE for elements
            return ListType(ANY_TYPE)
        
        # Check all elements and infer element type
        element_types = [self.check_expr(element) for element in expr.elements]
        
        # If all elements have the same type, use that as the list element type
        first_type = element_types[0]
        all_same = all(t == first_type for t in element_types)
        
        if all_same:
            return ListType(first_type)
        else:
            # Mixed types, use ANY_TYPE
            return ListType(ANY_TYPE)