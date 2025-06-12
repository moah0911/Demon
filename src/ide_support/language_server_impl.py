"""
Language Server Protocol implementation for the Demon programming language.
"""

import os
import sys
import json
import threading
import socketserver
import logging
from typing import Dict, List, Optional, Any, Union, Tuple

class DemonLanguageServer:
    """Language Server Protocol implementation for Demon."""
    
    def __init__(self):
        self.running = False
        self.workspace_folders = []
        self.open_documents = {}
        self.client_capabilities = {}
        self.client_writer = None
        self.server_capabilities = {
            "textDocumentSync": {
                "openClose": True,
                "change": 2,  # Incremental
                "willSave": True,
                "willSaveWaitUntil": True,
                "save": {
                    "includeText": True
                }
            },
            "completionProvider": {
                "resolveProvider": True,
                "triggerCharacters": [".", "("]
            },
            "hoverProvider": True,
            "signatureHelpProvider": {
                "triggerCharacters": ["(", ","]
            },
            "definitionProvider": True,
            "referencesProvider": True,
            "documentHighlightProvider": True,
            "documentSymbolProvider": True,
            "workspaceSymbolProvider": True,
            "codeActionProvider": True,
            "documentFormattingProvider": True,
            "documentRangeFormattingProvider": True,
            "renameProvider": True,
            "documentLinkProvider": {
                "resolveProvider": True
            },
            "colorProvider": True,
            "foldingRangeProvider": True,
            "declarationProvider": True,
            "executeCommandProvider": {
                "commands": [
                    "demon.restart",
                    "demon.typeCheck",
                    "demon.format"
                ]
            },
            "workspace": {
                "workspaceFolders": {
                    "supported": True,
                    "changeNotifications": True
                }
            }
        }
        
        # Components
        from ide_support.code_completion import CodeCompleter
        from ide_support.syntax_highlighter import SyntaxHighlighter
        from ide_support.formatter import CodeFormatter
        from ide_support.linter import CodeLinter
        
        self.completer = CodeCompleter(self)
        self.highlighter = SyntaxHighlighter(self)
        self.formatter = CodeFormatter(self)
        self.linter = CodeLinter(self)
        
        # Initialize demon
        from demon import Demon
        self.demon = Demon()
    
    def start(self, host="127.0.0.1", port=8123):
        """Start the language server."""
        self.running = True
        
        # Start server
        class TCPHandler(socketserver.StreamRequestHandler):
            def handle(self):
                try:
                    self.server.language_server.handle_client(self.rfile, self.wfile)
                except Exception as e:
                    logging.error(f"Error handling client: {e}")
        
        class LSPServer(socketserver.TCPServer):
            allow_reuse_address = True
            
            def __init__(self, server_address, RequestHandlerClass, language_server):
                self.language_server = language_server
                super().__init__(server_address, RequestHandlerClass)
        
        logging.info(f"Starting Demon Language Server on {host}:{port}")
        
        try:
            with LSPServer((host, port), TCPHandler, self) as server:
                server.serve_forever()
        except Exception as e:
            logging.error(f"Error starting server: {e}")
            self.running = False
    
    def handle_client(self, rfile, wfile):
        """Handle client connection."""
        logging.info("Client connected")
        
        # Store writer for publishing diagnostics
        self.client_writer = wfile
        
        while self.running:
            try:
                # Read header
                content_length = None
                while True:
                    try:
                        header = rfile.readline().decode("utf-8", errors="ignore").strip()
                        if not header:
                            break
                        
                        if header.startswith("Content-Length: "):
                            content_length = int(header[16:])
                    except UnicodeDecodeError:
                        # Skip invalid headers
                        continue
                
                if content_length is None:
                    break
                
                # Read content
                content = rfile.read(content_length).decode("utf-8", errors="ignore")
                message = json.loads(content)
                
                # Process message
                response = self.process_message(message)
                
                # Send response if needed
                if response:
                    response_str = json.dumps(response)
                    header = f"Content-Length: {len(response_str)}\r\n\r\n"
                    wfile.write(header.encode("utf-8"))
                    wfile.write(response_str.encode("utf-8"))
                    wfile.flush()
            except Exception as e:
                logging.error(f"Error in client communication: {e}")
                break
    
    def process_message(self, message):
        """Process a message from the client."""
        if "method" not in message:
            return self.create_error_response(message.get("id"), -32600, "Invalid request")
        
        method = message["method"]
        params = message.get("params", {})
        
        # Handle initialization
        if method == "initialize":
            return self.handle_initialize(message["id"], params)
        
        # Handle shutdown
        if method == "shutdown":
            return self.handle_shutdown(message["id"])
        
        # Handle exit
        if method == "exit":
            self.handle_exit()
            return None
        
        # Handle text document methods
        if method.startswith("textDocument/"):
            return self.handle_text_document(method, message["id"], params)
        
        # Handle workspace methods
        if method.startswith("workspace/"):
            return self.handle_workspace(method, message["id"], params)
        
        # Handle other methods
        logging.warning(f"Unhandled method: {method}")
        return self.create_error_response(message.get("id"), -32601, f"Method not implemented: {method}")
    
    def handle_initialize(self, id, params):
        """Handle initialize request."""
        logging.info("Initializing language server")
        
        # Store client capabilities
        self.client_capabilities = params.get("capabilities", {})
        
        # Store workspace folders
        self.workspace_folders = params.get("workspaceFolders", [])
        
        # Return server capabilities
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": {
                "capabilities": self.server_capabilities,
                "serverInfo": {
                    "name": "Demon Language Server",
                    "version": "1.0.0"
                }
            }
        }
    
    def handle_shutdown(self, id):
        """Handle shutdown request."""
        logging.info("Shutting down language server")
        self.running = False
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": None
        }
    
    def handle_exit(self):
        """Handle exit notification."""
        logging.info("Exiting language server")
        self.running = False
        sys.exit(0)
    
    def handle_text_document(self, method, id, params):
        """Handle text document methods."""
        method_name = method.split("/")[1]
        
        if method_name == "didOpen":
            return self.handle_did_open(id, params)
        elif method_name == "didChange":
            return self.handle_did_change(id, params)
        elif method_name == "didClose":
            return self.handle_did_close(id, params)
        elif method_name == "didSave":
            return self.handle_did_save(id, params)
        elif method_name == "completion":
            return self.handle_completion(id, params)
        elif method_name == "hover":
            return self.handle_hover(id, params)
        elif method_name == "signatureHelp":
            return self.handle_signature_help(id, params)
        elif method_name == "definition":
            return self.handle_definition(id, params)
        elif method_name == "references":
            return self.handle_references(id, params)
        elif method_name == "documentHighlight":
            return self.handle_document_highlight(id, params)
        elif method_name == "documentSymbol":
            return self.handle_document_symbol(id, params)
        elif method_name == "formatting":
            return self.handle_formatting(id, params)
        elif method_name == "rangeFormatting":
            return self.handle_range_formatting(id, params)
        elif method_name == "rename":
            return self.handle_rename(id, params)
        
        logging.warning(f"Unhandled text document method: {method_name}")
        return self.create_error_response(id, -32601, f"Method not implemented: {method}")
    
    def handle_workspace(self, method, id, params):
        """Handle workspace methods."""
        method_name = method.split("/")[1]
        
        if method_name == "symbol":
            return self.handle_workspace_symbol(id, params)
        elif method_name == "executeCommand":
            return self.handle_execute_command(id, params)
        elif method_name == "didChangeWorkspaceFolders":
            return self.handle_did_change_workspace_folders(id, params)
        
        logging.warning(f"Unhandled workspace method: {method_name}")
        return self.create_error_response(id, -32601, f"Method not implemented: {method}")
    
    def handle_did_open(self, id, params):
        """Handle textDocument/didOpen notification."""
        document = params["textDocument"]
        uri = document["uri"]
        text = document["text"]
        language_id = document["languageId"]
        
        # Store document
        self.open_documents[uri] = {
            "text": text,
            "languageId": language_id,
            "version": document["version"]
        }
        
        # Run linter
        diagnostics = self.linter.lint(uri, text)
        
        # Publish diagnostics
        self.publish_diagnostics(uri, diagnostics)
        
        return None
    
    def handle_did_change(self, id, params):
        """Handle textDocument/didChange notification."""
        document = params["textDocument"]
        uri = document["uri"]
        changes = params["contentChanges"]
        
        if uri not in self.open_documents:
            return None
        
        # Apply changes
        text = self.open_documents[uri]["text"]
        for change in changes:
            if "range" in change:
                # Apply incremental change
                start_line = change["range"]["start"]["line"]
                start_char = change["range"]["start"]["character"]
                end_line = change["range"]["end"]["line"]
                end_char = change["range"]["end"]["character"]
                
                lines = text.splitlines(True)
                
                # Calculate start and end positions
                start_pos = sum(len(lines[i]) for i in range(start_line)) + start_char
                end_pos = sum(len(lines[i]) for i in range(end_line)) + end_char
                
                # Apply change
                text = text[:start_pos] + change["text"] + text[end_pos:]
            else:
                # Full document update
                text = change["text"]
        
        # Update document
        self.open_documents[uri]["text"] = text
        self.open_documents[uri]["version"] = document["version"]
        
        # Run linter
        diagnostics = self.linter.lint(uri, text)
        
        # Publish diagnostics
        self.publish_diagnostics(uri, diagnostics)
        
        return None
    
    def handle_did_close(self, id, params):
        """Handle textDocument/didClose notification."""
        uri = params["textDocument"]["uri"]
        
        if uri in self.open_documents:
            del self.open_documents[uri]
        
        # Clear diagnostics
        self.publish_diagnostics(uri, [])
        
        return None
    
    def handle_did_save(self, id, params):
        """Handle textDocument/didSave notification."""
        uri = params["textDocument"]["uri"]
        
        if uri in self.open_documents:
            # Run linter
            text = self.open_documents[uri]["text"]
            diagnostics = self.linter.lint(uri, text)
            
            # Publish diagnostics
            self.publish_diagnostics(uri, diagnostics)
        
        return None
    
    def handle_completion(self, id, params):
        """Handle textDocument/completion request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Get completions
        completions = self.completer.complete(uri, position)
        
        return self.create_response(id, completions)
    
    def handle_hover(self, id, params):
        """Handle textDocument/hover request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        
        if uri not in self.open_documents:
            return self.create_response(id, None)
        
        # Get hover information
        hover_info = self.completer.hover(uri, position)
        
        return self.create_response(id, hover_info)
    
    def handle_signature_help(self, id, params):
        """Handle textDocument/signatureHelp request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        
        if uri not in self.open_documents:
            return self.create_response(id, None)
        
        # Get signature help
        signature_help = self.completer.signature_help(uri, position)
        
        return self.create_response(id, signature_help)
    
    def handle_definition(self, id, params):
        """Handle textDocument/definition request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        
        if uri not in self.open_documents:
            return self.create_response(id, None)
        
        # Get definition
        definition = self.completer.definition(uri, position)
        
        return self.create_response(id, definition)
    
    def handle_references(self, id, params):
        """Handle textDocument/references request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        include_declaration = params.get("context", {}).get("includeDeclaration", False)
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Get references
        references = self.completer.references(uri, position, include_declaration)
        
        return self.create_response(id, references)
    
    def handle_document_highlight(self, id, params):
        """Handle textDocument/documentHighlight request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Get highlights
        highlights = self.highlighter.highlight(uri, position)
        
        return self.create_response(id, highlights)
    
    def handle_document_symbol(self, id, params):
        """Handle textDocument/documentSymbol request."""
        uri = params["textDocument"]["uri"]
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Get symbols
        symbols = self.completer.document_symbols(uri)
        
        return self.create_response(id, symbols)
    
    def handle_formatting(self, id, params):
        """Handle textDocument/formatting request."""
        uri = params["textDocument"]["uri"]
        options = params["options"]
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Format document
        edits = self.formatter.format(uri, options)
        
        return self.create_response(id, edits)
    
    def handle_range_formatting(self, id, params):
        """Handle textDocument/rangeFormatting request."""
        uri = params["textDocument"]["uri"]
        range = params["range"]
        options = params["options"]
        
        if uri not in self.open_documents:
            return self.create_response(id, [])
        
        # Format range
        edits = self.formatter.format_range(uri, range, options)
        
        return self.create_response(id, edits)
    
    def handle_rename(self, id, params):
        """Handle textDocument/rename request."""
        uri = params["textDocument"]["uri"]
        position = params["position"]
        new_name = params["newName"]
        
        if uri not in self.open_documents:
            return self.create_response(id, None)
        
        # Rename symbol
        workspace_edit = self.completer.rename(uri, position, new_name)
        
        return self.create_response(id, workspace_edit)
    
    def handle_workspace_symbol(self, id, params):
        """Handle workspace/symbol request."""
        query = params["query"]
        
        # Get workspace symbols
        symbols = self.completer.workspace_symbols(query)
        
        return self.create_response(id, symbols)
    
    def handle_execute_command(self, id, params):
        """Handle workspace/executeCommand request."""
        command = params["command"]
        arguments = params.get("arguments", [])
        
        if command == "demon.restart":
            # Restart language server
            return self.create_response(id, None)
        elif command == "demon.typeCheck":
            # Run type checker
            uri = arguments[0]
            if uri in self.open_documents:
                text = self.open_documents[uri]["text"]
                diagnostics = self.linter.type_check(uri, text)
                self.publish_diagnostics(uri, diagnostics)
            return self.create_response(id, None)
        elif command == "demon.format":
            # Format document
            uri = arguments[0]
            if uri in self.open_documents:
                options = arguments[1] if len(arguments) > 1 else {}
                edits = self.formatter.format(uri, options)
                return self.create_response(id, edits)
            return self.create_response(id, [])
        
        return self.create_error_response(id, -32601, f"Command not implemented: {command}")
    
    def handle_did_change_workspace_folders(self, id, params):
        """Handle workspace/didChangeWorkspaceFolders notification."""
        added = params["event"]["added"]
        removed = params["event"]["removed"]
        
        # Update workspace folders
        for folder in removed:
            if folder in self.workspace_folders:
                self.workspace_folders.remove(folder)
        
        for folder in added:
            self.workspace_folders.append(folder)
        
        return None
    
    def publish_diagnostics(self, uri, diagnostics):
        """Publish diagnostics for a document."""
        notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        }
        
        # Convert notification to JSON and send to client
        notification_str = json.dumps(notification)
        header = f"Content-Length: {len(notification_str)}\r\n\r\n"
        
        try:
            # This is a critical fix - we need to actually send the diagnostics
            # to the client, not just create the notification
            if hasattr(self, 'client_writer'):
                self.client_writer.write(header.encode('utf-8'))
                self.client_writer.write(notification_str.encode('utf-8'))
                self.client_writer.flush()
        except Exception as e:
            logging.error(f"Error publishing diagnostics: {e}")
    
    def create_response(self, id, result):
        """Create a response message."""
        return {
            "jsonrpc": "2.0",
            "id": id,
            "result": result
        }
    
    def create_error_response(self, id, code, message, data=None):
        """Create an error response message."""
        error = {
            "code": code,
            "message": message
        }
        
        if data:
            error["data"] = data
        
        return {
            "jsonrpc": "2.0",
            "id": id,
            "error": error
        }