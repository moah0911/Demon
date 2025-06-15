"""
Advanced pattern matching for the Demon programming language.
This module provides powerful pattern matching capabilities beyond what most languages offer.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, Callable

class Pattern:
    """Base class for all patterns."""
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Match a value against this pattern.
        
        Returns:
            Tuple[bool, Dict[str, Any]]: (matched, bindings)
                - matched: True if the pattern matches, False otherwise
                - bindings: Dictionary of variable bindings if matched
        """
        raise NotImplementedError("Subclasses must implement match")

class LiteralPattern(Pattern):
    """Pattern that matches a literal value."""
    
    def __init__(self, value: Any):
        self.value = value
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        return value == self.value, {}

class VariablePattern(Pattern):
    """Pattern that binds a value to a variable."""
    
    def __init__(self, name: str):
        self.name = name
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        return True, {self.name: value}

class WildcardPattern(Pattern):
    """Pattern that matches anything."""
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        return True, {}

class TypePattern(Pattern):
    """Pattern that matches a value of a specific type."""
    
    def __init__(self, type_name: str):
        self.type_name = type_name
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        if self.type_name == "int":
            return isinstance(value, int), {}
        elif self.type_name == "float":
            return isinstance(value, float), {}
        elif self.type_name == "str":
            return isinstance(value, str), {}
        elif self.type_name == "bool":
            return isinstance(value, bool), {}
        elif self.type_name == "list":
            return isinstance(value, list), {}
        elif self.type_name == "dict":
            return isinstance(value, dict), {}
        return False, {}

class ListPattern(Pattern):
    """Pattern that matches a list with specific element patterns."""
    
    def __init__(self, elements: List[Pattern], rest: Optional[str] = None):
        self.elements = elements
        self.rest = rest  # Name to bind the rest of the list
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        if not isinstance(value, list):
            return False, {}
        
        # If we have a rest pattern, we need at least as many elements as patterns minus 1
        min_length = len(self.elements) if self.rest is None else len(self.elements) - 1
        
        if len(value) < min_length:
            return False, {}
        
        bindings = {}
        
        # Match fixed elements
        for i, pattern in enumerate(self.elements):
            if i >= len(value):
                return False, {}
            
            matched, new_bindings = pattern.match(value[i])
            if not matched:
                return False, {}
            
            bindings.update(new_bindings)
        
        # Bind rest if specified
        if self.rest is not None:
            bindings[self.rest] = value[len(self.elements):]
        
        return True, bindings

class DictPattern(Pattern):
    """Pattern that matches a dictionary with specific key-value patterns."""
    
    def __init__(self, items: Dict[str, Pattern], rest: Optional[str] = None):
        self.items = items
        self.rest = rest  # Name to bind the rest of the dict
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        if not isinstance(value, dict):
            return False, {}
        
        bindings = {}
        rest_dict = dict(value) if self.rest else {}
        
        # Match specified keys
        for key, pattern in self.items.items():
            if key not in value:
                return False, {}
            
            matched, new_bindings = pattern.match(value[key])
            if not matched:
                return False, {}
            
            bindings.update(new_bindings)
            
            if self.rest:
                rest_dict.pop(key, None)
        
        # Bind rest if specified
        if self.rest:
            bindings[self.rest] = rest_dict
        
        return True, bindings

class GuardPattern(Pattern):
    """Pattern with a guard condition."""
    
    def __init__(self, pattern: Pattern, guard: Callable[[Dict[str, Any]], bool]):
        self.pattern = pattern
        self.guard = guard
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        matched, bindings = self.pattern.match(value)
        if not matched:
            return False, {}
        
        if not self.guard(bindings):
            return False, {}
        
        return True, bindings

class OrPattern(Pattern):
    """Pattern that matches if any of its subpatterns match."""
    
    def __init__(self, patterns: List[Pattern]):
        self.patterns = patterns
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        for pattern in self.patterns:
            matched, bindings = pattern.match(value)
            if matched:
                return True, bindings
        
        return False, {}

class AndPattern(Pattern):
    """Pattern that matches if all of its subpatterns match."""
    
    def __init__(self, patterns: List[Pattern]):
        self.patterns = patterns
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        all_bindings = {}
        
        for pattern in self.patterns:
            matched, bindings = pattern.match(value)
            if not matched:
                return False, {}
            
            # Check for conflicting bindings
            for name, binding in bindings.items():
                if name in all_bindings and all_bindings[name] != binding:
                    return False, {}
            
            all_bindings.update(bindings)
        
        return True, all_bindings

class NotPattern(Pattern):
    """Pattern that matches if its subpattern does not match."""
    
    def __init__(self, pattern: Pattern):
        self.pattern = pattern
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        matched, _ = self.pattern.match(value)
        return not matched, {}

class DestructurePattern(Pattern):
    """Pattern that destructures an object by accessing its attributes."""
    
    def __init__(self, attrs: Dict[str, Pattern]):
        self.attrs = attrs
    
    def match(self, value: Any) -> Tuple[bool, Dict[str, Any]]:
        if not hasattr(value, "__dict__"):
            return False, {}
        
        bindings = {}
        
        for attr_name, pattern in self.attrs.items():
            if not hasattr(value, attr_name):
                return False, {}
            
            attr_value = getattr(value, attr_name)
            matched, new_bindings = pattern.match(attr_value)
            
            if not matched:
                return False, {}
            
            bindings.update(new_bindings)
        
        return True, bindings

def create_pattern(pattern_spec: Any) -> Pattern:
    """
    Create a pattern from a pattern specification.
    
    Args:
        pattern_spec: Pattern specification in Demon syntax
        
    Returns:
        Pattern: The compiled pattern
    """
    if isinstance(pattern_spec, dict) and "_type" in pattern_spec:
        pattern_type = pattern_spec["_type"]
        
        if pattern_type == "literal":
            return LiteralPattern(pattern_spec["value"])
        elif pattern_type == "variable":
            return VariablePattern(pattern_spec["name"])
        elif pattern_type == "wildcard":
            return WildcardPattern()
        elif pattern_type == "type":
            return TypePattern(pattern_spec["name"])
        elif pattern_type == "list":
            elements = [create_pattern(elem) for elem in pattern_spec["elements"]]
            rest = pattern_spec.get("rest")
            return ListPattern(elements, rest)
        elif pattern_type == "dict":
            items = {k: create_pattern(v) for k, v in pattern_spec["items"].items()}
            rest = pattern_spec.get("rest")
            return DictPattern(items, rest)
        elif pattern_type == "or":
            patterns = [create_pattern(p) for p in pattern_spec["patterns"]]
            return OrPattern(patterns)
        elif pattern_type == "and":
            patterns = [create_pattern(p) for p in pattern_spec["patterns"]]
            return AndPattern(patterns)
        elif pattern_type == "not":
            return NotPattern(create_pattern(pattern_spec["pattern"]))
        elif pattern_type == "destructure":
            attrs = {k: create_pattern(v) for k, v in pattern_spec["attrs"].items()}
            return DestructurePattern(attrs)
    
    # Default to literal pattern
    return LiteralPattern(pattern_spec)

def match_value(value: Any, patterns: List[Tuple[Pattern, Callable]]) -> Any:
    """
    Match a value against a list of patterns and execute the corresponding action.
    
    Args:
        value: The value to match
        patterns: List of (pattern, action) pairs
        
    Returns:
        Any: The result of the matching action, or None if no pattern matches
    """
    for pattern, action in patterns:
        matched, bindings = pattern.match(value)
        if matched:
            return action(bindings)
    
    return None