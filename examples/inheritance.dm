// Test script for inheritance

print("--- Testing Inheritance ---");

class Animal {
  speak() {
    print("The animal makes a sound.");
  }
}

class Dog < Animal {
  speak() {
    super.speak();
    print("The dog barks.");
  }
}

var dog = Dog();
dog.speak();
// Expected:
// The animal makes a sound.
// The dog barks.

print("--- Inheritance Tests Complete ---");
