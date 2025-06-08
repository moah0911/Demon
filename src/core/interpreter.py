"""
Interpreter for the Demon programming language.
"""

import time
from typing import Dict, List, Any, Optional, Union, Tuple
from .tokens import Token, TokenType
from . import ast

class RuntimeError(Exception):
    """Runtime error in the Demon language."""
    
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)

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
        
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        
        raise RuntimeError(name, f"Undefined property '{name.lexeme}'.")
    
    def set(self, name: Token, value: Any):
        """Set a property on this instance."""
        self.fields[name.lexeme] = value
    
    def __str__(self) -> str:
        return f"<{self.klass.name} instance>"

class Interpreter(ast.Visitor):
    """Interpreter for the Demon language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}
        self.NativeFunction = NativeFunction
        
        # Add native functions
        self.globals.define("clock", NativeFunction("clock", 0, lambda *args: time.time()))
        
        # Register standard library functions
        try:
            from ..stdlib.stdlib import DemonStdLib
            DemonStdLib.register_all(self)
        except ImportError:
            # Fallback to basic functions if stdlib is not available
            self.globals.define("print", NativeFunction("print", -1, lambda *args: print(*args)))
            self.globals.define("input", NativeFunction("input", 1, lambda prompt: input(prompt)))
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
                raise RuntimeError(expr.operator, "Division by zero.")
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
        
        if isinstance(obj, dict):
            if expr.name.lexeme in obj:
                return obj[expr.name.lexeme]
            raise RuntimeError(expr.name, f"Undefined property '{expr.name.lexeme}'.")
        
        if isinstance(obj, list):
            if expr.name.lexeme == "length":
                return len(obj)
            
            # Check for list methods
            if expr.name.lexeme in ["append", "pop", "insert", "remove", "index", "count"]:
                if expr.name.lexeme == "append":
                    return lambda x: obj.append(x) or obj
                elif expr.name.lexeme == "pop":
                    return lambda idx=-1: obj.pop(idx)
                elif expr.name.lexeme == "insert":
                    return lambda idx, x: obj.insert(idx, x) or obj
                elif expr.name.lexeme == "remove":
                    return lambda x: obj.remove(x) or obj
                elif expr.name.lexeme == "index":
                    return lambda x: obj.index(x)
                elif expr.name.lexeme == "count":
                    return lambda x: obj.count(x)
        
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
        
        raise RuntimeError(expr.name, "Only instances have properties.")
    
    def visit_set_expr(self, expr: ast.Set):
        obj = self.evaluate(expr.obj)
        
        if isinstance(obj, DemonInstance):
            value = self.evaluate(expr.value)
            obj.set(expr.name, value)
            return value
        
        if isinstance(obj, dict):
            value = self.evaluate(expr.value)
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