# Advanced Features in Demon

This document provides detailed information about the advanced algorithms and data structures available in the Demon programming language.

## Advanced Algorithms

### Dynamic Programming

#### Fibonacci with Memoization

Efficiently calculates Fibonacci numbers using memoization to avoid redundant calculations.

```demon
// Calculate the nth Fibonacci number
let fib = fibonacci_memo(30);  // Much faster than naive recursion
print(fib);  // 832040
```

#### Longest Common Subsequence (LCS)

Finds the longest subsequence common to two strings.

```demon
// Find the LCS of two strings
let result = lcs("ABCDGH", "AEDFHR");
print(result);  // "ADH"
```

#### Edit Distance (Levenshtein Distance)

Calculates the minimum number of operations (insertions, deletions, or substitutions) required to transform one string into another.

```demon
// Calculate edit distance
let distance = edit_distance("kitten", "sitting");
print(distance);  // 3
```

#### Knapsack Problem

Solves the 0/1 knapsack problem to find the maximum value that can be obtained by selecting items with given weights and values, without exceeding a capacity constraint.

```demon
// Solve knapsack problem
// Note: This requires array support which may be limited in Demon
let weights = [10, 20, 30];
let values = [60, 100, 120];
let capacity = 50;
let result = knapsack(weights, values, capacity);
print("Maximum value:", result[0]);  // 220
print("Selected items:", result[1]);  // [0, 1] (indices of selected items)
```

## Advanced Data Structures

### Heap

A binary heap data structure that can be used as either a min-heap (smallest element at the top) or a max-heap (largest element at the top).

```demon
// Min Heap
let min_heap_id = heap_create(true);  // true for min-heap
heap_push(min_heap_id, 5);
heap_push(min_heap_id, 3);
heap_push(min_heap_id, 8);

print(heap_peek(min_heap_id));  // 3 (smallest element)
print(heap_pop(min_heap_id));   // 3
print(heap_pop(min_heap_id));   // 5

// Max Heap
let max_heap_id = heap_create(false);  // false for max-heap
heap_push(max_heap_id, 5);
heap_push(max_heap_id, 3);
heap_push(max_heap_id, 8);

print(heap_peek(max_heap_id));  // 8 (largest element)
print(heap_pop(max_heap_id));   // 8
print(heap_pop(max_heap_id));   // 5
```

### LRU Cache

A Least Recently Used (LRU) cache that maintains a fixed-size cache of key-value pairs, evicting the least recently used items when the cache reaches capacity.

```demon
// Create an LRU cache with capacity 3
let cache_id = lru_create(3);

// Add items
lru_put(cache_id, "key1", "value1");
lru_put(cache_id, "key2", "value2");
lru_put(cache_id, "key3", "value3");

// Get items
print(lru_get(cache_id, "key1"));  // "value1"

// Adding a new item when at capacity evicts the least recently used item
lru_put(cache_id, "key4", "value4");
print(lru_contains(cache_id, "key2"));  // false (evicted)
print(lru_contains(cache_id, "key1"));  // true (was accessed recently)

// Clear the cache
lru_clear(cache_id);
print(lru_size(cache_id));  // 0
```

## Important Notes

1. When using these advanced data structures, avoid using variable names like `heap` or `cache` as they may conflict with language keywords.

2. Always use the appropriate variable names like `heap_id` for heaps and `cache_id` for LRU caches.

3. All data structures return an ID that must be used in subsequent operations.

4. The min-heap returns elements in ascending order, while the max-heap returns elements in descending order.

5. The LRU cache automatically evicts the least recently used item when it reaches capacity.

## Running the Demos

To see these advanced features in action, run the demo files:

```bash
python run.py examples/advanced/advanced_algorithms_demo.demon
python run.py examples/advanced/advanced_data_structures_demo.demon
```