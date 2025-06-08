# Demon Language Support for VS Code

This extension provides language support for the Demon programming language in Visual Studio Code.

## Features

- Syntax highlighting
- Code completion
- Error checking and linting
- Code formatting
- Debugging integration
- Snippets for common code patterns

## Requirements

- Visual Studio Code 1.60.0 or newer
- Python 3.7 or newer with the Demon language installed

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Demon Language"
4. Click Install

### From Source

1. Clone the Demon repository
2. Navigate to the VS Code extension directory:
   ```bash
   cd src/ide_support/vscode
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Compile the extension:
   ```bash
   npm run compile
   ```
5. Install the extension:
   ```bash
   code --install-extension .
   ```

## Usage

1. Open a `.demon` file or create a new file and save it with the `.demon` extension
2. The language server will start automatically
3. Enjoy features like syntax highlighting, code completion, and error checking

## Commands

- `Demon: Restart Language Server` - Restart the Demon language server
- `Demon: Run Type Checker` - Run the type checker on the current file
- `Demon: Format Document` - Format the current document

## Settings

- `demon.enable`: Enable/disable Demon language support
- `demon.languageServer.enable`: Enable/disable Demon language server
- `demon.typeChecking.enable`: Enable/disable type checking
- `demon.formatting.enable`: Enable/disable code formatting
- `demon.formatting.tabSize`: Number of spaces per tab
- `demon.formatting.insertSpaces`: Insert spaces instead of tabs
- `demon.formatting.bracesOnNewLine`: Place opening braces on a new line
- `demon.linting.enable`: Enable/disable linting

## Troubleshooting

If the language server fails to start:

1. Make sure Python is installed and in your PATH
2. Make sure the Demon language is installed
3. Try restarting VS Code
4. Check the Output panel (View > Output) and select "Demon Language Server" from the dropdown

## License

This extension is licensed under the same license as the Demon language.