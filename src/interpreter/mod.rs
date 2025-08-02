//! Interpreter for the Demon programming language.
//! This module contains the implementation of the interpreter that executes the AST.

mod callable;
mod class;
mod environment;
mod function;

use std::cell::RefCell;
use std::rc::Rc;

use crate::error::{Result, RuntimeError, InterpreterError};
use crate::lexer::{Token, TokenType};
use crate::parser::{Expr, Stmt};
use crate::parser::Literal;

pub use callable::{Callable, NativeFunction};
pub use class::{Class, Instance};
pub use environment::Environment;
pub use function::Function;

/// The main interpreter for the Demon language.
pub struct Interpreter {
    globals: Rc<RefCell<Environment>>,
    environment: Rc<RefCell<Environment>>,
    locals: std::collections::HashMap<usize, usize>,
}

impl Default for Interpreter {
    fn default() -> Self {
        let globals = Rc::new(RefCell::new(Environment::new()));
        let environment = Rc::clone(&globals);
        let interpreter = Self {
            globals: Rc::clone(&globals),
            environment,
            locals: std::collections::HashMap::new(),
        };

        // Add the clock function (kept for backward compatibility)
        let clock = NativeFunction::new("clock", 0, |_, _| {
            Ok(Literal::Number(
                std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)
                    .unwrap()
                    .as_secs_f64(),
            ))
        });

        interpreter.globals
            .borrow_mut()
            .define("clock".to_string(), Literal::Callable(Box::new(clock)));

        interpreter
    }
}

impl Interpreter {
    /// Returns a reference to the global environment.
    pub fn globals(&self) -> Rc<RefCell<Environment>> {
        self.globals.clone()
    }

    /// Creates a new interpreter with the given environment.
    pub fn with_environment(environment: Rc<RefCell<Environment>>) -> Self {
        Self {
            globals: Rc::clone(&environment),
            environment,
            locals: std::collections::HashMap::new(),
        }
    }

    /// Interprets a list of statements.
    pub fn interpret(&mut self, statements: &[Stmt]) -> Result<()> {
        for statement in statements {
            self.execute(statement)?;
        }
        Ok(())
    }

    /// Executes a single statement.
    pub fn execute(&mut self, stmt: &Stmt) -> Result<()> {
        match stmt {
            Stmt::Empty => Ok(()),
            Stmt::Expression(expr) => {
                self.evaluate(expr)?;
                Ok(())
            }
            Stmt::Print(expr) => {
                let value = self.evaluate(expr)?;
                println!("{}", value);
                Ok(())
            }
            Stmt::Var { name, initializer } => {
                let value = if let Some(expr) = initializer {
                    self.evaluate(expr)?
                } else {
                    Literal::Nil
                };

                self.environment
                    .borrow_mut()
                    .define(name.lexeme.clone(), value);
                Ok(())
            }
            Stmt::Const { name, initializer } => {
                let value = self.evaluate(initializer)?;
                self.environment
                    .borrow_mut()
                    .define(name.lexeme.clone(), value);
                Ok(())
            }
            Stmt::Block(statements) => {
                let environment = Rc::new(RefCell::new(Environment::with_enclosing(
                    Rc::clone(&self.environment),
                )));
                self.execute_block(statements, environment)
            }
            Stmt::If {
                condition,
                then_branch,
                else_branch,
            } => {
                let condition_value = self.evaluate(condition)?;
                if self.is_truthy(&condition_value) {
                    self.execute(then_branch)
                } else if let Some(else_branch) = else_branch {
                    self.execute(else_branch)
                } else {
                    Ok(())
                }
            }
            Stmt::While { condition, body } => {
                while {
                    let condition_value = self.evaluate(condition)?;
                    self.is_truthy(&condition_value)
                } {
                    self.execute(body)?;
                }
                Ok(())
            }
            Stmt::Function {
                name, ..
            } => {
                let function = Function::new(
                    Rc::new(stmt.clone()),
                    Rc::clone(&self.environment),
                    false,
                );
                self.environment
                    .borrow_mut()
                    .define(name.lexeme.clone(), Literal::Callable(Box::new(function)));
                Ok(())
            }
            Stmt::Return { value, .. } => {
                let value = if let Some(expr) = value {
                    self.evaluate(expr)?
                } else {
                    Literal::Nil
                };
                Err(InterpreterError::Return(value))
            }
            Stmt::Class {
                name,
                superclass,
                methods,
            } => self.visit_class_stmt(name, superclass, methods),
            
        }
    }

    /// Executes a block of statements in a new environment.
    pub fn execute_block(
        &mut self,
        statements: &[Stmt],
        environment: Rc<RefCell<Environment>>,
    ) -> Result<()> {
        let previous = std::mem::replace(&mut self.environment, environment);
        let result = (|| {
            for statement in statements {
                self.execute(statement)?;
            }
            Ok(())
        })();
        self.environment = previous;
        result
    }

