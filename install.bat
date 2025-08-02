@echo off
setlocal

REM =============================================================================
REM  Demon Language One-Click Installer for Windows
REM =============================================================================

REM --- Check for Rust installation ---
echo Checking for Rust (rustc)...
where rustc >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Rust is not installed or not found in your system's PATH.
    echo Please install Rust from https://www.rust-lang.org/tools/install and try again.
    echo.
    pause
    exit /b 1
)
echo Rust found.

REM --- Build the project using Cargo ---
echo.
echo Building the Demon interpreter... this may take a few moments.

REM Assuming this script is run from the root of the repository
cargo build --release
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The build failed. Please review the error messages from Cargo above.
    echo.
    pause
    exit /b 1
)
echo Build successful!

REM --- Add the binary to the user's PATH ---
echo.
echo Adding the Demon interpreter to your user PATH...

set "DEMON_INSTALL_DIR=%cd%\target\release"

REM Use setx to permanently modify the user's PATH.
REM This command appends the directory if it's not already there.
setx PATH "%%PATH%%;%DEMON_INSTALL_DIR%" >nul

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Failed to automatically add Demon to your PATH.
    echo This can happen if the script is not run with sufficient privileges.
    echo.
    echo You can add it manually by adding the following directory to your Environment Variables:
    echo %DEMON_INSTALL_DIR%
    echo.
) else (
    echo Demon has been added to your PATH.
)

REM --- Final success message ---
echo.
echo ==================================================
echo  Demon Language has been successfully installed!
echo ==================================================
echo.
echo You can now open a NEW terminal and run the 'demon' command.

echo To test the installation, try running one of the examples:

echo   demon examples\fibonacci.dm

echo.
pause
