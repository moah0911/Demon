# Demon Programming Language

Demon is a lightweight, dynamically-typed scripting language with a clean and simple syntax. It's designed for ease of use and learning while providing powerful programming constructs.

## Features

- **Simple Syntax**: Clean and minimal syntax inspired by modern languages
- **Dynamic Typing**: No need to declare variable types
- **First-class Functions**: Functions are first-class citizens
- **Lexical Scoping**: Variables are lexically scoped
- **Built-in Data Structures**: Support for lists and basic data types
- **Control Flow**: Familiar if/else, while, and for loops
- **Functions**: Define reusable code blocks with parameters

## Example

```demon
// Hello World in Demon
print("Hello, World!");

// Basic arithmetic
let x = 5 + 3 * 2;
print("5 + 3 * 2 = ", x);

// Conditional statement
if (x > 10) {
    print("x is greater than 10");
} else {
    print("x is less than or equal to 10");
}

// Function definition
func greet(name) {
    return "Hello, " + name + "!";
}

// Function call
print(greet("Demon"));

// Lists
let numbers = [1, 1, 2, 3, 5, 8];
print("Fibonacci sequence:", numbers);

// For loop
print("Counting from 1 to 5:");
for (let i = 1; i <= 5; i = i + 1) {
    print(i);
}

// While loop
let count = 3;
print("Countdown:");
while (count > 0) {
    print(count);
    count = count - 1;
}
print("Blast off!");
```

## Getting Started

1. Ensure you have Python 3.7+ installed
2. Clone this repository
3. Run a Demon script: `python src/demon.py examples/hello.demon`

## Advanced Features

### Type Checking

Demon now includes an optional static type checker that can catch type errors before runtime:

```bash
# Enable type checking
python src/demon_cli.py --type-check examples/test_type_checker.demon
```

### Bytecode Compilation

Demon can now compile programs to bytecode and execute them in a virtual machine:

```bash
# Enable bytecode VM
python src/demon_cli.py --bytecode examples/test_bytecode.demon
```

### Standard Library

Demon includes a comprehensive standard library with math functions, string operations, data structures, and more:

```bash
# Run the standard library demo
python src/demon_cli.py examples/stdlib_demo.demon
```

### Package Manager

Demon has a built-in package manager for downloading, installing, and managing packages:

```bash
# Install a package (when registry is available)
python src/demon_cli.py --package install example-package

# List installed packages
python src/demon_cli.py --package list
```

### Debugger

Demon includes a full-featured debugger with breakpoints, stepping, variable inspection, and watch expressions:

```bash
# Debug a program
python src/demon_cli.py --debug examples/debug_test.demon
```

### Command-line Interface

Demon now has a command-line interface with various options:

```bash
# Show help
python src/demon_cli.py --help

# Start REPL
python src/demon_cli.py --repl

# Run with both type checking and bytecode VM
python src/demon_cli.py --type-check --bytecode examples/hello.demon
```

### IDE Support

Demon includes IDE integration with features like syntax highlighting, code completion, and error checking:

```bash
# Install the VS Code extension
cd src/ide_support/vscode
npm install
npm run compile
code --install-extension .

# Start the language server
python src/demon_cli.py --ide
```

The IDE support includes:
- Syntax highlighting
- Code completion
- Error checking and linting
- Code formatting
- Debugging integration
- Snippets for common code patterns

## Language Features

### Variables
```demon
let x = 10;           // Integer
let name = "Demon";   // String
let isActive = true;  // Boolean
```

### Control Flow
```demon
// If-else
if (x > 10) {
    print("Greater than 10");
} else if (x > 5) {
    print("Greater than 5");
} else {
    print("5 or less");
}

// While loop
let i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}

// For loop
for (let j = 0; j < 3; j = j + 1) {
    print(j);
}
```

### Functions
```demon
// Function definition
func add(a, b) {
    return a + b;
}

// Function call
let sum = add(5, 3);
print("Sum:", sum);
```

### Lists
```demon
let fruits = ["apple", "banana", "cherry"];
fruits.push("date");
print("Fruits:", fruits);
print("First fruit:", fruits[0]);
```

## Implementation

Demon is implemented in Python and includes:
- Lexical analyzer (scanner)
- Recursive descent parser
- Interpreter with runtime environment
- Support for variables, functions, and control flow

## Roadmap

- [x] Basic lexer and parser
- [x] Type checker
- [x] Bytecode compiler
- [x] Virtual Machine
- [x] Standard library
- [x] Package manager
- [x] Debugger
- [x] IDE support

