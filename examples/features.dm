// Demon Language Feature Test
// This script tests various features of the Demon language

// 1. Basic I/O
print("=== Starting Demon Language Feature Test ===");
print("Hello, Demon!");

// 2. Variables and basic types
let name = "Demon";
let version = 1.0;
let isAwesome = true;
let nothing = nil;

print("\n=== Variables ===");
print("Name:", name);
print("Version:", version);
print("Is awesome?", isAwesome);
print("Nothing:", nothing);

// 3. Control flow
print("\n=== Control Flow ===");
if (isAwesome) {
    print("Demon is awesome!");
} else {
    print("This should not print");
}

let count = 0;
while (count < 3) {
    print("Count:", count);
    count = count + 1;
}

// 4. Functions
print("\n=== Functions ===");
fn greet(person) {
    return "Hello, " + person + "!";
}

print(greet("World"));

// 5. Arrays
print("\n=== Arrays ===");
let numbers = array(1, 2, 3, 4, 5);
print("Numbers:", numbers);
print("First number:", numbers[0]);
print("Array length:", len(numbers));

// Add a number to the array
numbers = push(numbers, 6);
print("After push:", numbers);

// Remove last number
let last = pop(numbers);
print("Popped:", last);
print("After pop:", numbers);

// 6. Maps
print("\n=== Maps ===");
let person = map_new();
person = map_set(person, "name", "Alice");
person = map_set(person, "age", 30);
person = map_set(person, "isStudent", false);

print("Person:", person);
print("Name:", map_get(person, "name"));
print("Has age?", map_has(person, "age"));
print("Keys:", map_keys(person));

// 7. Classes
print("\n=== Classes ===");
class Person {
    init(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return "Hello, my name is " + this.name + " and I'm " + to_string(this.age) + " years old.";
    }
    
    haveBirthday() {
        this.age = this.age + 1;
        return "Happy birthday! Now I'm " + this.age + " years old.";
    }
}

let alice = Person("Alice", 25);
print(alice.greet());
print(alice.haveBirthday());
print("New age:", alice.age);

// 8. Standard library functions
print("\n=== Standard Library ===");
print("Absolute value of -5:", abs(-5));
print("Square root of 16:", sqrt(16));
print("2 to the power of 3:", pow(2, 3));
print("Length of 'hello':", len("hello"));
print("Substring 'ell' from 'hello':", substring("hello", 1, 4));
print("Current time:", time());

// 9. Error handling
try {
    print("\n=== Error Handling ===");
    let result = 10 / 0;  // This will cause a runtime error
    print("This should not print:", result);
} catch (e) {
    print("Caught an error:", e);
}

print("\n=== Test Complete ===");
