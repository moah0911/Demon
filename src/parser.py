"""
Demon Parser
Handles the parsing of the Demon programming language.
"""

from typing import List, Dict, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto

from tokens import Token, TokenType
from demon_ast import ListLiteral

class RuntimeError(Exception):
    """Runtime error for the Demon interpreter."""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(self.message)

class Interpreter:
    """Dummy Interpreter class to satisfy type hints."""
    pass

class ParseError(Exception):
    """Raised when a parsing error occurs."""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)

class Expr:
    """Base class for all expression nodes in the AST."""
    pass

class Stmt:
    """Base class for all statement nodes in the AST."""
    pass

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
    params: List[Token]
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
    params: List[Token]
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

@dataclass
class ForEach(Stmt):
    variable: Token
    iterable: Expr
    body: Stmt

@dataclass
class MatchStmt(Stmt):
    value: Expr
    cases: List[Tuple[Expr, List[Stmt]]]  # (pattern, body) pairs
    default: Optional[List[Stmt]] = None

class Parser:
    """Recursive descent parser for the Demon language."""
    
    def __init__(self, tokens: List[Token], demon):
        self.tokens = tokens
        self.demon = demon
        self.current = 0
        self.loop_depth = 0
    
    def parse(self) -> List[Stmt]:
        """Parse the entire program."""
        statements = []
        while not self.is_at_end():
            stmt = self.declaration()
            if stmt is not None:
                statements.append(stmt)
        return statements
    
    def declaration(self) -> Stmt:
        """Parse a declaration."""
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUNC):
                return self.function("function")
            if self.match(TokenType.VAR, TokenType.LET, TokenType.CONST):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
    
    def class_declaration(self) -> Stmt:
        """Parse a class declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        
        superclass = None
        if self.match(TokenType.COLON):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods = []
        static_methods = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            is_static = self.match(TokenType.STATIC)
            method = self.function("method")
            if is_static:
                static_methods.append(method)
            else:
                methods.append(method)
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        return Class(name, superclass, methods, static_methods)
    
    def function(self, kind: str) -> Function:
        """Parse a function declaration."""
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        # Parse parameters
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Can't have more than 255 parameters.")
                
                param = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                
                # Type annotation
                param_type = None
                if self.match(TokenType.COLON):
                    param_type = self.consume(
                        TokenType.IDENTIFIER, "Expect parameter type.")
                
                parameters.append((param, param_type))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Return type
        return_type = None
        if self.match(TokenType.ARROW):
            return_type = self.consume(TokenType.IDENTIFIER, "Expect return type.")
        
        # Function body
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block_statement()
        
        return Function(name, parameters, body, return_type)
    
    def var_declaration(self) -> Stmt:
        """Parse a variable declaration."""
        is_const = self.previous().type == TokenType.CONST
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        # Initializer
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        elif is_const:
            self.error(self.previous(), "Constants must be initialized.")
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)
    
    def statement(self) -> Stmt:
        """Parse a statement."""
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.LEFT_BRACE):
            return Block(self.block_statement())
        if self.match(TokenType.MATCH):
            return self.match_statement()
        if self.match(TokenType.FOR_EACH):
            return self.foreach_statement()
        
        return self.expression_statement()
    
    def for_statement(self) -> Stmt:
        """Parse a for loop statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        
        # Initializer
        initializer = None
        if self.match(TokenType.SEMICOLON):
            pass  # No initializer
        elif self.match(TokenType.VAR, TokenType.LET, TokenType.CONST):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        
        # Condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        # Increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        
        # Body
        body = self.statement()
        
        # Desugar for loop to while loop
        if increment is not None:
            body = Block([body, Expression(increment)])
        
        if condition is None:
            condition = Literal(True)
        body = While(condition, body)
        
        if initializer is not None:
            body = Block([initializer, body])
        
        return body
    
    def if_statement(self) -> Stmt:
        """Parse an if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return If(condition, then_branch, else_branch)
    
    def print_statement(self) -> Stmt:
        """Parse a print statement."""
        expressions = []
        
        # Consume the opening parenthesis
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'print'.")
        
        # Parse the first expression
        if not self.check(TokenType.RIGHT_PAREN):
            expressions.append(self.expression())
            
            # Parse additional expressions separated by commas
            while self.match(TokenType.COMMA):
                if self.check(TokenType.RIGHT_PAREN):
                    break
                expressions.append(self.expression())
        
        # Consume the closing parenthesis and semicolon
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after print expressions.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        
        return Print(expressions)
    
    def return_statement(self) -> Stmt:
        """Parse a return statement."""
        keyword = self.previous()
        value = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)
    
    def while_statement(self) -> Stmt:
        """Parse a while loop statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        
        try:
            self.loop_depth += 1
            body = self.statement()
            return While(condition, body)
        finally:
            self.loop_depth -= 1
    
    def foreach_statement(self) -> Stmt:
        """Parse a foreach loop statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'foreach'.")
        
        # Variable declaration or name
        if self.match(TokenType.VAR, TokenType.LET, TokenType.CONST):
            is_const = self.previous().type == TokenType.CONST
            name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
            
            # Type annotation
            var_type = None
            if self.match(TokenType.COLON):
                var_type = self.consume(TokenType.IDENTIFIER, "Expect variable type.")
            
            variable = Var(name, None, var_type, is_const)
        else:
            name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
            variable = Variable(name)
        
        self.consume(TokenType.IN, "Expect 'in' after variable in foreach.")
        
        # Iterable expression
        iterable = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after foreach clauses.")
        
        # Body
        body = self.statement()
        
        # Desugar foreach to a for loop
        # This is a simplified version and would be expanded in the interpreter
        return ForEach(variable, iterable, body)
    
    def match_statement(self) -> Stmt:
        """Parse a match expression statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'match'.")
        value = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after match value.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before match cases.")
        
        cases = []
        default_case = None
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.match(TokenType.CASE):
                pattern = self.expression()
                self.consume(TokenType.FAT_ARROW, "Expect '=>' after pattern.")
                
                # Parse the case body
                body = []
                if self.match(TokenType.LEFT_BRACE):
                    while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
                        body.append(self.declaration())
                    self.consume(TokenType.RIGHT_BRACE, "Expect '}' after case body.")
                else:
                    # Single expression case
                    body = [Expression(self.expression())]
                
                cases.append((pattern, body))
            elif self.match(TokenType.DEFAULT):
                self.consume(TokenType.FAT_ARROW, "Expect '=>' after 'default'.")
                
                # Parse the default case body
                default_case = []
                if self.match(TokenType.LEFT_BRACE):
                    while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
                        default_case.append(self.declaration())
                    self.consume(TokenType.RIGHT_BRACE, "Expect '}' after default case body.")
                else:
                    # Single expression default case
                    default_case = [Expression(self.expression())]
            else:
                self.error(self.peek(), "Expect 'case' or 'default' in match.")
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after match cases.")
        return MatchStmt(value, cases, default_case)
    
    def block_statement(self) -> List[Stmt]:
        """Parse a block of statements."""
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def expression_statement(self) -> Stmt:
        """Parse an expression statement."""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return Expression(expr)
    
    def expression(self) -> Expr:
        """Parse an expression."""
        return self.assignment()
    
    def assignment(self) -> Expr:
        """Parse an assignment expression."""
        expr = self.pipeline()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def pipeline(self) -> Expr:
        """Parse a pipeline expression (|>)."""
        expr = self.or_expr()
        
        while self.match(TokenType.PIPE_GT, TokenType.PIPE_FIRST):
            operator = self.previous()
            right = self.or_expr()
            expr = Pipeline(expr, operator, right)
        
        return expr
    
    def or_expr(self) -> Expr:
        """Parse a logical or expression."""
        expr = self.and_expr()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def and_expr(self) -> Expr:
        """Parse a logical and expression."""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def equality(self) -> Expr:
        """Parse an equality expression."""
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self) -> Expr:
        """Parse a comparison expression."""
        expr = self.range_expr()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.range_expr()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def range_expr(self) -> Expr:
        """Parse a range expression (.. or ..<)."""
        expr = self.term()
        
        if self.match(TokenType.RANGE_INCL, TokenType.RANGE_EXCL):
            operator = self.previous()
            right = self.term()
            return Range(expr, right, operator.type == TokenType.RANGE_INCL)
        
        return expr
    
    def term(self) -> Expr:
        """Parse a term (addition/subtraction)."""
        expr = self.factor()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self) -> Expr:
        """Parse a factor (multiplication/division)."""
        expr = self.unary()
        
        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def unary(self) -> Expr:
        """Parse a unary expression."""
        if self.match(TokenType.BANG, TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self) -> Expr:
        """Parse a function call or property access."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after index.")
                expr = Get(expr, Token(TokenType.STRING, f"[{index}]", None, self.previous().line))
            else:
                break
        
        return expr
    
    def finish_call(self, callee: Expr) -> Expr:
        """Finish parsing a function call."""
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Can't have more than 255 arguments.")
                
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return Call(callee, paren, arguments)
    
    def primary(self) -> Expr:
        """Parse a primary expression."""
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        if self.match(TokenType.FAT_ARROW):
            # Lambda expression
            return self.lambda_expression()
        
        if self.match(TokenType.LEFT_BRACKET):
            # List literal
            return self.list_literal()
        
        if self.match(TokenType.LEFT_BRACE):
            # Map literal or block expression
            if self.check(TokenType.IDENTIFIER) and self.check_next(TokenType.COLON):
                return self.map_literal()
            else:
                return self.block_expression()
        
        raise self.error(self.peek(), "Expect expression.")
    
    def list_literal(self) -> Expr:
        """Parse a list literal."""
        elements = []
        
        if not self.check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
        return ListLiteral(elements)
    
    def lambda_expression(self) -> Expr:
        """Parse a lambda expression."""
        # Parameters
        params = []
        
        if not self.check(TokenType.FAT_ARROW):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' before lambda parameters.")
            
            if not self.check(TokenType.RIGHT_PAREN):
                while True:
                    if len(params) >= 255:
                        self.error(self.peek(), "Can't have more than 255 parameters.")
                    
                    param = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                    
                    # Type annotation
                    param_type = None
                    if self.match(TokenType.COLON):
                        param_type = self.consume(TokenType.IDENTIFIER, "Expect parameter type.")
                    
                    params.append((param, param_type))
                    
                    if not self.match(TokenType.COMMA):
                        break
            
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after lambda parameters.")
        
        # Return type
        return_type = None
        if self.match(TokenType.ARROW):
            return_type = self.consume(TokenType.IDENTIFIER, "Expect return type.")
        
        # Body
        self.consume(TokenType.FAT_ARROW, "Expect '=>' before lambda body.")
        
        # Single expression or block
        if self.match(TokenType.LEFT_BRACE):
            body = self.block_statement()
        else:
            # Single expression
            expr = self.expression()
            body = [Expression(expr)]
        
        return Lambda(params, body, return_type)
    
    def list_literal(self) -> Expr:
        """Parse a list literal."""
        elements = []
        
        if not self.check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
        return ListLiteral(elements)
    
    def map_literal(self) -> Expr:
        """Parse a map literal."""
        entries = []
        
        if not self.check(TokenType.RIGHT_BRACE):
            while True:
                key = self.consume(TokenType.IDENTIFIER, "Expect key name.")
                self.consume(TokenType.COLON, "Expect ':' after key.")
                value = self.expression()
                
                entries.append((key, value))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after map entries.")
        return MapLiteral(entries)
    
    def block_expression(self) -> Expr:
        """Parse a block expression."""
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        
        # The last expression is the result of the block
        if statements and isinstance(statements[-1], Expression):
            return Block(statements)
        
        return Block(statements + [Expression(Literal(None))])
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        """Consume a token of the expected type or raise an error."""
        if self.check(token_type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    def error(self, token: Token, message: str) -> ParseError:
        """Create a parse error."""
        if token.type == TokenType.EOF:
            return ParseError(token, f"{message} at end")
        else:
            return ParseError(token, f"{message} at '{token.lexeme}'")
    
    def synchronize(self):
        """Recover from an error by synchronizing the parser."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.CLASS,
                TokenType.FUNC,
                TokenType.VAR,
                TokenType.LET,
                TokenType.CONST,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return
            
            self.advance()
    
    def match(self, *types: TokenType) -> bool:
        """Check if the current token matches any of the given types."""
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    def check(self, type: TokenType) -> bool:
        """Check if the current token is of the given type."""
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def check_next(self, type: TokenType) -> bool:
        """Check if the next token is of the given type."""
        if self.is_at_end():
            return False
        
        if self.tokens[self.current + 1].type == TokenType.EOF:
            return False
            
        return self.tokens[self.current + 1].type == type
    
    def advance(self) -> Token:
        """Advance to the next token and return the previous one."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        """Check if we've consumed all tokens."""
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        """Return the current token without consuming it."""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Return the most recently consumed token."""
        return self.tokens[self.current - 1]
