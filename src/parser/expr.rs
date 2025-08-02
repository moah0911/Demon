//! Expression nodes for the Demon language AST.

use std::fmt;
use std::rc::Rc;
use std::cell::RefCell;
use crate::error::general_error;
use std::collections::HashMap;

use crate::interpreter::{Callable, Class, Instance};
use crate::lexer::Token;
use crate::error::Result;

/// Represents an expression in the Demon language.
#[derive(Debug, Clone)]
pub enum Expr {
    /// A literal value (number, string, boolean, nil, function, class)
    Literal(Token),
    
    /// A variable reference
    Variable(Token),
    
    /// A unary operation (e.g., !true, -5)
    Unary {
        operator: Token,
        right: Box<Expr>,
    },
    
    /// A binary operation (e.g., 1 + 2, 3 * 4)
    Binary {
        left: Box<Expr>,
        operator: Token,
        right: Box<Expr>,
    },
    
    /// A grouping expression (e.g., (1 + 2) * 3)
    Grouping(Box<Expr>),
    
    /// A function call (e.g., print("Hello"))
    Call {
        callee: Box<Expr>,
        arguments: Vec<Expr>,
    },
    
    /// A property access (e.g., object.property)
    Get {
        object: Box<Expr>,
        name: Token,
    },
    
    /// A property assignment (e.g., object.property = value)
    
    /// A new expression (e.g., new MyClass())
    New {
        class: Box<Expr>,
        arguments: Vec<Expr>,
    },
    
    /// A delete expression (e.g., delete ptr)
    Delete {
        target: Box<Expr>,
    },
    
    /// A pointer dereference (e.g., *ptr)
    Dereference {
        expression: Box<Expr>,
    },
    
    /// Address-of expression (e.g., &variable)
    AddressOf {
        expression: Box<Expr>,
    },
    
    /// Array allocation (e.g., new int[10])
    NewArray {
        element_type: Token,
        size: Box<Expr>,
    },
    
    /// Array deallocation (e.g., delete[] arr)
    DeleteArray {
        target: Box<Expr>,
    },
    
    /// Array access (e.g., arr[index])
    ArrayAccess {
        array: Box<Expr>,
        index: Box<Expr>,
    },
    
    /// Custom allocator expression (e.g., new(allocator) MyClass())
    CustomNew {
        allocator: Box<Expr>,
        class: Box<Expr>,
        arguments: Vec<Expr>,
    },
    Set {
        object: Box<Expr>,
        name: Token,
        value: Box<Expr>,
    },
    
    /// A logical operation (e.g., true or false)
    Logical {
        left: Box<Expr>,
        operator: Token,
        right: Box<Expr>,
    },
    
    /// An assignment (e.g., x = 5)
    Assign {
        name: Token,
        value: Box<Expr>,
    },

    /// A reference to 'this' in a class method
    This(Token),

    /// A reference to 'super' in a class method
    Super {
        keyword: Token,
        method: Token,
    },
}

/// Represents a literal value in the AST.
#[derive(Debug, Clone)]
pub enum Literal {
    /// A number literal (e.g., 123, 3.14)
    Number(f64),
    
    /// A string literal (e.g., "hello")
    String(String),
    
    /// A boolean literal (true or false)
    Boolean(bool),
    
    /// The nil value
    Nil,

    /// A callable value (function, method, or class)
    Callable(Box<dyn Callable>),

    /// A class instance
    Instance(Rc<RefCell<Instance>>),

    /// A class definition
    Class(Rc<Class>),
    
    /// An array of values
    Array(Vec<Literal>),
    
    /// A key-value map
    Map(Rc<RefCell<HashMap<String, Literal>>>),
}

impl Expr {
    /// Returns the first token of the expression for error reporting.
    pub fn first_token(&self) -> Token {
        match self {
            Expr::Literal(token) => token.clone(),
            Expr::Variable(token) => token.clone(),
            Expr::Unary { operator, .. } => operator.clone(),
            Expr::Binary { left, .. } => left.first_token(),
            Expr::Logical { left, .. } => left.first_token(),
            Expr::Assign { name, .. } => name.clone(),
            Expr::Grouping(expr) => expr.first_token(),
            Expr::Call { callee, .. } => callee.first_token(),
            Expr::Get { object, .. } => object.first_token(),
            Expr::Set { object, .. } => object.first_token(),
            Expr::This(keyword) => keyword.clone(),
            Expr::Super { keyword, .. } => keyword.clone(),
            Expr::New { class, .. } => class.first_token(),
            Expr::Delete { target } => target.first_token(),
            Expr::Dereference { expression } => expression.first_token(),
            Expr::AddressOf { expression } => expression.first_token(),
            Expr::NewArray { element_type, .. } => element_type.clone(),
            Expr::DeleteArray { target } => target.first_token(),
            Expr::ArrayAccess { array, .. } => array.first_token(),
            Expr::CustomNew { allocator, .. } => allocator.first_token(),
        }
    }
}

