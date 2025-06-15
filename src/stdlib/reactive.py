"""
Reactive programming support for the Demon programming language.
This module provides a reactive programming model with automatic dependency tracking.
"""

from typing import Any, Dict, List, Set, Callable, Optional
import threading
import time
import uuid
from .reactive_error_handler import error_handler, safe_call

class Signal:
    """
    A reactive signal that can be observed and will notify observers when its value changes.
    """
    
    _current_computation: Optional['Computation'] = None
    _global_lock = threading.RLock()
    _next_id = 0
    
    def __init__(self, initial_value: Any, name: str = None):
        self._value = initial_value
        self._observers: Set['Computation'] = set()
        self._on_change_callbacks: List[Callable[[Any], None]] = []
        self._id = f"signal_{Signal._next_id}"
        Signal._next_id += 1
        self._name = name or self._id
    
    @property
    def value(self) -> Any:
        """Get the current value, registering the current computation as a dependency."""
        if Signal._current_computation is not None:
            self._observers.add(Signal._current_computation)
            # Track dependency for cycle detection
            error_handler.track_dependency(Signal._current_computation._id, self._id)
        return self._value
    
    @value.setter
    def value(self, new_value: Any) -> None:
        """Set a new value and notify observers if the value has changed."""
        if self._value == new_value:
            return
            
        with Signal._global_lock:
            old_value = self._value
            self._value = new_value
            
            # Notify observers
            observers = set(self._observers)
            for observer in observers:
                observer.invalidate()
            
            # Call on_change callbacks
            for callback in self._on_change_callbacks:
                safe_call(callback, new_value)
    
    def on_change(self, callback: Callable[[Any], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the value changes.
        
        Returns a function that can be called to unregister the callback.
        """
        self._on_change_callbacks.append(callback)
        
        def unsubscribe():
            if callback in self._on_change_callbacks:
                self._on_change_callbacks.remove(callback)
        
        return unsubscribe
    
    def map(self, transform_fn: Callable[[Any], Any]) -> 'Computed':
        """Create a computed signal by applying a transform function to this signal."""
        return computed(lambda: transform_fn(self.value))
    
    def __str__(self) -> str:
        return f"{self._name}({self._value})"

class Computation:
    """Represents a computation that depends on signals."""
    
    _next_id = 0
    
    def __init__(self, fn: Callable[[], Any], name: str = None):
        self.fn = fn
        self.value = None
        self.is_dirty = True
        self.dependencies: Set[Signal] = set()
        self._id = f"computation_{Computation._next_id}"
        Computation._next_id += 1
        self._name = name or self._id
    
    def evaluate(self) -> Any:
        """Evaluate the computation function and track dependencies."""
        if not self.is_dirty:
            return self.value
            
        # Clear old dependencies
        old_dependencies = self.dependencies
        self.dependencies = set()
        
        # Set this computation as the current one being evaluated
        old_computation = Signal._current_computation
        Signal._current_computation = self
        
        try:
            # Evaluate the function
            self.value = safe_call(self.fn)
            self.is_dirty = False
            return self.value
        finally:
            # Restore the previous computation
            Signal._current_computation = old_computation
            
            # Remove this computation from signals it no longer depends on
            for dep in old_dependencies:
                if dep not in self.dependencies:
                    dep._observers.discard(self)
    
    def invalidate(self) -> None:
        """Mark this computation as dirty, requiring re-evaluation."""
        if not self.is_dirty:
            self.is_dirty = True
            # Immediately re-evaluate for effects
            if isinstance(self, EffectComputation):
                self.evaluate()

class EffectComputation(Computation):
    """A computation that represents an effect."""
    
    def __init__(self, effect_fn: Callable[[], None], name: str = None):
        super().__init__(effect_fn, name or "effect")

class Computed(Signal):
    """A signal whose value is computed from other signals."""
    
    def __init__(self, compute_fn: Callable[[], Any], name: str = None):
        super().__init__(None, name or "computed")
        self._computation = Computation(compute_fn, name)
        # Initial evaluation
        self._value = self._computation.evaluate()
    
    @property
    def value(self) -> Any:
        """Get the current computed value, re-evaluating if necessary."""
        if self._computation.is_dirty:
            self._value = self._computation.evaluate()
        
        # Register dependency if there's a current computation
        if Signal._current_computation is not None:
            self._observers.add(Signal._current_computation)
            # Track dependency for cycle detection
            error_handler.track_dependency(Signal._current_computation._id, self._id)
            
        return self._value
    
    @value.setter
    def value(self, _: Any) -> None:
        """Computed values cannot be set directly."""
        raise ValueError("Cannot set the value of a computed signal directly")

def signal(initial_value: Any, name: str = None) -> Signal:
    """Create a new signal with the given initial value."""
    return Signal(initial_value, name)

def computed(compute_fn: Callable[[], Any], name: str = None) -> Computed:
    """Create a new computed signal using the given compute function."""
    return Computed(compute_fn, name)

def effect(effect_fn: Callable[[], None], name: str = None) -> Callable[[], None]:
    """
    Create a new effect that runs when its dependencies change.
    
    Returns a function that can be called to stop the effect.
    """
    computation = EffectComputation(effect_fn, name)
    
    # Run the effect once to establish dependencies
    computation.evaluate()
    
    def dispose():
        # Remove this computation from all its dependencies
        for dep in computation.dependencies:
            dep._observers.discard(computation)
    
    return dispose

class ReactiveDict:
    """A dictionary-like object with reactive properties."""
    
    def __init__(self, initial_data: Dict[str, Any] = None):
        self._signals: Dict[str, Signal] = {}
        self._keys_signal = Signal([], "dict_keys")
        
        if initial_data:
            for key, value in initial_data.items():
                self._signals[key] = Signal(value, f"dict_{key}")
            self._keys_signal.value = list(initial_data.keys())
    
    def __getitem__(self, key: str) -> Any:
        if key not in self._signals:
            self._signals[key] = Signal(None, f"dict_{key}")
            keys = self._keys_signal.value.copy()
            keys.append(key)
            self._keys_signal.value = keys
        return self._signals[key].value
    
    def __setitem__(self, key: str, value: Any) -> None:
        if key not in self._signals:
            self._signals[key] = Signal(value, f"dict_{key}")
            keys = self._keys_signal.value.copy()
            keys.append(key)
            self._keys_signal.value = keys
        else:
            self._signals[key].value = value
    
    def __contains__(self, key: str) -> bool:
        return key in self._signals
    
    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._signals:
            return default
        return self._signals[key].value
    
    def keys(self) -> List[str]:
        # Access the keys signal to create a dependency
        _ = self._keys_signal.value
        return list(self._signals.keys())
    
    def values(self) -> List[Any]:
        # Access the keys signal to create a dependency
        _ = self._keys_signal.value
        return [signal.value for signal in self._signals.values()]
    
    def items(self) -> List[tuple]:
        # Access the keys signal to create a dependency
        _ = self._keys_signal.value
        return [(key, signal.value) for key, signal in self._signals.items()]
    
    def on_change(self, key: str, callback: Callable[[Any], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the value of the given key changes.
        
        Returns a function that can be called to unregister the callback.
        """
        if key not in self._signals:
            self._signals[key] = Signal(None, f"dict_{key}")
            keys = self._keys_signal.value.copy()
            keys.append(key)
            self._keys_signal.value = keys
        
        return self._signals[key].on_change(callback)
    
    def on_keys_change(self, callback: Callable[[List[str]], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the keys of the dictionary change.
        
        Returns a function that can be called to unregister the callback.
        """
        return self._keys_signal.on_change(callback)
    
    def delete(self, key: str) -> bool:
        """Delete a key from the dictionary and return True if it existed."""
        if key in self._signals:
            del self._signals[key]
            keys = self._keys_signal.value.copy()
            keys.remove(key)
            self._keys_signal.value = keys
            return True
        return False

class ReactiveList:
    """A list-like object with reactive properties."""
    
    def __init__(self, initial_data: List[Any] = None):
        self._items: List[Signal] = []
        self._length = Signal(0, "list_length")
        
        if initial_data:
            for i, item in enumerate(initial_data):
                self._items.append(Signal(item, f"list_item_{i}"))
            self._length.value = len(initial_data)
    
    def __getitem__(self, index: int) -> Any:
        if index < 0 or index >= len(self._items):
            raise IndexError("List index out of range")
        return self._items[index].value
    
    def __setitem__(self, index: int, value: Any) -> None:
        if index < 0 or index >= len(self._items):
            raise IndexError("List index out of range")
        self._items[index].value = value
    
    def __len__(self) -> int:
        return self._length.value
    
    def __iter__(self):
        """Make the list iterable, creating dependencies on all items."""
        for i in range(len(self._items)):
            yield self[i]
    
    def append(self, value: Any) -> None:
        index = len(self._items)
        self._items.append(Signal(value, f"list_item_{index}"))
        self._length.value += 1
    
    def pop(self, index: int = -1) -> Any:
        if not self._items:
            raise IndexError("Pop from empty list")
        
        if index < 0:
            index = len(self._items) + index
        
        if index < 0 or index >= len(self._items):
            raise IndexError("List index out of range")
        
        item = self._items.pop(index)
        self._length.value -= 1
        
        # Rename remaining items for better debugging
        for i in range(index, len(self._items)):
            self._items[i]._name = f"list_item_{i}"
            
        return item.value
    
    def insert(self, index: int, value: Any) -> None:
        if index < 0:
            index = len(self._items) + index + 1
        
        index = max(0, min(len(self._items), index))
        self._items.insert(index, Signal(value, f"list_item_{index}"))
        self._length.value += 1
        
        # Rename items after the insertion point for better debugging
        for i in range(index + 1, len(self._items)):
            self._items[i]._name = f"list_item_{i}"
    
    def remove(self, value: Any) -> None:
        for i, item in enumerate(self._items):
            if item.value == value:
                self._items.pop(i)
                self._length.value -= 1
                
                # Rename remaining items for better debugging
                for j in range(i, len(self._items)):
                    self._items[j]._name = f"list_item_{j}"
                return
        
        raise ValueError(f"{value} not in list")
    
    def clear(self) -> None:
        self._items.clear()
        self._length.value = 0
    
    def on_change(self, index: int, callback: Callable[[Any], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the value at the given index changes.
        
        Returns a function that can be called to unregister the callback.
        """
        if index < 0 or index >= len(self._items):
            raise IndexError("List index out of range")
        
        return self._items[index].on_change(callback)
    
    def on_length_change(self, callback: Callable[[int], None]) -> Callable[[], None]:
        """
        Register a callback to be called when the length of the list changes.
        
        Returns a function that can be called to unregister the callback.
        """
        return self._length.on_change(callback)
    
    def map(self, transform_fn: Callable[[Any], Any]) -> List[Any]:
        """
        Apply a transform function to each item in the list.
        This creates a dependency on the list length and all items.
        """
        result = []
        for i in range(len(self)):
            result.append(transform_fn(self[i]))
        return result
    
    def filter(self, predicate_fn: Callable[[Any], bool]) -> List[Any]:
        """
        Filter the list using a predicate function.
        This creates a dependency on the list length and all items.
        """
        result = []
        for i in range(len(self)):
            item = self[i]
            if predicate_fn(item):
                result.append(item)
        return result