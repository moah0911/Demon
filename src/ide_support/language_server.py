#!/usr/bin/env python3
"""
Language Server Protocol implementation for the Demon programming language.
This script starts the language server.
"""

import os
import sys
import argparse
import logging

# Add parent directory to path to import DemonLanguageServer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ide_support.language_server_impl import DemonLanguageServer

def main():
    """Start the language server."""
    parser = argparse.ArgumentParser(description="Demon Language Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8123, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("demon_lsp.log"),
            logging.StreamHandler()
        ]
    )
    
    # Start server
    server = DemonLanguageServer()
    server.start(args.host, args.port)

if __name__ == "__main__":
    main()