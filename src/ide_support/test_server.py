#!/usr/bin/env python3
"""
Simple test script for the Demon language server.
"""

import socket
import json
import sys
import time

def send_message(sock, method, params=None, id=None):
    """Send a message to the language server."""
    message = {
        "jsonrpc": "2.0",
        "method": method
    }
    
    if params is not None:
        message["params"] = params
    
    if id is not None:
        message["id"] = id
    
    content = json.dumps(message)
    header = f"Content-Length: {len(content)}\r\n\r\n"
    
    sock.sendall(header.encode('utf-8'))
    sock.sendall(content.encode('utf-8'))

def receive_message(sock):
    """Receive a message from the language server."""
    # Read header
    header = b""
    while b"\r\n\r\n" not in header:
        chunk = sock.recv(1)
        if not chunk:
            return None
        header += chunk
    
    # Parse content length
    content_length = None
    for line in header.split(b"\r\n"):
        if line.startswith(b"Content-Length: "):
            content_length = int(line[16:])
            break
    
    if content_length is None:
        return None
    
    # Read content
    content = b""
    while len(content) < content_length:
        chunk = sock.recv(content_length - len(content))
        if not chunk:
            return None
        content += chunk
    
    return json.loads(content.decode('utf-8'))

def main():
    """Test the language server."""
    # Connect to server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8123))
    
    # Initialize
    send_message(sock, "initialize", {
        "processId": None,
        "clientInfo": {
            "name": "Test Client",
            "version": "1.0.0"
        },
        "rootUri": None,
        "capabilities": {}
    }, 1)
    
    # Receive initialize response
    response = receive_message(sock)
    print("Initialize response:", json.dumps(response, indent=2))
    
    # Send initialized notification
    send_message(sock, "initialized", {})
    
    # Open a document
    send_message(sock, "textDocument/didOpen", {
        "textDocument": {
            "uri": "file:///test.demon",
            "languageId": "demon",
            "version": 1,
            "text": "// Test document\nlet x = 10;\nprint(x);\n"
        }
    })
    
    # Request completion
    send_message(sock, "textDocument/completion", {
        "textDocument": {
            "uri": "file:///test.demon"
        },
        "position": {
            "line": 2,
            "character": 6
        }
    }, 2)
    
    # Receive completion response
    response = receive_message(sock)
    print("Completion response:", json.dumps(response, indent=2))
    
    # Close document
    send_message(sock, "textDocument/didClose", {
        "textDocument": {
            "uri": "file:///test.demon"
        }
    })
    
    # Shutdown
    send_message(sock, "shutdown", None, 3)
    
    # Receive shutdown response
    response = receive_message(sock)
    print("Shutdown response:", json.dumps(response, indent=2))
    
    # Exit
    send_message(sock, "exit", None)
    
    # Close socket
    sock.close()

if __name__ == "__main__":
    main()