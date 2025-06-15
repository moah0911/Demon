"""
Subscript assignment expression for array/list indexing in the Demon language.
"""

from typing import Any
from .tokens import Token

class SubscriptAssignExpr:
    """Expression for array/list index assignment with square brackets."""
    
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value
    
    def accept(self, visitor):
        """Accept a visitor."""
        return visitor.visit_subscript_assign_expr(self)