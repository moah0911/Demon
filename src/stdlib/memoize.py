"""
Automatic memoization for the Demon programming language.
This module provides advanced memoization capabilities with various caching strategies.
"""

from typing import Any, Dict, List, Callable, Optional, Tuple, Union, TypeVar
import time
import threading
import functools
import inspect
import hashlib
import pickle

T = TypeVar('T')

class CacheStrategy:
    """Base class for cache strategies."""
    
    def get(self, key: Any) -> Tuple[bool, Any]:
        """
        Get a value from the cache.
        
        Returns:
            Tuple[bool, Any]: (hit, value) where hit is True if the key was found
        """
        raise NotImplementedError("Subclasses must implement get")
    
    def set(self, key: Any, value: Any) -> None:
        """Set a value in the cache."""
        raise NotImplementedError("Subclasses must implement set")
    
    def clear(self) -> None:
        """Clear the cache."""
        raise NotImplementedError("Subclasses must implement clear")
    
    def size(self) -> int:
        """Get the number of items in the cache."""
        raise NotImplementedError("Subclasses must implement size")

class UnlimitedCache(CacheStrategy):
    """A cache with unlimited capacity."""
    
    def __init__(self):
        self.cache: Dict[Any, Any] = {}
        self._lock = threading.RLock()
    
    def get(self, key: Any) -> Tuple[bool, Any]:
        with self._lock:
            if key in self.cache:
                return True, self.cache[key]
            return False, None
    
    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            self.cache[key] = value
    
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
    
    def size(self) -> int:
        with self._lock:
            return len(self.cache)

