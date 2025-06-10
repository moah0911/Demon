"""
Built-in algorithms for the Demon programming language.
"""

from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, Generic
import heapq
import random
import math

T = TypeVar('T')

# Sorting Algorithms
def quick_sort(arr: List[T]) -> List[T]:
    """Quick sort implementation."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

def merge_sort(arr: List[T]) -> List[T]:
    """Merge sort implementation."""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted arrays."""
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

def heap_sort(arr: List[T]) -> List[T]:
    """Heap sort implementation."""
    result = []
    heap = arr.copy()
    heapq.heapify(heap)
    
    while heap:
        result.append(heapq.heappop(heap))
    
    return result

def insertion_sort(arr: List[T]) -> List[T]:
    """Insertion sort implementation."""
    result = arr.copy()
    
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    
    return result

# Search Algorithms
def binary_search(arr: List[T], target: T) -> int:
    """Binary search implementation."""
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

def linear_search(arr: List[T], target: T) -> int:
    """Linear search implementation."""
    for i, item in enumerate(arr):
        if item == target:
            return i
    return -1

# Graph Algorithms
def dijkstra(graph: Dict[Any, Dict[Any, float]], start: Any) -> Dict[Any, float]:
    """Dijkstra's algorithm for shortest paths."""
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    unvisited = list(graph.keys())
    
    while unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        
        if distances[current] == float('infinity'):
            break
        
        unvisited.remove(current)
        
        for neighbor, weight in graph[current].items():
            distance = distances[current] + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
    
    return distances

def kruskal(graph: Dict[Any, Dict[Any, float]], nodes: List[Any]) -> List[tuple]:
    """Kruskal's algorithm for minimum spanning tree."""
    # Create edges list
    edges = []
    for u in graph:
        for v, weight in graph[u].items():
            edges.append((weight, u, v))
    
    # Sort edges by weight
    edges.sort()
    
    # Create disjoint set
    parent = {node: node for node in nodes}
    rank = {node: 0 for node in nodes}
    
    def find(node):
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]
    
    def union(u, v):
        root_u = find(u)
        root_v = find(v)
        
        if root_u == root_v:
            return
        
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_v] = root_u
            rank[root_u] += 1
    
    # Build MST
    mst = []
    for weight, u, v in edges:
        if find(u) != find(v):
            union(u, v)
            mst.append((u, v, weight))
    
    return mst

# String Algorithms
def levenshtein_distance(s1: str, s2: str) -> int:
    """Levenshtein distance (edit distance) between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def kmp_search(text: str, pattern: str) -> List[int]:
    """Knuth-Morris-Pratt string searching algorithm."""
    if not pattern:
        return [0]
    
    # Compute LPS array
    lps = [0] * len(pattern)
    length = 0
    i = 1
    
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    
    # Search pattern
    result = []
    i = j = 0
    
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1
            j += 1
        
        if j == len(pattern):
            result.append(i - j)
            j = lps[j - 1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    
    return result

# Numerical Algorithms
def gcd(a: int, b: int) -> int:
    """Greatest common divisor using Euclidean algorithm."""
    while b:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return a * b // gcd(a, b)

def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    
    return True

def sieve_of_eratosthenes(n: int) -> List[int]:
    """Find all prime numbers up to n using Sieve of Eratosthenes."""
    primes = []
    prime = [True for _ in range(n + 1)]
    p = 2
    
    while p * p <= n:
        if prime[p]:
            for i in range(p * p, n + 1, p):
                prime[i] = False
        p += 1
    
    for p in range(2, n + 1):
        if prime[p]:
            primes.append(p)
    
    return primes

# Machine Learning Algorithms
def k_means(points: List[List[float]], k: int, max_iterations: int = 100) -> tuple:
    """K-means clustering algorithm."""
    # Initialize centroids randomly
    centroids = random.sample(points, k)
    
    for _ in range(max_iterations):
        # Assign points to clusters
        clusters = [[] for _ in range(k)]
        
        for point in points:
            distances = [sum((a - b) ** 2 for a, b in zip(point, centroid)) for centroid in centroids]
            cluster_idx = distances.index(min(distances))
            clusters[cluster_idx].append(point)
        
        # Update centroids
        new_centroids = []
        for cluster in clusters:
            if cluster:
                centroid = [sum(dim) / len(cluster) for dim in zip(*cluster)]
                new_centroids.append(centroid)
            else:
                # If a cluster is empty, keep the old centroid
                new_centroids.append(centroids[len(new_centroids)])
        
        # Check for convergence
        if new_centroids == centroids:
            break
        
        centroids = new_centroids
    
    return centroids, clusters

def register_algorithms(interpreter):
    """Register all algorithms with the interpreter."""
    NativeFunction = interpreter.NativeFunction
    
    # Sorting Algorithms
    interpreter.globals.define("quick_sort", NativeFunction("quick_sort", 1, quick_sort))
    interpreter.globals.define("merge_sort", NativeFunction("merge_sort", 1, merge_sort))
    interpreter.globals.define("heap_sort", NativeFunction("heap_sort", 1, heap_sort))
    interpreter.globals.define("insertion_sort", NativeFunction("insertion_sort", 1, insertion_sort))
    
    # Search Algorithms
    interpreter.globals.define("binary_search", NativeFunction("binary_search", 2, binary_search))
    interpreter.globals.define("linear_search", NativeFunction("linear_search", 2, linear_search))
    
    # Graph Algorithms
    interpreter.globals.define("dijkstra", NativeFunction("dijkstra", 2, dijkstra))
    interpreter.globals.define("kruskal", NativeFunction("kruskal", 2, kruskal))
    
    # String Algorithms
    interpreter.globals.define("levenshtein_distance", NativeFunction("levenshtein_distance", 2, levenshtein_distance))
    interpreter.globals.define("kmp_search", NativeFunction("kmp_search", 2, kmp_search))
    
    # Numerical Algorithms
    interpreter.globals.define("gcd", NativeFunction("gcd", 2, gcd))
    interpreter.globals.define("lcm", NativeFunction("lcm", 2, lcm))
    interpreter.globals.define("is_prime", NativeFunction("is_prime", 1, is_prime))
    interpreter.globals.define("sieve_of_eratosthenes", NativeFunction("sieve_of_eratosthenes", 1, sieve_of_eratosthenes))
    
    # Machine Learning Algorithms
    interpreter.globals.define("k_means", NativeFunction("k_means", 2, k_means))