impl fmt::Display for Expr {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Expr::Literal(lit) => write!(f, "{}", lit),
            Expr::Variable(name) => write!(f, "{}", name.lexeme),
            Expr::Unary { operator, right } => write!(f, "({} {})", operator.lexeme, right),
            Expr::Binary {
                left,
                operator,
                right,
            } => write!(f, "({} {} {})", operator.lexeme, left, right),
            Expr::Grouping(expr) => write!(f, "(group {})", expr),
            Expr::Call {
                callee, arguments, ..
            } => {
                let args: Vec<String> = arguments.iter().map(ToString::to_string).collect();
                write!(f, "{}({})", callee, args.join(", "))
            }
            Expr::Get { object, name } => write!(f, "{}.{}", object, name.lexeme),
            Expr::Set { object, name, value } => write!(f, "{}.{} = {}", object, name.lexeme, value),
            Expr::Logical {
                left,
                operator,
                right,
            } => write!(f, "({} {} {})", operator.lexeme, left, right),
            Expr::Assign { name, value } => write!(f, "({} = {})", name.lexeme, value),
            Expr::This(_) => write!(f, "this"),
            Expr::Super { keyword, method } => write!(f, "{}.{}", keyword.lexeme, method.lexeme),
            Expr::New { class, arguments } => {
                let args: Vec<String> = arguments.iter().map(ToString::to_string).collect();
                write!(f, "new {}({})", class, args.join(", "))
            }
            Expr::Delete { target } => write!(f, "delete {}", target),
            Expr::Dereference { expression } => write!(f, "*{}", expression),
            Expr::AddressOf { expression } => write!(f, "&{}", expression),
            Expr::NewArray { element_type, size } => {
                write!(f, "new {}[{}]", element_type.lexeme, size)
            }
            Expr::DeleteArray { target } => write!(f, "delete[] {}", target),
            Expr::ArrayAccess { array, index } => write!(f, "{}[{}]", array, index),
            Expr::CustomNew { allocator, class, arguments } => {
                let args: Vec<String> = arguments.iter().map(ToString::to_string).collect();
                write!(f, "new({}) {}({})", allocator, class, args.join(", "))
            }
        }
    }
}

impl fmt::Display for Literal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Literal::Number(n) => write!(f, "{}", n),
            Literal::String(s) => write!(f, "\"{}\"", s),
            Literal::Boolean(b) => write!(f, "{}", b),
            Literal::Nil => write!(f, "nil"),
            Literal::Callable(callable) => write!(f, "{}", callable.to_string()),
            Literal::Instance(instance) => write!(f, "{:?}", instance.borrow()),
            Literal::Class(class) => write!(f, "<class {}>", class.name),
            Literal::Array(elements) => {
                let elements_str: Vec<String> = elements.iter().map(|e| e.to_string()).collect();
                write!(f, "[{}]", elements_str.join(", "))
            }
            Literal::Map(map) => {
                let pairs: Vec<String> = map
                    .borrow()
                    .iter()
                    .map(|(k, v)| format!("{}: {}", k, v))
                    .collect();
                write!(f, "{{{}}}", pairs.join(", "))
            },
        }
    }
}

impl PartialEq for Literal {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (Literal::Number(a), Literal::Number(b)) => a == b,
            (Literal::String(a), Literal::String(b)) => a == b,
            (Literal::Boolean(a), Literal::Boolean(b)) => a == b,
            (Literal::Nil, Literal::Nil) => true,
            _ => false,
        }
    }
}

impl std::ops::Neg for Literal {
    type Output = Result<Self>;

    fn neg(self) -> Self::Output {
        match self {
            Literal::Number(n) => Ok(Literal::Number(-n)),
            _ => Err(general_error("Operand must be a number.")),
        }
    }
}

impl std::ops::Not for Literal {
    type Output = bool;

    fn not(self) -> Self::Output {
        !self.is_truthy()
    }
}

impl Literal {
    /// Returns true if the value is truthy.
    pub fn is_truthy(&self) -> bool {
        match self {
            Literal::Nil => false,
            Literal::Boolean(b) => *b,
            _ => true,
        }
    }

    /// Checks if two values are equal.
    pub fn is_equal(&self, other: &Self) -> bool {
        match (self, other) {
            (Literal::Nil, Literal::Nil) => true,
            (Literal::Nil, _) => false,
            (_, Literal::Nil) => false,
            (Literal::Boolean(a), Literal::Boolean(b)) => a == b,
            (Literal::Number(a), Literal::Number(b)) => a == b,
            (Literal::String(a), Literal::String(b)) => a == b,
            _ => false,
        }
    }
}
