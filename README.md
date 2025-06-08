# Demon Programming Language

<div align="center">
  <img src="https://via.placeholder.com/200x200?text=Demon" alt="Demon Logo" width="200" height="200">
  <h3>A modern, expressive programming language</h3>
</div>

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
- **Object-Oriented** - Classes, inheritance, and methods
- **Data Structures** - Lists, maps, and more
- **Control Flow** - If/else, while loops, and blocks
- **Error Handling** - Graceful error handling patterns

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/demon.git
cd demon

# Run a Demon script
python run.py examples/basic/hello_fixed.demon
```

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
print("List:", numbers);

// Maps
let person = {"name": "John", "age": 30};
```

### Classes and Objects

```demon
class Point {
    init(x, y) {
        this.x = x;
        this.y = y;
    }
    
    distance() {
        return sqrt(this.x * this.x + this.y * this.y);
    }
    
    toString() {
        return "Point(" + this.x + ", " + this.y + ")";
    }
}

let p = Point(3, 4);
print(p.toString());         // Outputs: Point(3, 4)
print(p.distance());         // Outputs: 5.0
```

## Running the REPL

```bash
python run.py
```

## License

MIT License

## Acknowledgments

- Inspired by the book "Crafting Interpreters" by Robert Nystrom
- Thanks to all contributors who have helped shape Demon