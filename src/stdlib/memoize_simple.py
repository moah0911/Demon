"""
Simple memoization for the Demon programming language.
"""

from typing import Dict, Any, Callable
import functools

class Memoized:
    """A memoized function."""
    
    def __init__(self, fn):
        self.fn = fn
        self.cache = {}
        functools.update_wrapper(self, fn)
    
    def __call__(self, *args):
        # Create cache key from arguments
        key = str(args)
        
        # Check cache
        if key in self.cache:
            return self.cache[key]
        
        # Call function and cache result
        result = self.fn(*args)
        self.cache[key] = result
        return result
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()

def memoize(fn):
    """Decorator to memoize a function."""
    return Memoized(fn)