#!/bin/bash

# Exit on error
set -e

# Build the project in release mode
echo "Building Demon language interpreter..."
cargo build --release

# Create output directory
OUTPUT_DIR="target/release/package"
mkdir -p "$OUTPUT_DIR"

# Copy the binary
cp "target/release/Demon" "$OUTPUT_DIR/"

# Create a simple runner script
cat > "$OUTPUT_DIR/run-demo.sh" << 'EOF'
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
"$DIR/Demon" "$@"
EOF
chmod +x "$OUTPUT_DIR/run-demo.sh"

# Create a README
cat > "$OUTPUT_DIR/README.md" << 'EOF'
# Demon Language Interpreter

## Installation

1. Make sure you have the required dependencies installed:
   - Rust (1.60+)
   - Cargo

2. Run the interpreter:
   ```bash
   ./run-demo.sh [script.dm]
   ```

## Usage

Run a script:
```bash
./run-demo.sh examples/hello.dm
```

Start the REPL:
```bash
./run-demo.sh
```

## Building from Source

```bash
cargo build --release
```

The binary will be available at `target/release/demon-lang`
EOF

echo "Build complete! Find the packaged files in: $OUTPUT_DIR"
echo "To run the interpreter: $OUTPUT_DIR/run-demo.sh"
