"""
Parser for the Demon programming language.
"""

from typing import List, Optional, Any, Dict, Tuple
from .tokens import Token, TokenType
from . import ast
from .subscript_expr import SubscriptExpr

class ParseError(Exception):
    """Exception raised during parsing."""
    pass

class Parser:
    """Parser for the Demon language."""
    
    def __init__(self, tokens: List[Token], demon):
        self.tokens = tokens
        self.demon = demon
        self.current = 0
    
    def parse(self) -> List[ast.Stmt]:
        """Parse tokens into statements."""
        statements = []
        while not self.is_at_end():
            try:
                statements.append(self.declaration())
            except ParseError:
                self.synchronize()
        
        return statements
    
    def declaration(self) -> Optional[ast.Stmt]:
        """Parse a declaration."""
        try:
            if self.match(TokenType.CLASS):
                return self.class_declaration()
            if self.match(TokenType.FUNC):
                return self.function("function")
            if self.match(TokenType.LET):
                return self.var_declaration(False)
            if self.match(TokenType.CONST):
                return self.var_declaration(True)
            
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
    
    def class_declaration(self) -> ast.Stmt:
        """Parse a class declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        
        # Parse superclass if present
        superclass = None
        if self.match(TokenType.LESS):
            self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            superclass = ast.Variable(self.previous())
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")
        
        methods = []
        static_methods = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            if self.match(TokenType.STATIC):
                static_methods.append(self.function("method"))
            else:
                methods.append(self.function("method"))
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")
        
        return ast.Class(name, superclass, methods, static_methods)
    
    def function(self, kind: str) -> ast.Function:
        """Parse a function declaration."""
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters.")
                
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                param_type = None
                
                if self.match(TokenType.COLON):
                    param_type = self.consume(TokenType.IDENTIFIER, "Expect parameter type.")
                
                parameters.append((param_name, param_type))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Parse return type if present
        return_type = None
        if self.match(TokenType.COLON):
            return_type = self.consume(TokenType.IDENTIFIER, "Expect return type.")
        
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        
        return ast.Function(name, parameters, body)
    
    def var_declaration(self, is_const: bool) -> ast.Stmt:
        """Parse a variable declaration."""
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        # Parse type annotation if present
        type_annotation = None
        if self.match(TokenType.COLON):
            type_annotation = self.consume(TokenType.IDENTIFIER, "Expect type annotation.")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return ast.Var(name, initializer, is_const)
    
    def statement(self) -> ast.Stmt:
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
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.CONTINUE):
            return self.continue_statement()
        if self.match(TokenType.LEFT_BRACE):
            return ast.Block(self.block())
        
        return self.expression_statement()
    
    def for_statement(self) -> ast.Stmt:
        """Parse a for statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        
        # Check for for-each style loop with 'in' keyword
        if self.match(TokenType.LET):
            var_name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
            
            if self.match(TokenType.IN):
                # For-each loop
                iterable = self.expression()
                self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for-each clauses.")
                body = self.statement()
                
                # Create a variable for the loop variable
                variable = ast.Var(var_name, None, False)
                
                return ast.ForEach(variable, iterable, body)
            elif self.match(TokenType.EQUAL):
                # C-style for loop with initializer as part of declaration
                initializer_expr = self.expression()
                initializer = ast.Var(var_name, initializer_expr, False)
                
                self.consume(TokenType.SEMICOLON, "Expect ';' after loop initializer.")
                
                condition = None
                if not self.check(TokenType.SEMICOLON):
                    condition = self.expression()
                self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
                
                increment = None
                if not self.check(TokenType.RIGHT_PAREN):
                    increment = self.expression()
                self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
                
                body = self.statement()
                
                # Create a For node
                return ast.For(initializer, condition, increment, body)
            else:
                # Regular variable declaration
                initializer = self.var_declaration(False)
        elif self.match(TokenType.SEMICOLON):
            initializer = None
        else:
            initializer = self.expression_statement()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        
        body = self.statement()
        
        # Create a For node
        return ast.For(initializer, condition, increment, body)
    
    def if_statement(self) -> ast.Stmt:
        """Parse an if statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return ast.If(condition, then_branch, else_branch)
    
    def print_statement(self) -> ast.Stmt:
        """Parse a print statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'print'.")
        
        expressions = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            # Parse the first expression
            expressions.append(self.expression())
            
            # Parse additional expressions separated by commas
            while self.match(TokenType.COMMA):
                expressions.append(self.expression())
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        self.consume(TokenType.SEMICOLON, "Expect ';' after print statement.")
        
        return ast.Print(expressions)
    
    def return_statement(self) -> ast.Stmt:
        """Parse a return statement."""
        keyword = self.previous()
        value = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ast.Return(keyword, value)
    
    def while_statement(self) -> ast.Stmt:
        """Parse a while statement."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        
        return ast.While(condition, body)
    
    def break_statement(self) -> ast.Stmt:
        """Parse a break statement."""
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return ast.Break(keyword)
    
    def continue_statement(self) -> ast.Stmt:
        """Parse a continue statement."""
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'continue'.")
        return ast.Continue(keyword)
    
    def block(self) -> List[ast.Stmt]:
        """Parse a block of statements."""
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def expression_statement(self) -> ast.Stmt:
        """Parse an expression statement."""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ast.Expression(expr)
    
    def expression(self) -> ast.Expr:
        """Parse an expression."""
        return self.assignment()
    
    def assignment(self) -> ast.Expr:
        """Parse an assignment expression."""
        expr = self.or_expr()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, ast.Variable):
                name = expr.name
                return ast.Assign(name, value)
            elif isinstance(expr, ast.Get):
                return ast.Set(expr.obj, expr.name, value)
            elif isinstance(expr, SubscriptExpr):
                # Handle array/list index assignment
                from .subscript_assign_expr import SubscriptAssignExpr
                return SubscriptAssignExpr(expr.obj, expr.index, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def or_expr(self) -> ast.Expr:
        """Parse an or expression."""
        expr = self.and_expr()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = ast.Logical(expr, operator, right)
        
        return expr
    
    def and_expr(self) -> ast.Expr:
        """Parse an and expression."""
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = ast.Logical(expr, operator, right)
        
        return expr
    
    def equality(self) -> ast.Expr:
        """Parse an equality expression."""
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = ast.Binary(expr, operator, right)
        
        return expr
    
    def comparison(self) -> ast.Expr:
        """Parse a comparison expression."""
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = ast.Binary(expr, operator, right)
        
        return expr
    
    def term(self) -> ast.Expr:
        """Parse a term expression."""
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = ast.Binary(expr, operator, right)
        
        return expr
    
    def factor(self) -> ast.Expr:
        """Parse a factor expression."""
        expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.PERCENT):
            operator = self.previous()
            right = self.unary()
            expr = ast.Binary(expr, operator, right)
        
        return expr
    
    def unary(self) -> ast.Expr:
        """Parse a unary expression."""
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return ast.Unary(operator, right)
        
        return self.call()
    
    def call(self) -> ast.Expr:
        """Parse a call expression."""
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = ast.Get(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                # Parse array indexing with square brackets
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after array index.")
                expr = SubscriptExpr(expr, index)
            else:
                break
        
        return expr
    
    def finish_call(self, callee: ast.Expr) -> ast.Expr:
        """Finish parsing a call expression."""
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 arguments.")
                
                arguments.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return ast.Call(callee, paren, arguments)
    
    def primary(self) -> ast.Expr:
        """Parse a primary expression."""
        if self.match(TokenType.FALSE):
            return ast.Literal(False)
        if self.match(TokenType.TRUE):
            return ast.Literal(True)
        if self.match(TokenType.NIL):
            return ast.Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return ast.Literal(self.previous().literal)
        
        if self.match(TokenType.SUPER):
            keyword = self.previous()
            self.consume(TokenType.DOT, "Expect '.' after 'super'.")
            method = self.consume(TokenType.IDENTIFIER, "Expect superclass method name.")
            return ast.Super(keyword, method)
        
        if self.match(TokenType.THIS):
            return ast.This(self.previous())
        
        if self.match(TokenType.IDENTIFIER):
            return ast.Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return ast.Grouping(expr)
        
        if self.match(TokenType.LEFT_BRACKET):
            return self.list_literal()
        
        if self.match(TokenType.LEFT_BRACE):
            return self.map_literal()
        
        if self.match(TokenType.FUNC):
            return self.lambda_expression()
        
        self.error(self.peek(), "Expect expression.")
    
    def list_literal(self) -> ast.Expr:
        """Parse a list literal."""
        elements = []
        
        if not self.check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self.expression())
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
        
        return ast.ListLiteral(elements)
    
    def map_literal(self) -> ast.Expr:
        """Parse a map literal."""
        entries = []
        
        if not self.check(TokenType.RIGHT_BRACE):
            while True:
                key = self.consume(TokenType.STRING, "Expect string key in map literal.")
                self.consume(TokenType.COLON, "Expect ':' after map key.")
                value = self.expression()
                
                entries.append((key, value))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after map entries.")
        
        return ast.MapLiteral(entries)
    
    def lambda_expression(self) -> ast.Expr:
        """Parse a lambda expression."""
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'func' in lambda expression.")
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters.")
                
                param_name = self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                param_type = None
                
                if self.match(TokenType.COLON):
                    param_type = self.consume(TokenType.IDENTIFIER, "Expect parameter type.")
                
                parameters.append((param_name, param_type))
                
                if not self.match(TokenType.COMMA):
                    break
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        # Parse return type if present
        return_type = None
        if self.match(TokenType.COLON):
            return_type = self.consume(TokenType.IDENTIFIER, "Expect return type.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before lambda body.")
        body = self.block()
        
        return ast.Lambda(parameters, body)
    
    def match(self, *types) -> bool:
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
    
    def advance(self) -> Token:
        """Advance to the next token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self.peek().type == TokenType.EOF
    
    def peek(self) -> Token:
        """Return the current token."""
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        """Return the previous token."""
        return self.tokens[self.current - 1]
    
    def consume(self, type: TokenType, message: str) -> Token:
        """Consume a token of the given type or raise an error."""
        if self.check(type):
            return self.advance()
        
        self.error(self.peek(), message)
    
    def error(self, token: Token, message: str):
        """Report a parse error."""
        self.demon.error(token, message)
        raise ParseError()
    
    def synchronize(self):
        """Synchronize after a parse error."""
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.CLASS,
                TokenType.FUNC,
                TokenType.LET,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                return
            
            self.advance()