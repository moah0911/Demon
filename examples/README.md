# Demon Programming Language Examples

This directory contains example programs written in the Demon programming language to demonstrate its features and capabilities.

## Basic Examples

- **hello.demon**: Basic "Hello World" program demonstrating core language features including variables, functions, conditionals, loops, and lists.
- **calculator.demon**: A simple calculator implementation showing arithmetic operations and user input.
- **factorial.demon**: Demonstrates recursive function calls by calculating factorials.
- **fibonacci.demon**: Shows how to generate Fibonacci sequences using loops and recursion.

## Testing Examples

- **test_expressions.demon**: Tests various expression types and operators in the language.
- **test_bytecode.demon**: Demonstrates the bytecode compilation and virtual machine execution.
- **test_type_checker.demon**: Shows the optional static type checking functionality.

## Advanced Features

- **object_demo.demon**: Comprehensive demonstration of object-oriented programming features including property access, nested objects, method chaining, and factory functions.
- **stdlib_demo.demon**: Shows the standard library functions including math operations, string manipulation, list operations, and data structures.

## Development Tools

- **debug_test.demon**: Example program for testing the debugger functionality.
- **ide_test.demon**: Example for testing IDE integration features.

## Naming Convention

Files in this directory follow these naming conventions:

1. Feature demonstration files are named after the feature they demonstrate (e.g., `calculator.demon`, `fibonacci.demon`).
2. Test files are prefixed with `test_` (e.g., `test_expressions.demon`).
3. Files with similar content but different complexity levels use suffixes:
   - No suffix: Standard implementation (e.g., `stdlib_demo.demon`)
   - `_enhanced`: Extended version with more features (e.g., `stdlib_demo_enhanced.demon`)

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