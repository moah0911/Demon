//! Standard library for the Demon programming language.

use std::io;
use std::time::{SystemTime, UNIX_EPOCH};

use crate::interpreter::{Interpreter, NativeFunction};
use crate::{Literal, Result};

/// Registers all standard library functions in the global environment.
pub fn register_stdlib(interpreter: &mut Interpreter) {
    // I/O functions
    interpreter.globals().borrow_mut().define(
        "print".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("print", usize::MAX, print))),
    );
    
    interpreter.globals().borrow_mut().define(
        "input".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("input", 0, input))),
    );
    
    // Time functions
    interpreter.globals().borrow_mut().define(
        "time".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("time", 0, time))),
    );

    // Type conversion functions
    interpreter.globals().borrow_mut().define(
        "to_string".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("to_string", 1, to_string))),
    );
    
    interpreter.globals().borrow_mut().define(
        "to_number".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("to_number", 1, to_number))),
    );
    
    interpreter.globals().borrow_mut().define(
        "to_bool".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("to_bool", 1, to_bool))),
    );

    // Math functions
    interpreter.globals().borrow_mut().define(
        "abs".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("abs", 1, abs))),
    );
    
    interpreter.globals().borrow_mut().define(
        "sqrt".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("sqrt", 1, sqrt))),
    );
    
    interpreter.globals().borrow_mut().define(
        "pow".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("pow", 2, pow))),
    );

    // String functions
    interpreter.globals().borrow_mut().define(
        "len".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("len", 1, len))),
    );
    
    interpreter.globals().borrow_mut().define(
        "substring".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("substring", usize::MAX, substring))),
    );

    // Array functions
    interpreter.globals().borrow_mut().define(
        "array".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("array", usize::MAX, array))),
    );
    
    interpreter.globals().borrow_mut().define(
        "push".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("push", 2, push))),
    );
    
    interpreter.globals().borrow_mut().define(
        "pop".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("pop", 1, pop))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map", 2, map))),
    );

    // Map functions
    interpreter.globals().borrow_mut().define(
        "Map".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("Map", 0, map_new))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_has".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_has", 2, map_has))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_get".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_get", 2, map_get))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_set".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_set", 3, map_set))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_remove".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_remove", 2, map_remove))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_keys".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_keys", 1, map_keys))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_values".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_values", 1, map_values))),
    );
    
    interpreter.globals().borrow_mut().define(
        "map_entries".to_string(),
        Literal::Callable(Box::new(NativeFunction::new("map_entries", 1, map_entries))),
    );
}

/// Prints all arguments to stdout, separated by spaces and followed by a newline.
fn print(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let output: Vec<String> = args.iter().map(|arg| arg.to_string()).collect();
    println!("{}", output.join(" "));
    Ok(Literal::Nil)
}

/// Reads a line from stdin and returns it as a string.
fn input(_: &mut Interpreter, _: Vec<Literal>) -> Result<Literal> {
    let mut input = String::new();
    io::stdin().read_line(&mut input).map_err(|e| {
        crate::error::general_error(&format!("Failed to read input: {}", e))
    })?;
    // Remove trailing newline
    if input.ends_with('\n') {
        input.pop();
        if input.ends_with('\r') {
            input.pop();
        }
    }
    Ok(Literal::String(input))
}

/// Returns the current Unix timestamp in seconds.
fn time(_: &mut Interpreter, _: Vec<Literal>) -> Result<Literal> {
    let start = SystemTime::now();
    let since_the_epoch = start
        .duration_since(UNIX_EPOCH)
        .map_err(|e| crate::error::general_error(&format!("Time went backwards: {}", e)))?;
    Ok(Literal::Number(since_the_epoch.as_secs_f64()))
}

/// Converts a value to a string.
fn to_string(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    Ok(Literal::String(args[0].to_string()))
}

