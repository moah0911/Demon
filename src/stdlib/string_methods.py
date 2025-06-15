"""
String methods for the Demon language.
"""

class DemonStringMethods:
    @staticmethod
    def register_all(interpreter):
        # Create string module with methods
        string_module = {
            "length": interpreter.NativeFunction("length", 1, lambda s: len(s)),
            "upper": interpreter.NativeFunction("upper", 1, lambda s: s.upper()),
            "lower": interpreter.NativeFunction("lower", 1, lambda s: s.lower()),
            "trim": interpreter.NativeFunction("trim", 1, lambda s: s.strip()),
            "split": interpreter.NativeFunction("split", 2, lambda s, sep=" ": s.split(sep)),
            "join": interpreter.NativeFunction("join", 2, lambda sep, parts: sep.join(str(p) for p in parts)),
            "replace": interpreter.NativeFunction("replace", 3, lambda s, old, new: s.replace(old, new)),
            "contains": interpreter.NativeFunction("contains", 2, lambda s, substr: substr in s),
            "starts_with": interpreter.NativeFunction("starts_with", 2, lambda s, prefix: s.startswith(prefix)),
            "ends_with": interpreter.NativeFunction("ends_with", 2, lambda s, suffix: s.endswith(suffix)),
            "substring": interpreter.NativeFunction("substring", 3, lambda s, start, end=None: s[start:end]),
            "repeat": interpreter.NativeFunction("repeat", 2, lambda s, count: s * count),
            "reverse": interpreter.NativeFunction("reverse", 1, lambda s: s[::-1])
        }
        
        # Register the string module
        interpreter.globals.define("string", string_module)