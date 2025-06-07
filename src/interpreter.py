"""
Interpreter for the Demon programming language.
"""

from typing import List, Dict, Optional, Any, Union, Callable, Tuple
import time
from collections import ChainMap

class ContinueError(Exception):
    """Raised when a continue statement is encountered in a loop."""
    pass

class BreakError(Exception):
    """Raised when a break statement is encountered in a loop."""
    pass

class Return(Exception):
    """Raised when a return statement is encountered in a function."""
    def __init__(self, value):
        self.value = value

import demon_ast as ast
from tokens import Token, TokenType


class NativeFunction:
    """Represents a native function in the Demon language."""
    
    def __init__(self, name: str, arity: int, func: Callable):
        self.name = name
        self.arity = arity
        self.func = func
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the native function with the given arguments."""
        if len(arguments) != self.arity:
            raise RuntimeError(None, f"Expected {self.arity} arguments but got {len(arguments)}.")
        return self.func(*arguments)
    
    def arity(self) -> int:
        """Get the number of parameters this function expects."""
        return self.arity
    
    def __str__(self) -> str:
        return f"<native fn {self.name}>"

class RuntimeError(Exception):
    """Runtime error for the Demon interpreter."""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(self.message)

class Return(Exception):
    """Used to return from a function call."""
    def __init__(self, value: Any):
        self.value = value

class Break(Exception):
    """Used to break out of loops."""
    pass

class Continue(Exception):
    """Used to continue to the next iteration of a loop."""
    pass

class Environment:
    """ Environment for variable storage and scoping."""
    
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing
    
    def define(self, name: str, value: Any, mutable: bool = True):
        """Define a new variable in the current scope."""
        self.values[name] = (value, mutable)
    
    def get(self, name: Token) -> Any:
        """Get a variable's value."""
        if name.lexeme in self.values:
            return self.values[name.lexeme][0]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def get_at(self, distance: int, name: str) -> Any:
        """Get a variable at a specific scope depth."""
        return self.ancestor(distance).values.get(name, (None, True))[0]
    
    def assign(self, name: Token, value: Any):
        """Assign a value to a variable."""
        if name.lexeme in self.values:
            if not self.values[name.lexeme][1]:  # Check if mutable
                raise RuntimeError(name, f"Cannot assign to constant '{name.lexeme}'.")
            self.values[name.lexeme] = (value, True)
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign_at(self, distance: int, name: Token, value: Any):
        """Assign a value to a variable at a specific scope depth."""
        self.ancestor(distance).values[name.lexeme] = (value, True)
    
    def ancestor(self, distance: int) -> 'Environment':
        """Get an ancestor environment at the given distance."""
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

class DemonInstance:
    """Instance of a Demon class."""
    
    def __init__(self, klass: 'DemonClass'):
        self.klass = klass
        self.fields = {}
    
    def get(self, name: Token) -> Any:
        """Get a property or method from the instance."""
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        
        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any):
        """Set a property on the instance."""
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"<instance of {self.klass.name}>"

