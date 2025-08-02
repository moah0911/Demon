use std::any::Any;
use std::fmt;
use std::rc::Rc;

use crate::error::Result;
use crate::interpreter::Interpreter;
use crate::parser::Literal;

pub trait Callable: fmt::Debug + CallableClone {
    fn as_any(&self) -> &dyn Any;
    fn arity(&self) -> usize;
    fn call(&self, interpreter: &mut Interpreter, arguments: Vec<Literal>) -> Result<Literal>;
    fn to_string(&self) -> String;
}

// Helper trait for object-safe cloning
pub trait CallableClone {
    fn clone_box(&self) -> Box<dyn Callable>;
}

impl<T> CallableClone for T
where
    T: 'static + Callable + Clone,
{
    fn clone_box(&self) -> Box<dyn Callable> {
        Box::new(self.clone())
    }
}

impl Clone for Box<dyn Callable> {
    fn clone(&self) -> Box<dyn Callable> {
        self.clone_box()
    }
}

// Native function implementation
#[derive(Clone)]
pub struct NativeFunction {
    pub name: String,
    pub arity: usize,
    pub func: Rc<dyn Fn(&mut Interpreter, Vec<Literal>) -> Result<Literal>>,
}

// Manually implement Debug since we can't derive it due to the function pointer
impl fmt::Debug for NativeFunction {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("NativeFunction")
            .field("name", &self.name)
            .field("arity", &self.arity)
            .field("func", &"<function>")
            .finish()
    }
}

impl Callable for NativeFunction {
    fn as_any(&self) -> &dyn Any {
        self
    }

    fn arity(&self) -> usize {
        self.arity
    }

    fn call(&self, interpreter: &mut Interpreter, arguments: Vec<Literal>) -> Result<Literal> {
        (self.func)(interpreter, arguments)
    }

    fn to_string(&self) -> String {
        format!("<native fn {}>", self.name)
    }
}

impl NativeFunction {
    pub fn new<F>(name: &str, arity: usize, func: F) -> Self
    where
        F: 'static + Fn(&mut Interpreter, Vec<Literal>) -> Result<Literal>,
    {
        NativeFunction {
            name: name.to_string(),
            arity,
            func: Rc::new(func),
        }
    }
}
