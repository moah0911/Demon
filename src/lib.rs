//! The core library for the Demon programming language.
//! This library provides the lexer, parser, and interpreter for the Demon language.

pub mod error;
pub mod lexer;
pub mod parser;
pub mod interpreter;
pub mod memory;
pub mod stdlib;

// Re-exports for common types
pub use error::{Result, Error, ParseError, RuntimeError, InterpreterError};
pub use interpreter::Interpreter;
pub use lexer::{Scanner, Token, TokenType};
pub use parser::{Parser, Stmt, Expr};
pub use memory::{RawPointer, SharedPointer, Allocator, GlobalAllocator};

// Re-export Literal from the parser module's public interface
pub use parser::Literal;

/// The current version of the Demon language
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Creates a new Demon interpreter with the standard library loaded
pub fn new_interpreter() -> Interpreter {
    let mut interpreter = Interpreter::default();
    stdlib::register_stdlib(&mut interpreter);
    interpreter
}

/// Parses a string of Demon code into a vector of statements
pub fn parse(source: &str) -> Result<Vec<Stmt>> {
    let mut scanner = Scanner::new(source.to_string());
    let tokens = scanner.scan_tokens();
    let mut parser = Parser::new(&tokens);
    parser.parse()
}

/// Executes a string of Demon code
pub fn execute(source: &str) -> Result<()> {
    let stmts = parse(source)?;
    let mut interpreter = new_interpreter();
    interpreter.interpret(&stmts)
}
