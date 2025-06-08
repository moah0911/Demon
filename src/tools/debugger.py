"""
Debugger for the Demon programming language.
This module provides debugging capabilities for Demon programs.
"""

import os
import sys
import cmd
import time
import threading
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum, auto

import demon_ast as ast
from tokens import Token, TokenType
from interpreter import Interpreter, Environment

class BreakpointType(Enum):
    """Types of breakpoints."""
    LINE = auto()
    FUNCTION = auto()
    EXCEPTION = auto()
    CONDITION = auto()

class Breakpoint:
    """Represents a breakpoint in the debugger."""
    
    def __init__(self, id: int, type: BreakpointType, file: str, line: int = None, 
                 function: str = None, condition: str = None, enabled: bool = True):
        self.id = id
        self.type = type
        self.file = file
        self.line = line
        self.function = function
        self.condition = condition
        self.enabled = enabled
        self.hit_count = 0
    
    def __str__(self) -> str:
        if self.type == BreakpointType.LINE:
            return f"#{self.id} Line {self.line} in {self.file}"
        elif self.type == BreakpointType.FUNCTION:
            return f"#{self.id} Function {self.function} in {self.file}"
        elif self.type == BreakpointType.EXCEPTION:
            return f"#{self.id} Exception in {self.file}"
        elif self.type == BreakpointType.CONDITION:
            return f"#{self.id} Condition '{self.condition}' at line {self.line} in {self.file}"
        return f"#{self.id} Unknown breakpoint"

class DebuggerState(Enum):
    """States of the debugger."""
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STEPPING = auto()
    STEP_OVER = auto()
    STEP_INTO = auto()
    STEP_OUT = auto()

class DebuggerEvent(Enum):
    """Events that can occur during debugging."""
    BREAKPOINT_HIT = auto()
    STEP_COMPLETE = auto()
    EXCEPTION = auto()
    PROGRAM_EXIT = auto()

class DebugFrame:
    """Represents a stack frame in the debugger."""
    
    def __init__(self, function_name: str, file: str, line: int, environment: Environment):
        self.function_name = function_name
        self.file = file
        self.line = line
        self.environment = environment
    
    def __str__(self) -> str:
        return f"{self.function_name} at {self.file}:{self.line}"

class DebuggerInterpreter(Interpreter):
    """Extended interpreter with debugging capabilities."""
    
    def __init__(self, demon, debugger):
        super().__init__(demon)
        self.debugger = debugger
        self.current_file = "<stdin>"
        self.current_line = 0
        self.current_function = "global"
        self.call_stack: List[DebugFrame] = []
        self.step_depth = 0
    
    def execute(self, stmt: ast.Stmt):
        """Execute a statement with debugging."""
        # Update current position
        if hasattr(stmt, 'line'):
            self.current_line = stmt.line
        
        # Check for breakpoints
        self.debugger.check_breakpoints(self.current_file, self.current_line, self.current_function)
        
        # Check for stepping
        self.debugger.check_stepping()
        
        # Execute the statement
        return super().execute(stmt)
    
    def visit_function_stmt(self, stmt: ast.Function):
        """Visit a function statement with debugging."""
        self.current_function = stmt.name.lexeme
        result = super().visit_function_stmt(stmt)
        self.current_function = "global"
        return result
    
    def visit_call_expr(self, expr: ast.Call):
        """Visit a call expression with debugging."""
        # Get callee name
        callee_name = "anonymous"
        if isinstance(expr.callee, ast.Variable):
            callee_name = expr.callee.name.lexeme
        
        # Push call frame
        frame = DebugFrame(callee_name, self.current_file, self.current_line, self.environment)
        self.call_stack.append(frame)
        self.step_depth += 1
        
        # Call the function
        try:
            result = super().visit_call_expr(expr)
        except Exception as e:
            # Pop call frame
            self.call_stack.pop()
            self.step_depth -= 1
            raise e
        
        # Pop call frame
        self.call_stack.pop()
        self.step_depth -= 1
        
        return result

