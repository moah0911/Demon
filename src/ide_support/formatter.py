"""
Code formatter for the Demon programming language.
"""

import re
from typing import Dict, List, Optional, Any, Union, Tuple

class CodeFormatter:
    """Code formatter for the Demon language."""
    
    def __init__(self, language_server):
        self.language_server = language_server
        self.default_options = {
            "tabSize": 4,
            "insertSpaces": True,
            "trimTrailingWhitespace": True,
            "insertFinalNewline": True,
            "bracesOnNewLine": False,
            "maxLineLength": 80
        }
    
    def format(self, uri: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format the entire document."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        
        # Merge options with defaults
        format_options = {**self.default_options, **options}
        
        # Format the text
        formatted_text = self._format_text(text, format_options)
        
        # Create a single text edit for the entire document
        return [{
            "range": {
                "start": {"line": 0, "character": 0},
                "end": {"line": len(text.splitlines()), "character": 0}
            },
            "newText": formatted_text
        }]
    
    def format_range(self, uri: str, range: Dict[str, Any], options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format a range of the document."""
        document = self.language_server.open_documents.get(uri)
        if not document:
            return []
        
        text = document["text"]
        lines = text.splitlines()
        
        # Extract the range to format
        start_line = range["start"]["line"]
        end_line = range["end"]["line"]
        
        if start_line < 0 or end_line >= len(lines):
            return []
        
        # Extract the text in the range
        range_lines = lines[start_line:end_line + 1]
        range_text = "\n".join(range_lines)
        
        # Merge options with defaults
        format_options = {**self.default_options, **options}
        
        # Format the range text
        formatted_range_text = self._format_text(range_text, format_options)
        
        # Create a text edit for the range
        return [{
            "range": range,
            "newText": formatted_range_text
        }]
    
    def _format_text(self, text: str, options: Dict[str, Any]) -> str:
        """Format text according to options."""
        lines = text.splitlines()
        formatted_lines = []
        indent_level = 0
        in_multiline_comment = False
        
        # Get indentation string
        indent_str = " " * options["tabSize"] if options["insertSpaces"] else "\t"
        
        for i, line in enumerate(lines):
            # Handle multiline comments
            if "/*" in line and "*/" not in line[line.find("/*") + 2:]:
                in_multiline_comment = True
            elif in_multiline_comment and "*/" in line:
                in_multiline_comment = False
            
            # Skip formatting for comments
            if line.strip().startswith("//") or in_multiline_comment:
                formatted_lines.append(line)
                continue
            
            # Adjust indent level based on braces
            closing_brace_at_start = line.lstrip().startswith("}")
            if closing_brace_at_start:
                indent_level = max(0, indent_level - 1)
            
            # Remove leading/trailing whitespace
            trimmed_line = line.strip()
            
            # Skip empty lines
            if not trimmed_line:
                formatted_lines.append("")
                continue
            
            # Apply indentation
            indented_line = indent_str * indent_level + trimmed_line
            
            # Handle brace placement
            if options["bracesOnNewLine"] and "{" in trimmed_line and not trimmed_line.startswith("{"):
                # Move opening brace to next line
                brace_index = trimmed_line.index("{")
                before_brace = trimmed_line[:brace_index].rstrip()
                after_brace = trimmed_line[brace_index:]
                
                if before_brace:
                    formatted_lines.append(indent_str * indent_level + before_brace)
                    formatted_lines.append(indent_str * indent_level + after_brace)
                else:
                    formatted_lines.append(indent_str * indent_level + after_brace)
            else:
                formatted_lines.append(indented_line)
            
            # Adjust indent level for next line
            indent_level += trimmed_line.count("{") - (trimmed_line.count("}") - (1 if closing_brace_at_start else 0))
            indent_level = max(0, indent_level)  # Ensure non-negative
        
        # Join lines
        formatted_text = "\n".join(formatted_lines)
        
        # Ensure final newline if requested
        if options["insertFinalNewline"] and not formatted_text.endswith("\n"):
            formatted_text += "\n"
        
        return formatted_text
    
    def get_formatting_options(self, uri: str) -> Dict[str, Any]:
        """Get formatting options for the document."""
        # Check for .editorconfig or other configuration files
        return self.default_options