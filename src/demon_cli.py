#!/usr/bin/env python3
"""
Command-line interface for the Demon programming language.
"""

import sys
import os
import argparse
from demon import Demon

def main():
    """Entry point for the Demon CLI."""
    parser = argparse.ArgumentParser(description="Demon Programming Language")
    parser.add_argument("file", nargs="?", help="Script file to execute")
    parser.add_argument("--type-check", action="store_true", help="Enable type checking")
    parser.add_argument("--bytecode", action="store_true", help="Use bytecode VM")
    parser.add_argument("--repl", action="store_true", help="Start REPL mode")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--package", choices=["install", "uninstall", "update", "list", "search"],
                        help="Package manager commands")
    parser.add_argument("--package-name", help="Package name for package manager commands")
    parser.add_argument("--ide", action="store_true", help="Start IDE language server")
    parser.add_argument("--ide-host", default="127.0.0.1", help="Host for IDE language server")
    parser.add_argument("--ide-port", type=int, default=8123, help="Port for IDE language server")
    parser.add_argument("--version", action="store_true", help="Show version information")
    
    args = parser.parse_args()
    
    if args.version:
        print("Demon Programming Language v1.0.0")
        return
    
    if args.ide:
        # Start language server
        from ide_support.language_server_impl import DemonLanguageServer
        server = DemonLanguageServer()
        server.start(args.ide_host, args.ide_port)
        return
    
    demon = Demon()
    demon.enable_type_checking = args.type_check
    demon.use_bytecode = args.bytecode
    
    if args.package:
        from package_manager import PackageManager
        pm = PackageManager(demon)
        
        if args.package == "install" and args.package_name:
            pm.install(args.package_name)
        elif args.package == "uninstall" and args.package_name:
            pm.uninstall(args.package_name)
        elif args.package == "update":
            pm.update(args.package_name)
        elif args.package == "list":
            packages = pm.list_packages()
            if not packages:
                print("No packages installed.")
            else:
                print("Installed packages:")
                for pkg in packages:
                    print(f"  {pkg['name']} (version {pkg['version']})")
        elif args.package == "search" and args.package_name:
            results = pm.search(args.package_name)
            if not results:
                print(f"No packages found matching '{args.package_name}'.")
            else:
                print(f"Search results for '{args.package_name}':")
                for pkg in results:
                    print(f"  {pkg['name']} - {pkg['description']}")
        else:
            print("Invalid package command or missing package name.")
        
        return
    
    if args.debug and args.file:
        from debugger import Debugger
        debugger = Debugger(demon)
        debugger.start(args.file)
        return
    
    if args.repl or args.file is None:
        demon.run_prompt()
    else:
        demon.run_file(args.file)

if __name__ == "__main__":
    main()