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
- **Rich Control Flow** - If/else, while loops, and blocks
- **Error Handling** - Graceful error handling patterns

## Language Rules

1. **Semicolons**: All statements must end with a semicolon
2. **Functions**: Defined using the `func` keyword
3. **Variables**: Declared using `let` keyword
4. **Constants**: Declared using `const` keyword
5. **Logical Operators**: Use `&&` for AND and `||` for OR (not `and` and `or`)
6. **String Concatenation**: Use `+` operator to concatenate strings
7. **Comments**: Use `//` for single-line comments
8. **Blocks**: Use `{` and `}` to define code blocks
9. **Conditionals**: Use `if`, `else if`, and `else` for conditional logic
10. **Loops**: Use `while`, `for`, and `for-in` loops for iteration

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

// For-each loops
let items = ["apple", "banana", "cherry"];
for (let item in items) {
    print(item);
}
```

### Functions

```demon
// Function definition
func add(a, b) {
    return a + b;
}

// Higher-order functions
func applyTwice(f, x) {
    return f(f(x));
}

func addOne(x) {
    return x + 1;
}

print(applyTwice(addOne, 5)); // Outputs: 7
```

### Data Structures

```demon
// Lists
let numbers = [1, 2, 3, 4, 5];
print("List length:", len(numbers));

// Simple objects
let person = {"name": "John", "age": 30};
```

## Project Structure

- **src/**: Core implementation of the language
  - **core/**: Core language components (parser, interpreter, VM)
  - **stdlib/**: Standard library implementations
  - **ide_support/**: IDE integration tools
  - **tools/**: Development tools (CLI, debugger, package manager)
- **examples/**: Example Demon programs
- **docs/**: Documentation for various aspects of the language

## Running Demon Programs

```bash
# Run a Demon script
python run.py examples/hello.demon
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the Demon programming language.

## License

MIT License