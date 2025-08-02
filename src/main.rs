use clap::Parser;
use demon::{self, new_interpreter, Interpreter};
use log::info;
use std::error::Error;
use std::fs;
use std::path::PathBuf;

/// Demon Programming Language Interpreter
#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// The script file to execute
    script: Option<PathBuf>,

    /// Enables debug mode
    #[clap(short, long)]
    debug: bool,
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();

    if args.debug {
        std::env::set_var("RUST_LOG", "debug");
    } else {
        std::env::set_var("RUST_LOG", "info");
    }
    pretty_env_logger::init();

    let mut interpreter = new_interpreter();

    if let Some(script_path) = args.script {
        run_file(script_path.to_str().unwrap(), &mut interpreter)?;
    } else {
        run_prompt(&mut interpreter)?;
    }
    Ok(())
}

/// Runs the Demon script from a file
fn run_file(path: &str, interpreter: &mut Interpreter) -> Result<(), Box<dyn Error>> {
    let source = fs::read_to_string(path)?;
    run(interpreter, &source)?;
    Ok(())
}

/// Starts the Demon REPL (Read-Eval-Print Loop)
fn run_prompt(interpreter: &mut Interpreter) -> Result<(), Box<dyn Error>> {
    let mut rl = rustyline::DefaultEditor::new()?;
    info!("Demon REPL (Ctrl+C to exit)");
    println!("Type 'exit' or press Ctrl+C to quit.\n");
    
    loop {
        let readline = rl.readline("demon> ");
        match readline {
            Ok(line) => {
                if line.trim().eq_ignore_ascii_case("exit") {
                    break;
                }
                
                if !line.trim().is_empty() {
                    if let Err(e) = run(interpreter, &line) {
                        eprintln!("Error: {}", e);
                    }
                }
                
                // Add to history
                let _ = rl.add_history_entry(line);
            }
            Err(_) => {
                println!("\nGoodbye!");
                break;
            }
        }
    }
    
    Ok(())
}

/// Runs the Demon source code
fn run(interpreter: &mut Interpreter, source: &str) -> Result<(), Box<dyn Error>> {
    if cfg!(debug_assertions) {
        println!("=== Source Code ===");
        println!("{}", source);
        println!("===================\n");
    }
    
    // Lexical analysis
    let mut scanner = demon::lexer::Scanner::new(source.to_string());
    let tokens = scanner.scan_tokens();
    
    if cfg!(debug_assertions) {
        for token in &tokens {
            println!("Token: {:?}", token);
        }
    }
    
    let mut parser = demon::parser::Parser::new(&tokens);
    let statements = match parser.parse() {
        Ok(s) => s,
        Err(e) => {
            eprintln!("{}", e);
            return Ok(()); // Continue the REPL even if there's a parse error
        }
    };
    
    if cfg!(debug_assertions) {
        for stmt in &statements {
            println!("AST: {}", stmt);
        }
    }
    
    interpreter.interpret(&statements)?;
    Ok(())
}
