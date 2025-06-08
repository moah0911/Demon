# Demon Programming Language Architecture

This document describes the architecture of the Demon programming language implementation.

## Overview

Demon is implemented as a tree-walk interpreter with optional bytecode compilation and virtual machine execution. The implementation follows a traditional compiler/interpreter architecture with the following phases:

1. **Lexical Analysis**: Converting source code into tokens
2. **Parsing**: Converting tokens into an Abstract Syntax Tree (AST)
3. **Resolution**: Resolving variable references and scopes
4. **Execution**: Either interpreting the AST directly or compiling to bytecode and executing in a VM

## Core Components

### Scanner (`demon.py`)

The scanner (lexer) breaks the source code into tokens. Each token has:
- A type (e.g., identifier, number, string, operator)
- The lexeme (the actual text)
- A literal value (for numbers and strings)
- A line number

The scanner handles:
- Keywords
- Identifiers
- Numbers (integers and floats)
- Strings
- Operators
- Comments
- Whitespace

### Parser (`parser.py`)

The parser implements a recursive descent parser that converts tokens into an Abstract Syntax Tree (AST). It handles:
- Expressions (arithmetic, logical, etc.)
- Statements (variable declarations, control flow, etc.)
- Error recovery

### AST Nodes (`demon_ast.py`)

The AST nodes represent the structure of the program. Types include:
- Expression nodes (literals, variables, binary operations, etc.)
- Statement nodes (variable declarations, if statements, loops, etc.)

### Resolver (`resolver.py`)

The resolver performs static analysis on the AST:
- Resolves variable references to their declarations
- Detects variable shadowing
- Validates variable usage
- Prepares for efficient variable lookup during execution

### Interpreter (`interpreter.py`)

The interpreter evaluates the AST to execute the program:
- Manages variable environments and scopes
- Evaluates expressions
- Executes statements
- Handles function calls and returns
- Implements built-in functions

### Type Checker (`type_checker.py`)

The optional type checker performs static type analysis:
- Infers types for expressions
- Validates type compatibility
- Reports type errors before runtime

### Bytecode Compiler (`bytecode.py`)

The bytecode compiler converts the AST to bytecode instructions:
- Generates efficient bytecode
- Optimizes common patterns
- Manages constants and variables

### Virtual Machine (`vm.py`)

The VM executes bytecode instructions:
- Maintains a stack for operands
- Manages call frames for functions
- Executes instructions efficiently
- Handles runtime errors

## Standard Library (`stdlib.py`)

The standard library provides built-in functions and data structures:
- Math functions
- String operations
- List operations
- Higher-order functions
- Data structures (Stack, Queue, Set, Graph, etc.)

## Development Tools

### Command-Line Interface (`demon_cli.py`)

The CLI provides various options for running Demon programs:
- Running scripts
- REPL mode
- Type checking
- Bytecode VM
- Debugging
- Package management

### Debugger (`debugger.py`)

The debugger allows interactive debugging:
- Setting breakpoints
- Stepping through code
- Inspecting variables
- Watching expressions

### Package Manager (`package_manager.py`)

The package manager handles external libraries:
- Installing packages
- Uninstalling packages
- Updating packages
- Listing installed packages
- Searching for packages

## IDE Support

The IDE support components provide integration with code editors:
- Language Server Protocol implementation
- Code completion
- Error checking
- Syntax highlighting
- Code formatting

## Data Flow

1. Source code is read from a file or input
2. Scanner converts source code to tokens
3. Parser converts tokens to an AST
4. Resolver resolves variable references
5. (Optional) Type checker validates types
6. Execution:
   - Interpreter evaluates the AST directly, or
   - Bytecode compiler compiles the AST to bytecode, which is executed by the VM

## Error Handling

Errors are handled at different stages:
- **Scanning errors**: Invalid characters, unterminated strings
- **Parsing errors**: Invalid syntax, unexpected tokens
- **Resolution errors**: Undefined variables, invalid variable usage
- **Type errors**: Type mismatches, invalid operations
- **Runtime errors**: Division by zero, undefined properties, etc.

## Future Directions

Potential areas for future development:
- Just-In-Time (JIT) compilation
- Optimizations for common patterns
- Parallel execution
- Native code generation
- Enhanced type system