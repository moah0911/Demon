"""
Dataflow programming for the Demon programming language.
This module provides a powerful dataflow programming model with automatic parallelization.
"""

from typing import Any, Dict, List, Set, Callable, Optional, TypeVar, Generic, Union
import threading
import queue
import time
import concurrent.futures
from enum import Enum

T = TypeVar('T')
U = TypeVar('U')

class NodeState(Enum):
    """State of a dataflow node."""
    IDLE = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3

class DataNode(Generic[T]):
    """A node in a dataflow graph that produces data."""
    
    def __init__(self, name: str = None):
        self.name = name or f"Node-{id(self)}"
        self.state = NodeState.IDLE
        self.result: Optional[T] = None
        self.error: Optional[Exception] = None
        self.dependencies: Set['DataNode'] = set()
        self.dependents: Set['DataNode'] = set()
        self._on_complete_callbacks: List[Callable[[T], None]] = []
        self._on_error_callbacks: List[Callable[[Exception], None]] = []
        self._lock = threading.RLock()
    
    def depends_on(self, *nodes: 'DataNode') -> 'DataNode':
        """Add dependencies to this node."""
        for node in nodes:
            self.dependencies.add(node)
            node.dependents.add(self)
        return self
    
    def on_complete(self, callback: Callable[[T], None]) -> 'DataNode':
        """Register a callback to be called when this node completes successfully."""
        with self._lock:
            if self.state == NodeState.COMPLETED:
                callback(self.result)
            else:
                self._on_complete_callbacks.append(callback)
        return self
    
    def on_error(self, callback: Callable[[Exception], None]) -> 'DataNode':
        """Register a callback to be called when this node fails."""
        with self._lock:
            if self.state == NodeState.FAILED:
                callback(self.error)
            else:
                self._on_error_callbacks.append(callback)
        return self
    
    def _notify_complete(self) -> None:
        """Notify all completion callbacks."""
        callbacks = []
        with self._lock:
            callbacks = list(self._on_complete_callbacks)
            self._on_complete_callbacks = []
        
        for callback in callbacks:
            try:
                callback(self.result)
            except Exception as e:
                print(f"Error in completion callback: {e}")
    
    def _notify_error(self) -> None:
        """Notify all error callbacks."""
        callbacks = []
        with self._lock:
            callbacks = list(self._on_error_callbacks)
            self._on_error_callbacks = []
        
        for callback in callbacks:
            try:
                callback(self.error)
            except Exception as e:
                print(f"Error in error callback: {e}")
    
    def reset(self) -> 'DataNode':
        """Reset this node to its initial state."""
        with self._lock:
            self.state = NodeState.IDLE
            self.result = None
            self.error = None
        return self
    
    def is_ready(self) -> bool:
        """Check if this node is ready to execute."""
        return all(dep.state == NodeState.COMPLETED for dep in self.dependencies)
    
    def get_dependency_results(self) -> Dict[str, Any]:
        """Get the results of all dependencies."""
        return {dep.name: dep.result for dep in self.dependencies if dep.state == NodeState.COMPLETED}
    
    def execute(self) -> None:
        """Execute this node."""
        raise NotImplementedError("Subclasses must implement execute")

class FunctionNode(DataNode[T]):
    """A node that executes a function."""
    
    def __init__(self, fn: Callable[..., T], name: str = None):
        super().__init__(name)
        self.fn = fn
    
    def execute(self) -> None:
        """Execute the function."""
        with self._lock:
            if self.state == NodeState.RUNNING:
                return
            self.state = NodeState.RUNNING
        
        try:
            # Get dependency results
            dep_results = self.get_dependency_results()
            
            # Execute the function
            self.result = self.fn(**dep_results)
            
            # Update state
            with self._lock:
                self.state = NodeState.COMPLETED
            
            # Notify callbacks
            self._notify_complete()
            
        except Exception as e:
            # Update state
            with self._lock:
                self.state = NodeState.FAILED
                self.error = e
            
            # Notify callbacks
            self._notify_error()
            
            # Re-raise the exception
            raise

class ConstantNode(DataNode[T]):
    """A node that provides a constant value."""
    
    def __init__(self, value: T, name: str = None):
        super().__init__(name)
        self.result = value
        self.state = NodeState.COMPLETED
    
    def execute(self) -> None:
        """Nothing to execute for a constant node."""
        pass

