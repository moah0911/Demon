"""
Interpreter for the Demon programming language.
"""

import time
import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
from .tokens import Token, TokenType
from . import ast
from .subscript_expr import SubscriptExpr
from .static_methods import patch_interpreter
from .exceptions import DemonException, convert_python_exception

# Import standard library features
try:
    from ..stdlib.pattern_matching import match_value, create_pattern
    from ..stdlib.reactive import signal, computed, effect, ReactiveDict, ReactiveList
    from ..stdlib.dataflow import create_graph, create_pipeline
    from ..stdlib.contextual import create_context, with_context
    from ..stdlib.memoize import memoize, lru_cache, ttl_cache
    STDLIB_LOADED = True
except ImportError:
    STDLIB_LOADED = False

class RuntimeError(Exception):
    """Runtime error in the Demon language."""
    
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        self.line = token.line if token else 0
        super().__init__(message)

class ExceptionThrown(Exception):
    """Exception thrown by the user code."""
    
    def __init__(self, exception: DemonException):
        self.exception = exception
        super().__init__(str(exception))

class Return(Exception):
    """Return statement exception."""
    
    def __init__(self, value: Any):
        self.value = value
        super().__init__()

class Break(Exception):
    """Break statement exception."""
    pass

class Continue(Exception):
    """Continue statement exception."""
    pass

class Environment:
    """Environment for storing variables."""
    
    def __init__(self, enclosing=None):
        self.values: Dict[str, Tuple[Any, bool]] = {}  # (value, is_const)
        self.enclosing = enclosing
    
    def define(self, name: str, value: Any, is_const: bool = False):
        """Define a variable."""
        self.values[name] = (value, is_const)
    
    def get(self, name: Token) -> Any:
        """Get a variable's value."""
        if name.lexeme in self.values:
            return self.values[name.lexeme][0]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def assign(self, name: Token, value: Any):
        """Assign a value to a variable."""
        if name.lexeme in self.values:
            if self.values[name.lexeme][1]:  # is_const
                raise RuntimeError(name, f"Cannot reassign to constant '{name.lexeme}'.")
            self.values[name.lexeme] = (value, self.values[name.lexeme][1])
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise RuntimeError(name, f"Undefined variable '{name.lexeme}'.")
    
    def get_at(self, distance: int, name: str) -> Any:
        """Get a variable at a specific environment distance."""
        return self.ancestor(distance).values.get(name, (None, False))[0]
    
    def assign_at(self, distance: int, name: Token, value: Any):
        """Assign a value to a variable at a specific environment distance."""
        ancestor = self.ancestor(distance)
        if ancestor.values[name.lexeme][1]:  # is_const
            raise RuntimeError(name, f"Cannot reassign to constant '{name.lexeme}'.")
        ancestor.values[name.lexeme] = (value, ancestor.values[name.lexeme][1])
    
    def ancestor(self, distance: int) -> 'Environment':
        """Get an ancestor environment at a specific distance."""
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

class DemonCallable:
    """Base class for callable objects in Demon."""
    
    def arity(self) -> int:
        """Return the number of arguments this callable expects."""
        raise NotImplementedError()
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        """Call this callable with the given arguments."""
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return "<callable>"

class DemonFunction(DemonCallable):
    """Function object in Demon."""
    
    def __init__(self, declaration: ast.Function, closure: Environment, is_initializer: bool = False):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        for i, (param, _) in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        # Execute function body
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return return_value.value
        
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None
    
    def bind(self, instance: 'DemonInstance') -> 'DemonFunction':
        """Bind this function to an instance."""
        environment = Environment(self.closure)
        environment.define("this", instance)
        return DemonFunction(self.declaration, environment, self.is_initializer)
    
    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

class DemonLambda(DemonCallable):
    """Lambda function object in Demon."""
    
    def __init__(self, declaration: ast.Lambda, closure: Environment):
        self.declaration = declaration
        self.closure = closure
    
    def arity(self) -> int:
        return len(self.declaration.params)
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        for i, (param, _) in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])
        
        # Execute function body
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value
        
        return None
    
    def __str__(self) -> str:
        return "<lambda>"

class NativeFunction(DemonCallable):
    """Native function in Demon."""
    
    def __init__(self, name: str, arity_count: int, function):
        self.name = name
        self.arity_count = arity_count
        self.function = function
    
    def arity(self) -> int:
        return self.arity_count
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        return self.function(*arguments)
    
    def __str__(self) -> str:
        return f"<native fn {self.name}>"

