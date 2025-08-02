use std::collections::HashMap;
use std::rc::Rc;
use std::cell::RefCell;

use crate::error::{Result, Error, RuntimeError};
use crate::lexer::Token;
use crate::parser::Literal;

#[derive(Debug, Clone)]
pub struct Environment {
    values: HashMap<String, Literal>,
    pub enclosing: Option<Rc<RefCell<Environment>>>,
}

impl Environment {
    pub fn new() -> Self {
        Environment {
            values: HashMap::new(),
            enclosing: None,
        }
    }

    pub fn with_enclosing(enclosing: Rc<RefCell<Environment>>) -> Self {
        Environment {
            values: HashMap::new(),
            enclosing: Some(enclosing),
        }
    }

    pub fn define(&mut self, name: String, value: Literal) {
        self.values.insert(name, value);
    }

    pub fn get(&self, name: &Token) -> Result<Literal> {
        if let Some(value) = self.values.get(&name.lexeme) {
            return Ok(value.clone());
        }

        if let Some(enclosing) = &self.enclosing {
            return enclosing.borrow().get(name);
        }

        Err(Error::Runtime(RuntimeError::new(
            name.clone(),
            format!("Undefined variable '{}'.", name.lexeme),
        )))
    }

    pub fn assign(&mut self, name: &Token, value: Literal) -> Result<()> {
        if self.values.contains_key(&name.lexeme) {
            self.values.insert(name.lexeme.clone(), value);
            return Ok(());
        }

        if let Some(enclosing) = &mut self.enclosing {
            return enclosing.borrow_mut().assign(name, value);
        }

        Err(Error::Runtime(RuntimeError::new(
            name.clone(),
            format!("Undefined variable '{}'.", name.lexeme),
        )))
    }

    pub fn get_at(&self, distance: usize, name: &str) -> Result<Literal> {
        if distance == 0 {
            self.values.get(name)
                .cloned()
                .ok_or_else(|| Error::General(format!("Undefined variable '{}'.", name)))
        } else if let Some(enclosing) = &self.enclosing {
            enclosing.borrow().get_at(distance - 1, name)
        } else {
            Err(Error::General("Invalid environment depth.".to_string()))
        }
    }

    pub fn assign_at(&mut self, distance: usize, name: &Token, value: Literal) -> Result<()> {
        if distance == 0 {
            self.values.insert(name.lexeme.clone(), value);
            Ok(())
        } else if let Some(enclosing) = &mut self.enclosing {
            enclosing.borrow_mut().assign_at(distance - 1, name, value)
        } else {
            Err(Error::General("Invalid environment depth.".to_string()))
        }
    }
}
