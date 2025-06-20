"""
Implementation of static methods for Demon classes.
This module adds support for calling static methods directly on class objects.
"""

def patch_interpreter(interpreter_class):
    """
    Patch the interpreter to support static methods on classes.
    
    This function modifies the visit_get_expr method to check for static methods
    when accessing properties on class objects.
    """
    original_visit_get_expr = interpreter_class.visit_get_expr
    
    def patched_visit_get_expr(self, expr):
        obj = self.evaluate(expr.obj)
        
        # Check if the object is a class and has static methods
        if hasattr(obj, 'get_static_method') and callable(obj.get_static_method):
            static_method = obj.get_static_method(expr.name.lexeme)
            if static_method is not None:
                return static_method
        
        # Fall back to the original implementation
        return original_visit_get_expr(self, expr)
    
    # Replace the original method with our patched version
    interpreter_class.visit_get_expr = patched_visit_get_expr
    
    return interpreter_class