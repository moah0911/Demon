"""
Subscript expression for array/list indexing in the Demon language.
"""

from typing import Any
from .tokens import Token

class SubscriptExpr:
    """Expression for array/list indexing with square brackets."""
    
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index
    
    def accept(self, visitor):
        """Accept a visitor."""
        return visitor.visit_subscript_expr(self)