"""
Built-in design patterns for the Demon programming language.
"""

from typing import Dict, List, Any, Callable, Optional

# Singleton pattern
class Singleton:
    """Singleton pattern implementation."""
    
    def __init__(self, cls):
        self._cls = cls
        self._instance = None
    
    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance

# Observer pattern
class Observable:
    """Observable part of the Observer pattern."""
    
    def __init__(self):
        self._observers = []
    
    def add_observer(self, observer):
        """Add an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer):
        """Remove an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, *args, **kwargs):
        """Notify all observers."""
        for observer in self._observers:
            observer.update(*args, **kwargs)

class Observer:
    """Observer part of the Observer pattern."""
    
    def update(self, *args, **kwargs):
        """Update method called by Observable."""
        pass

# Factory pattern
class Factory:
    """Factory pattern implementation."""
    
    def __init__(self):
        self._creators = {}
    
    def register(self, type_name, creator):
        """Register a creator function for a type."""
        self._creators[type_name] = creator
    
    def create(self, type_name, *args, **kwargs):
        """Create an object of the specified type."""
        creator = self._creators.get(type_name)
        if not creator:
            raise ValueError(f"Unknown type: {type_name}")
        return creator(*args, **kwargs)

# Strategy pattern
class Strategy:
    """Strategy pattern implementation."""
    
    def __init__(self):
        self._strategies = {}
        self._default = None
    
    def register(self, name, strategy):
        """Register a strategy."""
        self._strategies[name] = strategy
    
    def set_default(self, name):
        """Set the default strategy."""
        if name not in self._strategies:
            raise ValueError(f"Unknown strategy: {name}")
        self._default = name
    
    def execute(self, name=None, *args, **kwargs):
        """Execute a strategy."""
        if name is None:
            if self._default is None:
                raise ValueError("No default strategy set")
            name = self._default
        
        strategy = self._strategies.get(name)
        if not strategy:
            raise ValueError(f"Unknown strategy: {name}")
        
        return strategy(*args, **kwargs)

# Command pattern
class Command:
    """Command pattern base class."""
    
    def execute(self):
        """Execute the command."""
        pass
    
    def undo(self):
        """Undo the command."""
        pass

class CommandManager:
    """Command manager for the Command pattern."""
    
    def __init__(self):
        self._commands = []
        self._current = -1
    
    def execute(self, command):
        """Execute a command and add it to the history."""
        # Remove any undone commands
        if self._current < len(self._commands) - 1:
            self._commands = self._commands[:self._current + 1]
        
        command.execute()
        self._commands.append(command)
        self._current += 1
    
    def undo(self):
        """Undo the last executed command."""
        if self._current >= 0:
            self._commands[self._current].undo()
            self._current -= 1
    
    def redo(self):
        """Redo the last undone command."""
        if self._current < len(self._commands) - 1:
            self._current += 1
            self._commands[self._current].execute()

# Decorator pattern
class Component:
    """Component interface for the Decorator pattern."""
    
    def operation(self):
        """Perform the operation."""
        pass

class Decorator:
    """Decorator base class for the Decorator pattern."""
    
    def __init__(self, component):
        self._component = component
    
    def operation(self):
        """Perform the operation."""
        return self._component.operation()

# Adapter pattern
class Adapter:
    """Adapter pattern implementation."""
    
    def __init__(self, adaptee, **adapted_methods):
        self.adaptee = adaptee
        self.__dict__.update(adapted_methods)
    
    def __getattr__(self, attr):
        """Delegate to adaptee for non-adapted methods."""
        return getattr(self.adaptee, attr)

# Proxy pattern
class Proxy:
    """Proxy pattern implementation."""
    
    def __init__(self, subject):
        self._subject = subject
    
    def __getattr__(self, name):
        """Delegate to subject."""
        return getattr(self._subject, name)

# Builder pattern
class Builder:
    """Builder pattern implementation."""
    
    def __init__(self):
        self._product = {}
    
    def add(self, key, value):
        """Add a component to the product."""
        self._product[key] = value
        return self
    
    def build(self):
        """Build and return the final product."""
        product = self._product.copy()
        self._product = {}
        return product

# State pattern
class State:
    """State pattern base class."""
    
    def handle(self, context):
        """Handle the state."""
        pass

class Context:
    """Context for the State pattern."""
    
    def __init__(self, initial_state):
        self._state = initial_state
    
    def set_state(self, state):
        """Set the current state."""
        self._state = state
    
    def request(self):
        """Handle a request."""
        return self._state.handle(self)

def register_design_patterns(interpreter):
    """Register all design patterns with the interpreter."""
    NativeFunction = interpreter.NativeFunction
    
    # Singleton
    interpreter.globals.define("Singleton", NativeFunction("Singleton", 1, Singleton))
    
    # Observer pattern
    interpreter.globals.define("Observable", NativeFunction("Observable", 0, lambda: Observable()))
    interpreter.globals.define("Observer", NativeFunction("Observer", 0, lambda: Observer()))
    
    # Factory pattern
    interpreter.globals.define("Factory", NativeFunction("Factory", 0, lambda: Factory()))
    
    # Strategy pattern
    interpreter.globals.define("Strategy", NativeFunction("Strategy", 0, lambda: Strategy()))
    
    # Command pattern
    interpreter.globals.define("Command", NativeFunction("Command", 0, lambda: Command()))
    interpreter.globals.define("CommandManager", NativeFunction("CommandManager", 0, lambda: CommandManager()))
    
    # Decorator pattern
    interpreter.globals.define("Component", NativeFunction("Component", 0, lambda: Component()))
    interpreter.globals.define("Decorator", NativeFunction("Decorator", 1, lambda component: Decorator(component)))
    
    # Adapter pattern
    def create_adapter(adaptee, **adapted_methods):
        return Adapter(adaptee, **adapted_methods)
    
    interpreter.globals.define("Adapter", NativeFunction("Adapter", -1, create_adapter))
    
    # Proxy pattern
    interpreter.globals.define("Proxy", NativeFunction("Proxy", 1, lambda subject: Proxy(subject)))
    
    # Builder pattern
    interpreter.globals.define("Builder", NativeFunction("Builder", 0, lambda: Builder()))
    
    # State pattern
    interpreter.globals.define("State", NativeFunction("State", 0, lambda: State()))
    interpreter.globals.define("Context", NativeFunction("Context", 1, lambda initial_state: Context(initial_state)))