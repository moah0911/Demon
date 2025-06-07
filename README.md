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
- [ ] Type checker
- [ ] Bytecode compiler
- [ ] Virtual Machine
- [ ] Standard library
- [ ] Package manager
- [ ] Debugger
- [ ] IDE support

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.
