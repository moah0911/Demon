// Test script for logical operators and short-circuiting

print("--- Testing Logical Operators ---");

func truthy() {
  print("truthy() called");
  return true;
}

func falsy() {
  print("falsy() called");
  return false;
}

print("\n-- Testing 'and' short-circuiting --");
// falsy() should be called, but truthy() should NOT be.
var result = falsy() and truthy();
print(result); // Expected: false
// Expected output:
// falsy() called
// false

print("\n-- Testing 'or' short-circuiting --");
// truthy() should be called, but falsy() should NOT be.
result = truthy() or falsy();
print(result); // Expected: true
// Expected output:
// truthy() called
// true

print("\n-- Testing precedence --");
// (false and true) or true -> false or true -> true
result = false and true or true;
print(result); // Expected: true

// true or true and false -> true or (true and false) -> true or false -> true
result = true or true and false;
print(result); // Expected: true

print("\n--- Logical Operators Tests Complete ---");
