"""
Built-in data structures for the Demon programming language.
"""

from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, Generic
from collections import defaultdict, deque, Counter, OrderedDict, namedtuple
import heapq

T = TypeVar('T')

class PriorityQueue(Generic[T]):
    """Priority queue implementation using a binary heap."""
    
    def __init__(self):
        self._heap = []
        self._index = 0
    
    def push(self, item: T, priority: float):
        """Push an item onto the queue with given priority."""
        heapq.heappush(self._heap, (priority, self._index, item))
        self._index += 1
    
    def pop(self) -> T:
        """Pop the item with highest priority."""
        if not self._heap:
            raise IndexError("Pop from empty priority queue")
        return heapq.heappop(self._heap)[2]
    
    def peek(self) -> T:
        """Peek at the item with highest priority without removing it."""
        if not self._heap:
            raise IndexError("Peek from empty priority queue")
        return self._heap[0][2]
    
    def is_empty(self) -> bool:
        """Check if the priority queue is empty."""
        return len(self._heap) == 0
    
    def size(self) -> int:
        """Get the number of items in the priority queue."""
        return len(self._heap)

class Trie:
    """Trie data structure for efficient string operations."""
    
    def __init__(self):
        self.root = {}
        self.end_symbol = "*"
    
    def insert(self, word: str):
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            if char not in node:
                node[char] = {}
            node = node[char]
        node[self.end_symbol] = True
    
    def search(self, word: str) -> bool:
        """Search for a word in the trie."""
        node = self.root
        for char in word:
            if char not in node:
                return False
            node = node[char]
        return self.end_symbol in node
    
    def starts_with(self, prefix: str) -> bool:
        """Check if any word in the trie starts with the given prefix."""
        node = self.root
        for char in prefix:
            if char not in node:
                return False
            node = node[char]
        return True
    
    def get_words_with_prefix(self, prefix: str) -> List[str]:
        """Get all words that start with the given prefix."""
        result = []
        node = self.root
        
        # Navigate to the prefix node
        for char in prefix:
            if char not in node:
                return result
            node = node[char]
        
        # Collect all words from this node
        self._collect_words(node, prefix, result)
        return result
    
    def _collect_words(self, node: Dict, prefix: str, result: List[str]):
        """Helper method to collect all words from a node."""
        if self.end_symbol in node:
            result.append(prefix)
        
        for char, child in node.items():
            if char != self.end_symbol:
                self._collect_words(child, prefix + char, result)

class DisjointSet:
    """Disjoint Set (Union-Find) data structure."""
    
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """Find the representative of the set containing x."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]
    
    def union(self, x: int, y: int):
        """Union the sets containing x and y."""
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1
    
    def connected(self, x: int, y: int) -> bool:
        """Check if x and y are in the same set."""
        return self.find(x) == self.find(y)

class BinarySearchTree:
    """Binary Search Tree implementation."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
    
    def __init__(self):
        self.root = None
    
    def insert(self, value):
        """Insert a value into the BST."""
        if self.root is None:
            self.root = self.Node(value)
            return
        
        self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = self.Node(value)
            else:
                self._insert_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = self.Node(value)
            else:
                self._insert_recursive(node.right, value)
    
    def search(self, value):
        """Search for a value in the BST."""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node, value):
        if node is None:
            return False
        
        if node.value == value:
            return True
        
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
    
    def in_order_traversal(self):
        """Perform an in-order traversal of the BST."""
        result = []
        self._in_order_recursive(self.root, result)
        return result
    
    def _in_order_recursive(self, node, result):
        if node:
            self._in_order_recursive(node.left, result)
            result.append(node.value)
            self._in_order_recursive(node.right, result)

class HashTable:
    """Hash table implementation."""
    
    def __init__(self, size=1024):
        self.size = size
        self.buckets = [[] for _ in range(size)]
    
    def _hash(self, key):
        """Hash function for keys."""
        if isinstance(key, str):
            return sum(ord(c) for c in key) % self.size
        return hash(key) % self.size
    
    def set(self, key, value):
        """Set a key-value pair in the hash table."""
        index = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key:
                self.buckets[index][i] = (key, value)
                return
        self.buckets[index].append((key, value))
    
    def get(self, key, default=None):
        """Get a value by key from the hash table."""
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return default
    
    def delete(self, key):
        """Delete a key-value pair from the hash table."""
        index = self._hash(key)
        for i, (k, v) in enumerate(self.buckets[index]):
            if k == key:
                del self.buckets[index][i]
                return True
        return False
    
    def contains(self, key):
        """Check if the hash table contains a key."""
        index = self._hash(key)
        return any(k == key for k, _ in self.buckets[index])

