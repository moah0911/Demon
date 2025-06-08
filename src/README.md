# Demon Programming Language Source Code

This directory contains the source code for the Demon programming language interpreter, compiler, and related tools.

## Core Components

### Language Implementation

- **demon.py**: Main entry point for the Demon language interpreter
- **tokens.py**: Token definitions and token types
- **demon_ast.py**: Abstract Syntax Tree node definitions
- **parser.py**: Parser that converts tokens into an AST
- **resolver.py**: Variable resolution and scope analysis
- **interpreter.py**: Evaluates the AST to execute programs

### Advanced Features

- **type_checker.py**: Optional static type checking
- **bytecode.py**: Bytecode compiler
- **vm.py**: Virtual machine for executing bytecode
- **stdlib.py**: Standard library implementation

### Tools

- **demon_cli.py**: Command-line interface with various options
- **debugger.py**: Interactive debugger
- **package_manager.py**: Package management system

## IDE Support

The `ide_support/` directory contains tools for IDE integration:

- **language_server.py**: Language Server Protocol implementation
- **code_completion.py**: Code completion functionality
- **formatter.py**: Code formatting
- **linter.py**: Linting and error checking
- **syntax_highlighter.py**: Syntax highlighting rules

### VS Code Extension

The `ide_support/vscode/` directory contains a VS Code extension for Demon:

- **extension.ts**: Extension entry point
- **language-configuration.json**: Language configuration
- **syntaxes/demon.tmLanguage.json**: TextMate grammar for syntax highlighting
- **snippets/demon.json**: Code snippets

## Architecture

The Demon language implementation follows a traditional compiler/interpreter architecture:

1. **Lexical Analysis**: The scanner in `demon.py` converts source code into tokens
2. **Parsing**: The parser in `parser.py` converts tokens into an AST
3. **Resolution**: The resolver in `resolver.py` resolves variable references
4. **Execution**: Either:
   - The interpreter in `interpreter.py` evaluates the AST directly
   - The bytecode compiler in `bytecode.py` compiles the AST to bytecode, which is then executed by the VM in `vm.py`

## File Organization

- **Core Files**: Essential files for the basic language functionality
- **Advanced Features**: Optional components that extend the language
- **Tools**: Utilities for development and usage
- **IDE Support**: Files for editor integration

## Development Guidelines

1. Keep core language features in the main source files
2. Add new standard library functions to `stdlib.py`
3. Maintain backward compatibility when adding new features
4. Add appropriate tests for new functionality
5. Update documentation when changing language behavior