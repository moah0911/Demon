#!/bin/bash

# Exit on error
set -e

# Build the project in release mode
echo "Building Demon language interpreter..."
cargo build --release

# Define the installation directory
INSTALL_DIR="$HOME/.local/bin"

# Create the installation directory if it doesn't exist
echo "Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Copy the binary to the installation directory (using lowercase 'demon' for convention)
echo "Installing demon executable..."
cp "target/release/Demon" "$INSTALL_DIR/demon"

# Make the binary executable
chmod +x "$INSTALL_DIR/demon"

# Provide instructions to the user
echo ""
echo "Installation complete!"
echo ""
echo "To run the 'demon' command from anywhere, you need to add the installation directory to your PATH."
echo "Add the following line to your shell configuration file (e.g., ~/.zshrc, ~/.bashrc):"
echo ""
echo '  export PATH="$HOME/.local/bin:$PATH"'
echo ""
echo "After adding the line, restart your terminal or run 'source ~/.zshrc' (or your shell's equivalent)."
