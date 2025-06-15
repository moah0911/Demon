"""
Standard library for the Demon programming language.
"""

from typing import Any, Dict, List, Optional, Union, Callable
import time
import math
import random
from .string_methods import DemonStringMethods

class DemonStdLib:
    """Standard library for the Demon programming language."""
    
    @staticmethod
    def register_all(interpreter):
        """Register all standard library functions with the interpreter."""
        # Math functions
        interpreter.globals.define("sqrt", interpreter.NativeFunction("sqrt", 1, math.sqrt))
        interpreter.globals.define("sin", interpreter.NativeFunction("sin", 1, math.sin))
        interpreter.globals.define("cos", interpreter.NativeFunction("cos", 1, math.cos))
        interpreter.globals.define("tan", interpreter.NativeFunction("tan", 1, math.tan))
        interpreter.globals.define("abs", interpreter.NativeFunction("abs", 1, abs))
        interpreter.globals.define("pow", interpreter.NativeFunction("pow", 2, pow))
        interpreter.globals.define("round", interpreter.NativeFunction("round", 1, round))
        interpreter.globals.define("floor", interpreter.NativeFunction("floor", 1, math.floor))
        interpreter.globals.define("ceil", interpreter.NativeFunction("ceil", 1, math.ceil))
        
        # Random functions
        interpreter.globals.define("random", interpreter.NativeFunction("random", 0, random.random))
        interpreter.globals.define("randint", interpreter.NativeFunction("randint", 2, random.randint))
        interpreter.globals.define("choice", interpreter.NativeFunction("choice", 1, random.choice))
        interpreter.globals.define("shuffle", interpreter.NativeFunction("shuffle", 1, lambda x: random.shuffle(x) or x))
        
        # Time functions
        interpreter.globals.define("time", interpreter.NativeFunction("time", 0, time.time))
        interpreter.globals.define("sleep", interpreter.NativeFunction("sleep", 1, time.sleep))
        
        # String functions
        interpreter.globals.define("str", interpreter.NativeFunction("str", 1, str))
        interpreter.globals.define("len", interpreter.NativeFunction("len", 1, len))
        interpreter.globals.define("split", interpreter.NativeFunction("split", 2, lambda s, sep=" ": s.split(sep)))
        interpreter.globals.define("join", interpreter.NativeFunction("join", 2, lambda sep, parts: sep.join(parts)))
        interpreter.globals.define("upper", interpreter.NativeFunction("upper", 1, lambda s: s.upper()))
        interpreter.globals.define("lower", interpreter.NativeFunction("lower", 1, lambda s: s.lower()))
        interpreter.globals.define("trim", interpreter.NativeFunction("trim", 1, lambda s: s.strip()))
        
        # Register enhanced string methods
        DemonStringMethods.register_all(interpreter)
        
        # List functions
        interpreter.globals.define("list", interpreter.NativeFunction("list", 1, list))
        interpreter.globals.define("append", interpreter.NativeFunction("append", 2, lambda lst, item: lst.append(item) or lst))
        interpreter.globals.define("pop", interpreter.NativeFunction("pop", 1, lambda lst, idx=-1: lst.pop(idx)))
        interpreter.globals.define("insert", interpreter.NativeFunction("insert", 3, lambda lst, idx, item: lst.insert(idx, item) or lst))
        interpreter.globals.define("remove", interpreter.NativeFunction("remove", 2, lambda lst, item: lst.remove(item) or lst))
        interpreter.globals.define("slice", interpreter.NativeFunction("slice", 3, lambda lst, start, end: lst[start:end]))
        
        # Dict functions
        interpreter.globals.define("dict", interpreter.NativeFunction("dict", 1, lambda pairs=None: dict(pairs or [])))
        interpreter.globals.define("keys", interpreter.NativeFunction("keys", 1, lambda d: list(d.keys())))
        interpreter.globals.define("values", interpreter.NativeFunction("values", 1, lambda d: list(d.values())))
        interpreter.globals.define("items", interpreter.NativeFunction("items", 1, lambda d: list(d.items())))
        interpreter.globals.define("get", interpreter.NativeFunction("get", 3, lambda d, key, default=None: d.get(key, default)))
        
        # Type conversion
        interpreter.globals.define("int", interpreter.NativeFunction("int", 1, lambda x: int(x)))
        interpreter.globals.define("float", interpreter.NativeFunction("float", 1, lambda x: float(x)))
        interpreter.globals.define("bool", interpreter.NativeFunction("bool", 1, lambda x: bool(x)))
        
        # Utility functions
        interpreter.globals.define("print", interpreter.NativeFunction("print", -1, lambda *args: print(*args)))
        interpreter.globals.define("input", interpreter.NativeFunction("input", 1, lambda prompt="": input(prompt)))
        interpreter.globals.define("range", interpreter.NativeFunction("range", -1, lambda *args: list(range(*args))))
        interpreter.globals.define("type", interpreter.NativeFunction("type", 1, lambda x: type(x).__name__))
        
        # Time module
        time_module = {
            "now": interpreter.NativeFunction("now", 0, time.time),
            "sleep": interpreter.NativeFunction("sleep", 1, time.sleep),
            "format": interpreter.NativeFunction("format", 1, lambda t=None: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t) if t else time.localtime())),
        }
        interpreter.globals.define("time", time_module)
        
        # Math module
        math_module = {
            "pi": math.pi,
            "e": math.e,
            "sqrt": interpreter.NativeFunction("sqrt", 1, math.sqrt),
            "sin": interpreter.NativeFunction("sin", 1, math.sin),
            "cos": interpreter.NativeFunction("cos", 1, math.cos),
            "tan": interpreter.NativeFunction("tan", 1, math.tan),
            "log": interpreter.NativeFunction("log", 1, math.log),
            "log10": interpreter.NativeFunction("log10", 1, math.log10),
            "exp": interpreter.NativeFunction("exp", 1, math.exp),
        }
        interpreter.globals.define("math", math_module)
        
        # Random module
        random_module = {
            "random": interpreter.NativeFunction("random", 0, random.random),
            "randint": interpreter.NativeFunction("randint", 2, random.randint),
            "choice": interpreter.NativeFunction("choice", 1, random.choice),
            "shuffle": interpreter.NativeFunction("shuffle", 1, lambda x: random.shuffle(x) or x),
        }
        interpreter.globals.define("random", random_module)