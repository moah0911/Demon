"""
Helper module for parsing call expressions with comma-separated arguments.
This is used to fix the issue with print statements that have multiple arguments.
"""

from typing import List
from .tokens import Token, TokenType
from . import ast

def parse_call_arguments(parser, closing_token=TokenType.RIGHT_PAREN):
    """Parse comma-separated arguments for a function call."""
    arguments = []
    
    if not parser.check(closing_token):
        while True:
            if len(arguments) >= 255:
                parser.error(parser.peek(), "Cannot have more than 255 arguments.")
            
            arguments.append(parser.expression())
            
            if not parser.match(TokenType.COMMA):
                break
    
    parser.consume(closing_token, f"Expect '{closing_token.value}' after arguments.")
    
    return arguments