# Build the project in release mode
Write-Host "Building Demon language interpreter..."
cargo build --release

# Create output directory
$OutputDir = "target\release\package"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# Copy the binary
Copy-Item "target\release\Demon.exe" -Destination $OutputDir

# Create a simple runner script
@"
@echo off
setlocal
set SCRIPT_DIR=%~dp0
"%SCRIPT_DIR%\Demon.exe" %*
"@ | Out-File -FilePath "$OutputDir\run-demo.bat" -Encoding ASCII

# Create a README
@"
# Demon Language Interpreter

## Installation

1. Make sure you have the required dependencies installed:
   - Rust (1.60+)
   - Cargo
   - Visual Studio Build Tools (for Windows)

2. Run the interpreter:
   ```
   .\run-demo.bat [script.dm]
   ```

## Usage

Run a script:
```
.\run-demo.bat examples\hello.dm
```

Start the REPL:
```
.\run-demo.bat
```

## Building from Source

```
cargo build --release
```

The binary will be available at `target\release\demon-lang.exe`
"@ | Out-File -FilePath "$OutputDir\README.md" -Encoding UTF8

Write-Host "Build complete! Find the packaged files in: $((Resolve-Path $OutputDir).Path)"
Write-Host "To run the interpreter: $((Resolve-Path $OutputDir).Path)\run-demo.bat"