class DemonClass(DemonCallable):
    """Class object in Demon."""
    
    def __init__(self, name: str, superclass: Optional['DemonClass'], methods: Dict[str, DemonFunction], static_methods: Dict[str, DemonFunction]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
        self.static_methods = static_methods
    
    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()
    
    def call(self, interpreter: 'Interpreter', arguments: List[Any]) -> Any:
        instance = DemonInstance(self)
        
        # Call initializer if it exists
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        
        return instance
    
    def find_method(self, name: str) -> Optional[DemonFunction]:
        """Find a method in this class or its superclass."""
        if name in self.methods:
            return self.methods[name]
        
        if self.superclass is not None:
            return self.superclass.find_method(name)
        
        return None
    
    def get_static_method(self, name: str) -> Optional[DemonFunction]:
        """Get a static method from this class."""
        if name in self.static_methods:
            return self.static_methods[name]
        
        if self.superclass is not None:
            return self.superclass.get_static_method(name)
        
        return None
    
    def __str__(self) -> str:
        return f"<class {self.name}>"

class DemonInstance:
    """Instance of a class in Demon."""
    
    def __init__(self, klass: DemonClass):
        self.klass = klass
        self.fields: Dict[str, Any] = {}
    
    def get(self, name: Token) -> Any:
        """Get a property or method from this instance."""
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        
        # Check if the object has a get_field method (for reactive objects)
        if hasattr(self, "get_field"):
            try:
                return self.get_field(name.lexeme)
            except AttributeError:
                pass
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        
        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any):
        """Set a property on this instance."""
        # Check if the object has a set_field method (for reactive objects)
        if hasattr(self, "set_field"):
            try:
                self.set_field(name.lexeme, value)
                return
            except AttributeError:
                pass
        
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"<{self.klass.name} instance>"

