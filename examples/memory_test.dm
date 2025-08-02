// Memory Management Test Script

// Test basic object allocation
let obj = new Object();
print "Created object:";
print obj;

// Test array allocation
let arr = new int[5];
print "\nCreated array:";
print arr;

// Test array access and modification
for (let i = 0; i < 5; i = i + 1) {
    arr[i] = i * 10;
}
print "\nArray after initialization:";
for (let i = 0; i < 5; i = i + 1) {
    print "arr[" + str(i) + "] = " + str(arr[i]);
}

// Test pointer operations
let x = 42;
let ptr = &x;  // Get address of x
print "\nValue of x:";
print x;
print "Address of x:";
print ptr;

// Test delete
print "\nDeleting array...";
delete[] arr;
print "Array after delete:";
print arr;  // Should be nil or equivalent

// Test custom allocator (placeholder for now)
print "\nTesting custom allocator...";
let alloc = CustomAllocator.new();
let customObj = new(alloc) Object();
print "Created object with custom allocator:";
print customObj;

delete customObj;
print "Test complete.";
