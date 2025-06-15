"""
Wrapper classes for reactive programming in Demon.
This module provides wrappers for reactive objects to work with Demon.
"""

from typing import Any, Dict, List, Callable
from .reactive import Signal, Computed, effect as reactive_effect

class DemonReactiveValue:
    """Base class for reactive values in Demon."""
    
    def __init__(self):
        self.fields = {}
    
    def get_field(self, name):
        """Get a field value."""
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")
    
    def set_field(self, name, value):
        """Set a field value."""
        self.fields[name] = value

class DemonSignal(DemonReactiveValue):
    """A wrapper for Signal that works with Demon."""
    
    def __init__(self, initial_value):
        super().__init__()
        self._signal = Signal(initial_value)
        self.fields["value"] = initial_value
    
    def get_field(self, name):
        """Get a field value, with special handling for 'value'."""
        if name == "value":
            return self._signal.value
        return super().get_field(name)
    
    def set_field(self, name, value):
        """Set a field value, with special handling for 'value'."""
        if name == "value":
            self._signal.value = value
            super().set_field(name, value)
        else:
            super().set_field(name, value)

class DemonComputed(DemonReactiveValue):
    """A wrapper for Computed that works with Demon."""
    
    def __init__(self, computed_signal):
        super().__init__()
        self._computed = computed_signal
    
    def get_field(self, name):
        """Get a field value, with special handling for 'value'."""
        if name == "value":
            return self._computed.value
        return super().get_field(name)
    
    def set_field(self, name, value):
        """Set a field value, with special handling for 'value'."""
        if name == "value":
            raise ValueError("Cannot set the value of a computed signal directly")
        super().set_field(name, value)

def create_signal(initial_value):
    """Create a new signal with the given initial value."""
    return DemonSignal(initial_value)

def create_computed(compute_fn):
    """Create a new computed signal using the given compute function."""
    return DemonComputed(Computed(compute_fn))

def create_effect(effect_fn):
    """Create a new effect that runs when its dependencies change."""
    dispose_fn = reactive_effect(effect_fn)
    
    # Create a callable wrapper that can be called from Demon
    class DisposeFn:
        def __call__(self):
            dispose_fn()
    
    return DisposeFn()