"""
Standard library for the Demon programming language.
This module provides built-in functions and data structures.
"""

import math
import random
import time
import json
import re
import os
from typing import Any, List, Dict, Callable, Optional, Union, Tuple

class DemonStdLib:
    """Standard library for the Demon language."""
    
    @staticmethod
    def register_all(interpreter):
        """Register all standard library functions with the interpreter."""
        # Math functions
        interpreter.globals.define("sin", lambda x: math.sin(x))
        interpreter.globals.define("cos", lambda x: math.cos(x))
        interpreter.globals.define("tan", lambda x: math.tan(x))
        interpreter.globals.define("sqrt", lambda x: math.sqrt(x))
        interpreter.globals.define("pow", lambda x, y: math.pow(x, y))
        interpreter.globals.define("log", lambda x, base=math.e: math.log(x, base))
        interpreter.globals.define("floor", lambda x: math.floor(x))
        interpreter.globals.define("ceil", lambda x: math.ceil(x))
        interpreter.globals.define("round", lambda x, n=0: round(x, n))
        interpreter.globals.define("abs", lambda x: abs(x))
        interpreter.globals.define("pi", math.pi)
        interpreter.globals.define("e", math.e)
        
        # Random functions
        interpreter.globals.define("random", lambda: random.random())
        interpreter.globals.define("randint", lambda a, b: random.randint(a, b))
        interpreter.globals.define("choice", lambda lst: random.choice(lst))
        interpreter.globals.define("shuffle", lambda lst: random.shuffle(lst) or lst)
        
        # Time functions
        interpreter.globals.define("time", lambda: time.time())
        interpreter.globals.define("sleep", lambda secs: time.sleep(secs))
        
        # String functions
        interpreter.globals.define("len", lambda s: len(s))
        interpreter.globals.define("lower", lambda s: s.lower())
        interpreter.globals.define("upper", lambda s: s.upper())
        interpreter.globals.define("trim", lambda s: s.strip())
        interpreter.globals.define("split", lambda s, sep=" ": s.split(sep))
        interpreter.globals.define("join", lambda lst, sep="": sep.join(lst))
        interpreter.globals.define("format", lambda s, *args: s.format(*args))
        interpreter.globals.define("startswith", lambda s, prefix: s.startswith(prefix))
        interpreter.globals.define("endswith", lambda s, suffix: s.endswith(suffix))
        interpreter.globals.define("replace", lambda s, old, new: s.replace(old, new))
        interpreter.globals.define("contains", lambda s, sub: sub in s)
        
        # List functions
        interpreter.globals.define("append", lambda lst, item: lst.append(item) or lst)
        interpreter.globals.define("insert", lambda lst, idx, item: lst.insert(idx, item) or lst)
        interpreter.globals.define("remove", lambda lst, item: lst.remove(item) or lst)
        interpreter.globals.define("pop", lambda lst, idx=-1: lst.pop(idx))
        interpreter.globals.define("slice", lambda lst, start=0, end=None: lst[start:end])
        interpreter.globals.define("reverse", lambda lst: lst.reverse() or lst)
        interpreter.globals.define("sort", lambda lst, key=None: lst.sort(key=key) or lst)
        interpreter.globals.define("map", lambda fn, lst: list(map(fn, lst)))
        interpreter.globals.define("filter", lambda fn, lst: list(filter(fn, lst)))
        interpreter.globals.define("reduce", lambda fn, lst, initial=None: DemonStdLib._reduce(fn, lst, initial))
        interpreter.globals.define("all", lambda lst: all(lst))
        interpreter.globals.define("any", lambda lst: any(lst))
        interpreter.globals.define("sum", lambda lst: sum(lst))
        interpreter.globals.define("min", lambda *args: min(*args))
        interpreter.globals.define("max", lambda *args: max(*args))
        
        # Dictionary functions
        interpreter.globals.define("keys", lambda d: list(d.keys()))
        interpreter.globals.define("values", lambda d: list(d.values()))
        interpreter.globals.define("items", lambda d: list(d.items()))
        interpreter.globals.define("get", lambda d, key, default=None: d.get(key, default))
        interpreter.globals.define("has_key", lambda d, key: key in d)
        
        # Type conversion
        interpreter.globals.define("int", lambda x: int(x))
        interpreter.globals.define("float", lambda x: float(x))
        interpreter.globals.define("str", lambda x: str(x))
        interpreter.globals.define("bool", lambda x: bool(x))
        interpreter.globals.define("list", lambda x=None: list(x) if x is not None else [])
        interpreter.globals.define("dict", lambda x=None: dict(x) if x is not None else {})
        
        # JSON functions
        interpreter.globals.define("json_parse", lambda s: json.loads(s))
        interpreter.globals.define("json_stringify", lambda obj: json.dumps(obj))
        
        # Regular expressions
        interpreter.globals.define("regex_match", lambda pattern, string: bool(re.match(pattern, string)))
        interpreter.globals.define("regex_search", lambda pattern, string: bool(re.search(pattern, string)))
        interpreter.globals.define("regex_find_all", lambda pattern, string: re.findall(pattern, string))
        interpreter.globals.define("regex_replace", lambda pattern, repl, string: re.sub(pattern, repl, string))
        
        # File I/O
        interpreter.globals.define("read_file", lambda path: DemonStdLib._read_file(path))
        interpreter.globals.define("write_file", lambda path, content: DemonStdLib._write_file(path, content))
        interpreter.globals.define("append_file", lambda path, content: DemonStdLib._append_file(path, content))
        interpreter.globals.define("file_exists", lambda path: os.path.exists(path))
        interpreter.globals.define("list_dir", lambda path=".": os.listdir(path))
        
        # Data structures
        interpreter.globals.define("Stack", lambda: DemonStdLib.Stack())
        interpreter.globals.define("Queue", lambda: DemonStdLib.Queue())
        interpreter.globals.define("PriorityQueue", lambda: DemonStdLib.PriorityQueue())
        interpreter.globals.define("Set", lambda items=None: DemonStdLib.Set(items))
        interpreter.globals.define("Graph", lambda: DemonStdLib.Graph())
    
    @staticmethod
    def _reduce(fn, lst, initial=None):
        """Implement reduce function."""
        if not lst:
            return initial
        
        if initial is None:
            result = lst[0]
            lst = lst[1:]
        else:
            result = initial
        
        for item in lst:
            result = fn(result, item)
        
        return result
    
    @staticmethod
    def _read_file(path):
        """Read a file and return its contents."""
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading file: {e}")
    
    @staticmethod
    def _write_file(path, content):
        """Write content to a file."""
        try:
            with open(path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            raise RuntimeError(f"Error writing file: {e}")
    
    @staticmethod
    def _append_file(path, content):
        """Append content to a file."""
        try:
            with open(path, 'a') as f:
                f.write(content)
            return True
        except Exception as e:
            raise RuntimeError(f"Error appending to file: {e}")
    
    class Stack:
        """Stack data structure."""
        
        def __init__(self):
            self.items = []
        
        def push(self, item):
            self.items.append(item)
            return self
        
        def pop(self):
            if not self.items:
                raise RuntimeError("Cannot pop from empty stack")
            return self.items.pop()
        
        def peek(self):
            if not self.items:
                raise RuntimeError("Cannot peek empty stack")
            return self.items[-1]
        
        def is_empty(self):
            return len(self.items) == 0
        
        def size(self):
            return len(self.items)
        
        def clear(self):
            self.items = []
            return self
        
        def __str__(self):
            return f"Stack({self.items})"
    
    class Queue:
        """Queue data structure."""
        
        def __init__(self):
            self.items = []
        
        def enqueue(self, item):
            self.items.append(item)
            return self
        
        def dequeue(self):
            if not self.items:
                raise RuntimeError("Cannot dequeue from empty queue")
            return self.items.pop(0)
        
        def peek(self):
            if not self.items:
                raise RuntimeError("Cannot peek empty queue")
            return self.items[0]
        
        def is_empty(self):
            return len(self.items) == 0
        
        def size(self):
            return len(self.items)
        
        def clear(self):
            self.items = []
            return self
        
        def __str__(self):
            return f"Queue({self.items})"
    
    class PriorityQueue:
        """Priority queue data structure."""
        
        def __init__(self):
            self.items = []
        
        def enqueue(self, item, priority):
            self.items.append((priority, item))
            self.items.sort(key=lambda x: x[0])
            return self
        
        def dequeue(self):
            if not self.items:
                raise RuntimeError("Cannot dequeue from empty priority queue")
            return self.items.pop(0)[1]
        
        def peek(self):
            if not self.items:
                raise RuntimeError("Cannot peek empty priority queue")
            return self.items[0][1]
        
        def is_empty(self):
            return len(self.items) == 0
        
        def size(self):
            return len(self.items)
        
        def clear(self):
            self.items = []
            return self
        
        def __str__(self):
            return f"PriorityQueue({self.items})"
    
    class Set:
        """Set data structure."""
        
        def __init__(self, items=None):
            self.items = set(items or [])
        
        def add(self, item):
            self.items.add(item)
            return self
        
        def remove(self, item):
            self.items.remove(item)
            return self
        
        def contains(self, item):
            return item in self.items
        
        def union(self, other_set):
            if isinstance(other_set, DemonStdLib.Set):
                return DemonStdLib.Set(self.items.union(other_set.items))
            return DemonStdLib.Set(self.items.union(set(other_set)))
        
        def intersection(self, other_set):
            if isinstance(other_set, DemonStdLib.Set):
                return DemonStdLib.Set(self.items.intersection(other_set.items))
            return DemonStdLib.Set(self.items.intersection(set(other_set)))
        
        def difference(self, other_set):
            if isinstance(other_set, DemonStdLib.Set):
                return DemonStdLib.Set(self.items.difference(other_set.items))
            return DemonStdLib.Set(self.items.difference(set(other_set)))
        
        def is_subset(self, other_set):
            if isinstance(other_set, DemonStdLib.Set):
                return self.items.issubset(other_set.items)
            return self.items.issubset(set(other_set))
        
        def is_empty(self):
            return len(self.items) == 0
        
        def size(self):
            return len(self.items)
        
        def clear(self):
            self.items = set()
            return self
        
        def to_list(self):
            return list(self.items)
        
        def __str__(self):
            return f"Set({self.to_list()})"
    
    class Graph:
        """Graph data structure."""
        
        def __init__(self):
            self.vertices = {}
        
        def add_vertex(self, vertex):
            if vertex not in self.vertices:
                self.vertices[vertex] = []
            return self
        
        def add_edge(self, from_vertex, to_vertex, weight=1):
            if from_vertex not in self.vertices:
                self.add_vertex(from_vertex)
            if to_vertex not in self.vertices:
                self.add_vertex(to_vertex)
            
            self.vertices[from_vertex].append((to_vertex, weight))
            return self
        
        def get_neighbors(self, vertex):
            if vertex not in self.vertices:
                return []
            return [(v, w) for v, w in self.vertices[vertex]]
        
        def get_vertices(self):
            return list(self.vertices.keys())
        
        def dfs(self, start_vertex):
            if start_vertex not in self.vertices:
                return []
            
            visited = set()
            result = []
            
            def dfs_helper(vertex):
                visited.add(vertex)
                result.append(vertex)
                
                for neighbor, _ in self.vertices[vertex]:
                    if neighbor not in visited:
                        dfs_helper(neighbor)
            
            dfs_helper(start_vertex)
            return result
        
        def bfs(self, start_vertex):
            if start_vertex not in self.vertices:
                return []
            
            visited = {start_vertex}
            queue = [start_vertex]
            result = []
            
            while queue:
                vertex = queue.pop(0)
                result.append(vertex)
                
                for neighbor, _ in self.vertices[vertex]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            
            return result
        
        def dijkstra(self, start_vertex):
            if start_vertex not in self.vertices:
                return {}
            
            distances = {vertex: float('infinity') for vertex in self.vertices}
            distances[start_vertex] = 0
            unvisited = list(self.vertices.keys())
            
            while unvisited:
                current = min(unvisited, key=lambda vertex: distances[vertex])
                
                if distances[current] == float('infinity'):
                    break
                
                unvisited.remove(current)
                
                for neighbor, weight in self.vertices[current]:
                    distance = distances[current] + weight
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
            
            return distances
        
        def __str__(self):
            result = "Graph:\n"
            for vertex, edges in self.vertices.items():
                result += f"{vertex} -> {edges}\n"
            return result