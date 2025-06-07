# Demon Programming Language

Demon is a modern, high-performance programming language that combines the best features of C++, Python, and Java. It aims to provide:

- **Performance**: Like C++ with manual memory management and zero-cost abstractions
- **Readability**: Clean, Python-like syntax
- **Safety**: Strong, static typing with type inference
- **Concurrency**: Built-in support for modern concurrency patterns
- **Interoperability**: Easy integration with C/C++ and Java libraries

## Features

1. **Syntax**
   - Python-like indentation-based blocks
   - C++-style type declarations with type inference
   - Java-like OOP with single inheritance + interfaces

2. **Type System**
   - Strong, static typing with `var` for type inference
   - Built-in primitives: `int`, `float`, `bool`, `string`, `char`
   - Complex types: `List<T>`, `Map<K,V>`, `Optional<T>`
   - Null safety built into the type system

3. **Memory Management**
   - Manual memory management with optional RAII
   - Smart pointers for automatic memory management
   - No garbage collection overhead

4. **Concurrency**
   - Lightweight threads (goroutine-style)
   - Message passing between threads
   - Built-in async/await support

## Example

```demon
// Function definition with type inference
func add(a: int, b: int) -> int {
    return a + b
}

// Class definition
class Person {
    // Constructor
    new(name: string, age: int) {
        this.name = name
        this.age = age
    }
    
    // Method
    func greet() -> string {
        return "Hello, my name is \(name) and I'm \(age) years old."
    }
}

// Main function
func main() {
    // Variables with type inference
    var x = 10
    var y = 20
    
    // Function call
    var result = add(x, y)
    print("Result: \(result)")
    
    // Object creation
    var person = Person("Alice", 30)
    print(person.greet())
    
    // List with type inference
    var numbers = [1, 2, 3, 4, 5]
    
    // For loop with range
    for i in 0..<numbers.length {
        print("Number: \(numbers[i])")
    }
    
    // Lambda function
    var square = (x: int) -> int { return x * x }
    print("Square of 5: \(square(5))")
}
```

## Getting Started

1. Clone this repository
2. Run `python demon.py your_script.dm`

## Language Specification

- **Comments**: `//` for single-line, `/* */` for multi-line
- **Variables**: `var name: Type = value` or `var name = value` (type inference)
- **Constants**: `const name = value`
- **Conditionals**: `if`, `elif`, `else` with `and`, `or`, `not`
- **Loops**: `while`, `for-in`, `for` with range
- **Functions**: `func name(params) -> ReturnType { ... }`
- **Classes**: `class Name { ... }` with single inheritance and interfaces
- **Error Handling**: `try-catch-finally` blocks
- **Concurrency**: `spawn` for goroutines, `channel<T>` for communication

## Roadmap

- [x] Basic lexer and parser
- [ ] Type checker
- [ ] Bytecode compiler
- [ ] Virtual Machine
- [ ] Standard library
- [ ] Package manager
- [ ] Debugger
- [ ] IDE support

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.
