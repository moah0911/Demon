"""
Error handling utilities for reactive programming in Demon.
This module provides error handling and debugging tools for reactive programming.
"""

import traceback
from typing import Any, Callable, Optional, List, Dict, Set

class ReactiveError(Exception):
    """Base class for reactive programming errors."""
    pass

class DependencyCycleError(ReactiveError):
    """Error raised when a dependency cycle is detected."""
    pass

class ReactiveErrorHandler:
    """Handles errors in reactive programming."""
    
    def __init__(self):
        self.error_listeners: List[Callable[[Exception], None]] = []
        self.debug_mode = False
        self.dependency_graph: Dict[str, Set[str]] = {}
    
    def handle_error(self, error: Exception, context: str = None):
        """Handle an error in reactive code."""
        if self.debug_mode:
            print(f"Reactive Error in {context or 'unknown context'}:")
            traceback.print_exc()
        
        for listener in self.error_listeners:
            try:
                listener(error)
            except Exception as e:
                print(f"Error in error listener: {e}")
    
    def add_error_listener(self, listener: Callable[[Exception], None]):
        """Add a listener for reactive errors."""
        self.error_listeners.append(listener)
        
        def remove_listener():
            if listener in self.error_listeners:
                self.error_listeners.remove(listener)
        
        return remove_listener
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self.debug_mode = enabled
    
    def track_dependency(self, source_id: str, target_id: str):
        """Track a dependency between reactive nodes."""
        if source_id not in self.dependency_graph:
            self.dependency_graph[source_id] = set()
        
        self.dependency_graph[source_id].add(target_id)
        
        # Check for cycles
        if self._has_cycle(source_id, target_id):
            raise DependencyCycleError(f"Dependency cycle detected between {source_id} and {target_id}")
    
    def _has_cycle(self, source: str, target: str, visited: Set[str] = None) -> bool:
        """Check if there's a cycle in the dependency graph."""
        if visited is None:
            visited = set()
        
        if source in visited:
            return True
        
        if target not in self.dependency_graph:
            return False
        
        visited.add(source)
        
        for next_target in self.dependency_graph[target]:
            if self._has_cycle(source, next_target, visited):
                return True
        
        visited.remove(source)
        return False

# Global error handler instance
error_handler = ReactiveErrorHandler()

def safe_call(fn: Callable, *args, **kwargs) -> Any:
    """Safely call a function and handle any errors."""
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, context=fn.__name__ if hasattr(fn, "__name__") else "anonymous function")
        return None

def enable_debug_mode():
    """Enable debug mode for reactive programming."""
    error_handler.set_debug_mode(True)

def disable_debug_mode():
    """Disable debug mode for reactive programming."""
    error_handler.set_debug_mode(False)

def on_reactive_error(listener: Callable[[Exception], None]) -> Callable[[], None]:
    """Register a listener for reactive errors."""
    return error_handler.add_error_listener(listener)