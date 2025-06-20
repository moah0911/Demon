# Demon Compilation Process

This document details the step-by-step process of how Demon code is compiled and executed.

## Overview

Demon uses a tree-walk interpreter that processes code in several distinct phases:

1. **Scanning** - Convert source text to tokens
2. **Parsing** - Convert tokens to an Abstract Syntax Tree (AST)
3. **Resolution** - Resolve variable references and scopes
4. **Interpretation** - Execute the AST

## Detailed Process

### 1. Scanning (Lexical Analysis)

The scanner reads the source code character by character and groups them into tokens:

```
Source: let x = 10 + 5;
Tokens: [LET, IDENTIFIER("x"), EQUAL, NUMBER(10), PLUS, NUMBER(5), SEMICOLON]
```

Key components:
- **Token Types**: Keywords, identifiers, literals, operators, etc.
- **Lexemes**: The actual text of the token
- **Literals**: The value for literals (numbers, strings)
- **Line Information**: For error reporting

### 2. Parsing (Syntax Analysis)

The parser takes the tokens and builds an Abstract Syntax Tree (AST) according to the grammar rules:

```
let x = 10 + 5;
```

Becomes:

```
VarStatement
├── name: "x"
└── initializer: BinaryExpression
    ├── left: NumberLiteral(10)
    ├── operator: PLUS
    └── right: NumberLiteral(5)
```

The parser uses recursive descent parsing with the following grammar rules:
- Expressions (binary, unary, literals, etc.)
- Statements (variable declarations, if/else, loops, etc.)
- Function and class declarations

### 3. Resolution (Static Analysis)

The resolver performs static analysis on the AST:

1. Tracks variable declarations and their scopes
2. Resolves variable references to their declarations
3. Detects variable usage errors (using before declaration, etc.)
4. Annotates the AST with scope information for the interpreter

```python
# When resolving a variable reference:
def visit_variable_expr(self, expr):
    if self.scopes and expr.name.lexeme in self.scopes[-1]:
        if self.scopes[-1][expr.name.lexeme] == False:
            self.demon.error(expr.name, "Cannot read local variable in its own initializer.")
    
    self.resolve_local(expr, expr.name)
    return None
```

### 4. Interpretation (Execution)

The interpreter walks the AST and executes each node:

1. For expressions, it evaluates and returns values
2. For statements, it executes side effects
3. It maintains an environment for variable storage
4. It handles function calls, object creation, etc.

```python
# When interpreting a binary expression:
def visit_binary_expr(self, expr):
    left = self.evaluate(expr.left)
    right = self.evaluate(expr.right)
    
    if expr.operator.type == TokenType.PLUS:
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left + right
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        # Handle other cases...
```

## Error Handling

Demon provides comprehensive error handling at each stage:

1. **Scanning Errors**: Invalid characters, unterminated strings
2. **Parsing Errors**: Invalid syntax, missing tokens
3. **Resolution Errors**: Variable scope issues, invalid references
4. **Runtime Errors**: Type errors, division by zero, etc.

Each error includes:
- Line number and position
- Descriptive error message
- Context information

## Performance Considerations

The tree-walk interpreter approach prioritizes clarity and flexibility over raw performance:

- **Pros**: Easy to implement, modify, and understand
- **Cons**: Slower than bytecode or native compilation

For a production language, this would be replaced with:
1. A bytecode compiler
2. A virtual machine
3. Optimization passes

## Example: Full Compilation Process

For the code:

```demon
func factorial(n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

print(factorial(5));
```

1. **Scanning**: Convert to tokens
2. **Parsing**: Build AST with function declaration and print statement
3. **Resolution**: Resolve the recursive call to `factorial`
4. **Interpretation**: Execute the function and print the result (120)

This process combines the flexibility of an interpreter with some of the safety guarantees of a compiler.