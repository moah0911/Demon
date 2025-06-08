# Demon Programming Language File Organization

This document describes the file organization and naming conventions for the Demon programming language project.

## Directory Structure

```
Demon/
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md    # Architecture overview
│   ├── EXAMPLES.md        # Examples guide
│   └── FILE_ORGANIZATION.md  # This file
├── examples/              # Example programs
│   ├── basic/             # Basic language examples
│   ├── advanced/          # Advanced feature examples
│   └── testing/           # Test programs
├── src/                   # Source code
│   ├── core/              # Core language implementation
│   ├── stdlib/            # Standard library
│   ├── tools/             # Development tools
│   └── ide_support/       # IDE integration
├── tests/                 # Test suite
├── CONTRIBUTING.md        # Contribution guidelines
├── LICENSE                # License information
└── README.md              # Project overview
```

## File Naming Conventions

### Source Code Files

1. **Core Components**: Named after their function
   - `demon.py`: Main entry point
   - `parser.py`: Parser implementation
   - `interpreter.py`: Interpreter implementation

2. **Module Files**: Named after the module they implement
   - `stdlib.py`: Standard library
   - `debugger.py`: Debugger implementation
   - `package_manager.py`: Package manager

3. **Support Files**: Named descriptively
   - `tokens.py`: Token definitions
   - `demon_ast.py`: AST node definitions

### Example Files

1. **Basic Examples**: Named after the feature they demonstrate
   - `hello.demon`: Hello world example
   - `calculator.demon`: Calculator example
   - `factorial.demon`: Factorial calculation

2. **Test Files**: Prefixed with `test_`
   - `test_expressions.demon`: Tests expressions
   - `test_bytecode.demon`: Tests bytecode compilation
   - `test_type_checker.demon`: Tests type checking

## Reorganization Plan

To improve the organization and documentation of the project, the following changes are recommended:

### 1. Reorganize Examples

Move example files into subdirectories based on their purpose:

```bash
mkdir -p examples/basic examples/advanced examples/testing
```

- Move basic examples to `examples/basic/`
- Move advanced examples to `examples/advanced/`
- Move test examples to `examples/testing/`

### 2. Consolidate Similar Files

Instead of having multiple versions of the same example (e.g., `stdlib_demo.demon` and `stdlib_demo_enhanced.demon`), create a single comprehensive example with clear sections.

### 3. Improve Documentation

- Add header comments to all source files explaining their purpose
- Create README files in each directory explaining its contents
- Add inline documentation for complex code sections

### 4. Standardize File Names

Replace ambiguous suffixes like `_simple`, `_enhanced`, and `_new` with more descriptive names:

- `object_demo_simple.demon` → `object_basics.demon`
- `stdlib_demo_enhanced.demon` → `stdlib_advanced.demon`
- `interpreter.py.new` → Merge into `interpreter.py` or rename to `interpreter_experimental.py`

## Implementation Guidelines

When implementing new features or examples:

1. **Choose the Right Location**: Place files in the appropriate directory based on their purpose
2. **Use Descriptive Names**: Choose names that clearly indicate the file's purpose
3. **Avoid Ambiguous Suffixes**: Don't use suffixes like `_simple`, `_enhanced`, or `_new`
4. **Document Purpose**: Include a header comment explaining the file's purpose
5. **Update Documentation**: Update relevant documentation files when adding new files

## Version Control Practices

1. **Commit Messages**: Include the file organization changes in commit messages
2. **Atomic Commits**: Make separate commits for file reorganization and content changes
3. **Documentation Updates**: Update documentation when changing file organization

## Conclusion

Following these file organization guidelines will improve the project's maintainability, readability, and usability. The consistent naming conventions and clear directory structure will make it easier for contributors to understand and navigate the codebase.