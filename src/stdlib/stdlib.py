"""
Standard library for the Demon programming language.
"""

import math
import random
import time
import os
import sys
from typing import List, Dict, Any, Optional, Union, Callable
from collections import defaultdict, deque, Counter, OrderedDict
import heapq

class DemonStdLib:
    """Standard library for the Demon programming language."""
    
    @staticmethod
    def register_all(interpreter):
        """Register all standard library functions with the interpreter."""
        # Create NativeFunction class reference
        NativeFunction = interpreter.NativeFunction
        
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
        interpreter.globals.define("shuffle", NativeFunction("shuffle", 1, lambda x: random.shuffle(x) or x))
        
        # String functions
        interpreter.globals.define("upper", NativeFunction("upper", 1, lambda s: s.upper()))
        interpreter.globals.define("lower", NativeFunction("lower", 1, lambda s: s.lower()))
        interpreter.globals.define("trim", NativeFunction("trim", 1, lambda s: s.strip()))
        interpreter.globals.define("split", NativeFunction("split", 2, lambda s, sep=" ": s.split(sep)))
        interpreter.globals.define("contains", NativeFunction("contains", 2, lambda s, sub: sub in s))
        interpreter.globals.define("replace", NativeFunction("replace", 3, lambda s, old, new: s.replace(old, new)))
        interpreter.globals.define("join", NativeFunction("join", 2, lambda sep, lst: sep.join(lst)))
        interpreter.globals.define("startsWith", NativeFunction("startsWith", 2, lambda s, prefix: s.startswith(prefix)))
        interpreter.globals.define("endsWith", NativeFunction("endsWith", 2, lambda s, suffix: s.endswith(suffix)))
        
        # List functions
        interpreter.globals.define("append", NativeFunction("append", 2, lambda lst, item: lst.append(item) or lst))
        interpreter.globals.define("insert", NativeFunction("insert", 3, lambda lst, idx, item: lst.insert(idx, item) or lst))
        interpreter.globals.define("slice", NativeFunction("slice", 3, lambda lst, start, end: lst[start:end]))
        interpreter.globals.define("reverse", NativeFunction("reverse", 1, lambda lst: lst[::-1]))
        interpreter.globals.define("sort", NativeFunction("sort", 1, lambda lst: sorted(lst)))
        interpreter.globals.define("indexOf", NativeFunction("indexOf", 2, lambda lst, item: lst.index(item) if item in lst else -1))
        interpreter.globals.define("count", NativeFunction("count", 2, lambda lst, item: lst.count(item)))
        interpreter.globals.define("flatten", NativeFunction("flatten", 1, lambda lst: [item for sublist in lst for item in sublist]))
        
        # Higher-order functions
        interpreter.globals.define("map", NativeFunction("map", 2, lambda fn, lst: [fn.call(interpreter, [x]) for x in lst]))
        interpreter.globals.define("filter", NativeFunction("filter", 2, lambda fn, lst: [x for x in lst if fn.call(interpreter, [x])]))
        interpreter.globals.define("reduce", NativeFunction("reduce", 3, lambda fn, lst, init: DemonStdLib._reduce(interpreter, fn, lst, init)))
        interpreter.globals.define("sum", NativeFunction("sum", 1, sum))
        interpreter.globals.define("min", NativeFunction("min", 1, min))
        interpreter.globals.define("max", NativeFunction("max", 1, max))
        interpreter.globals.define("all", NativeFunction("all", 1, all))
        interpreter.globals.define("any", NativeFunction("any", 1, any))
        interpreter.globals.define("zip", NativeFunction("zip", -1, lambda *args: list(zip(*args))))
        
        # Time functions
        interpreter.globals.define("sleep", NativeFunction("sleep", 1, time.sleep))
        interpreter.globals.define("time", NativeFunction("time", 0, time.time))
        interpreter.globals.define("clock", NativeFunction("clock", 0, time.time))
        
        # Type conversion functions
        interpreter.globals.define("str", NativeFunction("str", 1, str))
        interpreter.globals.define("int", NativeFunction("int", 1, lambda x: int(float(x)) if isinstance(x, str) else int(x)))
        interpreter.globals.define("float", NativeFunction("float", 1, float))
        interpreter.globals.define("bool", NativeFunction("bool", 1, bool))
        interpreter.globals.define("list", NativeFunction("list", 1, list))
        
        # I/O functions
        interpreter.globals.define("print", NativeFunction("print", -1, print))
        interpreter.globals.define("input", NativeFunction("input", 1, lambda prompt="": input(prompt)))
        interpreter.globals.define("len", NativeFunction("len", 1, len))
        
        # Register data structures and algorithms
        try:
            # Priority Queue functions
            _pq_heaps = {}
            _pq_indices = {}
            _pq_counter = [0]
            
            def pq_create():
                pq_id = str(_pq_counter[0])
                _pq_counter[0] += 1
                _pq_heaps[pq_id] = []
                _pq_indices[pq_id] = 0
                return pq_id
            
            def pq_push(pq_id, item, priority):
                heapq.heappush(_pq_heaps[pq_id], (priority, _pq_indices[pq_id], item))
                _pq_indices[pq_id] += 1
                return pq_id
            
            def pq_pop(pq_id):
                if not _pq_heaps[pq_id]:
                    raise IndexError("Pop from empty priority queue")
                return heapq.heappop(_pq_heaps[pq_id])[2]
            
            def pq_peek(pq_id):
                if not _pq_heaps[pq_id]:
                    raise IndexError("Peek from empty priority queue")
                return _pq_heaps[pq_id][0][2]
            
            def pq_is_empty(pq_id):
                return len(_pq_heaps[pq_id]) == 0
            
            def pq_size(pq_id):
                return len(_pq_heaps[pq_id])
            
            interpreter.globals.define("pq_create", NativeFunction("pq_create", 0, pq_create))
            interpreter.globals.define("pq_push", NativeFunction("pq_push", 3, pq_push))
            interpreter.globals.define("pq_pop", NativeFunction("pq_pop", 1, pq_pop))
            interpreter.globals.define("pq_peek", NativeFunction("pq_peek", 1, pq_peek))
            interpreter.globals.define("pq_is_empty", NativeFunction("pq_is_empty", 1, pq_is_empty))
            interpreter.globals.define("pq_size", NativeFunction("pq_size", 1, pq_size))
            
            # Hash Table functions
            _ht_tables = {}
            _ht_counter = [0]
            
            def ht_create(size=1024):
                ht_id = str(_ht_counter[0])
                _ht_counter[0] += 1
                _ht_tables[ht_id] = [[] for _ in range(size)]
                return ht_id
            
            def ht_hash(ht_id, key, size=1024):
                if isinstance(key, str):
                    return sum(ord(c) for c in key) % size
                return hash(key) % size
            
            def ht_set(ht_id, key, value):
                table = _ht_tables[ht_id]
                size = len(table)
                index = ht_hash(ht_id, key, size)
                
                for i, (k, v) in enumerate(table[index]):
                    if k == key:
                        table[index][i] = (key, value)
                        return ht_id
                table[index].append((key, value))
                return ht_id
            
            def ht_get(ht_id, key):
                table = _ht_tables[ht_id]
                size = len(table)
                index = ht_hash(ht_id, key, size)
                
                for k, v in table[index]:
                    if k == key:
                        return v
                return None
                
            def ht_get_default(ht_id, key, default):
                table = _ht_tables[ht_id]
                size = len(table)
                index = ht_hash(ht_id, key, size)
                
                for k, v in table[index]:
                    if k == key:
                        return v
                return default
            
            def ht_contains(ht_id, key):
                table = _ht_tables[ht_id]
                size = len(table)
                index = ht_hash(ht_id, key, size)
                
                return any(k == key for k, _ in table[index])
            
            interpreter.globals.define("ht_create", NativeFunction("ht_create", 0, ht_create))
            interpreter.globals.define("ht_set", NativeFunction("ht_set", 3, ht_set))
            interpreter.globals.define("ht_get", NativeFunction("ht_get", 2, ht_get))
            interpreter.globals.define("ht_get_default", NativeFunction("ht_get_default", 3, ht_get_default))
            interpreter.globals.define("ht_contains", NativeFunction("ht_contains", 2, ht_contains))
            
            # Binary Search Tree functions
            _bst_trees = {}
            _bst_counter = [0]
            
            def bst_create():
                bst_id = str(_bst_counter[0])
                _bst_counter[0] += 1
                _bst_trees[bst_id] = {}
                _bst_trees[bst_id]["root"] = None
                return bst_id
            
            def bst_insert(bst_id, value):
                tree = _bst_trees[bst_id]
                
                # Create a new node as a dictionary
                def create_node(val):
                    return {"value": val, "left": None, "right": None}
                
                # Insert recursively
                def _insert_recursive(node, val):
                    if node is None:
                        return create_node(val)
                    
                    if val < node["value"]:
                        node["left"] = _insert_recursive(node["left"], val)
                    else:
                        node["right"] = _insert_recursive(node["right"], val)
                    
                    return node
                
                tree["root"] = _insert_recursive(tree["root"], value)
                return bst_id
            
            def bst_search(bst_id, value):
                tree = _bst_trees[bst_id]
                
                def _search_recursive(node, val):
                    if node is None:
                        return False
                    
                    if node["value"] == val:
                        return True
                    
                    if val < node["value"]:
                        return _search_recursive(node["left"], val)
                    else:
                        return _search_recursive(node["right"], val)
                
                return _search_recursive(tree["root"], value)
            
            def bst_in_order(bst_id):
                tree = _bst_trees[bst_id]
                result = []
                
                def _in_order_recursive(node):
                    if node is not None:
                        _in_order_recursive(node["left"])
                        result.append(node["value"])
                        _in_order_recursive(node["right"])
                
                _in_order_recursive(tree["root"])
                return result
            
            interpreter.globals.define("bst_create", NativeFunction("bst_create", 0, bst_create))
            interpreter.globals.define("bst_insert", NativeFunction("bst_insert", 2, bst_insert))
            interpreter.globals.define("bst_search", NativeFunction("bst_search", 2, bst_search))
            interpreter.globals.define("bst_in_order", NativeFunction("bst_in_order", 1, bst_in_order))
            
            # Trie functions
            _tries = {}
            _trie_counter = [0]
            _END_SYMBOL = "*"
            
            def trie_create():
                trie_id = str(_trie_counter[0])
                _trie_counter[0] += 1
                _tries[trie_id] = {}
                return trie_id
            
            def trie_insert(trie_id, word):
                node = _tries[trie_id]
                for char in word:
                    if char not in node:
                        node[char] = {}
                    node = node[char]
                node[_END_SYMBOL] = True
                return trie_id
            
            def trie_search(trie_id, word):
                node = _tries[trie_id]
                for char in word:
                    if char not in node:
                        return False
                    node = node[char]
                return _END_SYMBOL in node
            
            def trie_starts_with(trie_id, prefix):
                node = _tries[trie_id]
                for char in prefix:
                    if char not in node:
                        return False
                    node = node[char]
                return True
            
            interpreter.globals.define("trie_create", NativeFunction("trie_create", 0, trie_create))
            interpreter.globals.define("trie_insert", NativeFunction("trie_insert", 2, trie_insert))
            interpreter.globals.define("trie_search", NativeFunction("trie_search", 2, trie_search))
            interpreter.globals.define("trie_starts_with", NativeFunction("trie_starts_with", 2, trie_starts_with))
            
            # Sorting algorithms
            def quick_sort(arr):
                if len(arr) <= 1:
                    return arr
                pivot = arr[len(arr) // 2]
                left = [x for x in arr if x < pivot]
                middle = [x for x in arr if x == pivot]
                right = [x for x in arr if x > pivot]
                return quick_sort(left) + middle + quick_sort(right)
            
            def merge_sort(arr):
                if len(arr) <= 1:
                    return arr
                
                mid = len(arr) // 2
                left = merge_sort(arr[:mid])
                right = merge_sort(arr[mid:])
                
                result = []
                i = j = 0
                
                while i < len(left) and j < len(right):
                    if left[i] <= right[j]:
                        result.append(left[i])
                        i += 1
                    else:
                        result.append(right[j])
                        j += 1
                
                result.extend(left[i:])
                result.extend(right[j:])
                return result
            
            # Graph algorithms
            _graphs = {}
            _graph_counter = [0]
            
            def graph_create():
                graph_id = str(_graph_counter[0])
                _graph_counter[0] += 1
                _graphs[graph_id] = {"nodes": [], "edges": []}
                return graph_id
            
            def graph_add_node(graph_id, node):
                if node not in _graphs[graph_id]["nodes"]:
                    _graphs[graph_id]["nodes"].append(node)
                return graph_id
            
            def graph_add_edge(graph_id, from_node, to_node, weight=1):
                if from_node not in _graphs[graph_id]["nodes"]:
                    _graphs[graph_id]["nodes"].append(from_node)
                if to_node not in _graphs[graph_id]["nodes"]:
                    _graphs[graph_id]["nodes"].append(to_node)
                
                _graphs[graph_id]["edges"].append((from_node, to_node, weight))
                return graph_id
            
            def graph_get_nodes(graph_id):
                return _graphs[graph_id]["nodes"]
            
            def graph_get_edges(graph_id):
                return _graphs[graph_id]["edges"]
            
            def graph_shortest_path(graph_id, start_node):
                graph = _graphs[graph_id]
                nodes = graph["nodes"]
                edges = graph["edges"]
                
                # Create adjacency list
                adj_list = {}
                for node in nodes:
                    adj_list[node] = {}
                
                for from_node, to_node, weight in edges:
                    adj_list[from_node][to_node] = weight
                
                # Initialize distances
                distances = {}
                for node in nodes:
                    distances[node] = float('inf')
                distances[start_node] = 0
                
                # Initialize visited
                visited = {}
                for node in nodes:
                    visited[node] = False
                
                # Dijkstra's algorithm
                for _ in range(len(nodes)):
                    # Find minimum distance node
                    min_dist = float('inf')
                    min_node = None
                    
                    for node in nodes:
                        if not visited[node] and distances[node] < min_dist:
                            min_dist = distances[node]
                            min_node = node
                    
                    if min_node is None:
                        break
                    
                    # Mark as visited
                    visited[min_node] = True
                    
                    # Update distances
                    for neighbor, weight in adj_list[min_node].items():
                        if not visited[neighbor]:
                            new_dist = distances[min_node] + weight
                            if new_dist < distances[neighbor]:
                                distances[neighbor] = new_dist
                
                return distances
            
            def graph_dfs(graph_id, start_node):
                graph = _graphs[graph_id]
                nodes = graph["nodes"]
                edges = graph["edges"]
                
                # Create adjacency list
                adj_list = {}
                for node in nodes:
                    adj_list[node] = []
                
                for from_node, to_node, _ in edges:
                    adj_list[from_node].append(to_node)
                
                # DFS
                visited = {}
                for node in nodes:
                    visited[node] = False
                
                result = []
                
                def dfs_recursive(node):
                    if visited[node]:
                        return
                    
                    visited[node] = True
                    result.append(node)
                    
                    for neighbor in adj_list[node]:
                        dfs_recursive(neighbor)
                
                dfs_recursive(start_node)
                return result
            
            interpreter.globals.define("quick_sort", NativeFunction("quick_sort", 1, quick_sort))
            interpreter.globals.define("merge_sort", NativeFunction("merge_sort", 1, merge_sort))
            
            # Register graph functions
            interpreter.globals.define("graph_create", NativeFunction("graph_create", 0, graph_create))
            interpreter.globals.define("graph_add_node", NativeFunction("graph_add_node", 2, graph_add_node))
            interpreter.globals.define("graph_add_edge", NativeFunction("graph_add_edge", 4, graph_add_edge))
            interpreter.globals.define("graph_get_nodes", NativeFunction("graph_get_nodes", 1, graph_get_nodes))
            interpreter.globals.define("graph_get_edges", NativeFunction("graph_get_edges", 1, graph_get_edges))
            interpreter.globals.define("graph_shortest_path", NativeFunction("graph_shortest_path", 2, graph_shortest_path))
            interpreter.globals.define("graph_dfs", NativeFunction("graph_dfs", 2, graph_dfs))
            
            # Search algorithms
            def binary_search(arr, target):
                low = 0
                high = len(arr) - 1
                
                while low <= high:
                    mid = (low + high) // 2
                    if arr[mid] < target:
                        low = mid + 1
                    elif arr[mid] > target:
                        high = mid - 1
                    else:
                        return mid
                
                return -1
            
            interpreter.globals.define("binary_search", NativeFunction("binary_search", 2, binary_search))
            
        except Exception as e:
            print(f"Error registering data structures: {e}")
    
    @staticmethod
    def _reduce(interpreter, fn, lst, init):
        """Implement reduce function."""
        result = init
        for item in lst:
            result = fn.call(interpreter, [result, item])
        return result