#!/bin/bash
# Installation script for Demon IDE support

echo "Installing Demon IDE support..."

# Create symbolic link for language server
if [ -f ~/.local/bin/demon-language-server ]; then
    echo "Removing existing language server link..."
    rm ~/.local/bin/demon-language-server
fi

echo "Creating language server link..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ln -s "$SCRIPT_DIR/../demon_cli.py" ~/.local/bin/demon-language-server
chmod +x ~/.local/bin/demon-language-server

# Install VSCode extension
echo "Installing VSCode extension..."
cd "$SCRIPT_DIR/vscode"
npm install
npm run compile
npm run package

echo "VSCode extension package created at $SCRIPT_DIR/vscode/demon-language-1.0.0.vsix"
echo "To install the extension in VSCode, run:"
echo "code --install-extension $SCRIPT_DIR/vscode/demon-language-1.0.0.vsix"

echo "Demon IDE support installation complete!"