class LRUCache(CacheStrategy):
    """A Least Recently Used (LRU) cache."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[Any, Any] = {}
        self.usage: List[Any] = []
        self._lock = threading.RLock()
    
    def get(self, key: Any) -> Tuple[bool, Any]:
        with self._lock:
            if key in self.cache:
                # Move key to the end (most recently used)
                self.usage.remove(key)
                self.usage.append(key)
                return True, self.cache[key]
            return False, None
    
    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self.cache:
                # Update existing key
                self.cache[key] = value
                self.usage.remove(key)
                self.usage.append(key)
            else:
                # Add new key
                if len(self.cache) >= self.capacity:
                    # Remove least recently used item
                    lru_key = self.usage.pop(0)
                    del self.cache[lru_key]
                
                self.cache[key] = value
                self.usage.append(key)
    
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
            self.usage.clear()
    
    def size(self) -> int:
        with self._lock:
            return len(self.cache)

class TTLCache(CacheStrategy):
    """A Time-To-Live (TTL) cache."""
    
    def __init__(self, ttl: float):
        self.ttl = ttl
        self.cache: Dict[Any, Tuple[Any, float]] = {}  # (value, expiry)
        self._lock = threading.RLock()
    
    def get(self, key: Any) -> Tuple[bool, Any]:
        with self._lock:
            if key in self.cache:
                value, expiry = self.cache[key]
                if time.time() < expiry:
                    return True, value
                else:
                    # Remove expired item
                    del self.cache[key]
            return False, None
    
    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            expiry = time.time() + self.ttl
            self.cache[key] = (value, expiry)
    
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
    
    def size(self) -> int:
        with self._lock:
            # Count only non-expired items
            now = time.time()
            return sum(1 for _, expiry in self.cache.values() if now < expiry)
    
    def cleanup(self) -> None:
        """Remove all expired items from the cache."""
        with self._lock:
            now = time.time()
            expired_keys = [k for k, (_, expiry) in self.cache.items() if now >= expiry]
            for key in expired_keys:
                del self.cache[key]

class LFUCache(CacheStrategy):
    """A Least Frequently Used (LFU) cache."""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: Dict[Any, Any] = {}
        self.frequency: Dict[Any, int] = {}
        self._lock = threading.RLock()
    
    def get(self, key: Any) -> Tuple[bool, Any]:
        with self._lock:
            if key in self.cache:
                # Increment frequency
                self.frequency[key] += 1
                return True, self.cache[key]
            return False, None
    
    def set(self, key: Any, value: Any) -> None:
        with self._lock:
            if key in self.cache:
                # Update existing key
                self.cache[key] = value
                self.frequency[key] += 1
            else:
                # Add new key
                if len(self.cache) >= self.capacity:
                    # Remove least frequently used item
                    lfu_key = min(self.frequency.items(), key=lambda x: x[1])[0]
                    del self.cache[lfu_key]
                    del self.frequency[lfu_key]
                
                self.cache[key] = value
                self.frequency[key] = 1
    
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
            self.frequency.clear()
    
    def size(self) -> int:
        with self._lock:
            return len(self.cache)

def make_key(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> str:
    """Create a cache key from function arguments."""
    key_parts = [pickle.dumps(args)]
    
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key_parts.append(pickle.dumps(sorted_items))
    
    key = hashlib.md5(b''.join(key_parts)).hexdigest()
    return key

class Memoized:
    """A memoized function."""
    
    def __init__(
        self, 
        fn: Callable[..., T], 
        strategy: CacheStrategy = None,
        key_fn: Callable[..., Any] = None
    ):
        self.fn = fn
        self.strategy = strategy or UnlimitedCache()
        self.key_fn = key_fn or make_key
        functools.update_wrapper(self, fn)
    
    def __call__(self, *args: Any, **kwargs: Any) -> T:
        # Create cache key
        if self.key_fn:
            key = self.key_fn(*args, **kwargs)
        else:
            key = make_key(args, kwargs)
        
        # Check cache
        hit, value = self.strategy.get(key)
        if hit:
            return value
        
        # Call function and cache result
        result = self.fn(*args, **kwargs)
        self.strategy.set(key, result)
        return result
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self.strategy.clear()
    
    def cache_size(self) -> int:
        """Get the number of items in the cache."""
        return self.strategy.size()

def memoize(
    fn: Optional[Callable] = None, 
    *, 
    strategy: Optional[CacheStrategy] = None,
    capacity: Optional[int] = None,
    ttl: Optional[float] = None,
    key_fn: Optional[Callable[..., Any]] = None
) -> Union[Memoized, Callable[[Callable], Memoized]]:
    """
    Decorator to memoize a function.
    
    Args:
        fn: The function to memoize
        strategy: The cache strategy to use
        capacity: The capacity for LRU or LFU cache
        ttl: The time-to-live for TTL cache
        key_fn: A function to create cache keys
    
    Returns:
        A memoized function
    """
    # Determine the cache strategy
    if strategy is None:
        if capacity is not None:
            strategy = LRUCache(capacity)
        elif ttl is not None:
            strategy = TTLCache(ttl)
        else:
            strategy = UnlimitedCache()
    
    def decorator(func):
        return Memoized(func, strategy, key_fn)
    
    if fn is None:
        return decorator
    return decorator(fn)

def lru_cache(capacity: int = 128):
    """
    Decorator to memoize a function with an LRU cache.
    
    Args:
        capacity: The maximum number of items to store in the cache
    
    Returns:
        A decorator that memoizes a function with an LRU cache
    """
    return lambda fn: memoize(fn, strategy=LRUCache(capacity))

def ttl_cache(ttl: float):
    """
    Decorator to memoize a function with a TTL cache.
    
    Args:
        ttl: The time-to-live in seconds
    
    Returns:
        A decorator that memoizes a function with a TTL cache
    """
    return lambda fn: memoize(fn, strategy=TTLCache(ttl))

def lfu_cache(capacity: int = 128):
    """
    Decorator to memoize a function with an LFU cache.
    
    Args:
        capacity: The maximum number of items to store in the cache
    
    Returns:
        A decorator that memoizes a function with an LFU cache
    """
    return lambda fn: memoize(fn, strategy=LFUCache(capacity))