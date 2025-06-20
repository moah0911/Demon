# Static Methods in Demon

Demon supports static methods on classes, which are methods that can be called directly on the class itself rather than on instances of the class.

## Basic Usage

### Defining Static Methods

To define a static method, use the `static` keyword before the method name:

```demon
class MathUtils {
    static add(a, b) {
        return a + b;
    }
    
    static multiply(a, b) {
        return a * b;
    }
}
```

### Calling Static Methods

Static methods are called directly on the class, not on instances:

```demon
// Call static methods directly on the class
let sum = MathUtils.add(5, 3);      // 8
let product = MathUtils.multiply(4, 6);  // 24
```

## Common Use Cases

### Factory Methods

Static methods are often used as factory methods to create instances of a class:

```demon
class Person {
    init(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return "Hello, my name is " + this.name;
    }
    
    static create(name, age) {
        return Person(name, age);
    }
    
    static createAnonymous() {
        return Person("Anonymous", 0);
    }
}

// Create instances using static factory methods
let john = Person.create("John", 30);
let anonymous = Person.createAnonymous();
```

### Utility Methods

Static methods are useful for utility functions related to a class:

```demon
class StringUtils {
    static capitalize(str) {
        if (str.length == 0) {
            return str;
        }
        return string.upper(str[0]) + string.slice(str, 1);
    }
    
    static reverse(str) {
        // Implementation of string reversal
        return string.reverse(str);
    }
}

// Use utility methods
let capitalized = StringUtils.capitalize("hello");  // "Hello"
let reversed = StringUtils.reverse("hello");        // "olleh"
```

## Static Methods vs. Instance Methods

- **Static methods** belong to the class itself and can be called without creating an instance
- **Instance methods** belong to instances of the class and require an instance to be called

```demon
class Example {
    init(value) {
        this.value = value;
    }
    
    // Instance method - needs an instance
    getValue() {
        return this.value;
    }
    
    // Static method - called on the class
    static createDefault() {
        return Example(0);
    }
}

// Using static method
let default = Example.createDefault();

// Using instance method
let example = Example(42);
let value = example.getValue();  // 42
```

## Implementation Details

Static methods in Demon are stored separately from instance methods in the class definition. When you call a method on a class (rather than an instance), the interpreter first checks if a static method with that name exists before proceeding with normal property access.