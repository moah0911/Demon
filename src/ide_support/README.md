# Demon IDE Support

This directory contains the IDE support components for the Demon programming language.

## Components

- **Language Server**: Implements the Language Server Protocol (LSP) for Demon
- **Code Completion**: Provides code completion suggestions
- **Syntax Highlighting**: Defines syntax highlighting rules
- **Formatter**: Formats Demon code
- **Linter**: Checks for errors and style issues
- **VSCode Extension**: Extension for Visual Studio Code

## Installation

### Prerequisites

- Python 3.6+
- Node.js 14+ (for VSCode extension)
- npm (for VSCode extension)

### Installing

Run the installation script:

```bash
cd /path/to/Demon/src/ide_support
chmod +x install.sh
./install.sh
```

This will:
1. Create a symbolic link for the language server
2. Build and package the VSCode extension

### Manual Installation

#### Language Server

Create a symbolic link to the language server:

```bash
ln -s /path/to/Demon/src/demon_cli.py ~/.local/bin/demon-language-server
chmod +x ~/.local/bin/demon-language-server
```

#### VSCode Extension

Build and install the VSCode extension:

```bash
cd /path/to/Demon/src/ide_support/vscode
npm install
npm run compile
npm run package
code --install-extension ./demon-language-1.0.0.vsix
```

## Troubleshooting

### Language Server Not Starting

Check if the language server is executable:

```bash
which demon-language-server
chmod +x $(which demon-language-server)
```

### VSCode Extension Not Working

- Check the VSCode output panel for errors (View > Output > Demon Language Server)
- Make sure the language server is installed and executable
- Check if the correct Python interpreter is being used

### Missing Features

If certain features like code completion or diagnostics are not working:

1. Check if the language server is running (`ps aux | grep demon-language-server`)
2. Restart the language server (Command Palette > Demon: Restart Language Server)
3. Check the language server logs (`cat demon_lsp.log`)

## Development

### Language Server

The language server is implemented in Python using the Language Server Protocol.

Main components:
- `language_server.py`: Entry point for the language server
- `language_server_impl.py`: Implementation of the language server
- `code_completion.py`: Code completion provider
- `linter.py`: Linting and diagnostics provider
- `formatter.py`: Code formatting provider

### VSCode Extension

The VSCode extension is implemented in TypeScript.

Main components:
- `extension.ts`: Entry point for the extension
- `package.json`: Extension manifest
- `syntaxes/demon.tmLanguage.json`: TextMate grammar for syntax highlighting
- `snippets/demon.json`: Code snippets

To build the extension:

```bash
cd /path/to/Demon/src/ide_support/vscode
npm install
npm run compile
```

To debug the extension:
1. Open the VSCode extension folder in VSCode
2. Press F5 to start debugging
3. A new VSCode window will open with the extension loaded