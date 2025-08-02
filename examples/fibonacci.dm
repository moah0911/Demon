// Test script for a more complex example: Fibonacci sequence

print("--- Testing Fibonacci Sequence ---");

func fib(n) {
  if (n <= 1) return n;
  return fib(n - 2) + fib(n - 1);
}

var i = 0;
while (i < 10) {
  print(fib(i));
  i = i + 1;
}

print("--- Fibonacci Sequence Test Complete ---");