class DataflowGraph:
    """A dataflow graph that manages execution of nodes."""
    
    def __init__(self, max_workers: int = None):
        self.nodes: Set[DataNode] = set()
        self.max_workers = max_workers or min(32, (threading.cpu_count() or 1) * 2)
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self._lock = threading.RLock()
    
    def add_node(self, node: DataNode) -> DataNode:
        """Add a node to the graph."""
        with self._lock:
            self.nodes.add(node)
        return node
    
    def create_function(self, fn: Callable[..., T], name: str = None) -> FunctionNode[T]:
        """Create and add a function node."""
        node = FunctionNode(fn, name)
        return self.add_node(node)
    
    def create_constant(self, value: T, name: str = None) -> ConstantNode[T]:
        """Create and add a constant node."""
        node = ConstantNode(value, name)
        return self.add_node(node)
    
    def reset(self) -> 'DataflowGraph':
        """Reset all nodes in the graph."""
        with self._lock:
            for node in self.nodes:
                if node.state != NodeState.IDLE:
                    node.reset()
        return self
    
    def execute(self, target_nodes: Optional[List[DataNode]] = None) -> Dict[str, Any]:
        """
        Execute the graph, optionally targeting specific nodes.
        
        Returns:
            Dict[str, Any]: A dictionary mapping node names to their results.
        """
        # If no target nodes are specified, use all nodes without dependents
        if target_nodes is None:
            target_nodes = [node for node in self.nodes if not node.dependents]
        
        # Reset all nodes
        self.reset()
        
        # Create a queue of nodes to execute
        node_queue = queue.Queue()
        
        # Add all nodes with no dependencies to the queue
        for node in self.nodes:
            if not node.dependencies:
                node_queue.put(node)
        
        # Create a set to track completed nodes
        completed_nodes = set()
        failed_nodes = set()
        
        # Create a dictionary to store futures
        futures = {}
        
        # Execute nodes until all target nodes are completed or failed
        while not all(node in completed_nodes or node in failed_nodes for node in target_nodes):
            # Get the next node to execute
            try:
                node = node_queue.get(block=False)
            except queue.Empty:
                # Wait for some futures to complete
                if futures:
                    done, _ = concurrent.futures.wait(
                        futures.keys(),
                        return_when=concurrent.futures.FIRST_COMPLETED,
                        timeout=0.1
                    )
                    
                    # Process completed futures
                    for future in done:
                        node = futures.pop(future)
                        
                        # Add dependent nodes to the queue if they're ready
                        for dependent in node.dependents:
                            if dependent.is_ready() and dependent not in completed_nodes and dependent not in failed_nodes:
                                node_queue.put(dependent)
                else:
                    # No nodes to execute and no futures to wait for
                    break
                
                continue
            
            # Skip nodes that are already completed or failed
            if node in completed_nodes or node in failed_nodes:
                continue
            
            # Skip nodes that aren't ready
            if not node.is_ready():
                continue
            
            # Execute the node
            future = self._executor.submit(self._execute_node, node)
            futures[future] = node
        
        # Wait for all futures to complete
        if futures:
            concurrent.futures.wait(futures.keys())
        
        # Return the results of the target nodes
        return {node.name: node.result for node in target_nodes if node.state == NodeState.COMPLETED}
    
    def _execute_node(self, node: DataNode) -> None:
        """Execute a node and handle its completion."""
        try:
            node.execute()
            
            # Add the node to the completed set
            with self._lock:
                if node.state == NodeState.COMPLETED:
                    completed_nodes = {node}
                else:
                    failed_nodes = {node}
            
        except Exception as e:
            # Add the node to the failed set
            with self._lock:
                failed_nodes = {node}
            
            print(f"Error executing node {node.name}: {e}")

class Pipeline:
    """A pipeline of transformations that can be applied to data."""
    
    def __init__(self):
        self.transformations: List[Callable[[Any], Any]] = []
    
    def add(self, transformation: Callable[[Any], Any]) -> 'Pipeline':
        """Add a transformation to the pipeline."""
        self.transformations.append(transformation)
        return self
    
    def process(self, data: Any) -> Any:
        """Process data through the pipeline."""
        result = data
        for transformation in self.transformations:
            result = transformation(result)
        return result
    
    def compose(self, other: 'Pipeline') -> 'Pipeline':
        """Compose this pipeline with another pipeline."""
        result = Pipeline()
        result.transformations = list(self.transformations)
        result.transformations.extend(other.transformations)
        return result

def create_graph() -> DataflowGraph:
    """Create a new dataflow graph."""
    return DataflowGraph()

def create_pipeline() -> Pipeline:
    """Create a new pipeline."""
    return Pipeline()