# Exception Handling in Demon

Demon provides a robust exception handling mechanism similar to other modern programming languages. This allows you to gracefully handle errors and exceptional conditions in your code.

## Basic Syntax

### Try-Catch

The basic structure of exception handling in Demon uses `try` and `catch` blocks:

```demon
try {
    // Code that might throw an exception
    let result = riskyOperation();
} catch (e) {
    // Code to handle the exception
    print("An error occurred: " + e);
}
```

### Try-Catch-Finally

You can also include a `finally` block that always executes, whether an exception was thrown or not:

```demon
try {
    // Code that might throw an exception
    openFile("data.txt");
} catch (e) {
    // Code to handle the exception
    print("Error opening file: " + e);
} finally {
    // Code that always runs
    cleanupResources();
}
```

## Exception Propagation

If an exception is not caught in a function, it propagates up the call stack until it's caught or reaches the top level:

```demon
func inner() {
    let result = 10 / 0;  // Throws an exception
}

func outer() {
    try {
        inner();
    } catch (e) {
        print("Caught in outer: " + e);
    }
}

outer();  // Prints: "Caught in outer: Division by zero."
```

## Nested Try-Catch Blocks

You can nest try-catch blocks to handle different types of exceptions at different levels:

```demon
try {
    try {
        // Risky operation
        let result = 10 / 0;
    } catch (e) {
        print("Inner catch: " + e);
        // Re-throw or throw a new exception
        throw "New exception";
    }
} catch (e) {
    print("Outer catch: " + e);
}
```

## Best Practices

1. **Use Finally for Cleanup**: Always use `finally` blocks to clean up resources
2. **Catch Specific Exceptions**: Be as specific as possible about what exceptions you catch
3. **Don't Swallow Exceptions**: Always handle or re-throw exceptions
4. **Keep Try Blocks Small**: Only include code that might throw exceptions in try blocks
5. **Provide Meaningful Error Messages**: Make error messages descriptive and helpful

## Example: Resource Management

```demon
func processFile(filename) {
    let file = null;
    try {
        // Open file (hypothetical API)
        file = openFile(filename);
        
        // Process file
        let data = file.readAll();
        return processData(data);
    } catch (e) {
        print("Error processing file: " + e);
        return null;
    } finally {
        // Always close the file, even if an exception occurred
        if (file != null) {
            file.close();
        }
    }
}
```

## Current Limitations

- Custom exception types are not yet fully supported
- Stack traces are limited
- No built-in exception hierarchy

These features are planned for future versions of the language.