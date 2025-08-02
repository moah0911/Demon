// Test script for control flow

print("--- Testing Control Flow ---");

var a = 5;

// If statement
if (a == 5) {
  print("a is 5"); // Expected: a is 5
}

// If-else statement
if (a > 10) {
  print("a is greater than 10");
} else {
  print("a is not greater than 10"); // Expected: a is not greater than 10
}

// While loop
var i = 0;
while (i < 3) {
  print(i); // Expected: 0, 1, 2
  i = i + 1;
}

print("--- Control Flow Tests Complete ---");
