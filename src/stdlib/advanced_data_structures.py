"""
Advanced data structures for the Demon programming language.
"""

from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, Generic
import heapq
from collections import OrderedDict

def register_advanced_data_structures(interpreter):
    """Register advanced data structures with the interpreter."""
    NativeFunction = interpreter.NativeFunction
    
    # Heap implementation
    _heaps = {}
    _heap_counter = [0]
    
    def heap_create(min_heap=True):
        """Create a new heap (min-heap by default)."""
        heap_id = str(_heap_counter[0])
        _heap_counter[0] += 1
        _heaps[heap_id] = {"data": [], "min_heap": min_heap}
        return heap_id
    
    def heap_push(heap_id, value):
        """Push a value onto the heap."""
        heap = _heaps[heap_id]
        # For max heap, negate the value to use Python's min-heap
        if not heap["min_heap"]:
            value = -value
        heapq.heappush(heap["data"], value)
        return heap_id
    
    def heap_pop(heap_id):
        """Pop the smallest (or largest) value from the heap."""
        heap = _heaps[heap_id]
        if not heap["data"]:
            return None
        value = heapq.heappop(heap["data"])
        # For max heap, negate the value back
        if not heap["min_heap"]:
            value = -value
        return value
    
    def heap_peek(heap_id):
        """Peek at the top value without removing it."""
        heap = _heaps[heap_id]
        if not heap["data"]:
            return None
        value = heap["data"][0]
        # For max heap, negate the value back
        if not heap["min_heap"]:
            value = -value
        return value
    
    def heap_size(heap_id):
        """Get the number of elements in the heap."""
        return len(_heaps[heap_id]["data"])
    
    def heap_is_empty(heap_id):
        """Check if the heap is empty."""
        return len(_heaps[heap_id]["data"]) == 0
    
    # LRU Cache implementation
    _lru_caches = {}
    _lru_counter = [0]
    
    def lru_create(capacity):
        """Create a new LRU cache with the given capacity."""
        lru_id = str(_lru_counter[0])
        _lru_counter[0] += 1
        _lru_caches[lru_id] = {"cache": OrderedDict(), "capacity": capacity}
        return lru_id
    
    def lru_get(lru_id, key):
        """Get a value from the LRU cache."""
        cache = _lru_caches[lru_id]["cache"]
        if key not in cache:
            return None
        # Move to end to show it was recently used
        value = cache.pop(key)
        cache[key] = value
        return value
    
    def lru_put(lru_id, key, value):
        """Put a value in the LRU cache."""
        cache_data = _lru_caches[lru_id]
        cache = cache_data["cache"]
        capacity = cache_data["capacity"]
        
        # If key exists, update its value and move to end
        if key in cache:
            cache.pop(key)
        # If at capacity, remove the least recently used item (first item)
        elif len(cache) >= capacity:
            cache.popitem(last=False)
        
        cache[key] = value
        return lru_id
    
    def lru_contains(lru_id, key):
        """Check if a key exists in the LRU cache."""
        return key in _lru_caches[lru_id]["cache"]
    
    def lru_size(lru_id):
        """Get the current size of the LRU cache."""
        return len(_lru_caches[lru_id]["cache"])
    
    def lru_capacity(lru_id):
        """Get the capacity of the LRU cache."""
        return _lru_caches[lru_id]["capacity"]
    
    def lru_clear(lru_id):
        """Clear all items from the LRU cache."""
        _lru_caches[lru_id]["cache"].clear()
        return lru_id
    
    # Bloom Filter implementation
    _bloom_filters = {}
    _bloom_counter = [0]
    
    def bloom_create(size=1000, hash_count=3):
        """Create a new Bloom filter."""
        bloom_id = str(_bloom_counter[0])
        _bloom_counter[0] += 1
        _bloom_filters[bloom_id] = {
            "size": size,
            "hash_count": hash_count,
            "bits": [False] * size
        }
        return bloom_id
    
    def bloom_add(bloom_id, item):
        """Add an item to the Bloom filter."""
        bloom = _bloom_filters[bloom_id]
        size = bloom["size"]
        hash_count = bloom["hash_count"]
        bits = bloom["bits"]
        
        # Simple hash functions
        h1 = hash(item) % size
        h2 = hash(str(item) + "salt1") % size
        h3 = hash(str(item) + "salt2") % size
        
        # Set bits based on hash functions
        bits[h1] = True
        if hash_count > 1:
            bits[h2] = True
        if hash_count > 2:
            bits[h3] = True
        
        return bloom_id
    
    def bloom_contains(bloom_id, item):
        """Check if an item might be in the Bloom filter."""
        bloom = _bloom_filters[bloom_id]
        size = bloom["size"]
        hash_count = bloom["hash_count"]
        bits = bloom["bits"]
        
        # Simple hash functions
        h1 = hash(item) % size
        if not bits[h1]:
            return False
        
        if hash_count > 1:
            h2 = hash(str(item) + "salt1") % size
            if not bits[h2]:
                return False
        
        if hash_count > 2:
            h3 = hash(str(item) + "salt2") % size
            if not bits[h3]:
                return False
        
        return True
    
    def bloom_clear(bloom_id):
        """Clear all items from the Bloom filter."""
        bloom = _bloom_filters[bloom_id]
        bloom["bits"] = [False] * bloom["size"]
        return bloom_id
    
    # Register Heap functions
    interpreter.globals.define("heap_create", NativeFunction("heap_create", 1, heap_create))
    interpreter.globals.define("heap_push", NativeFunction("heap_push", 2, heap_push))
    interpreter.globals.define("heap_pop", NativeFunction("heap_pop", 1, heap_pop))
    interpreter.globals.define("heap_peek", NativeFunction("heap_peek", 1, heap_peek))
    interpreter.globals.define("heap_size", NativeFunction("heap_size", 1, heap_size))
    interpreter.globals.define("heap_is_empty", NativeFunction("heap_is_empty", 1, heap_is_empty))
    
    # Register LRU Cache functions
    interpreter.globals.define("lru_create", NativeFunction("lru_create", 1, lru_create))
    interpreter.globals.define("lru_get", NativeFunction("lru_get", 2, lru_get))
    interpreter.globals.define("lru_put", NativeFunction("lru_put", 3, lru_put))
    interpreter.globals.define("lru_contains", NativeFunction("lru_contains", 2, lru_contains))
    interpreter.globals.define("lru_size", NativeFunction("lru_size", 1, lru_size))
    interpreter.globals.define("lru_capacity", NativeFunction("lru_capacity", 1, lru_capacity))
    interpreter.globals.define("lru_clear", NativeFunction("lru_clear", 1, lru_clear))
    
    # Register Bloom Filter functions
    interpreter.globals.define("bloom_create", NativeFunction("bloom_create", 2, bloom_create))
    interpreter.globals.define("bloom_add", NativeFunction("bloom_add", 2, bloom_add))
    interpreter.globals.define("bloom_contains", NativeFunction("bloom_contains", 2, bloom_contains))
    interpreter.globals.define("bloom_clear", NativeFunction("bloom_clear", 1, bloom_clear))