    /// Evaluates an expression.
    pub fn evaluate(&mut self, expr: &Expr) -> Result<Literal> {
        match expr {
            Expr::Literal(token) => match &token.token_type {
                TokenType::Number(n) => Ok(Literal::Number(*n)),
                TokenType::String(s) => Ok(Literal::String(s.clone())),
                TokenType::True => Ok(Literal::Boolean(true)),
                TokenType::False => Ok(Literal::Boolean(false)),
                TokenType::Nil => Ok(Literal::Nil),
                _ => Err(InterpreterError::Runtime(RuntimeError::new(
                    token.clone(),
                    "Invalid literal value.".to_string(),
                ))),
            },
            Expr::Grouping(expr) => self.evaluate(expr),
            Expr::Unary { operator, right } => {
                let right = self.evaluate(right)?;
                match operator.token_type {
                    TokenType::Bang => Ok(Literal::Boolean(!self.is_truthy(&right))),
                    TokenType::Minus => {
                        if let Literal::Number(n) = right {
                            Ok(Literal::Number(-n))
                        } else {
                            Err(InterpreterError::Runtime(RuntimeError::new(
                                operator.clone(),
                                "Operand must be a number.".to_string(),
                            )))
                        }
                    }
                    _ => Err(InterpreterError::Runtime(RuntimeError::new(
                        operator.clone(),
                        "Invalid unary operator.".to_string(),
                    ))),
                }
            }
            Expr::Binary {
                left,
                operator,
                right,
            } => {
                let left = self.evaluate(left)?;
                let right = self.evaluate(right)?;

                match (&left, &operator.token_type, &right) {
                    (Literal::Number(a), TokenType::Plus, Literal::Number(b)) => {
                        Ok(Literal::Number(a + b))
                    }
                    (Literal::String(a), TokenType::Plus, Literal::String(b)) => {
                        Ok(Literal::String(format!("{}{}", a, b)))
                    }
                    (Literal::Number(a), TokenType::Minus, Literal::Number(b)) => {
                        Ok(Literal::Number(a - b))
                    }
                    (Literal::Number(a), TokenType::Star, Literal::Number(b)) => {
                        Ok(Literal::Number(a * b))
                    }
                    (Literal::Number(a), TokenType::Slash, Literal::Number(b)) => {
                        if *b == 0.0 {
                            return Err(InterpreterError::Runtime(RuntimeError::new(
                                operator.clone(),
                                "Division by zero.".to_string(),
                            )));
                        }
                        Ok(Literal::Number(a / b))
                    }
                    (_, TokenType::EqualEqual, _) => {
                        Ok(Literal::Boolean(self.is_equal(&left, &right)))
                    }
                    (_, TokenType::BangEqual, _) => {
                        Ok(Literal::Boolean(!self.is_equal(&left, &right)))
                    }
                    (Literal::Number(a), TokenType::Greater, Literal::Number(b)) => {
                        Ok(Literal::Boolean(a > b))
                    }
                    (Literal::Number(a), TokenType::GreaterEqual, Literal::Number(b)) => {
                        Ok(Literal::Boolean(a >= b))
                    }
                    (Literal::Number(a), TokenType::Less, Literal::Number(b)) => {
                        Ok(Literal::Boolean(a < b))
                    }
                    (Literal::Number(a), TokenType::LessEqual, Literal::Number(b)) => {
                        Ok(Literal::Boolean(a <= b))
                    }
                    _ => Err(InterpreterError::Runtime(RuntimeError::new(
                        operator.clone(),
                        "Invalid operands.".to_string(),
                    ))),
                }
            }
            Expr::Logical {
                left,
                operator,
                right,
            } => {
                let left = self.evaluate(left)?;

                match operator.token_type {
                    TokenType::Or => {
                        if self.is_truthy(&left) {
                            Ok(left)
                        } else {
                            self.evaluate(right)
                        }
                    }
                    TokenType::And => {
                        if !self.is_truthy(&left) {
                            Ok(left)
                        } else {
                            self.evaluate(right)
                        }
                    }
                    _ => Err(InterpreterError::Runtime(RuntimeError::new(
                        operator.clone(),
                        "Invalid logical operator.".to_string(),
                    ))),
                }
            }
            Expr::Call { callee, arguments, .. } => {
                let callee = self.evaluate(callee)?;
                let mut args = Vec::new();

                for arg in arguments {
                    args.push(self.evaluate(arg)?);
                }

                if let Literal::Callable(function) = callee {
                    if args.len() != function.arity() {
                        return Err(InterpreterError::Runtime(RuntimeError::new(
                            arguments[0].first_token(),
                            format!("Expected {} arguments but got {}.", function.arity(), args.len()),
                        )));
                    }
                    function.call(self, args)
                } else {
                    Err(InterpreterError::Runtime(RuntimeError::new(
                        arguments[0].first_token(),
                        "Can only call functions and classes.".to_string(),
                    )))
                }
            }
            Expr::Get { object, name } => {
                let object = self.evaluate(object)?;

                if let Literal::Instance(instance) = &object {
                    instance.borrow().get(name, &object)
                } else {
                    Err(RuntimeError::new(
                        name.clone(),
                        "Only instances have properties.".to_string(),
                    )
                    .into())
                }
            }
            Expr::Set { object, name, value } => {
                let value = self.evaluate(value)?;
                let object = self.evaluate(object)?;

                if let Literal::Instance(instance) = object {
                    instance.borrow_mut().set(name.clone(), value.clone());
                    Ok(value)
                } else {
                    Err(RuntimeError::new(
                        name.clone(),
                        "Only instances have fields.".to_string(),
                    )
                    .into())
                }
            },
            Expr::Variable(name) => self.look_up_variable(name, expr),
            Expr::Assign { name, value } => {
                let value = self.evaluate(value)?;
                self.environment.borrow_mut().assign(name, value.clone())?;
                Ok(value)
            },
            Expr::This(keyword) => self.look_up_variable(keyword, expr),
            Expr::Super { keyword, method } => {
                // This is a temporary solution until we have a resolver.
                let superclass = self.environment.borrow().get(&Token::new(
                    TokenType::Identifier("super".to_string()),
                    "super".to_string(),
                    keyword.line,
                ))?;

                let object = self.environment.borrow().get(&Token::new(
                    TokenType::Identifier("this".to_string()),
                    "this".to_string(),
                    keyword.line,
                ))?;

                if let Literal::Class(superclass) = superclass {
                    if let Some(method) = superclass.find_method(&method.lexeme) {
                        Ok(Literal::Callable(Box::new(method.bind(object))))
                    } else {
                        Err(RuntimeError::new(
                            method.clone(),
                            format!("Undefined property '{}'.", method.lexeme),
                        )
                        .into())
                    }
                } else {
                    // This can happen if 'super' is used outside of a class that inherits.
                    Err(RuntimeError::new(
                        keyword.clone(),
                        "'super' is not a class.".to_string(),
                    )
                    .into())
                }
            },
            _ => Err(InterpreterError::Runtime(RuntimeError::new(
                Token::new(TokenType::Eof, "".to_string(), 0),
                "Unimplemented expression type".to_string(),
            ))),
        }
    }

