# Demon Programming Language Rules

This document outlines the syntax rules and conventions for the Demon programming language.

## Syntax Rules

### 1. Statements and Semicolons

All statements in Demon must end with a semicolon:

```demon
print("Hello, World!");
let x = 10;
```

### 2. Variables and Constants

- Variables are declared using the `let` keyword:
  ```demon
  let name = "John";
  let age = 30;
  ```

- Constants are declared using the `const` keyword:
  ```demon
  const PI = 3.14159;
  const MAX_SIZE = 100;
  ```

### 3. Data Types

Demon supports the following primitive data types:
- Numbers: `10`, `3.14`
- Strings: `"Hello"`, `'World'`
- Booleans: `true`, `false`
- Null: `nil`
- Arrays: `[1, 2, 3]`
- Objects: `{"name": "John", "age": 30}`

### 4. Functions

Functions are defined using the `func` keyword:

```demon
func add(a, b) {
    return a + b;
}
```

Anonymous functions can be defined using arrow syntax:

```demon
let double = (x) => x * 2;
```

### 5. Control Flow

#### Conditionals

```demon
if (condition) {
    // code
} else if (another_condition) {
    // code
} else {
    // code
}
```

#### Loops

While loops:

```demon
while (condition) {
    // code
}
```

### 6. Operators

#### Arithmetic Operators
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulo: `%`

#### Comparison Operators
- Equal to: `==`
- Not equal to: `!=`
- Greater than: `>`
- Less than: `<`
- Greater than or equal to: `>=`
- Less than or equal to: `<=`

#### Logical Operators
- AND: `&&` (not `and`)
- OR: `||` (not `or`)
- NOT: `!`

### 7. String Operations

String concatenation uses the `+` operator:

```demon
let greeting = "Hello, " + name + "!";
```

### 8. Comments

Single-line comments start with `//`:

```demon
// This is a comment
let x = 10; // This is also a comment
```

### 9. Arrays

Arrays are defined using square brackets:

```demon
let numbers = [1, 2, 3, 4, 5];
```

### 10. Objects

Objects are defined using curly braces:

```demon
let person = {
    "name": "John",
    "age": 30
};
```

## Common Pitfalls to Avoid

1. **Don't use `and` and `or`** - Use `&&` and `||` instead
2. **Don't use template literals** - Use string concatenation with `+` instead
3. **Don't use object property access with dot notation** - This is not supported yet
4. **Don't use array indexing with brackets** - This is not supported yet
5. **Don't use for loops** - Use while loops instead
6. **Don't concatenate arrays with strings** - Convert array elements to strings first

## Standard Library Functions

- `print()` - Print values to the console
- `len()` - Get the length of a string or array
- `sin()`, `cos()`, `tan()` - Trigonometric functions
- `sqrt()` - Square root function
- `pow()` - Power function

## Best Practices

1. Use meaningful variable and function names
2. Add comments to explain complex logic
3. Break down complex functions into smaller, reusable functions
4. Use consistent indentation (2 or 4 spaces)
5. Always include semicolons at the end of statements