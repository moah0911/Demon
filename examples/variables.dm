// Test script for variables

print("--- Testing Variables ---");

var a = 1;
print(a); // Expected: 1

a = 2;
print(a); // Expected: 2

const b = 10;
print(b); // Expected: 10

// b = 11; // This should cause a runtime error

{
  var c = 3;
  print(c); // Expected: 3
  print(a); // Expected: 2
}

// print(c); // This should cause a runtime error (out of scope)

print("--- Variable Tests Complete ---");
