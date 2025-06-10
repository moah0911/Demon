# Data Structures and Algorithms in Demon

This document provides detailed information about the built-in data structures and algorithms available in the Demon programming language.

## Data Structures

### Priority Queue

A priority queue is a data structure that allows you to retrieve elements based on their priority.

```demon
// Create a priority queue
let pq_id = pq_create();

// Add items with priorities (lower number = higher priority)
pq_push(pq_id, "Task 1", 3);
pq_push(pq_id, "Task 2", 1);
pq_push(pq_id, "Task 3", 2);

// Check if empty
print(pq_is_empty(pq_id));  // false

// Get the size
print(pq_size(pq_id));  // 3

// Pop items (returns highest priority item)
print(pq_pop(pq_id));  // "Task 2" (priority 1)
print(pq_pop(pq_id));  // "Task 3" (priority 2)
print(pq_pop(pq_id));  // "Task 1" (priority 3)
```

### Hash Table

A hash table provides fast key-value lookups.

```demon
// Create a hash table
let ht_id = ht_create();

// Set key-value pairs
ht_set(ht_id, "name", "John");
ht_set(ht_id, "age", 30);

// Get values
print(ht_get(ht_id, "name"));  // "John"

// Check if a key exists
print(ht_contains(ht_id, "name"));  // true
print(ht_contains(ht_id, "email"));  // false

// Get with default value
print(ht_get_default(ht_id, "email", "Not found"));  // "Not found"
```

### Binary Search Tree

A binary search tree maintains ordered data with efficient search operations.

```demon
// Create a binary search tree
let tree_id = bst_create();

// Insert values
bst_insert(tree_id, 5);
bst_insert(tree_id, 3);
bst_insert(tree_id, 7);

// Search for values
print(bst_search(tree_id, 3));  // true
print(bst_search(tree_id, 4));  // false

// Get in-order traversal
print(bst_in_order(tree_id));  // [3, 5, 7]
```

### Trie

A trie is a tree-like data structure optimized for string operations and prefix searches.

```demon
// Create a trie
let trie_id = trie_create();

// Insert words
trie_insert(trie_id, "apple");
trie_insert(trie_id, "application");
trie_insert(trie_id, "banana");

// Search for words
print(trie_search(trie_id, "apple"));  // true
print(trie_search(trie_id, "app"));  // false

// Check if a prefix exists
print(trie_starts_with(trie_id, "app"));  // true
print(trie_starts_with(trie_id, "ban"));  // true
print(trie_starts_with(trie_id, "car"));  // false
```

### Graph

A graph represents connections between nodes.

```demon
// Create a graph
let g_id = graph_create();

// Add nodes
graph_add_node(g_id, "A");
graph_add_node(g_id, "B");
graph_add_node(g_id, "C");

// Add edges with weights
graph_add_edge(g_id, "A", "B", 1);
graph_add_edge(g_id, "B", "C", 2);
graph_add_edge(g_id, "A", "C", 4);

// Get nodes and edges
print(graph_get_nodes(g_id));  // ["A", "B", "C"]
print(graph_get_edges(g_id));  // [("A", "B", 1), ("B", "C", 2), ("A", "C", 4)]
```

## Algorithms

### Sorting Algorithms

```demon
let unsorted = [5, 3, 8, 1, 2];

// Quick sort
print(quick_sort(unsorted));  // [1, 2, 3, 5, 8]

// Merge sort
print(merge_sort(unsorted));  // [1, 2, 3, 5, 8]

// Built-in sort
print(sort(unsorted));  // [1, 2, 3, 5, 8]
```

### Search Algorithms

```demon
let array = [1, 2, 3, 4, 5];

// Binary search (returns index or -1 if not found)
print(binary_search(array, 3));  // 2 (index)
print(binary_search(array, 6));  // -1 (not found)
```

### Graph Algorithms

```demon
let g_id = graph_create();
graph_add_node(g_id, "A");
graph_add_node(g_id, "B");
graph_add_node(g_id, "C");
graph_add_node(g_id, "D");
graph_add_edge(g_id, "A", "B", 1);
graph_add_edge(g_id, "A", "C", 4);
graph_add_edge(g_id, "B", "C", 2);
graph_add_edge(g_id, "B", "D", 5);
graph_add_edge(g_id, "C", "D", 1);

// Shortest path (Dijkstra's algorithm)
print(graph_shortest_path(g_id, "A"));  
// {"A": 0, "B": 1, "C": 3, "D": 4}

// Depth-first search
print(graph_dfs(g_id, "A"));  // ["A", "B", "C", "D"]
```

## Important Notes

1. When using these data structures, avoid using variable names like `bst` or `graph` as they may conflict with language keywords.

2. Always use the appropriate variable names like `tree_id` for binary search trees and `g_id` for graphs.

3. All data structures return an ID that must be used in subsequent operations.

4. The priority queue pops items in order of priority (lowest number first).

5. Binary search requires a sorted array to work correctly.