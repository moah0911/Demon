//! Lexical analysis module for the Demon language.
//! This module is responsible for converting source code into tokens.

mod token;
pub mod scanner;

pub use token::{Token, TokenType};
pub use scanner::Scanner;

#[derive(Debug)]
pub struct Lexer {
    source: String,
    tokens: Vec<Token>,
    start: usize,
    current: usize,
    line: usize,
}

impl Lexer {
    pub fn new(source: &str) -> Self {
        Self {
            source: source.to_string(),
            tokens: Vec::new(),
            start: 0,
            current: 0,
            line: 1,
        }
    }

    pub fn scan_tokens(&mut self) -> Vec<Token> {
        while !self.is_at_end() {
            self.start = self.current;
            self.scan_token();
        }

        // Add EOF token at the end
        self.tokens.push(Token::new(
            TokenType::Eof,
            "".to_string(),
            self.line
        ));
        self.tokens.clone()
    }

    fn is_at_end(&self) -> bool {
        self.current >= self.source.len()
    }

    fn scan_token(&mut self) {
        // Implementation will be added in the next steps
        self.advance();
    }

    fn advance(&mut self) -> char {
        self.current += 1;
        self.source.chars().nth(self.current - 1).unwrap()
    }
}