/// Converts a value to a number.
fn to_number(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    match &args[0] {
        Literal::Number(n) => Ok(Literal::Number(*n)),
        Literal::String(s) => {
            let n: f64 = s.parse().map_err(|_| {
                crate::error::general_error(&format!("Cannot convert '{}' to number", s))
            })?;
            Ok(Literal::Number(n))
        }
        Literal::Boolean(true) => Ok(Literal::Number(1.0)),
        Literal::Boolean(false) | Literal::Nil => Ok(Literal::Number(0.0)),
        _ => Err(crate::error::general_error("Cannot convert value to number")),
    }
}

/// Converts a value to a boolean.
fn to_bool(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    Ok(Literal::Boolean(args[0].is_truthy()))
}

/// Returns the absolute value of a number.
fn abs(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    match &args[0] {
        Literal::Number(n) => Ok(Literal::Number(n.abs())),
        _ => Err(crate::error::general_error("abs() argument must be a number")),
    }
}

/// Returns the square root of a number.
fn sqrt(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    match &args[0] {
        Literal::Number(n) => {
            if *n < 0.0 {
                return Err(crate::error::general_error("sqrt() of negative number"));
            }
            Ok(Literal::Number(n.sqrt()))
        }
        _ => Err(crate::error::general_error("sqrt() argument must be a number")),
    }
}

/// Returns the first argument raised to the power of the second argument.
fn pow(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    match (&args[0], &args[1]) {
        (Literal::Number(base), Literal::Number(exp)) => {
            Ok(Literal::Number(base.powf(*exp)))
        }
        _ => Err(crate::error::general_error(
            "pow() arguments must be numbers",
        )),
    }
}

/// Returns the length of a string or array.
fn len(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    match &args[0] {
        Literal::String(s) => Ok(Literal::Number(s.len() as f64)),
        Literal::Array(elements) => Ok(Literal::Number(elements.len() as f64)),
        _ => Err(crate::error::general_error("len() argument must be a string or array")),
    }
}

/// Returns a substring of a string.
fn substring(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let s = match &args[0] {
        Literal::String(s) => s,
        _ => return Err(crate::error::general_error("substring() first argument must be a string")),
    };
    
    let start = match &args[1] {
        Literal::Number(n) => *n as usize,
        _ => return Err(crate::error::general_error("substring() second argument must be a number")),
    };
    
    let end = match &args[2] {
        Literal::Number(n) => *n as usize,
        _ => return Err(crate::error::general_error("substring() third argument must be a number")),
    };
    
    if start > end || end > s.len() {
        return Err(crate::error::general_error("substring() indices out of range"));
    }
    
    let result = s.chars().skip(start).take(end - start).collect();
    Ok(Literal::String(result))
}

/// Creates a new array with the given elements.
fn array(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    Ok(Literal::Array(args))
}

/// Adds an element to the end of an array.
fn push(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let mut array = match &args[0] {
        Literal::Array(elements) => elements.clone(),
        _ => return Err(crate::error::general_error("push() first argument must be an array")),
    };
    
    array.push(args[1].clone());
    Ok(Literal::Array(array))
}

/// Removes and returns the last element of an array.
fn pop(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let mut array = match &args[0] {
        Literal::Array(elements) => elements.clone(),
        _ => return Err(crate::error::general_error("pop() argument must be an array")),
    };
    
    if array.is_empty() {
        return Ok(Literal::Nil);
    }
    
    let last = array.pop().unwrap();
    Ok(last)
}

/// Applies a function to each element of an array and returns a new array with the results.
fn map(interpreter: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let array = match &args[0] {
        Literal::Array(elements) => elements,
        _ => return Err(crate::error::general_error("map() first argument must be an array")),
    };
    
    let func = match &args[1] {
        Literal::Callable(func) => func,
        _ => return Err(crate::error::general_error("map() second argument must be a function")),
    };
    
    let mut result = Vec::new();
    for (_i, item) in array.iter().enumerate() {
        let mapped = func.call(interpreter, vec![item.clone()])?;
        result.push(mapped);
    }
    
    Ok(Literal::Array(result))
}

/// Creates a new empty map.
fn map_new(_: &mut Interpreter, _: Vec<Literal>) -> Result<Literal> {
    Ok(Literal::Map(Default::default()))
}

