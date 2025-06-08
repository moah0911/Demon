# Demon Programming Language Examples Guide

This document provides a comprehensive guide to the example programs included with the Demon programming language.

## Basic Examples

### Hello World (`hello.demon`)

The classic "Hello World" program demonstrates basic syntax, variables, functions, conditionals, and loops:

```demon
// Hello World in Demon
print("Hello, World!");

// Variables and arithmetic
let x = 5 + 3 * 2;
print("5 + 3 * 2 = ", x);

// Functions
func greet(name) {
    return "Hello, " + name + "!";
}
```

### Calculator (`calculator.demon`)

A simple calculator that demonstrates user input, arithmetic operations, and control flow:

```demon
// Simple calculator
print("Demon Calculator");
let num1 = parseFloat(input("Enter first number: "));
let num2 = parseFloat(input("Enter second number: "));
let op = input("Enter operation (+, -, *, /): ");

if (op == "+") {
    print(num1 + num2);
} else if (op == "-") {
    print(num1 - num2);
} else if (op == "*") {
    print(num1 * num2);
} else if (op == "/") {
    print(num1 / num2);
} else {
    print("Invalid operation");
}
```

### Factorial (`factorial.demon`)

Demonstrates recursive function calls:

```demon
func factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

print(factorial(5));  // 120
```

### Fibonacci (`fibonacci.demon`)

Shows both iterative and recursive approaches to generating Fibonacci numbers:

```demon
// Iterative Fibonacci
func fibonacci_iterative(n) {
    if (n <= 1) return n;
    
    let a = 0;
    let b = 1;
    let result = 0;
    
    for (let i = 2; i <= n; i = i + 1) {
        result = a + b;
        a = b;
        b = result;
    }
    
    return result;
}

// Recursive Fibonacci
func fibonacci_recursive(n) {
    if (n <= 1) return n;
    return fibonacci_recursive(n - 1) + fibonacci_recursive(n - 2);
}
```

## Advanced Examples

### Object Demo (`object_demo.demon`)

Demonstrates object-oriented programming features:

- Object creation and property access
- Method definition and invocation
- Nested objects
- Factory functions
- Method chaining

### Standard Library Demo (`stdlib_demo.demon`)

Shows the standard library functions:

- Math operations
- String manipulation
- List operations
- Higher-order functions
- Data structures (Stack, Queue, Set, Graph)

The enhanced version (`stdlib_demo_enhanced.demon`) includes additional features:

- More math functions
- Advanced string operations
- Dictionary functions
- Functional programming utilities
- Additional data structures (Priority Queue, Tree)

## Testing Examples

### Expression Tests (`test_expressions.demon`)

Tests various expression types and operators:

- Arithmetic expressions
- Logical expressions
- Comparison operators
- Operator precedence

### Bytecode Tests (`test_bytecode.demon`)

Demonstrates the bytecode compilation and virtual machine execution.

### Type Checker Tests (`test_type_checker.demon`)

Shows the optional static type checking functionality.

## Development Tool Examples

### Debug Test (`debug_test.demon`)

Example program for testing the debugger functionality:

- Breakpoints
- Variable inspection
- Step-by-step execution

### IDE Test (`ide_test.demon`)

Example for testing IDE integration features:

- Code completion
- Error highlighting
- Hover information

## Running Examples

To run any example:

```bash
python src/demon_cli.py examples/hello.demon
```

With type checking enabled:

```bash
python src/demon_cli.py --type-check examples/test_type_checker.demon
```

Using the bytecode VM:

```bash
python src/demon_cli.py --bytecode examples/test_bytecode.demon
```

In debug mode:

```bash
python src/demon_cli.py --debug examples/debug_test.demon
```