//! Statement nodes for the Demon language AST.

use crate::lexer::Token;
use crate::parser::expr::Expr;
use std::fmt;

/// Represents a statement in the Demon language.
#[derive(Debug, Clone)]
pub enum Stmt {
    /// An empty statement (e.g., `;`)
    Empty,
    /// An expression statement (e.g., `1 + 2;`)
    Expression(Expr),
    
    /// A print statement (e.g., `print "Hello";`)
    Print(Expr),
    
    /// A variable declaration (e.g., `let x = 5;`)
    Var {
        name: Token,
        initializer: Option<Expr>,
    },
    
    /// A constant declaration (e.g., `const PI = 3.14;`)
    Const {
        name: Token,
        initializer: Expr,
    },
    
    /// A block statement (e.g., `{ let x = 5; print x; }`)
    Block(Vec<Stmt>),
    
    /// An if statement (e.g., `if (x > 0) { print "positive"; }`)
    If {
        condition: Expr,
        then_branch: Box<Stmt>,
        else_branch: Option<Box<Stmt>>,
    },
    
    /// A while loop (e.g., `while (x > 0) { x = x - 1; }`)
    While {
        condition: Expr,
        body: Box<Stmt>,
    },
    
    /// A function declaration (e.g., `func add(a, b) { return a + b; }`)
    Function {
        name: Token,
        params: Vec<Token>,
        body: Vec<Stmt>,
    },
    
    /// A return statement (e.g., `return 42;`)
    Return {
        keyword: Token,
        value: Option<Expr>,
    },
    
    /// A class declaration (e.g., `class Person { init(name) { this.name = name; } }`)
    Class {
        name: Token,
        superclass: Option<Expr>,
        methods: Vec<Stmt>,
    }
}

impl fmt::Display for Stmt {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Stmt::Empty => write!(f, ";"),
            Stmt::Expression(expr) => write!(f, "{}", expr),
            Stmt::Print(expr) => write!(f, "print {}", expr),
            Stmt::Var { name, initializer } => {
                if let Some(init) = initializer {
                    write!(f, "let {} = {};", name.lexeme, init)
                } else {
                    write!(f, "let {};", name.lexeme)
                }
            }
            Stmt::Const { name, initializer } => {
                write!(f, "const {} = {};", name.lexeme, initializer)
            }
            Stmt::Block(statements) => {
                writeln!(f, "{{")?;
                for stmt in statements {
                    writeln!(f, "    {};", stmt)?;
                }
                write!(f, "}}")
            }
            Stmt::If {
                condition,
                then_branch,
                else_branch,
            } => {
                write!(f, "if ({}) {}", condition, then_branch)?;
                if let Some(else_stmt) = else_branch {
                    write!(f, " else {}", else_stmt)?;
                }
                Ok(())
            }
            Stmt::While { condition, body } => {
                write!(f, "while ({}) {}", condition, body)
            }
            Stmt::Function { name, params, body } => {
                let param_list: Vec<String> = params.iter().map(|p| p.lexeme.clone()).collect();
                write!(f, "func {}({}) ", name.lexeme, param_list.join(", "))?;
                write!(f, "{}", Stmt::Block(body.clone()))
            }
            Stmt::Return { keyword, value } => {
                if let Some(expr) = value {
                    write!(f, "{} {};", keyword.lexeme, expr)
                } else {
                    write!(f, "{};", keyword.lexeme)
                }
            }
            Stmt::Class { name, superclass, methods } => {
                if let Some(sup) = superclass {
                    writeln!(f, "class {} < {} {{", name.lexeme, sup)?;
                } else {
                    writeln!(f, "class {} {{", name.lexeme)?;
                }
                for method in methods {
                    writeln!(f, "    {}", method)?;
                }
                write!(f, "}}")
            }
        }
    }
}
