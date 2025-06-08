"""
Standard library for the Demon programming language.
"""

import math
import random
import time
from typing import List, Dict, Any, Optional, Union, Callable

class DemonStdLib:
    """Standard library for the Demon programming language."""
    
    @staticmethod
    def register_all(interpreter):
        """Register all standard library functions with the interpreter."""
        # Create NativeFunction class reference
        NativeFunction = interpreter.NativeFunction if hasattr(interpreter, 'NativeFunction') else type('NativeFunction', (), {
            '__init__': lambda self, name, arity, function: setattr(self, 'name', name) or setattr(self, 'arity', arity) or setattr(self, 'function', function),
            '__call__': lambda self, *args: self.function(*args)
        })
        
        # Math functions
        interpreter.globals.define("sin", NativeFunction("sin", 1, math.sin))
        interpreter.globals.define("cos", NativeFunction("cos", 1, math.cos))
        interpreter.globals.define("tan", NativeFunction("tan", 1, math.tan))
        interpreter.globals.define("sqrt", NativeFunction("sqrt", 1, math.sqrt))
        interpreter.globals.define("pow", NativeFunction("pow", 2, math.pow))
        interpreter.globals.define("exp", NativeFunction("exp", 1, math.exp))
        interpreter.globals.define("log", NativeFunction("log", 1, math.log))
        interpreter.globals.define("log10", NativeFunction("log10", 1, math.log10))
        interpreter.globals.define("floor", NativeFunction("floor", 1, math.floor))
        interpreter.globals.define("ceil", NativeFunction("ceil", 1, math.ceil))
        interpreter.globals.define("round", NativeFunction("round", 2, round))
        interpreter.globals.define("abs", NativeFunction("abs", 1, abs))
        interpreter.globals.define("pi", math.pi)
        interpreter.globals.define("e", math.e)
        
        # Random functions
        interpreter.globals.define("random", NativeFunction("random", 0, random.random))
        interpreter.globals.define("randint", NativeFunction("randint", 2, random.randint))
        interpreter.globals.define("choice", NativeFunction("choice", 1, random.choice))
        
        # String functions
        interpreter.globals.define("upper", NativeFunction("upper", 1, lambda s: s.upper()))
        interpreter.globals.define("lower", NativeFunction("lower", 1, lambda s: s.lower()))
        interpreter.globals.define("trim", NativeFunction("trim", 1, lambda s: s.strip()))
        interpreter.globals.define("split", NativeFunction("split", 2, lambda s, sep=" ": s.split(sep)))
        interpreter.globals.define("contains", NativeFunction("contains", 2, lambda s, sub: sub in s))
        interpreter.globals.define("replace", NativeFunction("replace", 3, lambda s, old, new: s.replace(old, new)))
        
        # List functions
        interpreter.globals.define("append", NativeFunction("append", 2, lambda lst, item: lst.append(item) or lst))
        interpreter.globals.define("insert", NativeFunction("insert", 3, lambda lst, idx, item: lst.insert(idx, item) or lst))
        interpreter.globals.define("slice", NativeFunction("slice", 3, lambda lst, start, end: lst[start:end]))
        interpreter.globals.define("reverse", NativeFunction("reverse", 1, lambda lst: lst[::-1]))
        interpreter.globals.define("sort", NativeFunction("sort", 1, lambda lst: sorted(lst)))
        
        # Higher-order functions
        interpreter.globals.define("map", NativeFunction("map", 2, lambda fn, lst: [fn.call(interpreter, [x]) for x in lst]))
        interpreter.globals.define("filter", NativeFunction("filter", 2, lambda fn, lst: [x for x in lst if fn.call(interpreter, [x])]))
        interpreter.globals.define("reduce", NativeFunction("reduce", 3, lambda fn, lst, init: DemonStdLib._reduce(interpreter, fn, lst, init)))
        interpreter.globals.define("sum", NativeFunction("sum", 1, sum))
        interpreter.globals.define("min", NativeFunction("min", 1, min))
        interpreter.globals.define("max", NativeFunction("max", 1, max))
        
        # Time functions
        interpreter.globals.define("sleep", NativeFunction("sleep", 1, time.sleep))
        interpreter.globals.define("time", NativeFunction("time", 0, time.time))
    
    @staticmethod
    def _reduce(interpreter, fn, lst, init):
        """Implement reduce function."""
        result = init
        for item in lst:
            result = fn.call(interpreter, [result, item])
        return result