class Debugger:
    """Debugger for the Demon language."""
    
    def __init__(self, demon):
        self.demon = demon
        self.state = DebuggerState.STOPPED
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.next_breakpoint_id = 1
        self.interpreter = DebuggerInterpreter(demon, self)
        self.current_file = "<stdin>"
        self.source_files: Dict[str, List[str]] = {}
        self.event_queue = []
        self.event_lock = threading.Lock()
        self.event_condition = threading.Condition(self.event_lock)
        self.watch_expressions: Dict[int, str] = {}
        self.next_watch_id = 1
    
    def start(self, file_path: str) -> None:
        """Start debugging a file."""
        self.current_file = file_path
        self.state = DebuggerState.RUNNING
        
        # Load source file
        self._load_source_file(file_path)
        
        # Create debugger CLI
        cli = DebuggerCLI(self)
        cli_thread = threading.Thread(target=cli.cmdloop)
        cli_thread.daemon = True
        cli_thread.start()
        
        # Run the program
        try:
            self.demon.run_file(file_path)
        except Exception as e:
            self._handle_exception(e)
        finally:
            self.state = DebuggerState.STOPPED
            self._notify_event(DebuggerEvent.PROGRAM_EXIT)
    
    def add_breakpoint(self, file: str, line: int = None, function: str = None, 
                      condition: str = None) -> int:
        """Add a breakpoint."""
        bp_id = self.next_breakpoint_id
        self.next_breakpoint_id += 1
        
        if line is not None:
            bp_type = BreakpointType.LINE
            if condition:
                bp_type = BreakpointType.CONDITION
        elif function is not None:
            bp_type = BreakpointType.FUNCTION
        else:
            bp_type = BreakpointType.EXCEPTION
        
        bp = Breakpoint(bp_id, bp_type, file, line, function, condition)
        self.breakpoints[bp_id] = bp
        
        return bp_id
    
    def remove_breakpoint(self, bp_id: int) -> bool:
        """Remove a breakpoint."""
        if bp_id in self.breakpoints:
            del self.breakpoints[bp_id]
            return True
        return False
    
    def enable_breakpoint(self, bp_id: int) -> bool:
        """Enable a breakpoint."""
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = True
            return True
        return False
    
    def disable_breakpoint(self, bp_id: int) -> bool:
        """Disable a breakpoint."""
        if bp_id in self.breakpoints:
            self.breakpoints[bp_id].enabled = False
            return True
        return False
    
    def list_breakpoints(self) -> List[Breakpoint]:
        """List all breakpoints."""
        return list(self.breakpoints.values())
    
    def check_breakpoints(self, file: str, line: int, function: str) -> bool:
        """Check if any breakpoint is hit."""
        if self.state == DebuggerState.STOPPED:
            return False
        
        for bp in self.breakpoints.values():
            if not bp.enabled:
                continue
            
            if bp.type == BreakpointType.LINE and bp.file == file and bp.line == line:
                return self._handle_breakpoint_hit(bp)
            
            if bp.type == BreakpointType.FUNCTION and bp.file == file and bp.function == function:
                return self._handle_breakpoint_hit(bp)
            
            if bp.type == BreakpointType.CONDITION and bp.file == file and bp.line == line:
                # Evaluate condition
                try:
                    result = self._evaluate_expression(bp.condition)
                    if result:
                        return self._handle_breakpoint_hit(bp)
                except Exception:
                    pass
        
        return False
    
    def check_stepping(self) -> bool:
        """Check if stepping should pause execution."""
        if self.state == DebuggerState.STEPPING:
            self.state = DebuggerState.PAUSED
            self._notify_event(DebuggerEvent.STEP_COMPLETE)
            return True
        
        if self.state == DebuggerState.STEP_OVER and self.interpreter.step_depth <= 0:
            self.state = DebuggerState.PAUSED
            self._notify_event(DebuggerEvent.STEP_COMPLETE)
            return True
        
        if self.state == DebuggerState.STEP_OUT and self.interpreter.step_depth < 0:
            self.state = DebuggerState.PAUSED
            self._notify_event(DebuggerEvent.STEP_COMPLETE)
            return True
        
        return False
    
    def step(self) -> None:
        """Step to the next statement."""
        self.state = DebuggerState.STEPPING
        self._continue_execution()
    
    def step_over(self) -> None:
        """Step over function calls."""
        self.state = DebuggerState.STEP_OVER
        self._continue_execution()
    
    def step_into(self) -> None:
        """Step into function calls."""
        self.state = DebuggerState.STEP_INTO
        self._continue_execution()
    
    def step_out(self) -> None:
        """Step out of the current function."""
        self.state = DebuggerState.STEP_OUT
        self._continue_execution()
    
    def continue_execution(self) -> None:
        """Continue execution until next breakpoint."""
        self.state = DebuggerState.RUNNING
        self._continue_execution()
    
    def pause(self) -> None:
        """Pause execution."""
        if self.state == DebuggerState.RUNNING:
            self.state = DebuggerState.PAUSED
    
    def get_stack_trace(self) -> List[DebugFrame]:
        """Get the current stack trace."""
        return self.interpreter.call_stack.copy()
    
    def get_variables(self, frame_index: int = 0) -> Dict[str, Any]:
        """Get variables in the specified stack frame."""
        if not self.interpreter.call_stack:
            return self._get_global_variables()
        
        if frame_index < 0 or frame_index >= len(self.interpreter.call_stack):
            return {}
        
        frame = self.interpreter.call_stack[frame_index]
        return self._get_environment_variables(frame.environment)
    
    def evaluate_expression(self, expression: str) -> Any:
        """Evaluate an expression in the current context."""
        return self._evaluate_expression(expression)
    
    def add_watch(self, expression: str) -> int:
        """Add a watch expression."""
        watch_id = self.next_watch_id
        self.next_watch_id += 1
        self.watch_expressions[watch_id] = expression
        return watch_id
    
    def remove_watch(self, watch_id: int) -> bool:
        """Remove a watch expression."""
        if watch_id in self.watch_expressions:
            del self.watch_expressions[watch_id]
            return True
        return False
    
    def get_watches(self) -> Dict[int, Tuple[str, Any]]:
        """Get all watch expressions and their values."""
        result = {}
        for watch_id, expr in self.watch_expressions.items():
            try:
                value = self._evaluate_expression(expr)
                result[watch_id] = (expr, value)
            except Exception as e:
                result[watch_id] = (expr, f"Error: {str(e)}")
        return result
    
    def get_source_lines(self, file: str, start_line: int, end_line: int) -> List[str]:
        """Get source lines from a file."""
        if file not in self.source_files:
            self._load_source_file(file)
        
        if file not in self.source_files:
            return []
        
        lines = self.source_files[file]
        start_line = max(0, start_line - 1)  # Convert to 0-based index
        end_line = min(len(lines), end_line)
        
        return lines[start_line:end_line]
    
    def _load_source_file(self, file_path: str) -> None:
        """Load a source file."""
        try:
            with open(file_path, 'r') as f:
                self.source_files[file_path] = f.read().splitlines()
        except Exception:
            pass
    
    def _handle_breakpoint_hit(self, bp: Breakpoint) -> bool:
        """Handle a breakpoint hit."""
        bp.hit_count += 1
        self.state = DebuggerState.PAUSED
        self._notify_event(DebuggerEvent.BREAKPOINT_HIT, bp)
        return True
    
    def _handle_exception(self, exception: Exception) -> None:
        """Handle an exception during debugging."""
        self.state = DebuggerState.PAUSED
        self._notify_event(DebuggerEvent.EXCEPTION, exception)
    
    def _continue_execution(self) -> None:
        """Continue execution after being paused."""
        with self.event_condition:
            self.event_condition.notify_all()
    
    def _notify_event(self, event: DebuggerEvent, data: Any = None) -> None:
        """Notify about a debugging event."""
        with self.event_condition:
            self.event_queue.append((event, data))
            self.event_condition.notify_all()
            
            # Wait for continue signal
            if self.state == DebuggerState.PAUSED:
                self.event_condition.wait()
    
    def _get_global_variables(self) -> Dict[str, Any]:
        """Get global variables."""
        return self._get_environment_variables(self.interpreter.globals)
    
    def _get_environment_variables(self, env: Environment) -> Dict[str, Any]:
        """Get variables from an environment."""
        result = {}
        
        # Get variables from current environment
        for name, (value, _) in env.values.items():
            result[name] = value
        
        # Get variables from enclosing environments
        if env.enclosing:
            enclosing_vars = self._get_environment_variables(env.enclosing)
            # Only add variables that don't shadow local ones
            for name, value in enclosing_vars.items():
                if name not in result:
                    result[name] = value
        
        return result
    
    def _evaluate_expression(self, expression: str) -> Any:
        """Evaluate an expression in the current context."""
        # Parse expression
        from scanner import Scanner
        from parser import Parser
        
        scanner = Scanner(expression, "<debugger>")
        tokens = scanner.scan_tokens()
        
        parser = Parser(tokens, self.demon)
        expr = parser.expression()
        
        # Evaluate expression
        return self.interpreter.evaluate(expr)

