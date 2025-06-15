"""
Abstract Syntax Tree (AST) nodes for the Demon programming language.
"""

from typing import List, Dict, Optional, Any, Union, Tuple
from .tokens import Token

class Visitor:
    """Base visitor class for AST nodes."""
    
    def visit_expr(self, expr):
        """Visit an expression."""
        method_name = f"visit_{expr.__class__.__name__.lower()}_expr"
        method = getattr(self, method_name, self.visit_default_expr)
        return method(expr)
    
    def visit_stmt(self, stmt):
        """Visit a statement."""
        method_name = f"visit_{stmt.__class__.__name__.lower()}_stmt"
        method = getattr(self, method_name, self.visit_default_stmt)
        return method(stmt)
    
    def visit_default_expr(self, expr):
        """Default expression visitor."""
        raise NotImplementedError(f"No visit method for {expr.__class__.__name__}")
    
    def visit_default_stmt(self, stmt):
        """Default statement visitor."""
        raise NotImplementedError(f"No visit method for {stmt.__class__.__name__}")
    
    def visit_subscript_expr(self, expr):
        """Visit a subscript expression."""
        return self.visit_default_expr(expr)
        
    def visit_subscript_assign_expr(self, expr):
        """Visit a subscript assignment expression."""
        return self.visit_default_expr(expr)

class Expr:
    """Base class for expressions."""
    
    def accept(self, visitor):
        """Accept a visitor."""
        return visitor.visit_expr(self)

class Stmt:
    """Base class for statements."""
    
    def accept(self, visitor):
        """Accept a visitor."""
        return visitor.visit_stmt(self)

class Binary(Expr):
    """Binary expression."""
    
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class Grouping(Expr):
    """Grouping expression."""
    
    def __init__(self, expression: Expr):
        self.expression = expression

class Literal(Expr):
    """Literal expression."""
    
    def __init__(self, value: Any):
        self.value = value

class Unary(Expr):
    """Unary expression."""
    
    def __init__(self, operator: Token, right: Expr):
        self.operator = operator
        self.right = right

class Variable(Expr):
    """Variable expression."""
    
    def __init__(self, name: Token):
        self.name = name

class Assign(Expr):
    """Assignment expression."""
    
    def __init__(self, name: Token, value: Expr):
        self.name = name
        self.value = value

class Logical(Expr):
    """Logical expression."""
    
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class Call(Expr):
    """Function call expression."""
    
    def __init__(self, callee: Expr, paren: Token, arguments: List[Expr]):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments

class Get(Expr):
    """Property access expression."""
    
    def __init__(self, obj: Expr, name: Token):
        self.obj = obj
        self.name = name

class Set(Expr):
    """Property assignment expression."""
    
    def __init__(self, obj: Expr, name: Token, value: Expr):
        self.obj = obj
        self.name = name
        self.value = value

class This(Expr):
    """This expression."""
    
    def __init__(self, keyword: Token):
        self.keyword = keyword

class Super(Expr):
    """Super expression."""
    
    def __init__(self, keyword: Token, method: Token):
        self.keyword = keyword
        self.method = method

class Lambda(Expr):
    """Lambda expression."""
    
    def __init__(self, params: List[Tuple[Token, Optional[Token]]], body: List[Stmt]):
        self.params = params
        self.body = body

class ListLiteral(Expr):
    """List literal expression."""
    
    def __init__(self, elements: List[Expr]):
        self.elements = elements

class MapLiteral(Expr):
    """Map literal expression."""
    
    def __init__(self, entries: List[Tuple[Token, Expr]]):
        self.entries = entries

class Range(Expr):
    """Range expression."""
    
    def __init__(self, start: Expr, end: Expr, inclusive: bool):
        self.start = start
        self.end = end
        self.inclusive = inclusive

class Match(Expr):
    """Match expression."""
    
    def __init__(self, value: Expr, cases: List[Tuple[Expr, List[Stmt]]], default: Optional[List[Stmt]]):
        self.value = value
        self.cases = cases
        self.default = default

class Pipeline(Expr):
    """Pipeline expression."""
    
    def __init__(self, left: Expr, operator: Token, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right

class BlockExpr(Expr):
    """Block expression."""
    
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

class Decorator(Expr):
    """Decorator expression."""
    
    def __init__(self, name: Token, arguments: List[Expr], target: Expr):
        self.name = name
        self.arguments = arguments
        self.target = target

class Expression(Stmt):
    """Expression statement."""
    
    def __init__(self, expression: Expr):
        self.expression = expression

class Print(Stmt):
    """Print statement."""
    
    def __init__(self, expressions: List[Expr]):
        self.expressions = expressions

class Var(Stmt):
    """Variable declaration statement."""
    
    def __init__(self, name: Token, initializer: Optional[Expr], is_const: bool = False):
        self.name = name
        self.initializer = initializer
        self.is_const = is_const

class Block(Stmt):
    """Block statement."""
    
    def __init__(self, statements: List[Stmt]):
        self.statements = statements

class If(Stmt):
    """If statement."""
    
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt]):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(Stmt):
    """While statement."""
    
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body

class For(Stmt):
    """For statement."""
    
    def __init__(self, initializer: Optional[Stmt], condition: Optional[Expr], increment: Optional[Expr], body: Stmt):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

class ForEach(Stmt):
    """ForEach statement."""
    
    def __init__(self, variable: Union[Var, Variable], iterable: Expr, body: Stmt):
        self.variable = variable
        self.iterable = iterable
        self.body = body

class Function(Stmt):
    """Function declaration statement."""
    
    def __init__(self, name: Token, params: List[Tuple[Token, Optional[Token]]], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body

class Return(Stmt):
    """Return statement."""
    
    def __init__(self, keyword: Token, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value

class Break(Stmt):
    """Break statement."""
    
    def __init__(self, keyword: Token):
        self.keyword = keyword

class Continue(Stmt):
    """Continue statement."""
    
    def __init__(self, keyword: Token):
        self.keyword = keyword

class Class(Stmt):
    """Class declaration statement."""
    
    def __init__(self, name: Token, superclass: Optional[Variable], methods: List[Function], static_methods: List[Function]):
        self.name = name
        self.superclass = superclass
        self.methods = methods
        self.static_methods = static_methods