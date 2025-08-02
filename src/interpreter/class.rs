use std::any::Any;
use std::collections::HashMap;
use std::fmt;
use std::rc::Rc;

use crate::error::{Result, RuntimeError};
use crate::interpreter::{Callable, Function};
use crate::lexer::Token;
use crate::parser::Literal;

#[derive(Clone, Debug)]
pub struct Class {
    pub name: String,
    pub superclass: Option<Rc<Class>>,
    pub methods: HashMap<String, Function>,
}

impl Class {
    pub fn new(
        name: String,
        superclass: Option<Rc<Class>>,
        methods: HashMap<String, Function>,
    ) -> Self {
        Self {
            name,
            superclass,
            methods,
        }
    }

    pub fn find_method(&self, name: &str) -> Option<Function> {
        if let Some(method) = self.methods.get(name) {
            return Some(method.clone());
        }

        if let Some(ref superclass) = self.superclass {
            return superclass.find_method(name);
        }

        None
    }
}

impl Callable for Class {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn arity(&self) -> usize {
        if let Some(initializer) = self.find_method("init") {
            initializer.arity()
        } else {
            0
        }
    }

    fn call(&self, interpreter: &mut crate::interpreter::Interpreter, arguments: Vec<Literal>) -> Result<Literal> {
        let instance = Instance::new(Rc::new(self.clone()));
        
        if let Some(initializer) = self.find_method("init") {
            if let Literal::Instance(instance_ref) = &instance {
                let instance_literal = Literal::Instance(Rc::clone(instance_ref));
                initializer
                    .bind(instance_literal)
                    .call(interpreter, arguments)?;
            }
        }

        Ok(instance)
    }

    fn to_string(&self) -> String {
        self.name.clone()
    }
}

#[derive(Clone)]
pub struct Instance {
    pub class: Rc<Class>,
    pub fields: HashMap<String, Literal>,
}

impl Instance {
    pub fn new(class: Rc<Class>) -> Literal {
        Literal::Instance(Rc::new(std::cell::RefCell::new(Self {
            class,
            fields: HashMap::new(),
        })))
    }

    pub fn get(&self, name: &Token, self_ref: &Literal) -> Result<Literal> {
        if let Some(field) = self.fields.get(&name.lexeme) {
            return Ok(field.clone());
        }

        if let Some(method) = self.class.find_method(&name.lexeme) {
            return Ok(Literal::Callable(Box::new(method.bind(self_ref.clone()))));
        }

        Err(RuntimeError::new(
            name.clone(),
            format!("Undefined property '{}'.", name.lexeme),
        ).into())
    }

    pub fn set(&mut self, name: Token, value: Literal) {
        self.fields.insert(name.lexeme, value);
    }
}

impl fmt::Debug for Instance {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} instance", self.class.name)
    }
}