class Interpreter(ast.Visitor):
    """Interpreter for the Demon language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.globals = Environment(None)
        self.environment = self.globals
        self.locals = {}
        self.NativeFunction = NativeFunction
        
        # Add native functions
        self.globals.define("clock", NativeFunction("clock", 0, lambda *args: time.time()))
        
        # Register standard library functions
        try:
            # Add the project root to the Python path
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            from src.stdlib.stdlib import DemonStdLib
            DemonStdLib.register_all(self)
            
            # Register unique features if stdlib is loaded
            if STDLIB_LOADED:
                # Import the reactive bridge and error handler
                from ..stdlib.reactive_bridge import demon_computed, demon_effect, create_reactive_bridge
                from ..stdlib.reactive_error_handler import enable_debug_mode, disable_debug_mode, on_reactive_error
                
                # Create a reactive bridge with proper error handling
                reactive_bridge = create_reactive_bridge(self)
                
                # Register reactive programming functions
                self.globals.define("signal", NativeFunction("signal", 1, reactive_bridge["signal"]))
                self.globals.define("computed", NativeFunction("computed", 1, reactive_bridge["computed"]))
                self.globals.define("effect", NativeFunction("effect", 1, reactive_bridge["effect"]))
                
                # Register reactive debugging functions
                self.globals.define("enable_reactive_debug", NativeFunction("enable_reactive_debug", 0, enable_debug_mode))
                self.globals.define("disable_reactive_debug", NativeFunction("disable_reactive_debug", 0, disable_debug_mode))
                self.globals.define("on_reactive_error", NativeFunction("on_reactive_error", 1, 
                                                                      lambda fn: on_reactive_error(reactive_bridge["computed"](fn))))
                
                # Register other advanced features
                self.globals.define("create_graph", NativeFunction("create_graph", 0, create_graph))
                self.globals.define("create_pipeline", NativeFunction("create_pipeline", 0, create_pipeline))
                self.globals.define("create_context", NativeFunction("create_context", 1, create_context))
                self.globals.define("with_context", NativeFunction("with_context", 3, with_context))
                self.globals.define("memoize", NativeFunction("memoize", 1, memoize))
                self.globals.define("lru_cache", NativeFunction("lru_cache", 1, lru_cache))
                self.globals.define("ttl_cache", NativeFunction("ttl_cache", 1, ttl_cache))
                
                # Add reactive collections with improved implementations
                self.globals.define("reactive_dict", NativeFunction("reactive_dict", 1, lambda init=None: ReactiveDict(init or {})))
                self.globals.define("reactive_list", NativeFunction("reactive_list", 1, lambda init=None: ReactiveList(init or [])))
        except ImportError as e:
            print(f"Error importing standard library: {e}")
            # Fallback to basic functions if stdlib is not available
            self.globals.define("print", NativeFunction("print", -1, lambda *args: print(*args)))
            self.globals.define("input", NativeFunction("input", 1, lambda prompt="": input(prompt)))
            self.globals.define("len", NativeFunction("len", 1, lambda obj: len(obj)))
    
    def interpret(self, statements: List[ast.Stmt]):
        """Interpret a list of statements."""
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            self.demon.runtime_error(error)
    
    def execute(self, stmt: ast.Stmt):
        """Execute a statement."""
        return stmt.accept(self)
    
    def resolve(self, expr: ast.Expr, depth: int):
        """Resolve a variable reference."""
        self.locals[expr] = depth
    
    def evaluate(self, expr: ast.Expr) -> Any:
        """Evaluate an expression."""
        return expr.accept(self)
    
    def execute_block(self, statements: List[ast.Stmt], environment: Environment):
        """Execute a block of statements in the given environment."""
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def visit_block_stmt(self, stmt: ast.Block):
        self.execute_block(stmt.statements, Environment(self.environment))
    
    def visit_expression_stmt(self, stmt: ast.Expression):
        self.evaluate(stmt.expression)
    
    def visit_function_stmt(self, stmt: ast.Function):
        function = DemonFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)
    
    def visit_if_stmt(self, stmt: ast.If):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
    
    def visit_print_stmt(self, stmt: ast.Print):
        values = [self.evaluate(expr) for expr in stmt.expressions]
        print(*values)
    
    def visit_return_stmt(self, stmt: ast.Return):
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        
        raise Return(value)
    
    def visit_break_stmt(self, stmt: ast.Break):
        raise Break()
    
    def visit_continue_stmt(self, stmt: ast.Continue):
        raise Continue()
        
    def visit_try_stmt(self, stmt: ast.Try):
        # Execute try block
        try:
            self.execute(stmt.try_block)
        except ExceptionThrown as thrown:
            # Handle caught exception
            exception = thrown.exception
            handled = False
            # Handle caught exception
            exception = thrown.exception
            handled = False
            
            # Check each catch clause
            for exception_type, exception_var, catch_block in stmt.catch_clauses:
                # If no exception type specified, catch all exceptions
                if exception_type is None:
                    handled = True
                # Otherwise, check if the exception matches the specified type
                elif exception_type.lexeme == exception.__class__.__name__:
                    handled = True
                
                if handled:
                    # Create a new environment for the catch block
                    environment = Environment(self.environment)
                    
                    # Bind exception to variable if specified
                    if exception_var is not None:
                        environment.define(exception_var.name.lexeme, exception)
                    else:
                        # Always bind to 'e' for convenience
                        environment.define("e", exception)
                    
                    # Execute catch block in the new environment
                    previous = self.environment
                    try:
                        self.environment = environment
                        self.execute(catch_block)
                    finally:
                        self.environment = previous
                    break
            
            # If no catch clause handled the exception and there's no finally block,
            # re-throw the exception
            if not handled and stmt.finally_block is None:
                raise thrown
        finally:
            # Execute finally block if present
            if stmt.finally_block is not None:
                self.execute(stmt.finally_block)
    
    def visit_var_stmt(self, stmt: ast.Var):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value, stmt.is_const)
    
    def visit_while_stmt(self, stmt: ast.While):
        while self.is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except Break:
                break
            except Continue:
                continue
                
    def visit_for_stmt(self, stmt: ast.For):
        # Execute initializer once
        if stmt.initializer:
            self.execute(stmt.initializer)
            
        while True:
            # Check condition
            if stmt.condition and not self.is_truthy(self.evaluate(stmt.condition)):
                break
                
            try:
                # Execute body
                self.execute(stmt.body)
            except Break:
                break
            except Continue:
                # When continue is encountered, skip to the increment
                if stmt.increment:
                    self.evaluate(stmt.increment)
                continue
                
            # Execute increment
            if stmt.increment:
                self.evaluate(stmt.increment)
    
    def visit_foreach_stmt(self, stmt: ast.ForEach):
        iterable = self.evaluate(stmt.iterable)
        
        if not hasattr(iterable, "__iter__"):
            raise RuntimeError(stmt.iterable, "Object is not iterable.")
        
        for item in iterable:
            try:
                # Create a new environment for each iteration
                environment = Environment(self.environment)
                
                if isinstance(stmt.variable, ast.Var):
                    environment.define(stmt.variable.name.lexeme, item, stmt.variable.is_const)
                else:  # Variable
                    environment.define(stmt.variable.name.lexeme, item)
                
                # Execute the body in the new environment
                previous = self.environment
                try:
                    self.environment = environment
                    self.execute(stmt.body)
                finally:
                    self.environment = previous
            except Break:
                break
            except Continue:
                continue
    
    def visit_class_stmt(self, stmt: ast.Class):
        # Evaluate superclass if present
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, DemonClass):
                raise RuntimeError(stmt.superclass.name, "Superclass must be a class.")
        
        # Define the class in the current environment
        self.environment.define(stmt.name.lexeme, None)
        
        # Create environment for methods
        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        
        # Define methods
        methods = {}
        for method in stmt.methods:
            function = DemonFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        
        # Define static methods
        static_methods = {}
        for method in stmt.static_methods:
            function = DemonFunction(method, self.environment)
            static_methods[method.name.lexeme] = function
        
        # Create class
        klass = DemonClass(stmt.name.lexeme, superclass, methods, static_methods)
        
        # Restore environment
        if stmt.superclass is not None:
            self.environment = self.environment.enclosing
        
        # Update class definition
        self.environment.assign(stmt.name, klass)
    
    def visit_assign_expr(self, expr: ast.Assign):
        value = self.evaluate(expr.value)
        
        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        
        return value
    
    def visit_binary_expr(self, expr: ast.Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        elif expr.operator.type == TokenType.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                exception = DemonException("Division by zero.", expr.operator)
                raise ExceptionThrown(exception)
            return left / right
        elif expr.operator.type == TokenType.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left * right
        elif expr.operator.type == TokenType.PLUS:
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, str) and isinstance(right, (int, float)):
                return left + str(right)
            if isinstance(left, (int, float)) and isinstance(right, str):
                return str(left) + right
            raise RuntimeError(expr.operator, "Operands must be two numbers or two strings.")
        elif expr.operator.type == TokenType.PERCENT:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeError(expr.operator, "Modulo by zero.")
            return left % right
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
    
    def visit_call_expr(self, expr: ast.Call):
        callee = self.evaluate(expr.callee)
        
        arguments = [self.evaluate(argument) for argument in expr.arguments]
        
        if not isinstance(callee, DemonCallable):
            raise RuntimeError(expr.paren, "Can only call functions and classes.")
        
        if callee.arity() != -1 and len(arguments) != callee.arity():
            raise RuntimeError(expr.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        
        return callee.call(self, arguments)
    
    def visit_get_expr(self, expr: ast.Get):
        obj = self.evaluate(expr.obj)
        
        if isinstance(obj, DemonInstance):
            return obj.get(expr.name)
        
        # Check for reactive objects with get_field method
        if hasattr(obj, "get_field"):
            try:
                return obj.get_field(expr.name.lexeme)
            except AttributeError:
                pass
        
        if isinstance(obj, dict):
            if expr.name.lexeme in obj:
                return obj[expr.name.lexeme]
            # For dictionary access, return None for undefined properties
            return None
        
        if isinstance(obj, list):
            if expr.name.lexeme == "length":
                return len(obj)
            
            # Support indexing with a property name that's a number
            try:
                index = int(expr.name.lexeme)
                if 0 <= index < len(obj):
                    return obj[index]
                else:
                    raise RuntimeError(expr.name, f"Index {index} out of bounds for list of length {len(obj)}.")
            except ValueError:
                pass
            
            # Check for list methods
            if expr.name.lexeme in ["append", "pop", "insert", "remove", "index", "count"]:
                if expr.name.lexeme == "append":
                    # Create a callable that will append an item to the list
                    return NativeFunction("append", 1, lambda x: obj.append(x) or obj)
                elif expr.name.lexeme == "pop":
                    # Create a callable that will pop an item from the list
                    return NativeFunction("pop", -1, lambda idx=-1: obj.pop(idx))
                elif expr.name.lexeme == "insert":
                    # Create a callable that will insert an item into the list
                    return NativeFunction("insert", 2, lambda idx, x: obj.insert(idx, x) or obj)
                elif expr.name.lexeme == "remove":
                    # Create a callable that will remove an item from the list
                    return NativeFunction("remove", 1, lambda x: obj.remove(x) or obj)
                elif expr.name.lexeme == "index":
                    # Create a callable that will return the index of an item in the list
                    return NativeFunction("index", 1, lambda x: obj.index(x))
                elif expr.name.lexeme == "count":
                    # Create a callable that will count occurrences of an item in the list
                    return NativeFunction("count", 1, lambda x: obj.count(x))
        
        if isinstance(obj, str):
            if expr.name.lexeme == "length":
                return len(obj)
            
            # Check for string methods
            if expr.name.lexeme in ["upper", "lower", "trim", "split", "replace"]:
                if expr.name.lexeme == "upper":
                    return lambda: obj.upper()
                elif expr.name.lexeme == "lower":
                    return lambda: obj.lower()
                elif expr.name.lexeme == "trim":
                    return lambda: obj.strip()
                elif expr.name.lexeme == "split":
                    return lambda sep=" ": obj.split(sep)
                elif expr.name.lexeme == "replace":
                    return lambda old, new: obj.replace(old, new)
        
        # Check if the object has the method as an attribute
        if hasattr(obj, expr.name.lexeme):
            attr = getattr(obj, expr.name.lexeme)
            if callable(attr):
                return attr
            return attr
        
        raise RuntimeError(expr.name, "Only instances have properties.")
    
    def visit_set_expr(self, expr: ast.Set):
        obj = self.evaluate(expr.obj)
        value = self.evaluate(expr.value)
        
        if isinstance(obj, DemonInstance):
            obj.set(expr.name, value)
            return value
        
        # Check for reactive objects with set_field method
        if hasattr(obj, "set_field"):
            try:
                obj.set_field(expr.name.lexeme, value)
                return value
            except AttributeError:
                pass
        
        if isinstance(obj, dict):
            obj[expr.name.lexeme] = value
            return value
        
        raise RuntimeError(expr.name, "Only instances have fields.")
    
    def visit_super_expr(self, expr: ast.Super):
        distance = self.locals.get(expr)
        superclass = self.environment.get_at(distance, "super")
        
        # "this" is always one level nearer than "super"
        instance = self.environment.get_at(distance - 1, "this")
        
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise RuntimeError(expr.method, f"Undefined property '{expr.method.lexeme}'.")
        
        return method.bind(instance)
    
    def visit_this_expr(self, expr: ast.This):
        return self.look_up_variable(expr.keyword, expr)
    
    def visit_grouping_expr(self, expr: ast.Grouping):
        return self.evaluate(expr.expression)
    
    def visit_literal_expr(self, expr: ast.Literal):
        return expr.value
    
    def visit_logical_expr(self, expr: ast.Logical):
        left = self.evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:  # AND
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expr.right)
    
    def visit_unary_expr(self, expr: ast.Unary):
        right = self.evaluate(expr.right)
        
        if expr.operator.type == TokenType.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        elif expr.operator.type == TokenType.BANG:
            return not self.is_truthy(right)
        
        # Unreachable
        return None
    
    def visit_variable_expr(self, expr: ast.Variable):
        return self.look_up_variable(expr.name, expr)
    
    def visit_lambda_expr(self, expr: ast.Lambda):
        return DemonLambda(expr, self.environment)
    
    def visit_listliteral_expr(self, expr: ast.ListLiteral):
        elements = [self.evaluate(element) for element in expr.elements]
        return elements
    
    def visit_mapliteral_expr(self, expr: ast.MapLiteral):
        result = {}
        for key, value in expr.entries:
            result[key.lexeme] = self.evaluate(value)
        return result
    
    def visit_range_expr(self, expr: ast.Range):
        start = self.evaluate(expr.start)
        end = self.evaluate(expr.end)
        
        if not isinstance(start, int) or not isinstance(end, int):
            raise RuntimeError(expr.start.operator if hasattr(expr.start, 'operator') else expr.start.name, 
                              "Range bounds must be integers.")
        
        if expr.inclusive:
            return list(range(start, end + 1))
        return list(range(start, end))
    
    def visit_match_expr(self, expr: ast.Match):
        value = self.evaluate(expr.value)
        
        for case_value, case_body in expr.cases:
            case_result = self.evaluate(case_value)
            if self.is_equal(value, case_result):
                environment = Environment(self.environment)
                result = None
                for stmt in case_body:
                    result = self.execute(stmt)
                return result
        
        if expr.default is not None:
            environment = Environment(self.environment)
            result = None
            for stmt in expr.default:
                result = self.execute(stmt)
            return result
        
        return None
    
    def visit_pipeline_expr(self, expr: ast.Pipeline):
        left = self.evaluate(expr.left)
        
        # Evaluate right side as a function and call it with left as argument
        right = self.evaluate(expr.right)
        
        if not isinstance(right, DemonCallable):
            raise RuntimeError(expr.operator, "Right side of pipeline must be callable.")
        
        return right.call(self, [left])
    
    def visit_blockexpr_expr(self, expr: ast.BlockExpr):
        environment = Environment(self.environment)
        previous = self.environment
        result = None
        
        try:
            self.environment = environment
            
            for statement in expr.statements:
                result = self.execute(statement)
        finally:
            self.environment = previous
        
        return result
        
    def visit_subscript_expr(self, expr: SubscriptExpr):
        """Evaluate a subscript expression (array indexing)."""
        obj = self.evaluate(expr.obj)
        index = self.evaluate(expr.index)
        
        # Handle list/array indexing
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise RuntimeError(None, f"Array index must be an integer, got {type(index).__name__}")
            
            if index < 0 or index >= len(obj):
                raise RuntimeError(None, f"Array index out of bounds: {index} (array length: {len(obj)})")
                
            return obj[index]
            
        # Handle string indexing
        elif isinstance(obj, str):
            if not isinstance(index, int):
                raise RuntimeError(None, f"String index must be an integer, got {type(index).__name__}")
                
            if index < 0 or index >= len(obj):
                raise RuntimeError(None, f"String index out of bounds: {index} (string length: {len(obj)})")
                
            return obj[index]
            
        # Handle dictionary access
        elif isinstance(obj, dict):
            # For dictionaries, we want to allow accessing keys that don't exist yet
            # This is common in many languages and makes dictionary usage more flexible
            return obj.get(index, None)
            
        else:
            raise RuntimeError(None, f"Cannot use subscript operator on type {type(obj).__name__}")
            
    def visit_subscript_assign_expr(self, expr):
        """Evaluate a subscript assignment expression (array[index] = value)."""
        obj = self.evaluate(expr.obj)
        index = self.evaluate(expr.index)
        value = self.evaluate(expr.value)
        
        # Handle list/array assignment
        if isinstance(obj, list):
            if not isinstance(index, int):
                raise RuntimeError(None, f"Array index must be an integer, got {type(index).__name__}")
            
            if index < 0 or index >= len(obj):
                raise RuntimeError(None, f"Array index out of bounds: {index} (array length: {len(obj)})")
                
            obj[index] = value
            return value
            
        # Handle dictionary assignment
        elif isinstance(obj, dict):
            obj[index] = value
            return value
            
        else:
            raise RuntimeError(None, f"Cannot assign to subscript of type {type(obj).__name__}")
    
    def look_up_variable(self, name: Token, expr: ast.Expr) -> Any:
        """Look up a variable in the appropriate environment."""
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)
    
    def is_truthy(self, value: Any) -> bool:
        """Determine if a value is truthy."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True
    
    def is_equal(self, a: Any, b: Any) -> bool:
        """Check if two values are equal."""
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        return a == b
    
    def check_number_operand(self, operator: Token, operand: Any):
        """Check if an operand is a number."""
        if isinstance(operand, (int, float)):
            return
        raise RuntimeError(operator, "Operand must be a number.")
    
    def check_number_operands(self, operator: Token, left: Any, right: Any):
        """Check if both operands are numbers."""
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def visit_throw_stmt(self, stmt: ast.Throw):
        value = self.evaluate(stmt.value)
        
        # If the value is already a DemonException, throw it
        if isinstance(value, DemonException):
            exception = value
        # Otherwise, create a new DemonException with the value as the message
        else:
            exception = DemonException(str(value), stmt.keyword)
        
        # Add current location to traceback
        if hasattr(self, 'current_function'):
            exception.add_traceback_entry(
                self.current_function.name.lexeme if hasattr(self.current_function, 'name') else '<anonymous>',
                stmt.keyword.line
            )
        
        raise ExceptionThrown(exception)
    def visit_throw_stmt(self, stmt: ast.Throw):
        value = self.evaluate(stmt.value)
        
        # If the value is already a DemonException, throw it
        if isinstance(value, DemonException):
            exception = value
        # Otherwise, create a new DemonException with the value as the message
        else:
            exception = DemonException(str(value), stmt.keyword)
        
        # Add current location to traceback
        if hasattr(self, 'current_function'):
            exception.add_traceback_entry(
                self.current_function.name.lexeme if hasattr(self.current_function, 'name') else '<anonymous>',
                stmt.keyword.line
            )
        
        raise ExceptionThrown(exception)

# Apply the static methods patch to the Interpreter class
Interpreter = patch_interpreter(Interpreter)