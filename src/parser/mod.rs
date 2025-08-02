//! Parser for the Demon programming language.
//! Converts a sequence of tokens into an Abstract Syntax Tree (AST).

mod expr;
mod stmt;
mod expression_parser;
mod statement_parser;

use crate::error::{parse_error, InterpreterError as Error, ParseError, Result};
use crate::lexer::{Token, TokenType};

// Re-export the public API
pub use expr::{Expr, Literal};
pub use stmt::Stmt;

/// The Parser converts a sequence of tokens into an Abstract Syntax Tree (AST).
pub struct Parser<'a> {
    tokens: &'a [Token],
    current: usize,
}

impl<'a> Parser<'a> {
    /// Creates a new parser with the given tokens.
    pub fn new(tokens: &'a [Token]) -> Self {
        Self { tokens, current: 0 }
    }

    /// Parses the tokens into a vector of statements.
    pub fn parse(&mut self) -> Result<Vec<Stmt>> {
        let mut statements = Vec::new();
        
        while !self.is_at_end() {
            // Check if the next token is EOF, if so, break the loop
            if self.peek().token_type == TokenType::Eof {
                break;
            }

            if let Some(statement) = self.declaration()? {
                statements.push(statement);
            }
        }
        
        Ok(statements)
    }

    /// Checks if we've consumed all tokens.
    fn is_at_end(&self) -> bool {
        self.current >= self.tokens.len()
    }

    /// Returns the current token without consuming it.
    fn peek(&self) -> &Token {
        &self.tokens[self.current]
    }

    /// Returns the previous token.
    fn previous(&self) -> &Token {
        &self.tokens[self.current - 1]
    }

    /// Checks if the current token matches any of the given token types.
    fn match_tokens(&mut self, types: &[TokenType]) -> bool {
        for token_type in types {
            if self.check(token_type) {
                self.advance();
                return true;
            }
        }
        false
    }

    /// Checks if the current token matches the given token type.
    fn check(&self, token_type: &TokenType) -> bool {
        if self.is_at_end() {
            return false;
        }
        std::mem::discriminant(&self.peek().token_type) == std::mem::discriminant(token_type)
    }

    /// Consumes the current token and returns it.
    fn advance(&mut self) -> &Token {
        if !self.is_at_end() {
            self.current += 1;
        }
        self.previous()
    }

    /// Consumes the current token if it matches the expected type, otherwise returns an error.
    fn consume(&mut self, token_type: TokenType, message: &str) -> Result<&Token> {
        if self.check(&token_type) {
            Ok(self.advance())
        } else {
            Err(Error::Parse(ParseError::Custom(format!("{} at '{}'", message, self.peek().lexeme))))
        }
    }

    /// Checks if the current token is an identifier and consumes it if so.
    /// Returns the identifier token if matched, None otherwise.
    fn match_identifier(&mut self) -> Option<Token> {
        if let TokenType::Identifier(_) = self.peek().token_type {
            Some(self.advance().clone())
        } else {
            None
        }
    }
    
    /// Checks if the current token is a number and consumes it if so.
    /// Returns the number token if matched, None otherwise.
    fn match_number(&mut self) -> Option<Token> {
        if let TokenType::Number(_) = self.peek().token_type {
            Some(self.advance().clone())
        } else {
            None
        }
    }
    
    /// Checks if the current token is a string and consumes it if so.
    /// Returns the string token if matched, None otherwise.
    fn match_string(&mut self) -> Option<Token> {
        if let TokenType::String(_) = self.peek().token_type {
            Some(self.advance().clone())
        } else {
            None
        }
    }
}
