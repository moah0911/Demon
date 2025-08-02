//! Memory management module for the Demon language.
//! Provides C++-like memory management features including raw pointers and custom allocators.

use std::alloc::{alloc, dealloc, Layout};
use std::ptr;
use std::cell::RefCell;
use std::rc::Rc;

/// A raw pointer type for Demon language
#[derive(Debug, Clone)]
pub struct RawPointer<T> {
    ptr: *mut T,
    layout: Layout,
}

impl<T> RawPointer<T> {
    /// Allocates memory for a single value of type T
    pub fn new(value: T) -> Self {
        let layout = Layout::new::<T>();
        unsafe {
            let ptr = alloc(layout) as *mut T;
            ptr.write(value);
            Self { ptr, layout }
        }
    }

    /// Allocates memory for an array of values
    pub fn new_array(len: usize, value: T) -> Self 
    where
        T: Clone,
    {
        let layout = Layout::array::<T>(len).unwrap();
        unsafe {
            let ptr = alloc(layout) as *mut T;
            for i in 0..len {
                ptr.add(i).write(value.clone());
            }
            Self { ptr, layout }
        }
    }

    /// Gets a reference to the pointed value
    pub fn get(&self) -> &T {
        unsafe { &*self.ptr }
    }

    /// Gets a mutable reference to the pointed value
    pub fn get_mut(&mut self) -> &mut T {
        unsafe { &mut *self.ptr }
    }
}

impl<T> Drop for RawPointer<T> {
    fn drop(&mut self) {
        unsafe {
            ptr::drop_in_place(self.ptr);
            dealloc(self.ptr as *mut u8, self.layout);
        }
    }
}

/// A smart pointer with reference counting
#[derive(Debug, Clone)]
pub struct SharedPointer<T> {
    inner: Rc<RefCell<T>>,
}

impl<T> SharedPointer<T> {
    /// Creates a new shared pointer
    pub fn new(value: T) -> Self {
        Self {
            inner: Rc::new(RefCell::new(value)),
        }
    }

    /// Gets a reference to the inner value
    pub fn borrow(&self) -> std::cell::Ref<T> {
        self.inner.borrow()
    }

    /// Gets a mutable reference to the inner value
    pub fn borrow_mut(&self) -> std::cell::RefMut<T> {
        self.inner.borrow_mut()
    }
}

/// Custom allocator trait
pub trait Allocator {
    /// Allocates memory with the given layout
    unsafe fn allocate(&self, layout: Layout) -> *mut u8;
    
    /// Deallocates memory previously allocated with this allocator
    unsafe fn deallocate(&self, ptr: *mut u8, layout: Layout);
}

/// The default global allocator
pub struct GlobalAllocator;

impl Allocator for GlobalAllocator {
    unsafe fn allocate(&self, layout: Layout) -> *mut u8 {
        alloc(layout)
    }

    unsafe fn deallocate(&self, ptr: *mut u8, layout: Layout) {
        dealloc(ptr, layout);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_raw_pointer() {
        let mut ptr = RawPointer::new(42);
        assert_eq!(*ptr.get(), 42);
        *ptr.get_mut() = 24;
        assert_eq!(*ptr.get(), 24);
    }

    #[test]
    fn test_shared_pointer() {
        let ptr = SharedPointer::new(String::from("test"));
        assert_eq!(*ptr.borrow(), "test");
        ptr.borrow_mut().push_str("ing");
        assert_eq!(*ptr.borrow(), "testing");
    }
}
