# Demon Programming Language

![The Letter D with Ho](https://github.com/user-attachments/assets/4f3946f0-9607-445f-98a1-51a656249503)

## Overview
Demon is a dynamic programming language designed for clarity, expressiveness, and ease of use. It combines the best features of modern languages with a clean syntax and powerful abstractions.

```demon
// Hello World in Demon
print("Hello, World!");

// Functions
func greet(name) {
    return "Hello, " + name + "!";
}

print(greet("Demon"));
```

## Features

- **Clean, Readable Syntax** - Inspired by JavaScript, Python, and Rust
- **First-class Functions** - Functions as values, closures, and higher-order functions
- **Dynamic Typing** - Flexible type system with runtime type checking
- **Rich Control Flow** - If/else, while loops, and for loops
- **Object-Oriented Programming** - Classes with inheritance
- **Closures** - Powerful lexical scoping and state encapsulation
- **Exception Handling** - Try/catch/finally blocks for robust error management

## Language Rules

1. **Semicolons**: All statements must end with a semicolon
2. **Functions**: Defined using the `func` keyword
3. **Variables**: Declared using `let` keyword
4. **Constants**: Declared using `const` keyword
5. **Logical Operators**: Use `and` for AND and `or` for OR (not `&&` and `||`)
6. **String Concatenation**: Use `+` operator to concatenate strings
7. **Comments**: Use `//` for single-line comments
8. **Blocks**: Use `{` and `}` to define code blocks
9. **Conditionals**: Use `if`, `else if`, and `else` for conditional logic
10. **Loops**: Use `while`, `for`, and `for-in` loops for iteration
11. **Classes**: Use `class` keyword with `init` method for constructors
12. **Inheritance**: Use `<` symbol for class inheritance
13. **Exception Handling**: Use `try`, `catch`, and `finally` blocks

## Language Examples

### Variables and Constants

```demon
let x = 10;        // Variable
const PI = 3.14159; // Constant
```

### Control Flow

```demon
// Conditional statements
if (x > 10) {
    print("x is greater than 10");
} else if (x < 10) {
    print("x is less than 10");
} else {
    print("x is equal to 10");
}

// While loops
let i = 1;
while (i <= 5) {
    print(i);
    i = i + 1;
}

// For loops
for (let j = 1; j <= 5; j = j + 1) {
    print(j);
}
```

### Functions and Closures

```demon
// Function definition
func add(a, b) {
    return a + b;
}

// Closures
func makeCounter() {
    let count = 0;
    func counter() {
        count = count + 1;
        return count;
    }
    return counter;
}

let counter = makeCounter();
print(counter()); // Outputs: 1
print(counter()); // Outputs: 2
```

### Classes and Inheritance

```demon
// Class definition
class Person {
    init(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return "Hello, my name is " + this.name + " and I am " + this.age + " years old.";
    }
    
    // Static method
    static create(name, age) {
        return Person(name, age);
    }
}

// Inheritance
class Employee < Person {
    init(name, age, job) {
        super.init(name, age);
        this.job = job;
    }
    
    greet() {
        return super.greet() + " I work as a " + this.job + ".";
    }
}

// Create instances
let john = Person.create("John", 30);  // Using static method
let jane = Employee("Jane", 28, "Developer");
print(jane.greet());
```

### Data Structures

```demon
// Arrays
let numbers = [10, 20, 30, 40, 50];
print("First element: " + numbers[0]);
print("Length: " + numbers.length);

// Array methods
numbers.append(60);
print("Popped value: " + numbers.pop());
numbers.insert(1, 15);
numbers.remove(30);
```

### Exception Handling

```demon
// Try-catch-finally
try {
    print("Attempting division...");
    let result = 10 / 0;  // This will throw an exception
    print("This line won't execute");
} catch (e) {
    print("Caught exception");
} finally {
    print("This always executes");
}

// Exception propagation
func riskyFunction() {
    let result = 5 / 0;  // Throws an exception
}

try {
    riskyFunction();  // Call function that throws
} catch (e) {
    print("Caught exception from function");
}
```

## Advanced Features

Demon includes several advanced features for more complex programming tasks:

- **Closures**: Create functions that encapsulate state
- **Array Operations**: Methods like append, pop, insert, and remove
- **String Manipulation**: Methods for case conversion, searching, and transformation
- **Pattern Matching**: Conditional logic based on value patterns
- **Reactive Programming**: Build reactive data flows (experimental)
- **Automatic Memoization**: Cache function results for improved performance
- **Static Methods**: Class-level methods that don't require instances
- **Exception Handling**: Try/catch/finally blocks with error handling

For more details, see [ADVANCED_FEATURES.md](docs/ADVANCED_FEATURES.md), [MEMOIZATION.md](docs/MEMOIZATION.md), [STATIC_METHODS.md](docs/STATIC_METHODS.md), and [EXCEPTION_HANDLING.md](docs/EXCEPTION_HANDLING.md).

## Project Structure

- **src/**: Core implementation of the language
  - **core/**: Core language components (parser, interpreter, VM)
  - **stdlib/**: Standard library implementations
  - **ide_support/**: IDE integration tools and VSCode extension
  - **tools/**: Development tools (CLI, debugger, package manager)
- **examples/**: Example Demon programs
  - **basic/**: Simple language examples
  - **advanced/**: Advanced programming patterns
  - **testing/**: Comprehensive test files
- **docs/**: Documentation for various aspects of the language

## Running Demon Programs

```bash
# Run a Demon script
python run.py examples/basic/hello.demon

# Run comprehensive tests
python run.py examples/testing/comprehensive_test.demon
```

## Known Limitations

- Limited standard library compared to mature languages
- Performance optimizations are still in progress
- Custom exception types are not yet fully supported

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the Demon programming language.

## License

MIT License
# Implementation Documentation

For details on how Demon is implemented and executed, see:

- [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) - Overview of the implementation approach
- [COMPILATION_PROCESS.md](docs/COMPILATION_PROCESS.md) - How code is compiled and executed
- [PYTHON_RATIONALE.md](docs/PYTHON_RATIONALE.md) - Why Python was chosen
- [BYTECODE_FUTURE.md](docs/BYTECODE_FUTURE.md) - Future bytecode VM plans