    fn visit_class_stmt(
        &mut self,
        name: &Token,
        superclass: &Option<Expr>,
        methods: &[Stmt],
    ) -> Result<()> {
        let superclass_val = if let Some(superclass_expr) = superclass {
            let value = self.evaluate(superclass_expr)?;
            if let Literal::Class(_) = &value {
                Some(value)
            } else if let Literal::Callable(c) = &value {
                if let Some(class) = c.as_any().downcast_ref::<Class>() {
                     Some(Literal::Class(Rc::new(class.clone())))
                } else {
                    return Err(RuntimeError::new(
                        superclass_expr.first_token(),
                        "Superclass must be a class.".to_string(),
                    )
                    .into());
                }
            } else {
                return Err(RuntimeError::new(
                    superclass_expr.first_token(),
                    "Superclass must be a class.".to_string(),
                )
                .into());
            }
        } else {
            None
        };

        self.environment
            .borrow_mut()
            .define(name.lexeme.clone(), Literal::Nil);

        if let Some(sc) = &superclass_val {
            self.environment = Rc::new(RefCell::new(Environment::with_enclosing(
                Rc::clone(&self.environment),
            )));
            self.environment
                .borrow_mut()
                .define("super".to_string(), sc.clone());
        }

        let mut class_methods = std::collections::HashMap::new();
        for method in methods {
            if let Stmt::Function { name, .. } = method {
                let function = Function::new(
                    Rc::new(method.clone()),
                    Rc::clone(&self.environment),
                    name.lexeme == "init",
                );
                class_methods.insert(name.lexeme.clone(), function);
            } else {
                unreachable!();
            }
        }

        let superclass_rc = if let Some(Literal::Class(c)) = superclass_val {
            Some(c)
        } else {
            None
        };

        let class = Class::new(name.lexeme.clone(), superclass_rc, class_methods);

        if superclass.is_some() {
            let enclosing = self.environment.borrow().enclosing.clone();
            if let Some(enclosing_env) = enclosing {
                self.environment = enclosing_env;
            }
        }

        self.environment
            .borrow_mut()
            .assign(name, Literal::Callable(Box::new(class)))?;
        Ok(())
    }

    /// Looks up a variable in the environment.
    fn look_up_variable(&self, name: &Token, expr: &Expr) -> Result<Literal> {
        if let Some(distance) = self.locals.get(&(expr as *const _ as usize)) {
            self.environment.borrow().get_at(*distance, &name.lexeme)
        } else {
            // Fallback for global variables if resolver is not used
            self.environment.borrow().get(name)
        }
    }

    /// Checks if a value is truthy.
    fn is_truthy(&self, value: &Literal) -> bool {
        match value {
            Literal::Nil => false,
            Literal::Boolean(b) => *b,
            _ => true,
        }
    }

    /// Checks if two values are equal.
    fn is_equal(&self, a: &Literal, b: &Literal) -> bool {
        match (a, b) {
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
