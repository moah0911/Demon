"""
Bridge module for reactive programming in Demon.
This module provides adapters between Demon functions and Python callables.
"""

from typing import Any, Callable, Dict
from .reactive import Signal, Computed, effect as reactive_effect
from .reactive_error_handler import safe_call, error_handler
from .reactive_wrapper import DemonSignal, DemonComputed, create_signal

class DemonCallableAdapter:
    """Adapter that makes a Demon callable work as a Python function."""
    
    def __init__(self, demon_callable, interpreter, name=None):
        self.demon_callable = demon_callable
        self.interpreter = interpreter
        self.name = name or "anonymous"
    
    def __call__(self, *args):
        try:
            return self.demon_callable.call(self.interpreter, list(args))
        except Exception as e:
            # Use the error handler for better error reporting
            error_handler.handle_error(e, context=f"Demon function '{self.name}'")
            return None

def demon_computed(interpreter, compute_fn):
    """Create a computed signal that works with Demon functions."""
    # Adapt the Demon function to a Python callable
    name = getattr(compute_fn, "name", "computed")
    adapter = DemonCallableAdapter(compute_fn, interpreter, name)
    # Create the computed signal and wrap it
    computed_signal = Computed(adapter)
    return DemonComputed(computed_signal)

def demon_effect(interpreter, effect_fn):
    """Create an effect that works with Demon functions."""
    # Adapt the Demon function to a Python callable
    name = getattr(effect_fn, "name", "effect")
    adapter = DemonCallableAdapter(effect_fn, interpreter, name)
    
    # Create the effect and get the dispose function
    dispose_fn = reactive_effect(adapter)
    
    # Create a callable wrapper that can be called from Demon
    from ..core.interpreter import DemonCallable
    
    class DisposeFn(DemonCallable):
        def arity(self):
            return 0
        
        def call(self, interpreter, arguments):
            dispose_fn()
            return None
        
        def __str__(self):
            return "<effect dispose function>"
    
    return DisposeFn()

def create_reactive_bridge(interpreter):
    """Create a bridge between Demon and the reactive system."""
    return {
        "signal": create_signal,
        "computed": lambda fn: demon_computed(interpreter, fn),
        "effect": lambda fn: demon_effect(interpreter, fn),
        "enable_debug": lambda: error_handler.set_debug_mode(True),
        "disable_debug": lambda: error_handler.set_debug_mode(False),
        "on_error": lambda fn: error_handler.add_error_listener(
            DemonCallableAdapter(fn, interpreter, "error_listener")
        )
    }