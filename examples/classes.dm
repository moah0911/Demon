// Test script for classes

print("--- Testing Classes ---");

class Greeter {
  init(greeting) {
    this.greeting = greeting;
  }

  greet() {
    print(this.greeting);
  }
}

var greeter = Greeter("Hello from a class!");
greeter.greet(); // Expected: Hello from a class!

// Test field access
greeter.greeting = "Hello again!";
greeter.greet(); // Expected: Hello again!

print("--- Class Tests Complete ---");
