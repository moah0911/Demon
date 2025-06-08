"""
Syntax highlighter for the Demon programming language.
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple

class SyntaxHighlighter:
    """Syntax highlighter for the Demon language."""
    
    def __init__(self, language_server):
        self.language_server = language_server
        
        # Define token types
        self.token_types = {
            "keyword": ["if", "else", "for", "while", "func", "return", "break", "continue", "let", "true", "false", "nil"],
            "operator": ["+", "-", "*", "/", "%", "=", "==", "!=", "<", ">", "<=", ">=", "&&", "||", "!"],
            "string": ['"', "'"],
            "number": [r"\d+(\.\d+)?"],
            "comment": [r"//.*$", r"/\*[\s\S]*?\*/"],
            "function": [r"\b\w+(?=\s*\()"],
            "variable": [r"\b\w+\b"]
        }
    
    def highlight(self, uri: str, position: Dict[str, int]) -> List[Dict[str, Any]]:
        """Highlight occurrences of the symbol at the given position."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        line = position["line"]
        character = position["character"]
        
        # Get word at cursor
        lines = text.splitlines()
        if line >= len(lines):
            return []
        
        line_text = lines[line]
        word_match = re.search(r'\b(\w+)\b', line_text[max(0, character - 20):character + 20])
        if not word_match:
            return []
        
        word = word_match.group(1)
        
        # Find all occurrences of the word
        highlights = []
        for i, line in enumerate(lines):
            for match in re.finditer(r'\b' + re.escape(word) + r'\b', line):
                highlights.append({
                    "range": {
                        "start": {"line": i, "character": match.start()},
                        "end": {"line": i, "character": match.end()}
                    },
                    "kind": 1  # Text
                })
        
        return highlights
    
    def get_token_types(self) -> Dict[str, List[str]]:
        """Get token types for syntax highlighting."""
        return self.token_types
    
    def tokenize(self, text: str) -> List[Dict[str, Any]]:
        """Tokenize text for syntax highlighting."""
        tokens = []
        lines = text.splitlines()
        
        for line_num, line in enumerate(lines):
            pos = 0
            while pos < len(line):
                # Skip whitespace
                match = re.match(r'\s+', line[pos:])
                if match:
                    pos += match.end()
                    continue
                
                # Try to match tokens
                token_matched = False
                
                # Comments
                match = re.match(r'//.*$', line[pos:])
                if match:
                    tokens.append({
                        "type": "comment",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    token_matched = True
                    continue
                
                # Multi-line comments
                if pos == 0 or line[pos-1] != '\\':  # Not escaped
                    match = re.match(r'/\*', line[pos:])
                    if match:
                        # Find end of comment
                        comment_end = None
                        for i in range(line_num, len(lines)):
                            if i == line_num:
                                end_pos = line[pos:].find('*/')
                                if end_pos != -1:
                                    comment_end = (i, pos + end_pos + 2)
                                    break
                            else:
                                end_pos = lines[i].find('*/')
                                if end_pos != -1:
                                    comment_end = (i, end_pos + 2)
                                    break
                        
                        if comment_end:
                            end_line, end_pos = comment_end
                            if end_line == line_num:
                                tokens.append({
                                    "type": "comment",
                                    "text": line[pos:end_pos],
                                    "range": {
                                        "start": {"line": line_num, "character": pos},
                                        "end": {"line": line_num, "character": end_pos}
                                    }
                                })
                                pos = end_pos
                                token_matched = True
                                continue
                
                # Strings
                for quote in ['"', "'"]:
                    if pos < len(line) and line[pos] == quote:
                        # Find end of string
                        i = pos + 1
                        while i < len(line):
                            if line[i] == quote and line[i-1] != '\\':
                                break
                            i += 1
                        
                        if i < len(line):  # Found closing quote
                            tokens.append({
                                "type": "string",
                                "text": line[pos:i+1],
                                "range": {
                                    "start": {"line": line_num, "character": pos},
                                    "end": {"line": line_num, "character": i+1}
                                }
                            })
                            pos = i + 1
                            token_matched = True
                            break
                
                if token_matched:
                    continue
                
                # Numbers
                match = re.match(r'\d+(\.\d+)?', line[pos:])
                if match:
                    tokens.append({
                        "type": "number",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    continue
                
                # Keywords
                match = re.match(r'\b(' + '|'.join(self.token_types["keyword"]) + r')\b', line[pos:])
                if match:
                    tokens.append({
                        "type": "keyword",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    continue
                
                # Functions
                match = re.match(r'\b\w+(?=\s*\()', line[pos:])
                if match:
                    tokens.append({
                        "type": "function",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    continue
                
                # Operators
                match = re.match(r'[+\-*/=%<>!&|]+', line[pos:])
                if match:
                    tokens.append({
                        "type": "operator",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    continue
                
                # Variables and other identifiers
                match = re.match(r'\b\w+\b', line[pos:])
                if match:
                    tokens.append({
                        "type": "variable",
                        "text": match.group(0),
                        "range": {
                            "start": {"line": line_num, "character": pos},
                            "end": {"line": line_num, "character": pos + match.end()}
                        }
                    })
                    pos += match.end()
                    continue
                
                # Other characters
                tokens.append({
                    "type": "text",
                    "text": line[pos],
                    "range": {
                        "start": {"line": line_num, "character": pos},
                        "end": {"line": line_num, "character": pos + 1}
                    }
                })
                pos += 1
        
        return tokens
    
    def get_semantic_tokens(self, uri: str) -> List[int]:
        """Get semantic tokens for the document."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        tokens = self.tokenize(text)
        
        # Convert to semantic tokens format
        # [line, character, length, tokenType, tokenModifiers]
        semantic_tokens = []
        prev_line = 0
        prev_char = 0
        
        token_types = {
            "keyword": 0,
            "operator": 1,
            "string": 2,
            "number": 3,
            "comment": 4,
            "function": 5,
            "variable": 6,
            "text": 7
        }
        
        for token in tokens:
            line = token["range"]["start"]["line"]
            char = token["range"]["start"]["character"]
            length = token["range"]["end"]["character"] - char
            token_type = token_types.get(token["type"], 7)  # Default to text
            
            # Calculate delta encoding
            delta_line = line - prev_line
            delta_char = char - prev_char if line == prev_line else char
            
            semantic_tokens.extend([delta_line, delta_char, length, token_type, 0])
            
            prev_line = line
            prev_char = char
        
        return semantic_tokens
    
    def get_folding_ranges(self, uri: str) -> List[Dict[str, Any]]:
        """Get folding ranges for the document."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        lines = text.splitlines()
        folding_ranges = []
        
        # Stack to track open braces
        stack = []
        
        for i, line in enumerate(lines):
            # Count opening and closing braces
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            # Process opening braces
            for _ in range(open_braces):
                stack.append(i)
            
            # Process closing braces
            for _ in range(close_braces):
                if stack:
                    start_line = stack.pop()
                    if i > start_line:
                        folding_ranges.append({
                            "startLine": start_line,
                            "endLine": i,
                            "kind": "region"
                        })
        
        # Find comment blocks
        in_comment = False
        comment_start = 0
        
        for i, line in enumerate(lines):
            if not in_comment and "/*" in line and "*/" not in line[line.index("/*") + 2:]:
                in_comment = True
                comment_start = i
            elif in_comment and "*/" in line:
                in_comment = False
                if i > comment_start:
                    folding_ranges.append({
                        "startLine": comment_start,
                        "endLine": i,
                        "kind": "comment"
                    })
        
        return folding_ranges