class DemonFunction:
    """Function in the Demon language."""
    
    def __init__(self, declaration: ast.Function, closure: Environment, is_initializer: bool = False, is_static: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
        self.is_static = is_static
    
    def bind(self, instance: 'DemonInstance') -> 'DemonFunction':
        """Bind the function to an instance (for methods)."""
        environment = Environment(self.closure)
        environment.define("this", instance)
        return DemonFunction(self.declaration, environment, self.is_initializer, self.is_static)
    
    def arity(self) -> int:
        """Get the number of parameters."""
        return len(self.declaration.params)
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the function with the given arguments."""
        environment = Environment(self.closure)
        
        for (param, _), arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        
        return None
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

class DemonClass:
    """Class in the Demon language."""
    
    def __init__(self, name: str, superclass: Optional['DemonClass'], methods: Dict[str, 'DemonFunction'], static_methods: Dict[str, 'DemonFunction']):
        self.name = name
        self.superclass = superclass
        self.methods = methods
        self.static_methods = static_methods
    
    def find_method(self, name: str) -> Optional['DemonFunction']:
        """Find a method by name, checking superclasses."""
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)
        
        return None
    
    def find_static_method(self, name: str) -> Optional['DemonFunction']:
        """Find a static method by name."""
        return self.static_methods.get(name)
    
    def arity(self) -> int:
        """Get the arity of the initializer."""
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Create a new instance of the class."""
        instance = DemonInstance(self)
        
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance
    
    def __str__(self) -> str:
        return self.name

class DemonFunction:
    """Function in the Demon language."""
    
    def __init__(self, declaration: ast.Function, closure: Environment, is_initializer: bool = False, is_static: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
        self.is_static = is_static
    
    def bind(self, instance: DemonInstance) -> 'DemonFunction':
        """Bind the function to an instance (for methods)."""
        environment = Environment(self.closure)
        environment.define("this", instance)
        return DemonFunction(self.declaration, environment, self.is_initializer, self.is_static)
    
    def arity(self) -> int:
        """Get the number of parameters."""
        return len(self.declaration.params)
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call the function with the given arguments."""
        environment = Environment(self.closure)
        
        for (param, _), arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        
        return None
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

class Interpreter(ast.Visitor):
    """Interpreter for the Demon programming language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        
        # Add native functions
        self.globals.define("clock", NativeFunction("clock", 0, lambda *args: time.time()))
    
    def interpret(self, statements: List[ast.Stmt]):
        """Interpret a list of statements."""
        if not statements:
            return
            
        for statement in statements:
            if statement is None:
                continue
                
            try:
                self.execute(statement)
            except RuntimeError as e:
                if hasattr(e, 'token') and hasattr(e.token, 'line'):
                    print(f"[line {e.token.line}] {str(e)}")
                else:
                    print(f"Runtime error: {str(e)}")
                self.demon.had_error = True
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                self.demon.had_error = True
    
    def resolve(self, expr: ast.Expr, depth: int):
        """Resolve a variable's scope depth."""
        self.locals[id(expr)] = depth
    
    def execute(self, stmt: ast.Stmt):
        """Execute a statement."""
        return self.visit_stmt(stmt)
    
    def execute_block(self, statements: List[ast.Stmt], environment: Environment):
        """Execute a block of statements in a new environment."""
        previous = self.environment
        
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def evaluate(self, expr: ast.Expr) -> Any:
        """Evaluate an expression."""
        return self.visit_expr(expr)
    
    def lookup_variable(self, name: Token, expr: ast.Expr) -> Any:
        """Look up a variable in the appropriate scope."""
        distance = self.locals.get(id(expr))
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    # Statement visitors
    def visit_expression_stmt(self, stmt: ast.Expression):
        self.evaluate(stmt.expression)
        
    def visit_print(self, stmt: ast.Print) -> None:
        """Visit a print statement."""
        output = []
        for expr in stmt.expressions:
            value = self.evaluate(expr)
            if isinstance(value, list):
                output.append('[' + ', '.join(self.stringify(v) for v in value) + ']')
            else:
                output.append(self.stringify(value))
        print(' '.join(output))
        return None
        
    def visit_grouping(self, expr: ast.Grouping):
        return self.evaluate(expr.expression)
        
    def visit_literal(self, expr: ast.Literal):
        return expr.value
        
    def visit_listliteral(self, expr: ast.ListLiteral):
        return [self.evaluate(element) for element in expr.elements]
        
    def visit_var(self, stmt: ast.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)
        
    def visit_binary(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeError(expr.operator, "Division by zero.")
            return left / right
        elif expr.operator.type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return left > right
        elif expr.operator.type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right
        elif expr.operator.type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right
        elif expr.operator.type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right
        elif expr.operator.type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        elif expr.operator.type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
            
        # Unreachable
        return None
        
    def visit_if(self, stmt: ast.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
            
    def visit_function(self, stmt: ast.Function):
        function = DemonFunction(stmt, self.environment, False)
        if hasattr(stmt, 'name') and stmt.name is not None:
            self.environment.define(stmt.name.lexeme, function)
        return function
        
    def visit_call(self, expr: ast.Call):
        callee = self.evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        # Handle native functions
        if hasattr(callee, '__call__') and not hasattr(callee, 'call'):
            try:
                return callee(*arguments)
            except Exception as e:
                raise RuntimeError(expr.paren, f"Error calling native function: {str(e)}")
        
        # Handle Demon functions and methods
        if hasattr(callee, 'call'):
            if hasattr(callee, 'arity') and callee.arity() != len(arguments):
                raise RuntimeError(expr.paren, 
                                f"Expected {callee.arity()} arguments but got {len(arguments)}.")
            
            try:
                return callee.call(self, arguments)
            except Return as return_value:
                return return_value
            except Exception as e:
                raise RuntimeError(expr.paren, f"Error calling function: {str(e)}")
        
        raise RuntimeError(expr.paren, "Can only call functions and classes.")
            
    def visit_block(self, stmt: ast.Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        
    def visit_while(self, stmt: ast.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
            
    def visit_foreach(self, stmt: ast.ForEach):
        # Evaluate the iterable
        iterable = self.evaluate(stmt.iterable)
        
        if not isinstance(iterable, (list, tuple, range)):
            raise RuntimeError(None, "Can only iterate over lists, tuples, or ranges")
        
        # For each item in the iterable
        for item in iterable:
            # Create a new scope for the loop variable
            previous_env = self.environment
            self.environment = Environment(previous_env)
            
            # Define the loop variable
            if isinstance(stmt.variable, ast.Var):
                self.environment.define(stmt.variable.name.lexeme, item)
            elif isinstance(stmt.variable, ast.Variable):
                self.environment.define(stmt.variable.name.lexeme, item)
            
            try:
                # Execute the loop body
                self.execute(stmt.body)
            except ContinueError:
                pass  # Continue with the next iteration
            except BreakError:
                break  # Exit the loop
            finally:
                # Restore the previous environment
                self.environment = previous_env
            
    def visit_variable(self, expr: ast.Variable):
        return self.lookup_variable(expr.name, expr)
        
    def visit_expression(self, stmt: ast.Expression):
        return self.evaluate(stmt.expression)
        
    def visit_assign(self, expr: ast.Assign):
        value = self.evaluate(expr.value)
        distance = self.locals.get(id(expr))
        
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
            
        return value
        
    def visit_return(self, stmt: ast.Return):
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        else:
            value = None
        raise Return(value)
    
    def visit_var_stmt(self, stmt: ast.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value, not stmt.is_const)
        return None
    
    def visit_block_stmt(self, stmt: ast.Block):
        self.execute_block(stmt.statements, Environment(self.environment))
        return None
    
    def visit_if_stmt(self, stmt: ast.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None
    
    def visit_while_stmt(self, stmt: ast.While):
        try:
            while self.is_truthy(self.evaluate(stmt.condition)):
                try:
                    self.execute(stmt.body)
                except Continue:
                    continue
        except Break:
            pass
        
        return None
    
    def visit_foreach_stmt(self, stmt: ast.ForEach):
        iterable = self.evaluate(stmt.iterable)
        
        if not hasattr(iterable, '__iter__'):
            raise RuntimeError(stmt.variable.name, "Can only iterate over iterable types.")
        
        try:
            for item in iterable:
                try:
                    # Set the loop variable
                    if isinstance(stmt.variable, ast.Var):
                        self.environment.define(stmt.variable.name.lexeme, item, not stmt.variable.is_const)
                    else:
                        self.environment.define(stmt.variable.name.lexeme, item)
                    
                    # Execute the loop body
                    self.execute(stmt.body)
                except Continue:
                    continue
                except Break:
                    break
        except RuntimeError as e:
            raise RuntimeError(stmt.variable.name, str(e))
        
        return None
    
    def visit_function_stmt(self, stmt: ast.Function):
        function = DemonFunction(stmt, self.environment, stmt.name.lexeme == "init")
        self.environment.define(stmt.name.lexeme, function)
        return None
    
    def visit_return_stmt(self, stmt: ast.Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        raise Return(value)
    
    def visit_break_stmt(self, stmt: ast.Break):
        raise Break()
    
    def visit_continue_stmt(self, stmt: ast.Continue):
        raise Continue()
    
    def visit_class_stmt(self, stmt: ast.Class):
        # Handle inheritance
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, DemonClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")
        
        # Define the class in the current environment
        self.environment.define(stmt.name.lexeme, None)
        
        # Create a new environment for 'super'
        if superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        
        # Define methods
        methods = {}
        for method in stmt.methods:
            function = DemonFunction(
                method, 
                self.environment, 
                method.name.lexeme == "init",
                False
            )
            methods[method.name.lexeme] = function
        
        # Define static methods
        static_methods = {}
        for method in stmt.static_methods:
            function = DemonFunction(
                method,
                self.environment,
                False,
                True
            )
            static_methods[method.name.lexeme] = function
        
        klass = DemonClass(stmt.name.lexeme, superclass, methods, static_methods)
        
        # Restore the environment
        if superclass is not None:
            self.environment = self.environment.enclosing
        
        # Assign the class to its name
        self.environment.assign(stmt.name, klass)
        return None
    
    # Expression visitors
    def visit_literal_expr(self, expr: ast.Literal):
        return expr.value
    
    def visit_variable_expr(self, expr: ast.Variable):
        return self.lookup_variable(expr.name, expr)
    
    def visit_assign_expr(self, expr: ast.Assign):
        value = self.evaluate(expr.value)
        
        distance = self.locals.get(id(expr))
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        
        return value
    
    def visit_binary_expr(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        operator_type = expr.operator.type
        
        if operator_type == TokenType.PLUS:
            if isinstance(left, (str, str)) and isinstance(right, (str, str)):
                return str(left) + str(right)
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        
        if operator_type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        
        if operator_type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
        
        if operator_type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeError(expr.operator, "Division by zero.")
            return left / right
        
        if operator_type == TokenType.PERCENT:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeError(expr.operator, "Modulo by zero.")
            return left % right
        
        if operator_type == TokenType.GREATER:
            self.check_number_operands(expr.operator, left, right)
            return left > right
        
        if operator_type == TokenType.GREATER_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left >= right
        
        if operator_type == TokenType.LESS:
            self.check_number_operands(expr.operator, left, right)
            return left < right
        
        if operator_type == TokenType.LESS_EQUAL:
            self.check_number_operands(expr.operator, left, right)
            return left <= right
        
        if operator_type == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        
        if operator_type == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        
        # Unreachable
        return None
    
    def visit_unary_expr(self, expr: ast.Unary):
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        
        if expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        
        # Unreachable
        return None
    
    def visit_logical_expr(self, expr: ast.Logical):
        left = self.evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    def visit_grouping_expr(self, expr: ast.Grouping):
        return self.evaluate(expr.expression)
    
    def visit_call_expr(self, expr: ast.Call):
        callee = self.evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        
        if not callable(callee):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")
        
        if len(arguments) != callee.arity() if hasattr(callee, 'arity') else 0:
            raise RuntimeError(
                expr.paren, 
                f"Expected {callee.arity()} arguments but got {len(arguments)}."
            )
        
        return callee.call(self, arguments)
    
    def visit_get_expr(self, expr: ast.Get):
        obj = self.evaluate(expr.obj)
        
        if isinstance(obj, DemonInstance):
            return obj.get(expr.name)
        
        raise RuntimeError(expr.name, "Only instances have properties.")
    
    def visit_set_expr(self, expr: ast.Set):
        obj = self.evaluate(expr.obj)
        
        if not isinstance(obj, DemonInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")
        
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value
    
    def visit_this_expr(self, expr: ast.This):
        return self.lookup_variable(expr.keyword, expr)
    
    def visit_super_expr(self, expr: ast.Super):
        distance = self.locals.get(id(expr))
        superclass = self.environment.get_at(distance, "super")
        
        # 'this' is always one scope closer than 'super'
        obj = self.environment.get_at(distance - 1, "this")
        
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")
        
        return method.bind(obj)
    
    def visit_lambda_expr(self, expr: ast.Lambda):
        return DemonFunction(expr, self.environment)
    
    def visit_match_expr(self, expr: ast.Match):
        value = self.evaluate(expr.value)
        
        # Check each case
        for pattern, body in expr.cases:
            if pattern is None:  # Default case (should be last)
                continue
                
            if self.matches_pattern(value, pattern):
                try:
                    return self.execute_block(body, Environment(self.environment))
                except Return as ret:
                    return ret.value
        
        # Check for default case
        if expr.default is not None:
            try:
                return self.execute_block(expr.default, Environment(self.environment))
            except Return as ret:
                return ret.value
        
        return None
    
    def visit_pipeline_expr(self, expr: ast.Pipeline):
        left = self.evaluate(expr.left)
        
        if expr.operator.type == TokenType.PIPE_GT:
            # Pipe operator: left |> right
            if not isinstance(expr.right, ast.Call):
                raise RuntimeError(expr.operator, "Right side of |> must be a function call.")
            
            # Replace the first argument with the left value
            if not expr.right.arguments:
                expr.right.arguments = [ast.Literal(left)]
            else:
                expr.right.arguments.insert(0, ast.Literal(left))
            
            return self.evaluate(expr.right)
        
        # Other pipeline operators can be added here
        
        return None
    
    def visit_range_expr(self, expr: ast.Range):
        start = self.evaluate(expr.start)
        end = self.evaluate(expr.end)
        
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise RuntimeError(None, "Range bounds must be numbers.")
        
        # In a real implementation, we'd return a range object
        # For simplicity, we'll return a tuple
        return (start, end, expr.inclusive)
    
    def visit_listliteral(self, expr: ast.ListLiteral):
        return [self.evaluate(element) for element in expr.elements]
    
    def visit_map_literal_expr(self, expr: ast.MapLiteral):
        return {key.lexeme: self.evaluate(value) for key, value in expr.entries}
    
    def visit_block_expr(self, expr: ast.BlockExpr):
        result = None
        for stmt in expr.statements:
            result = self.execute(stmt)
        return result
    
    # Helper methods
    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, (int, float)):
            return
        raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(operator, "Operands must be numbers.")
    
    def is_truthy(self, obj: Any) -> bool:
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True
    
    def is_equal(self, a: Any, b: Any) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b
    
    def stringify(self, obj: Any) -> str:
        if obj is None:
            return "nil"
        if isinstance(obj, bool):
            return str(obj).lower()
        if isinstance(obj, (int, float)):
            text = str(obj)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        if isinstance(obj, list):
            return "[" + ", ".join(self.stringify(v) for v in obj) + "]"
        return str(obj)
    
    def matches_pattern(self, value: Any, pattern: ast.Expr) -> bool:
        """Check if a value matches a pattern."""
        if isinstance(pattern, ast.Literal):
            return value == pattern.value
        
        if isinstance(pattern, ast.Variable):
            # In a real implementation, we'd bind the variable here
            return True
        
        if isinstance(pattern, ast.ListLiteral):
            if not isinstance(value, list):
                return False
            
            if len(pattern.elements) != len(value):
                return False
            
            for pat, val in zip(pattern.elements, value):
                if not self.matches_pattern(val, pat):
                    return False
            
            return True
        
        # Add more pattern matching cases as needed
        
        # Default to equality comparison
        return value == self.evaluate(pattern)
