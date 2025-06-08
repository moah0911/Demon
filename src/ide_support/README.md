# Demon IDE Support

This directory contains the IDE support components for the Demon programming language.

## Components

- **Language Server**: Implements the Language Server Protocol (LSP) for IDE integration
- **Code Completion**: Provides intelligent code completion
- **Syntax Highlighting**: Defines syntax highlighting rules
- **Formatter**: Formats Demon code according to style guidelines
- **Linter**: Checks for errors and style issues
- **VS Code Extension**: Extension for Visual Studio Code

## Installation

### VS Code Extension

To install the VS Code extension:

```bash
# Run the installation script
./install.sh
```

### Using the Language Server

The language server can be started in two ways:

1. **From the CLI**:
   ```bash
   python src/demon_cli.py --ide
   ```

2. **From the VS Code extension**:
   The extension will automatically start the language server when you open a `.demon` file.

## Testing

To test the language server without an IDE:

```bash
# Start the language server in one terminal
python src/demon_cli.py --ide

# Run the test script in another terminal
python src/ide_support/test_server.py
```

## Troubleshooting

If you encounter issues with the language server:

1. **Unicode decode errors**: The server now handles these gracefully
2. **Connection issues**: Make sure the server is running on the expected port (default: 8123)
3. **VS Code extension errors**: Check the extension output in VS Code (View > Output > Demon Language Server)

If the VS Code extension fails to install:

1. Build the VSIX package manually:
   ```bash
   cd vscode
   npm install
   npm run compile
   npm run package
   ```

2. Install the VSIX package in VS Code:
   - Press Ctrl+Shift+P
   - Type "Extensions: Install from VSIX"
   - Select the generated .vsix file

## Development

To modify or extend the IDE support:

1. **Language Server**: Edit `language_server_impl.py` to add new LSP features
2. **Code Completion**: Modify `code_completion.py` to improve suggestions
3. **Syntax Highlighting**: Update `syntax_highlighter.py` and VS Code grammar files
4. **Formatter**: Change `formatter.py` to adjust formatting rules
5. **Linter**: Enhance `linter.py` to add new checks
6. **VS Code Extension**: Edit files in the `vscode` directory