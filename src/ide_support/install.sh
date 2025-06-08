#!/bin/bash
# Install script for Demon IDE support

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install VS Code extension
cd vscode

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install Node.js and npm."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
npm install

# Compile TypeScript
echo "Compiling TypeScript..."
npm run compile

# Create VSIX package
echo "Creating VSIX package..."
npm run package

# Find the generated VSIX file
VSIX_FILE=$(find . -name "*.vsix" | head -n 1)

if [ -z "$VSIX_FILE" ]; then
    echo "Error: Failed to create VSIX package."
    exit 1
fi

# Install extension
echo "Installing VS Code extension..."
if command -v code &> /dev/null; then
    code --install-extension "$VSIX_FILE"
    echo "VS Code extension installed successfully."
else
    echo "Warning: VS Code command line tool not found. Please install the extension manually:"
    echo "  1. Open VS Code"
    echo "  2. Press Ctrl+Shift+P"
    echo "  3. Type 'Extensions: Install from VSIX'"
    echo "  4. Select the file: $VSIX_FILE"
fi

echo "Installation complete."