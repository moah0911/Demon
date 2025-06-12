# Contributing to Demon Programming Language

Thank you for your interest in contributing to the Demon programming language! This document provides guidelines for contributing to the project.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/moah0911/Demon.git
   cd Demon
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Project Structure

- **src/**: Source code for the language implementation
- **examples/**: Example Demon programs
- **tests/**: Test suite
- **docs/**: Documentation

## Coding Standards

- Follow PEP 8 style guidelines for Python code
- Use type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep lines under 100 characters when possible

## File Naming Conventions

1. **Core Language Files**: Use descriptive names for core components (e.g., `parser.py`, `interpreter.py`)
2. **Example Files**: Name examples after the feature they demonstrate (e.g., `calculator.demon`)
3. **Test Files**: Prefix with `test_` (e.g., `test_parser.py`)

### Avoid Ambiguous Naming

Do not use suffixes like `_simple`, `_enhanced`, or `_new` for permanent files. Instead:

- For different versions of the same feature, use version numbers or descriptive names
- For examples showing different complexity levels, use clear naming like `basic_calculator.demon` and `advanced_calculator.demon`
- For experimental features, use a dedicated `experimental/` directory

## Documentation

- Update the README.md when adding new features
- Document public APIs with docstrings
- Add examples for new language features
- Keep documentation in sync with code changes

## Testing

- Write tests for new features
- Ensure all tests pass before submitting a pull request
- Run tests with:
  ```bash
  python -m unittest discover tests
  ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests to ensure they pass
5. Update documentation as needed
6. Commit your changes (`git commit -am 'Add your feature'`)
7. Push to your branch (`git push origin feature/your-feature`)
8. Create a new Pull Request

## Example Organization

When adding new examples:

1. Place them in the `examples/` directory
2. Follow the naming conventions
3. Include comments explaining the code
4. Update the examples README.md if necessary

## Version Control Practices

- Make atomic commits (one feature/fix per commit)
- Write clear commit messages
- Reference issue numbers in commit messages when applicable

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## License

By contributing to Demon, you agree that your contributions will be licensed under the project's license.