/// Checks if a map contains a key.
fn map_has(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map,
        _ => return Err(crate::error::general_error("map_has() first argument must be a map")),
    };
    
    let key = args[1].to_string();
    Ok(Literal::Boolean(map.borrow().contains_key(&key)))
}

/// Gets a value from a map by key.
fn map_get(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map,
        _ => return Err(crate::error::general_error("map_get() first argument must be a map")),
    };
    
    let key = args[1].to_string();
    match map.borrow().get(&key) {
        Some(value) => Ok(value.clone()),
        None => Ok(Literal::Nil),
    }
}

/// Sets a value in a map by key.
fn map_set(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map.clone(),
        _ => return Err(crate::error::general_error("map_set() first argument must be a map")),
    };
    
    let key = args[1].to_string();
    let value = args[2].clone();
    
    let mut map_ref = map.borrow_mut();
    map_ref.insert(key, value);
    
    Ok(Literal::Map(map.clone()))
}

/// Removes a key-value pair from a map.
fn map_remove(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map.clone(),
        _ => return Err(crate::error::general_error("map_remove() first argument must be a map")),
    };
    
    let key = args[1].to_string();
    
    let mut map_ref = map.borrow_mut();
    let removed = map_ref.remove(&key);
    
    Ok(removed.unwrap_or(Literal::Nil))
}

/// Returns an array of all keys in a map.
fn map_keys(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map,
        _ => return Err(crate::error::general_error("map_keys() argument must be a map")),
    };
    
    let keys: Vec<Literal> = map
        .borrow()
        .keys()
        .map(|k| Literal::String(k.clone()))
        .collect();
    
    Ok(Literal::Array(keys))
}

/// Returns an array of all values in a map.
fn map_values(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map,
        _ => return Err(crate::error::general_error("map_values() argument must be a map")),
    };
    
    let values: Vec<Literal> = map.borrow().values().cloned().collect();
    Ok(Literal::Array(values))
}

/// Returns an array of [key, value] pairs from a map.
fn map_entries(_: &mut Interpreter, args: Vec<Literal>) -> Result<Literal> {
    let map = match &args[0] {
        Literal::Map(map) => map,
        _ => return Err(crate::error::general_error("map_entries() argument must be a map")),
    };
    
    let entries: Vec<Literal> = map
        .borrow()
        .iter()
        .map(|(k, v)| {
            let pair = vec![
                Literal::String(k.clone()),
                v.clone(),
            ];
            Literal::Array(pair)
        })
        .collect();
    
    Ok(Literal::Array(entries))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::interpreter::Interpreter;
    use crate::parser::Literal;
    
    #[test]
    fn test_to_string() {
        let mut interp = Interpreter::default();
        assert_eq!(
            to_string(&mut interp, vec![Literal::Number(42.0)]).unwrap(),
            Literal::String("42".to_string())
        );
        assert_eq!(
            to_string(&mut interp, vec![Literal::Boolean(true)]).unwrap(),
            Literal::String("true".to_string())
        );
    }
    
    #[test]
    fn test_to_number() {
        let mut interp = Interpreter::default();
        assert_eq!(
            to_number(&mut interp, vec![Literal::String("42".to_string())]).unwrap(),
            Literal::Number(42.0)
        );
        assert_eq!(
            to_number(&mut interp, vec![Literal::Boolean(true)]).unwrap(),
            Literal::Number(1.0)
        );
    }
    
    #[test]
    fn test_math_functions() {
        let mut interp = Interpreter::default();
        assert_eq!(
            abs(&mut interp, vec![Literal::Number(-42.0)]).unwrap(),
            Literal::Number(42.0)
        );
        assert_eq!(
            sqrt(&mut interp, vec![Literal::Number(16.0)]).unwrap(),
            Literal::Number(4.0)
        );
        assert_eq!(
            pow(&mut interp, vec![Literal::Number(2.0), Literal::Number(3.0)]).unwrap(),
            Literal::Number(8.0)
        );
    }
}
