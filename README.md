# Demon Programming Language

<div align="center">
  <img src="https://via.placeholder.com/200x200?text=Demon" alt="Demon Logo" width="200" height="200">
  <h3>A modern, expressive programming language</h3>
</div>

## Overview

Demon is a dynamic programming language designed for clarity, expressiveness, and ease of use. It combines the best features of modern languages with a clean syntax and powerful abstractions.

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
- **Data Structures** - Lists, maps, and more
- **Control Flow** - If/else, while loops, and blocks
- **Error Handling** - Graceful error handling patterns
- **Built-in DSA** - Common data structures and algorithms included

## Installation

```bash
# Clone the repository
git clone https://github.com/moah0911/Demon.git
cd demon

# Run a Demon script
python run.py examples/basic/hello_fixed.demon
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

## Built-in Data Structures and Algorithms

Demon comes with a rich set of built-in data structures and algorithms:

### Data Structures

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

### Algorithms

```demon
// Sorting
let unsorted = [5, 3, 8, 1, 2];
print(quick_sort(unsorted));  // Outputs: [1, 2, 3, 5, 8]
print(merge_sort(unsorted));  // Outputs: [1, 2, 3, 5, 8]

// Searching
let array = [1, 2, 3, 4, 5];
print(binary_search(array, 3));  // Outputs: 2 (index)

// Graph Algorithms
let g_id = graph_create();
graph_add_node(g_id, "A");
graph_add_node(g_id, "B");
graph_add_edge(g_id, "A", "B", 1);
print(graph_shortest_path(g_id, "A"));  // Outputs: {"A": 0, "B": 1}
print(graph_dfs(g_id, "A"));  // Outputs: ["A", "B"]
```

### Functional Utilities

```demon
// Map, Filter, Reduce
let nums = [1, 2, 3, 4, 5];
print(map(func(x) { return x * 2; }, nums));  // Outputs: [2, 4, 6, 8, 10]
print(filter(func(x) { return x % 2 == 0; }, nums));  // Outputs: [2, 4]
print(reduce(func(acc, x) { return acc + x; }, nums, 0));  // Outputs: 15
```

## Running the REPL

```bash
python run.py
```

## Running the Demo

To see all data structures and algorithms in action:

```bash
python run.py examples/advanced/all_algorithms_demo.demon
```

## License

MIT License
