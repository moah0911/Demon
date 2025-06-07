"""
Abstract Syntax Tree (AST) nodes for the Demon programming language.
"""

from typing import List, Dict, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum

from tokens import Token, TokenType

# Base classes
class Expr:
    """Base class for all expression nodes in the AST."""
    pass

class Stmt:
    """Base class for all statement nodes in the AST."""
    pass

@dataclass
class Break(Stmt):
    """Break statement."""
    keyword: Token

@dataclass
class Continue(Stmt):
    """Continue statement."""
    keyword: Token

# Expression nodes
@dataclass
class Literal(Expr):
    value: Any

@dataclass
class Variable(Expr):
    name: Token

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

@dataclass
class ListLiteral(Expr):
    elements: List[Expr]

@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class Grouping(Expr):
    expression: Expr

@dataclass
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr]

@dataclass
class Get(Expr):
    obj: Expr
    name: Token

@dataclass
class Set(Expr):
    obj: Expr
    name: Token
    value: Expr

@dataclass
class This(Expr):
    keyword: Token

@dataclass
class Super(Expr):
    keyword: Token
    method: Token

@dataclass
class Lambda(Expr):
    params: List[Tuple[Token, Optional[Token]]]  # (name, type) pairs
    body: List[Stmt]
    return_type: Optional[Token] = None

@dataclass
class Match(Expr):
    value: Expr
    cases: List[Tuple[Optional[Expr], List[Stmt]]]  # (pattern, body) pairs
    default: Optional[List[Stmt]] = None

@dataclass
class Pipeline(Expr):
    left: Expr
    operator: Token
    right: Expr

@dataclass
class Range(Expr):
    start: Expr
    end: Expr
    inclusive: bool  # True for .., False for ..<


@dataclass
class MapLiteral(Expr):
    entries: List[Tuple[Token, Expr]]  # (key, value) pairs

@dataclass
class BlockExpr(Expr):
    statements: List[Stmt]

# Statement nodes
@dataclass
class Expression(Stmt):
    expression: Expr

@dataclass
class Print(Stmt):
    expressions: List[Expr]  # Changed from expression to expressions to support multiple args

@dataclass
class Var(Stmt):
    name: Token
    initializer: Optional[Expr] = None
    var_type: Optional[Token] = None
    is_const: bool = False

@dataclass
class Block(Stmt):
    statements: List[Stmt]

@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None

@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

@dataclass
class Function(Stmt):
    name: Token
    params: List[Tuple[Token, Optional[Token]]]  # (name, type) pairs
    body: List[Stmt]
    return_type: Optional[Token] = None

@dataclass
class Return(Stmt):
    keyword: Token
    value: Optional[Expr] = None

@dataclass
class Class(Stmt):
    name: Token
    superclass: Optional[Variable] = None
    methods: List[Function] = None
    static_methods: List[Function] = None

    def __post_init__(self):
        if self.methods is None:
            self.methods = []
        if self.static_methods is None:
            self.static_methods = []

@dataclass
class ForEach(Stmt):
    variable: Union[Var, Variable]
    iterable: Expr
    body: Stmt

@dataclass
class MatchStmt(Stmt):
    value: Expr
    cases: List[Tuple[Optional[Expr], List[Stmt]]]  # (pattern, body) pairs
    default: Optional[List[Stmt]] = None

# Visitor pattern for AST traversal
class Visitor:
    """Base visitor class for AST traversal."""
    
    def visit_expr(self, expr: Expr) -> Any:
        method_name = f'visit_{type(expr).__name__.lower()}'
        method = getattr(self, method_name, self.generic_visit_expr)
        return method(expr)
    
    def visit_stmt(self, stmt: Stmt) -> Any:
        method_name = f'visit_{type(stmt).__name__.lower()}'
        method = getattr(self, method_name, self.generic_visit_stmt)
        return method(stmt)
    
    def generic_visit_expr(self, expr: Expr) -> Any:
        raise NotImplementedError(f'No visit method for {type(expr).__name__}')
    
    def generic_visit_stmt(self, stmt: Stmt) -> Any:
        raise NotImplementedError(f'No visit method for {type(stmt).__name__}')