class AVLTree:
    """Self-balancing AVL Tree implementation."""
    
    class Node:
        def __init__(self, value):
            self.value = value
            self.left = None
            self.right = None
            self.height = 1
    
    def __init__(self):
        self.root = None
    
    def height(self, node):
        """Get the height of a node."""
        if node is None:
            return 0
        return node.height
    
    def balance_factor(self, node):
        """Get the balance factor of a node."""
        if node is None:
            return 0
        return self.height(node.left) - self.height(node.right)
    
    def update_height(self, node):
        """Update the height of a node."""
        if node is None:
            return
        node.height = 1 + max(self.height(node.left), self.height(node.right))
    
    def right_rotate(self, y):
        """Right rotation."""
        x = y.left
        T2 = x.right
        
        # Perform rotation
        x.right = y
        y.left = T2
        
        # Update heights
        self.update_height(y)
        self.update_height(x)
        
        return x
    
    def left_rotate(self, x):
        """Left rotation."""
        y = x.right
        T2 = y.left
        
        # Perform rotation
        y.left = x
        x.right = T2
        
        # Update heights
        self.update_height(x)
        self.update_height(y)
        
        return y
    
    def insert(self, value):
        """Insert a value into the AVL tree."""
        self.root = self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node, value):
        # Standard BST insert
        if node is None:
            return self.Node(value)
        
        if value < node.value:
            node.left = self._insert_recursive(node.left, value)
        else:
            node.right = self._insert_recursive(node.right, value)
        
        # Update height
        self.update_height(node)
        
        # Get balance factor
        balance = self.balance_factor(node)
        
        # Left Left Case
        if balance > 1 and value < node.left.value:
            return self.right_rotate(node)
        
        # Right Right Case
        if balance < -1 and value > node.right.value:
            return self.left_rotate(node)
        
        # Left Right Case
        if balance > 1 and value > node.left.value:
            node.left = self.left_rotate(node.left)
            return self.right_rotate(node)
        
        # Right Left Case
        if balance < -1 and value < node.right.value:
            node.right = self.right_rotate(node.right)
            return self.left_rotate(node)
        
        return node
    
    def in_order_traversal(self):
        """Perform an in-order traversal of the AVL tree."""
        result = []
        self._in_order_recursive(self.root, result)
        return result
    
    def _in_order_recursive(self, node, result):
        if node:
            self._in_order_recursive(node.left, result)
            result.append(node.value)
            self._in_order_recursive(node.right, result)

def register_data_structures(interpreter):
    """Register all data structures with the interpreter."""
    NativeFunction = interpreter.NativeFunction
    
    # Priority Queue
    interpreter.globals.define("PriorityQueue", NativeFunction("PriorityQueue", 0, lambda: PriorityQueue()))
    
    # Trie
    interpreter.globals.define("Trie", NativeFunction("Trie", 0, lambda: Trie()))
    
    # Disjoint Set
    interpreter.globals.define("DisjointSet", NativeFunction("DisjointSet", 1, lambda n: DisjointSet(n)))
    
    # Binary Search Tree
    interpreter.globals.define("BinarySearchTree", NativeFunction("BinarySearchTree", 0, lambda: BinarySearchTree()))
    
    # Hash Table
    interpreter.globals.define("HashTable", NativeFunction("HashTable", 0, lambda: HashTable()))
    
    # AVL Tree
    interpreter.globals.define("AVLTree", NativeFunction("AVLTree", 0, lambda: AVLTree()))
    
    # OrderedDict
    interpreter.globals.define("OrderedDict", NativeFunction("OrderedDict", 0, lambda: OrderedDict()))
    
    # Counter
    interpreter.globals.define("Counter", NativeFunction("Counter", 1, lambda iterable=None: Counter(iterable)))
    
    # Named Tuple
    def create_named_tuple(name, fields):
        return namedtuple(name, fields)
    
    interpreter.globals.define("NamedTuple", NativeFunction("NamedTuple", 2, create_named_tuple))