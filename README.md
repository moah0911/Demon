# Demon Programming Language

<div align="center">
  <img src="./Demon.png" alt="Demon Logo" width="200" height="200">
  <h3>A modern, expressive programming language with built-in data structures and algorithms</h3>
</div>

## Overview

Demon is a dynamic programming language designed for clarity, expressiveness, and ease of use. It combines the best features of modern languages with a clean syntax and powerful abstractions, with a special focus on built-in data structures and algorithms.

```demon
// Hello World in Demon
print("Hello, World!");

// Functions
func greet(name) {
    return "Hello, " + name + "!";
}

print(greet("Demon"));
```

## Features

- **Clean, Readable Syntax** - Inspired by JavaScript, Python, and Rust
- **First-class Functions** - Functions as values, closures, and higher-order functions
- **Dynamic Typing** - Flexible type system with runtime type checking
- **Object-Oriented** - Classes, inheritance, and methods
- **Rich Data Structures** - Priority queues, hash tables, BSTs, tries, heaps, and more
- **Built-in Algorithms** - Sorting, searching, graph algorithms, and dynamic programming
- **Control Flow** - If/else, while loops, and blocks
- **Error Handling** - Graceful error handling patterns
- **IDE Support** - Syntax highlighting, code completion, and error checking

## Installation

```bash
# Clone the repository
git clone https://github.com/moah0911/Demon.git
cd Demon

# Run a Demon script
python run.py examples/basic/hello.demon

# Set up IDE support
cd src/ide_support
chmod +x install.sh
./install.sh
```

## Language Examples

### Variables and Constants

```demon
let x = 10;        // Variable
const PI = 3.14159; // Constant
```

### Control Flow

```demon
// Conditional statements
if (x > 10) {
    print("x is greater than 10");
} else if (x < 10) {
    print("x is less than 10");
} else {
    print("x is equal to 10");
}

// While loops
let i = 1;
while (i <= 5) {
    print(i);
    i = i + 1;
}
```

### Functions

```demon
// Function definition
func add(a, b) {
    return a + b;
}

// Higher-order functions
func applyTwice(f, x) {
    return f(f(x));
}

func addOne(x) {
    return x + 1;
}

print(applyTwice(addOne, 5)); // Outputs: 7
```

### Data Structures

```demon
// Lists
let numbers = [1, 2, 3, 4, 5];
print("List:", numbers);

// Maps
let person = {"name": "John", "age": 30};
```

### Classes and Objects

```demon
class Point {
    init(x, y) {
        this.x = x;
        this.y = y;
    }
    
    distance() {
        return sqrt(this.x * this.x + this.y * this.y);
    }
    
    toString() {
        return "Point(" + this.x + ", " + this.y + ")";
    }
}

let p = Point(3, 4);
print(p.toString());         // Outputs: Point(3, 4)
print(p.distance());         // Outputs: 5.0
```

## Built-in Data Structures

Demon comes with a rich set of built-in data structures:

### Basic Data Structures

```demon
// Priority Queue
let pq_id = pq_create();
pq_push(pq_id, "Task 1", 3);
pq_push(pq_id, "Task 2", 1);
print(pq_pop(pq_id));  // Outputs: "Task 2" (lowest priority first)

// Hash Table
let ht_id = ht_create();
ht_set(ht_id, "name", "John");
print(ht_get(ht_id, "name"));  // Outputs: "John"
print(ht_contains(ht_id, "age"));  // Outputs: false

// Binary Search Tree
let tree_id = bst_create();
bst_insert(tree_id, 5);
bst_insert(tree_id, 3);
print(bst_search(tree_id, 3));  // Outputs: true
print(bst_in_order(tree_id));  // Outputs: [3, 5]

// Trie
let trie_id = trie_create();
trie_insert(trie_id, "apple");
print(trie_search(trie_id, "apple"));  // Outputs: true
print(trie_starts_with(trie_id, "app"));  // Outputs: true
```

### Advanced Data Structures

```demon
// Min Heap
let min_heap_id = heap_create(true);
heap_push(min_heap_id, 5);
heap_push(min_heap_id, 3);
print(heap_pop(min_heap_id));  // Outputs: 3

// Max Heap
let max_heap_id = heap_create(false);
heap_push(max_heap_id, 5);
heap_push(max_heap_id, 10);
print(heap_pop(max_heap_id));  // Outputs: 10

// LRU Cache
let cache_id = lru_create(3);
lru_put(cache_id, "key1", "value1");
lru_put(cache_id, "key2", "value2");
print(lru_get(cache_id, "key1"));  // Outputs: "value1"
```

## Built-in Algorithms

### Sorting and Searching

```demon
// Sorting
let unsorted = [5, 3, 8, 1, 2];
print(quick_sort(unsorted));  // Outputs: [1, 2, 3, 5, 8]
print(merge_sort(unsorted));  // Outputs: [1, 2, 3, 5, 8]

// Searching
let array = [1, 2, 3, 4, 5];
print(binary_search(array, 3));  // Outputs: 2 (index)
```

### Graph Algorithms

```demon
let g_id = graph_create();
graph_add_node(g_id, "A");
graph_add_node(g_id, "B");
graph_add_node(g_id, "C");
graph_add_edge(g_id, "A", "B", 1);
graph_add_edge(g_id, "B", "C", 2);

// Shortest path (Dijkstra's algorithm)
print(graph_shortest_path(g_id, "A"));  // Outputs: {"A": 0, "B": 1, "C": 3}

// Depth-first search
print(graph_dfs(g_id, "A"));  // Outputs: ["A", "B", "C"]
```

### Dynamic Programming

```demon
// Fibonacci with memoization
print(fibonacci_memo(30));  // Fast calculation with memoization

// Longest Common Subsequence
print(lcs("ABCDGH", "AEDFHR"));  // Outputs: "ADH"

// Edit Distance
print(edit_distance("kitten", "sitting"));  // Outputs: 3
```

## Current Limitations

- **For Loops**: Currently, Demon only supports while loops. For loops are not yet implemented.
- **Array Access in Type Checker**: The type checker doesn't fully support array literals and array access operations.
- **Bytecode Compilation**: The bytecode compiler is still under development and doesn't support all language features.
- **Logical Operators**: Use `and`, `or`, and `not` instead of `&&`, `||`, and `!`.

## IDE Support

Demon includes IDE support with the following features:
- Syntax highlighting
- Code completion
- Error checking
- Code formatting
- Navigation to definitions

To install IDE support:
```bash
cd src/ide_support
chmod +x install.sh
./install.sh
```

## Running the Tests

```bash
# Run all tests
python run.py examples/testing/test_expressions.demon
python run.py examples/testing/debug_test.demon
python run.py examples/testing/ide_test.demon
python run.py examples/testing/test_type_checker.demon --type-check

# Run the complete demo
python run.py examples/advanced/complete_demo.demon
```

## Project Structure

- **src/**: Core implementation of the language
  - **core/**: Core language components (parser, interpreter, VM)
  - **stdlib/**: Standard library implementations
  - **ide_support/**: IDE integration tools
  - **tools/**: Development tools (CLI, debugger, package manager)
- **examples/**: Example Demon programs
  - **basic/**: Simple examples for beginners
  - **advanced/**: Complex examples showcasing advanced features
  - **testing/**: Test cases for the language implementation
- **docs/**: Documentation for various aspects of the language

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to the Demon programming language.

## License

MIT License