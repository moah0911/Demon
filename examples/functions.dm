// Test script for functions

print("--- Testing Functions ---");

// Function with no arguments
func say_hello() {
  print("Hello, from a function!");
}

say_hello(); // Expected: Hello, from a function!

// Function with arguments
func add(a, b) {
  return a + b;
}

var sum = add(3, 4);
print(sum); // Expected: 7

// Function with local scope
var x = "global";
func show_scope() {
  var x = "local";
  print(x); // Expected: local
}

show_scope();
print(x); // Expected: global

print("--- Function Tests Complete ---");
