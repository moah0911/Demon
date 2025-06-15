"""
Contextual programming for the Demon programming language.
This module provides a powerful contextual programming model with dynamic scoping.
"""

from typing import Any, Dict, List, Optional, Callable
import threading
from contextlib import contextmanager

class Context:
    """A context that can be used to store and retrieve values."""
    
    # Thread-local storage for the current context stack
    _local = threading.local()
    
    @classmethod
    def _get_stack(cls) -> List['Context']:
        """Get the current context stack for this thread."""
        if not hasattr(cls._local, 'stack'):
            cls._local.stack = []
        return cls._local.stack
    
    @classmethod
    def current(cls) -> Optional['Context']:
        """Get the current context for this thread."""
        stack = cls._get_stack()
        return stack[-1] if stack else None
    
    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """Get a value from the current context."""
        ctx = cls.current()
        if ctx is None:
            return default
        return ctx.get(key, default)
    
    def __init__(self, values: Dict[str, Any] = None, parent: Optional['Context'] = None):
        self.values = values or {}
        self.parent = parent
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from this context or its parent."""
        if key in self.values:
            return self.values[key]
        if self.parent:
            return self.parent.get(key, default)
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in this context."""
        self.values[key] = value
    
    def update(self, values: Dict[str, Any]) -> None:
        """Update multiple values in this context."""
        self.values.update(values)
    
    def derive(self, values: Dict[str, Any] = None) -> 'Context':
        """Create a new context derived from this one."""
        return Context(values, self)
    
    @contextmanager
    def activate(self):
        """Activate this context for the duration of the context manager."""
        stack = self._get_stack()
        stack.append(self)
        try:
            yield self
        finally:
            stack.pop()

class ContextualFunction:
    """A function that has access to the current context."""
    
    def __init__(self, fn: Callable):
        self.fn = fn
    
    def __call__(self, *args, **kwargs):
        """Call the function with the current context."""
        ctx = Context.current()
        if ctx is None:
            return self.fn(*args, **kwargs)
        
        # Add context values as keyword arguments
        ctx_kwargs = dict(kwargs)
        for key, value in ctx.values.items():
            if key not in ctx_kwargs:
                ctx_kwargs[key] = value
        
        return self.fn(*args, **ctx_kwargs)

def contextual(fn: Callable) -> ContextualFunction:
    """Decorator to make a function contextual."""
    return ContextualFunction(fn)

def create_context(values: Dict[str, Any] = None, parent: Optional[Context] = None) -> Context:
    """Create a new context."""
    return Context(values, parent)

def with_context(ctx: Context, fn: Callable, *args, **kwargs) -> Any:
    """Run a function with a specific context."""
    with ctx.activate():
        return fn(*args, **kwargs)

def get_context_value(key: str, default: Any = None) -> Any:
    """Get a value from the current context."""
    return Context.get_value(key, default)

class ContextVar:
    """A variable that gets its value from the current context."""
    
    def __init__(self, key: str, default: Any = None):
        self.key = key
        self.default = default
    
    def get(self) -> Any:
        """Get the value from the current context."""
        return Context.get_value(self.key, self.default)
    
    def set(self, value: Any) -> None:
        """Set the value in the current context."""
        ctx = Context.current()
        if ctx is None:
            raise ValueError("No active context")
        ctx.set(self.key, value)

class ContextualObject:
    """An object that has access to the current context."""
    
    def __getattr__(self, name: str) -> Any:
        """Get an attribute from the current context."""
        ctx = Context.current()
        if ctx is None:
            raise AttributeError(f"No active context, cannot access '{name}'")
        
        value = ctx.get(name, None)
        if value is None:
            raise AttributeError(f"'{name}' not found in context")
        
        return value

# Create a global contextual object
ctx = ContextualObject()

class ContextDecorator:
    """A decorator that activates a context for the decorated function."""
    
    def __init__(self, **kwargs):
        self.context = Context(kwargs)
    
    def __call__(self, fn):
        def wrapper(*args, **kwargs):
            with self.context.activate():
                return fn(*args, **kwargs)
        return wrapper

def with_values(**kwargs):
    """Decorator to run a function with specific context values."""
    return ContextDecorator(**kwargs)