class DebuggerCLI(cmd.Cmd):
    """Command-line interface for the debugger."""
    
    intro = "Demon Debugger. Type 'help' for help."
    prompt = "(demon-debug) "
    
    def __init__(self, debugger: Debugger):
        super().__init__()
        self.debugger = debugger
        self.event_thread = threading.Thread(target=self._event_loop)
        self.event_thread.daemon = True
        self.event_thread.start()
    
    def _event_loop(self):
        """Event loop for handling debugger events."""
        while True:
            with self.debugger.event_condition:
                while not self.debugger.event_queue:
                    self.debugger.event_condition.wait()
                
                event, data = self.debugger.event_queue.pop(0)
            
            self._handle_event(event, data)
    
    def _handle_event(self, event: DebuggerEvent, data: Any):
        """Handle a debugger event."""
        if event == DebuggerEvent.BREAKPOINT_HIT:
            bp = data
            print(f"\nBreakpoint {bp.id} hit at {bp.file}:{bp.line}")
            self._show_current_line()
        
        elif event == DebuggerEvent.STEP_COMPLETE:
            print("\nStepped to:")
            self._show_current_line()
        
        elif event == DebuggerEvent.EXCEPTION:
            exception = data
            print(f"\nException: {exception}")
            self._show_current_line()
        
        elif event == DebuggerEvent.PROGRAM_EXIT:
            print("\nProgram exited.")
    
    def _show_current_line(self):
        """Show the current source line."""
        interpreter = self.debugger.interpreter
        file = interpreter.current_file
        line = interpreter.current_line
        
        # Get source context
        context_lines = self.debugger.get_source_lines(file, max(1, line - 2), line + 3)
        
        # Print context
        for i, source_line in enumerate(context_lines):
            line_num = max(1, line - 2) + i
            marker = ">" if line_num == line else " "
            print(f"{marker} {line_num:4d}: {source_line}")
    
    def do_break(self, arg):
        """Set a breakpoint. Usage: break <file>:<line> [condition]"""
        args = arg.split()
        if not args:
            print("Error: Missing file:line")
            return
        
        # Parse file:line
        file_line = args[0]
        if ":" not in file_line:
            print("Error: Invalid format. Use file:line")
            return
        
        file, line_str = file_line.split(":", 1)
        try:
            line = int(line_str)
        except ValueError:
            print("Error: Line must be a number")
            return
        
        # Parse condition
        condition = None
        if len(args) > 1:
            condition = " ".join(args[1:])
        
        # Add breakpoint
        bp_id = self.debugger.add_breakpoint(file, line, condition=condition)
        print(f"Breakpoint {bp_id} set at {file}:{line}")
    
    def do_break_function(self, arg):
        """Set a breakpoint at function. Usage: break_function <file>:<function>"""
        if not arg:
            print("Error: Missing file:function")
            return
        
        # Parse file:function
        if ":" not in arg:
            print("Error: Invalid format. Use file:function")
            return
        
        file, function = arg.split(":", 1)
        
        # Add breakpoint
        bp_id = self.debugger.add_breakpoint(file, function=function)
        print(f"Breakpoint {bp_id} set at function {function} in {file}")
    
    def do_info(self, arg):
        """Show debugger information. Usage: info breakpoints|stack|variables|watches"""
        if not arg:
            print("Error: Missing argument")
            return
        
        if arg == "breakpoints":
            breakpoints = self.debugger.list_breakpoints()
            if not breakpoints:
                print("No breakpoints set.")
                return
            
            print("Breakpoints:")
            for bp in breakpoints:
                status = "enabled" if bp.enabled else "disabled"
                print(f"  {bp} ({status}, hit {bp.hit_count} times)")
        
        elif arg == "stack":
            stack = self.debugger.get_stack_trace()
            if not stack:
                print("No stack frames.")
                return
            
            print("Stack trace:")
            for i, frame in enumerate(stack):
                print(f"  #{i}: {frame}")
        
        elif arg == "variables":
            variables = self.debugger.get_variables()
            if not variables:
                print("No variables.")
                return
            
            print("Variables:")
            for name, value in variables.items():
                print(f"  {name} = {value}")
        
        elif arg == "watches":
            watches = self.debugger.get_watches()
            if not watches:
                print("No watch expressions.")
                return
            
            print("Watch expressions:")
            for watch_id, (expr, value) in watches.items():
                print(f"  #{watch_id}: {expr} = {value}")
        
        else:
            print(f"Unknown info command: {arg}")
    
    def do_delete(self, arg):
        """Delete a breakpoint. Usage: delete <breakpoint_id>"""
        try:
            bp_id = int(arg)
        except ValueError:
            print("Error: Breakpoint ID must be a number")
            return
        
        if self.debugger.remove_breakpoint(bp_id):
            print(f"Breakpoint {bp_id} deleted")
        else:
            print(f"No breakpoint with ID {bp_id}")
    
    def do_enable(self, arg):
        """Enable a breakpoint. Usage: enable <breakpoint_id>"""
        try:
            bp_id = int(arg)
        except ValueError:
            print("Error: Breakpoint ID must be a number")
            return
        
        if self.debugger.enable_breakpoint(bp_id):
            print(f"Breakpoint {bp_id} enabled")
        else:
            print(f"No breakpoint with ID {bp_id}")
    
    def do_disable(self, arg):
        """Disable a breakpoint. Usage: disable <breakpoint_id>"""
        try:
            bp_id = int(arg)
        except ValueError:
            print("Error: Breakpoint ID must be a number")
            return
        
        if self.debugger.disable_breakpoint(bp_id):
            print(f"Breakpoint {bp_id} disabled")
        else:
            print(f"No breakpoint with ID {bp_id}")
    
    def do_step(self, arg):
        """Step to the next statement."""
        self.debugger.step()
    
    def do_next(self, arg):
        """Step over function calls."""
        self.debugger.step_over()
    
    def do_stepin(self, arg):
        """Step into function calls."""
        self.debugger.step_into()
    
    def do_stepout(self, arg):
        """Step out of the current function."""
        self.debugger.step_out()
    
    def do_continue(self, arg):
        """Continue execution until next breakpoint."""
        self.debugger.continue_execution()
    
    def do_pause(self, arg):
        """Pause execution."""
        self.debugger.pause()
    
    def do_print(self, arg):
        """Print the value of an expression. Usage: print <expression>"""
        if not arg:
            print("Error: Missing expression")
            return
        
        try:
            value = self.debugger.evaluate_expression(arg)
            print(f"{arg} = {value}")
        except Exception as e:
            print(f"Error evaluating expression: {e}")
    
    def do_watch(self, arg):
        """Add a watch expression. Usage: watch <expression>"""
        if not arg:
            print("Error: Missing expression")
            return
        
        watch_id = self.debugger.add_watch(arg)
        print(f"Watch #{watch_id} added: {arg}")
    
    def do_unwatch(self, arg):
        """Remove a watch expression. Usage: unwatch <watch_id>"""
        try:
            watch_id = int(arg)
        except ValueError:
            print("Error: Watch ID must be a number")
            return
        
        if self.debugger.remove_watch(watch_id):
            print(f"Watch #{watch_id} removed")
        else:
            print(f"No watch with ID {watch_id}")
    
    def do_list(self, arg):
        """List source code. Usage: list [file:line] [count]"""
        # Default values
        file = self.debugger.interpreter.current_file
        line = self.debugger.interpreter.current_line
        count = 10
        
        args = arg.split()
        if args:
            # Parse file:line
            if ":" in args[0]:
                file_line = args[0]
                file, line_str = file_line.split(":", 1)
                try:
                    line = int(line_str)
                except ValueError:
                    print("Error: Line must be a number")
                    return
                
                args = args[1:]
            
            # Parse count
            if args:
                try:
                    count = int(args[0])
                except ValueError:
                    print("Error: Count must be a number")
                    return
        
        # Get source lines
        start_line = max(1, line - count // 2)
        end_line = start_line + count
        lines = self.debugger.get_source_lines(file, start_line, end_line)
        
        # Print lines
        for i, source_line in enumerate(lines):
            line_num = start_line + i
            marker = ">" if line_num == line else " "
            print(f"{marker} {line_num:4d}: {source_line}")
    
    def do_quit(self, arg):
        """Quit the debugger."""
        print("Exiting debugger...")
        return True
    
    def do_exit(self, arg):
        """Exit the debugger."""
        return self.do_quit(arg)
    
    def do_help(self, arg):
        """Show help message."""
        if not arg:
            print("Available commands:")
            print("  break <file>:<line> [condition] - Set a breakpoint")
            print("  break_function <file>:<function> - Set a breakpoint at function")
            print("  delete <breakpoint_id> - Delete a breakpoint")
            print("  enable <breakpoint_id> - Enable a breakpoint")
            print("  disable <breakpoint_id> - Disable a breakpoint")
            print("  info breakpoints|stack|variables|watches - Show debugger information")
            print("  step - Step to the next statement")
            print("  next - Step over function calls")
            print("  stepin - Step into function calls")
            print("  stepout - Step out of the current function")
            print("  continue - Continue execution until next breakpoint")
            print("  pause - Pause execution")
            print("  print <expression> - Print the value of an expression")
            print("  watch <expression> - Add a watch expression")
            print("  unwatch <watch_id> - Remove a watch expression")
            print("  list [file:line] [count] - List source code")
            print("  quit, exit - Quit the debugger")
            print("  help [command] - Show help message")
        else:
            # Show help for specific command
            cmd.Cmd.do_help(self, arg)