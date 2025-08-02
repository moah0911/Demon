// Comprehensive test script for the Demon language

print("--- Demon Language Full Feature Test ---");

// 1. Variables and Scoping
print("\n--- Testing Variables and Scoping ---");
var a = "global";
const PI = 3.14;
{
    var a = "local";
    print(a); // Expected: local
    print(PI); // Expected: 3.14
}
print(a); // Expected: global

// 2. Control Flow
print("\n--- Testing Control Flow ---");
var i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}

if (PI > 3) {
    print("PI is greater than 3.");
} else {
    print("PI is not greater than 3.");
}

// 3. Functions and Closures
print("\n--- Testing Functions and Closures ---");
func make_counter() {
    var i = 0;
    func count() {
        i = i + 1;
        return i;
    }
    return count;
}

var counter = make_counter();
print(counter()); // Expected: 1
print(counter()); // Expected: 2

// 4. Recursive Function (Fibonacci)
print("\n--- Testing Recursion (Fibonacci) ---");
func fib(n) {
    if (n <= 1) return n;
    return fib(n - 2) + fib(n - 1);
}
print(fib(10)); // Expected: 55

// 5. Classes and Methods
print("\n--- Testing Classes and Methods ---");
class Greeter {
    init(name) {
        this.name = name;
    }

    greet() {
        print("Hello, " + this.name + "!");
    }
}

var greeter = Greeter("Demon");
greeter.greet(); // Expected: Hello, Demon!

// 6. Inheritance
print("\n--- Testing Inheritance ---");
class LoudGreeter < Greeter {
    greet() {
        super.greet();
        print("I said, HELLO, " + this.name + "!");
    }
}

var loud_greeter = LoudGreeter("Developer");
loud_greeter.greet();

print("\n--- Full Feature Test Complete ---");
