use std::any::Any;
use std::fmt;
use std::rc::Rc;
use std::cell::RefCell;

use crate::error::{InterpreterError, Result};
use crate::interpreter::{Environment, Interpreter, Callable};
use crate::parser::{Stmt, Literal};

#[derive(Clone)]
pub struct Function {
    pub declaration: Rc<Stmt>,
    pub closure: Rc<RefCell<Environment>>,
    pub is_initializer: bool,
}

impl Function {
    pub fn new(declaration: Rc<Stmt>, closure: Rc<RefCell<Environment>>, is_initializer: bool) -> Self {
        Self {
            declaration,
            closure,
            is_initializer,
        }
    }

    pub fn bind(&self, instance: Literal) -> Self {
        let environment = Rc::new(RefCell::new(Environment::with_enclosing(Rc::clone(&self.closure))));
        environment.borrow_mut().define("this".to_string(), instance);
        
        Function::new(
            Rc::clone(&self.declaration),
            environment,
            self.is_initializer,
        )
    }
}

impl Callable for Function {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn arity(&self) -> usize {
        match &*self.declaration {
            Stmt::Function { params, .. } => params.len(),
            _ => 0,
        }
    }

    fn call(&self, interpreter: &mut Interpreter, arguments: Vec<Literal>) -> Result<Literal> {
        let environment = Rc::new(RefCell::new(
            Environment::with_enclosing(Rc::clone(&self.closure))
        ));

        // Clone the params and body from the Rc<Stmt> without moving
        let (params, body) = match &*self.declaration {
            Stmt::Function { params, body, .. } => (params.clone(), body.clone()),
            _ => unreachable!("Function declaration expected"),
        };

        for (i, param) in params.iter().enumerate() {
            environment
                .borrow_mut()
                .define(param.lexeme.clone(), arguments[i].clone());
        }

        match interpreter.execute_block(&body, environment) {
            Ok(()) => {
                if self.is_initializer {
                    self.closure.borrow().get_at(0, "this")
                } else {
                    Ok(Literal::Nil)
                }
            }
            Err(e) => match e {
                InterpreterError::Return(value) => {
                    if self.is_initializer {
                        self.closure.borrow().get_at(0, "this")
                    } else {
                        Ok(value)
                    }
                }
                other_error => Err(other_error),
            },
        }
    }

    fn to_string(&self) -> String {
        if let Stmt::Function { name, .. } = &*self.declaration {
            format!("<fn {}>", name.lexeme)
        } else {
            "<lambda>".to_string()
        }
    }
}

impl fmt::Debug for Function {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.to_string())
    }
}
