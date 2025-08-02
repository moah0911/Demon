//! Error handling for the Demon language implementation.

use crate::lexer::Token;
use crate::parser::Literal;
use std::error::Error as StdError;
use std::fmt;

/// Type alias for Result that uses InterpreterError as the error type
pub type Result<T> = std::result::Result<T, InterpreterError>;

/// Type alias for compatibility with existing code
pub type Error = InterpreterError;

/// Represents different types of errors that can occur during parsing.
#[derive(Debug)]
pub enum ParseError {
    UnexpectedToken(Token, String),
    UnclosedParen(Token),
    UnclosedBrace(Token),
    ExpectedExpression(Token),
    ExpectedSemicolon(Token),
    ExpectedIdentifier(Token),
    ExpectedVariableName(Token),
    TooManyArguments(Token, usize, usize), // token, expected, got
    InvalidAssignmentTarget(Token),
    ExpectedClass(Token),
    ExpectedSuperclass(Token),
    ExpectedMethod(Token),
    ExpectedProperty(Token),
    Custom(String),
}

/// Represents runtime errors that occur during execution.
#[derive(Debug)]
pub struct RuntimeError {
    pub token: Token,
    pub message: String,
}

impl RuntimeError {
    /// Creates a new runtime error with the given token and message
    pub fn new(token: Token, message: String) -> Self {
        Self { token, message }
    }
}

/// A general error type that can represent both parse and runtime errors.
#[derive(Debug)]
pub enum InterpreterError {
    Parse(ParseError),
    Runtime(RuntimeError),
    Return(Literal),
    Break,
    Continue,
    General(String), // For general errors that don't fit other categories
}

impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ParseError::UnexpectedToken(token, msg) => {
                write!(f, "[line {}] Error at '{}': {}", token.line, token.lexeme, msg)
            }
            ParseError::UnclosedParen(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Unclosed parenthesis",
                    token.line, token.lexeme
                )
            }
            ParseError::UnclosedBrace(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Unclosed brace",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedExpression(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected expression",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedSemicolon(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected ';' after expression",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedIdentifier(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected identifier",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedVariableName(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected variable name",
                    token.line, token.lexeme
                )
            }
            ParseError::TooManyArguments(token, expected, got) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected {} arguments but got {}",
                    token.line, token.lexeme, expected, got
                )
            }
            ParseError::InvalidAssignmentTarget(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Invalid assignment target",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedClass(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected class name",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedSuperclass(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected superclass name",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedMethod(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected method name",
                    token.line, token.lexeme
                )
            }
            ParseError::ExpectedProperty(token) => {
                write!(
                    f,
                    "[line {}] Error at '{}': Expected property name",
                    token.line, token.lexeme
                )
            }
            ParseError::Custom(msg) => write!(f, "{}", msg),
        }
    }
}

impl fmt::Display for RuntimeError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "[line {}] Runtime error: {}",
            self.token.line, self.message
        )
    }
}

impl fmt::Display for InterpreterError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            InterpreterError::Parse(err) => write!(f, "Parse error: {}", err),
            InterpreterError::Runtime(err) => write!(f, "Runtime error: {}", err),
            InterpreterError::Return(value) => write!(f, "Return({})", value),
            InterpreterError::Break => write!(f, "Break statement outside of loop"),
            InterpreterError::Continue => write!(f, "Continue statement outside of loop"),
            InterpreterError::General(msg) => write!(f, "Error: {}", msg),
        }
    }
}

impl StdError for ParseError {}
impl StdError for RuntimeError {}
impl StdError for InterpreterError {
    fn source(&self) -> Option<&(dyn StdError + 'static)> {
        match self {
            InterpreterError::Parse(err) => Some(err),
            InterpreterError::Runtime(err) => Some(err),
            InterpreterError::Return(_) => None,
            InterpreterError::Break => None,
            InterpreterError::Continue => None,
            InterpreterError::General(_) => None,
        }
    }
}

impl From<ParseError> for InterpreterError {
    fn from(err: ParseError) -> Self {
        InterpreterError::Parse(err)
    }
}

impl From<RuntimeError> for InterpreterError {
    fn from(err: RuntimeError) -> Self {
        InterpreterError::Runtime(err)
    }
}

/// Creates a new runtime error with the given token and message.
pub fn runtime_error(token: &Token, message: &str) -> RuntimeError {
    RuntimeError {
        token: token.clone(),
        message: message.to_string(),
    }
}

/// Creates a new parse error with the given token and message.
pub fn parse_error(token: &Token, message: &str) -> ParseError {
    ParseError::UnexpectedToken(token.clone(), message.to_string())
}

/// Creates a new general error with the given message.
pub fn general_error(message: &str) -> InterpreterError {
    InterpreterError::Parse(ParseError::Custom(message.to_string()))
}

/// Extension trait for converting std::io::Error to InterpreterError.
pub trait IoErrorExt<T> {
    fn map_io_error(self) -> Result<T>;
}

impl<T> IoErrorExt<T> for std::io::Result<T> {
    fn map_io_error(self) -> Result<T> {
        self.map_err(|e| InterpreterError::Parse(ParseError::Custom(e.to_string())))
    }
}
