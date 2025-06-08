"""
Enhanced standard library for the Demon programming language.
This module provides built-in functions and data structures.
"""

import math
import random
import time
import json
import re
import os
import sys
import datetime
import hashlib
import base64
import urllib.request
import urllib.parse
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
        interpreter.globals.define("asin", lambda x: math.asin(x))
        interpreter.globals.define("acos", lambda x: math.acos(x))
        interpreter.globals.define("atan", lambda x: math.atan(x))
        interpreter.globals.define("atan2", lambda y, x: math.atan2(y, x))
        interpreter.globals.define("sqrt", lambda x: math.sqrt(x))
        interpreter.globals.define("pow", lambda x, y: math.pow(x, y))
        interpreter.globals.define("exp", lambda x: math.exp(x))
        interpreter.globals.define("log", lambda x, base=math.e: math.log(x, base))
        interpreter.globals.define("log10", lambda x: math.log10(x))
        interpreter.globals.define("floor", lambda x: math.floor(x))
        interpreter.globals.define("ceil", lambda x: math.ceil(x))
        interpreter.globals.define("round", lambda x, n=0: round(x, n))
        interpreter.globals.define("abs", lambda x: abs(x))
        interpreter.globals.define("pi", math.pi)
        interpreter.globals.define("e", math.e)
        interpreter.globals.define("tau", math.tau)
        interpreter.globals.define("inf", math.inf)
        interpreter.globals.define("nan", math.nan)
        interpreter.globals.define("is_nan", lambda x: math.isnan(x))
        interpreter.globals.define("is_inf", lambda x: math.isinf(x))
        interpreter.globals.define("degrees", lambda x: math.degrees(x))
        interpreter.globals.define("radians", lambda x: math.radians(x))
        
        # Random functions
        interpreter.globals.define("random", lambda: random.random())
        interpreter.globals.define("randint", lambda a, b: random.randint(a, b))
        interpreter.globals.define("uniform", lambda a, b: random.uniform(a, b))
        interpreter.globals.define("choice", lambda lst: random.choice(lst))
        interpreter.globals.define("choices", lambda lst, k=1, weights=None: random.choices(lst, weights=weights, k=k))
        interpreter.globals.define("sample", lambda lst, k: random.sample(lst, k))
        interpreter.globals.define("shuffle", lambda lst: random.shuffle(lst) or lst)
        interpreter.globals.define("random_seed", lambda seed=None: random.seed(seed))
        
        # Time functions
        interpreter.globals.define("time", lambda: time.time())
        interpreter.globals.define("sleep", lambda secs: time.sleep(secs))
        interpreter.globals.define("time_ns", lambda: time.time_ns())
        interpreter.globals.define("format_time", lambda fmt, t=None: time.strftime(fmt, time.localtime(t) if t else time.localtime()))
        interpreter.globals.define("parse_time", lambda s, fmt: time.mktime(time.strptime(s, fmt)))
        
        # Date functions
        interpreter.globals.define("now", lambda: datetime.datetime.now())
        interpreter.globals.define("date", lambda y, m, d: datetime.date(y, m, d))
        interpreter.globals.define("time_of_day", lambda h, m, s=0, ms=0: datetime.time(h, m, s, ms))
        interpreter.globals.define("datetime", lambda y, m, d, h=0, min=0, s=0, ms=0: datetime.datetime(y, m, d, h, min, s, ms))
        interpreter.globals.define("date_diff", lambda d1, d2: (d1 - d2).total_seconds())
        interpreter.globals.define("date_add", lambda d, **kwargs: d + datetime.timedelta(**kwargs))
        
        # String functions
        interpreter.globals.define("len", lambda s: len(s))
        interpreter.globals.define("lower", lambda s: s.lower())
        interpreter.globals.define("upper", lambda s: s.upper())
        interpreter.globals.define("capitalize", lambda s: s.capitalize())
        interpreter.globals.define("title", lambda s: s.title())
        interpreter.globals.define("trim", lambda s: s.strip())
        interpreter.globals.define("ltrim", lambda s: s.lstrip())
        interpreter.globals.define("rtrim", lambda s: s.rstrip())
        interpreter.globals.define("split", lambda s, sep=" ": s.split(sep))
        interpreter.globals.define("join", lambda lst, sep="": sep.join(lst))
        interpreter.globals.define("format", lambda s, *args, **kwargs: s.format(*args, **kwargs))
        interpreter.globals.define("startswith", lambda s, prefix: s.startswith(prefix))
        interpreter.globals.define("endswith", lambda s, suffix: s.endswith(suffix))
        interpreter.globals.define("replace", lambda s, old, new, count=-1: s.replace(old, new, count))
        interpreter.globals.define("contains", lambda s, sub: sub in s)
        interpreter.globals.define("find", lambda s, sub, start=0, end=None: s.find(sub, start, end))
        interpreter.globals.define("rfind", lambda s, sub, start=0, end=None: s.rfind(sub, start, end))
        interpreter.globals.define("count", lambda s, sub, start=0, end=None: s.count(sub, start, end))
        interpreter.globals.define("slice", lambda s, start=0, end=None: s[start:end])
        interpreter.globals.define("char_at", lambda s, i: s[i])
        interpreter.globals.define("pad_left", lambda s, width, char=" ": s.rjust(width, char))
        interpreter.globals.define("pad_right", lambda s, width, char=" ": s.ljust(width, char))
        interpreter.globals.define("pad_center", lambda s, width, char=" ": s.center(width, char))
        
        # Regular expressions
        interpreter.globals.define("regex_match", lambda pattern, string: bool(re.match(pattern, string)))
        interpreter.globals.define("regex_search", lambda pattern, string: bool(re.search(pattern, string)))
        interpreter.globals.define("regex_find_all", lambda pattern, string: re.findall(pattern, string))
        interpreter.globals.define("regex_replace", lambda pattern, repl, string: re.sub(pattern, repl, string))
        interpreter.globals.define("regex_split", lambda pattern, string: re.split(pattern, string))
        
        # List functions
        interpreter.globals.define("append", lambda lst, item: lst.append(item) or lst)
        interpreter.globals.define("insert", lambda lst, idx, item: lst.insert(idx, item) or lst)
        interpreter.globals.define("remove", lambda lst, item: lst.remove(item) or lst)
        interpreter.globals.define("pop", lambda lst, idx=-1: lst.pop(idx))
        interpreter.globals.define("slice", lambda lst, start=0, end=None: lst[start:end])
        interpreter.globals.define("reverse", lambda lst: lst.reverse() or lst)
        interpreter.globals.define("sort", lambda lst, key=None, reverse=False: lst.sort(key=key, reverse=reverse) or lst)
        interpreter.globals.define("map", lambda fn, lst: list(map(fn, lst)))
        interpreter.globals.define("filter", lambda fn, lst: list(filter(fn, lst)))
        interpreter.globals.define("reduce", lambda fn, lst, initial=None: DemonStdLib._reduce(fn, lst, initial))
        interpreter.globals.define("all", lambda lst: all(lst))
        interpreter.globals.define("any", lambda lst: any(lst))
        interpreter.globals.define("sum", lambda lst: sum(lst))
        interpreter.globals.define("min", lambda *args: min(*args))
        interpreter.globals.define("max", lambda *args: max(*args))
        interpreter.globals.define("zip", lambda *lsts: list(zip(*lsts)))
        interpreter.globals.define("enumerate", lambda lst, start=0: list(enumerate(lst, start)))
        interpreter.globals.define("flatten", lambda lst: [item for sublist in lst for item in sublist])
        interpreter.globals.define("chunk", lambda lst, size: [lst[i:i+size] for i in range(0, len(lst), size)])
        interpreter.globals.define("unique", lambda lst: list(dict.fromkeys(lst)))
        interpreter.globals.define("count_items", lambda lst: {item: lst.count(item) for item in set(lst)})
        
        # Dictionary functions
        interpreter.globals.define("keys", lambda d: list(d.keys()))
        interpreter.globals.define("values", lambda d: list(d.values()))
        interpreter.globals.define("items", lambda d: list(d.items()))
        interpreter.globals.define("get", lambda d, key, default=None: d.get(key, default))
        interpreter.globals.define("has_key", lambda d, key: key in d)
        interpreter.globals.define("update", lambda d, other: d.update(other) or d)
        interpreter.globals.define("merge", lambda d1, d2: {**d1, **d2})
        interpreter.globals.define("pick", lambda d, keys: {k: d[k] for k in keys if k in d})
        interpreter.globals.define("omit", lambda d, keys: {k: v for k, v in d.items() if k not in keys})
        
        # Type conversion
        interpreter.globals.define("int", lambda x: int(x))
        interpreter.globals.define("float", lambda x: float(x))
        interpreter.globals.define("str", lambda x: str(x))
        interpreter.globals.define("bool", lambda x: bool(x))
        interpreter.globals.define("list", lambda x=None: list(x) if x is not None else [])
        interpreter.globals.define("dict", lambda x=None: dict(x) if x is not None else {})
        interpreter.globals.define("set", lambda x=None: set(x) if x is not None else set())
        interpreter.globals.define("tuple", lambda x=None: tuple(x) if x is not None else ())
        interpreter.globals.define("type", lambda x: type(x).__name__)
        interpreter.globals.define("is_type", lambda x, t: isinstance(x, t))
        
        # JSON functions
        interpreter.globals.define("json_parse", lambda s: json.loads(s))
        interpreter.globals.define("json_stringify", lambda obj, indent=None: json.dumps(obj, indent=indent))
        interpreter.globals.define("json_read", lambda path: DemonStdLib._json_read(path))
        interpreter.globals.define("json_write", lambda obj, path, indent=None: DemonStdLib._json_write(obj, path, indent))
        
        # File I/O
        interpreter.globals.define("read_file", lambda path: DemonStdLib._read_file(path))
        interpreter.globals.define("write_file", lambda path, content: DemonStdLib._write_file(path, content))
        interpreter.globals.define("append_file", lambda path, content: DemonStdLib._append_file(path, content))
        interpreter.globals.define("file_exists", lambda path: os.path.exists(path))
        interpreter.globals.define("list_dir", lambda path=".": os.listdir(path))
        interpreter.globals.define("make_dir", lambda path, exist_ok=True: os.makedirs(path, exist_ok=exist_ok) or path)
        interpreter.globals.define("remove_file", lambda path: os.remove(path))
        interpreter.globals.define("remove_dir", lambda path: os.rmdir(path))
        interpreter.globals.define("copy_file", lambda src, dst: DemonStdLib._copy_file(src, dst))
        interpreter.globals.define("move_file", lambda src, dst: DemonStdLib._move_file(src, dst))
        interpreter.globals.define("file_size", lambda path: os.path.getsize(path))
        interpreter.globals.define("file_time", lambda path: os.path.getmtime(path))
        
        # Cryptography and encoding
        interpreter.globals.define("md5", lambda s: hashlib.md5(s.encode()).hexdigest())
        interpreter.globals.define("sha1", lambda s: hashlib.sha1(s.encode()).hexdigest())
        interpreter.globals.define("sha256", lambda s: hashlib.sha256(s.encode()).hexdigest())
        interpreter.globals.define("base64_encode", lambda s: base64.b64encode(s.encode()).decode())
        interpreter.globals.define("base64_decode", lambda s: base64.b64decode(s.encode()).decode())
        interpreter.globals.define("url_encode", lambda s: urllib.parse.quote(s))
        interpreter.globals.define("url_decode", lambda s: urllib.parse.unquote(s))
        
        # Network functions
        interpreter.globals.define("http_get", lambda url, headers=None: DemonStdLib._http_get(url, headers))
        interpreter.globals.define("http_post", lambda url, data=None, headers=None: DemonStdLib._http_post(url, data, headers))
        interpreter.globals.define("parse_url", lambda url: dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query)))
        interpreter.globals.define("build_url", lambda base, params: f"{base}?{urllib.parse.urlencode(params)}")
        
        # System functions
        interpreter.globals.define("args", sys.argv[1:])
        interpreter.globals.define("env", lambda name, default=None: os.environ.get(name, default))
        interpreter.globals.define("exit", lambda code=0: sys.exit(code))
        interpreter.globals.define("platform", sys.platform)
        interpreter.globals.define("cwd", lambda: os.getcwd())
        interpreter.globals.define("chdir", lambda path: os.chdir(path))
        interpreter.globals.define("exec", lambda cmd: os.system(cmd))
        
        # Data structures
        interpreter.globals.define("Stack", lambda: DemonStdLib.Stack())
        interpreter.globals.define("Queue", lambda: DemonStdLib.Queue())
        interpreter.globals.define("PriorityQueue", lambda: DemonStdLib.PriorityQueue())
        interpreter.globals.define("Set", lambda items=None: DemonStdLib.Set(items))
        interpreter.globals.define("Graph", lambda: DemonStdLib.Graph())
        interpreter.globals.define("Tree", lambda: DemonStdLib.Tree())
        interpreter.globals.define("HashMap", lambda: {})
        
        # Functional programming
        interpreter.globals.define("compose", lambda *fns: DemonStdLib._compose(*fns))
        interpreter.globals.define("pipe", lambda x, *fns: DemonStdLib._pipe(x, *fns))
        interpreter.globals.define("curry", lambda fn, *args: lambda *more_args: fn(*(args + more_args)))
        interpreter.globals.define("partial", lambda fn, *args, **kwargs: lambda *more_args, **more_kwargs: fn(*args, *more_args, **{**kwargs, **more_kwargs}))
        interpreter.globals.define("memoize", lambda fn: DemonStdLib._memoize(fn))
    
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
    def _compose(*fns):
        """Compose functions from right to left."""
        def composed(*args, **kwargs):
            result = fns[-1](*args, **kwargs)
            for fn in reversed(fns[:-1]):
                result = fn(result)
            return result
        return composed
    
    @staticmethod
    def _pipe(x, *fns):
        """Pipe a value through a series of functions."""
        result = x
        for fn in fns:
            result = fn(result)
        return result
    
    @staticmethod
    def _memoize(fn):
        """Memoize a function."""
        cache = {}
        def memoized(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            if key not in cache:
                cache[key] = fn(*args, **kwargs)
            return cache[key]
        return memoized
    
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
    
    @staticmethod
    def _json_read(path):
        """Read JSON from a file."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error reading JSON file: {e}")
    
    @staticmethod
    def _json_write(obj, path, indent=None):
        """Write JSON to a file."""
        try:
            with open(path, 'w') as f:
                json.dump(obj, f, indent=indent)
            return True
        except Exception as e:
            raise RuntimeError(f"Error writing JSON file: {e}")
    
    @staticmethod
    def _copy_file(src, dst):
        """Copy a file."""
        try:
            import shutil
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            raise RuntimeError(f"Error copying file: {e}")
    
    @staticmethod
    def _move_file(src, dst):
        """Move a file."""
        try:
            import shutil
            shutil.move(src, dst)
            return True
        except Exception as e:
            raise RuntimeError(f"Error moving file: {e}")
    
    @staticmethod
    def _http_get(url, headers=None):
        """Make an HTTP GET request."""
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req) as response:
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": response.read().decode()
                }
        except Exception as e:
            raise RuntimeError(f"HTTP GET error: {e}")
    
    @staticmethod
    def _http_post(url, data=None, headers=None):
        """Make an HTTP POST request."""
        try:
            headers = headers or {}
            if isinstance(data, dict):
                data = urllib.parse.urlencode(data).encode()
                headers["Content-Type"] = headers.get("Content-Type", "application/x-www-form-urlencoded")
            elif isinstance(data, str):
                data = data.encode()
            
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "body": response.read().decode()
                }
        except Exception as e:
            raise RuntimeError(f"HTTP POST error: {e}")
    
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
        
        def to_list(self):
            return self.items.copy()
        
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
        
        def to_list(self):
            return self.items.copy()
        
        def __str__(self):
            return f"Queue({self.items})"
    
    class PriorityQueue:
        """Priority queue data structure."""
        
        def __init__(self):
            self.items = []
        
        def enqueue(self, item, priority):
            import heapq
            heapq.heappush(self.items, (priority, item))
            return self
        
        def dequeue(self):
            if not self.items:
                raise RuntimeError("Cannot dequeue from empty priority queue")
            import heapq
            return heapq.heappop(self.items)[1]
        
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
        
        def to_list(self):
            return [(p, i) for p, i in self.items]
        
        def __str__(self):
            return f"PriorityQueue({self.to_list()})"
    
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
            
            import heapq
            distances = {vertex: float('infinity') for vertex in self.vertices}
            distances[start_vertex] = 0
            priority_queue = [(0, start_vertex)]
            
            while priority_queue:
                current_distance, current_vertex = heapq.heappop(priority_queue)
                
                if current_distance > distances[current_vertex]:
                    continue
                
                for neighbor, weight in self.vertices[current_vertex]:
                    distance = current_distance + weight
                    
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(priority_queue, (distance, neighbor))
            
            return distances
        
        def __str__(self):
            result = "Graph:\n"
            for vertex, edges in self.vertices.items():
                result += f"{vertex} -> {edges}\n"
            return result
    
    class TreeNode:
        """Tree node for the Tree data structure."""
        
        def __init__(self, value):
            self.value = value
            self.children = []
        
        def add_child(self, value):
            child = DemonStdLib.TreeNode(value)
            self.children.append(child)
            return child
        
        def __str__(self):
            return f"TreeNode({self.value})"
    
    class Tree:
        """Tree data structure."""
        
        def __init__(self):
            self.root = None
        
        def set_root(self, value):
            self.root = DemonStdLib.TreeNode(value)
            return self.root
        
        def dfs(self):
            if not self.root:
                return []
            
            result = []
            
            def dfs_helper(node):
                result.append(node.value)
                for child in node.children:
                    dfs_helper(child)
            
            dfs_helper(self.root)
            return result
        
        def bfs(self):
            if not self.root:
                return []
            
            result = []
            queue = [self.root]
            
            while queue:
                node = queue.pop(0)
                result.append(node.value)
                queue.extend(node.children)
            
            return result
        
        def __str__(self):
            if not self.root:
                return "Tree(empty)"
            return f"Tree(root={self.root.value})"