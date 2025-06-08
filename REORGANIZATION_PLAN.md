# Demon Programming Language Reorganization Plan

This document outlines a plan to reorganize the Demon programming language project to improve its structure, documentation, and maintainability.

## Current Issues

1. **Inconsistent File Naming**: Files with suffixes like `_simple`, `_enhanced`, and `_new` make the codebase harder to navigate
2. **Flat Directory Structure**: All examples are in a single directory without categorization
3. **Incomplete Documentation**: Some components and examples lack proper documentation
4. **Duplicate Functionality**: Multiple files with similar content but slight variations

## Reorganization Steps

### 1. Directory Structure Improvement

Create a more organized directory structure:

```bash
# Create new directories
mkdir -p examples/basic examples/advanced examples/testing
mkdir -p src/core src/stdlib src/tools
mkdir -p docs/api docs/tutorials
```

### 2. File Reorganization

Move files to appropriate directories based on their purpose:

```bash
# Move basic examples
mv examples/hello.demon examples/basic/
mv examples/calculator.demon examples/basic/
mv examples/factorial.demon examples/basic/
mv examples/fibonacci.demon examples/basic/

# Move advanced examples
mv examples/object_demo.demon examples/advanced/
mv examples/stdlib_demo.demon examples/advanced/

# Move testing examples
mv examples/test_*.demon examples/testing/
mv examples/debug_test.demon examples/testing/
mv examples/ide_test.demon examples/testing/
```

### 3. File Renaming

Rename files with ambiguous suffixes to more descriptive names:

```bash
# Rename ambiguous files
mv examples/advanced/object_demo_simple.demon examples/basic/object_basics.demon
mv examples/advanced/stdlib_demo_enhanced.demon examples/advanced/stdlib_complete.demon
```

### 4. Source Code Organization

Organize source code files:

```bash
# Move core language files
mv src/demon.py src/core/
mv src/tokens.py src/core/
mv src/demon_ast.py src/core/
mv src/parser.py src/core/
mv src/resolver.py src/core/
mv src/interpreter.py src/core/

# Move standard library files
mv src/stdlib.py src/stdlib/

# Move tool files
mv src/demon_cli.py src/tools/
mv src/debugger.py src/tools/
mv src/package_manager.py src/tools/

# Handle backup/alternative files
# Review and merge or delete .bak and .new files
```

### 5. Documentation Improvement

Create comprehensive documentation:

```bash
# Create main documentation files
touch docs/README.md
touch docs/api/README.md
touch docs/tutorials/getting_started.md
touch docs/tutorials/advanced_features.md
```

## Implementation Timeline

1. **Phase 1: Documentation** (Week 1)
   - Create documentation files
   - Document file organization plan
   - Update existing README files

2. **Phase 2: Example Reorganization** (Week 2)
   - Create new directory structure for examples
   - Move and rename example files
   - Update example documentation

3. **Phase 3: Source Code Reorganization** (Week 3)
   - Create new directory structure for source code
   - Move and rename source files
   - Update import statements and references

4. **Phase 4: Testing and Validation** (Week 4)
   - Test all examples after reorganization
   - Verify all functionality works as expected
   - Fix any issues that arise

## File Naming Guidelines

### Source Code Files

- Use descriptive names that indicate the file's purpose
- Use lowercase with underscores for Python files
- Avoid version-indicating suffixes like `_v2` or `_new`

### Example Files

- Use descriptive names that indicate what the example demonstrates
- Group related examples in appropriate directories
- Use a consistent naming scheme within each category

## Documentation Guidelines

- Each directory should have a README.md file explaining its contents
- Each source file should have a header comment explaining its purpose
- Examples should include comments explaining key concepts

## Conclusion

This reorganization will improve the project's maintainability, readability, and usability. By following consistent naming conventions and creating a clear directory structure, we'll make it easier for contributors to understand and navigate the codebase.