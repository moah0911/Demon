<p align="center">
  <img src="Demon.png" alt="Demon Logo" width="200"/>
</p>

# Demon Language

Welcome to the official repository for the Demon programming language, a simple, dynamic, and object-oriented scripting language implemented in Rust.

## Features

*   **Dynamic Typing:** Variables are dynamically typed.
*   **Familiar Syntax:** C-style syntax that is easy to learn for developers coming from languages like C++, Java, or JavaScript.
*   **Object-Oriented:** Supports classes, methods, and inheritance.
*   **First-Class Functions:** Functions are first-class citizens and can be passed around like any other value.
*   **Garbage Collection:** Automatic memory management using a simple garbage collector.
*   **Tree-Walk Interpreter:** A straightforward and easy-to-understand interpreter implementation.

## Getting Started

### Prerequisites

*   [Rust](https://www.rust-lang.org/tools/install) (latest stable version)
*   For Windows users, [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) are required.

### Installation

We provide simple installation scripts for both Linux/macOS and Windows.

#### Linux and macOS

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/moah0911/Demon.git
    cd Demon/
    ```

2.  **Run the installation script:**
    ```sh
    chmod +x install.sh
    ./install.sh
    ```
    This will build the interpreter and install it to `$HOME/.local/bin`.

3.  **Update your PATH:**
    Add the following line to your shell's configuration file (e.g., `~/.zshrc` or `~/.bashrc`):
    ```sh
    export PATH="$HOME/.local/bin:$PATH"
    ```
    Then, restart your terminal or run `source ~/.zshrc` (or your shell's equivalent).

#### Windows

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/moah0911/Demon.git
    cd Demon/demon-lang
    ```

2.  **Run the installation script:**
    ```powershell
    .\install.bat
    ```
    This will build the interpreter and add it to your user's `PATH`.

### Hello, World!

Create a file named `hello.dm` with the following content:

```demon
print("Hello, World!");
```

Once installed, you can run it from your terminal:

```sh
demon hello.dm
```

## Next Steps

For a deeper dive into the language features, check out the example scripts in the `examples/` directory. They cover everything from basic control flow to classes and inheritance.
