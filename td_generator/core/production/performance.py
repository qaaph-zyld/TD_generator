"""
Performance optimization system.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
import logging
import asyncio
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import psutil

@dataclass
class ResourceMetrics:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float

class CacheManager:
    """Manages caching system."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Any] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
        self.logger = logging.getLogger(__name__)
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache."""
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
    
    def clear(self):
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }

class ParallelProcessor:
    """Manages parallel processing."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or multiprocessing.cpu_count()
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = multiprocessing.Pool(processes=self.max_workers)
        self.logger = logging.getLogger(__name__)
    
    async def process_parallel(self,
                             func: Callable,
                             items: List[Any],
                             use_processes: bool = False) -> List[Any]:
        """Process items in parallel."""
        try:
            if use_processes:
                # Use process pool for CPU-intensive tasks
                results = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.process_pool.map(func, items)
                )
            else:
                # Use thread pool for I/O-bound tasks
                results = await asyncio.gather(*[
                    asyncio.get_event_loop().run_in_executor(
                        self.thread_pool,
                        func,
                        item
                    )
                    for item in items
                ])
            
            return list(results)
            
        except Exception as e:
            self.logger.error(f"Parallel processing failed: {str(e)}")
            raise
    
    def shutdown(self):
        """Shutdown processor."""
        self.thread_pool.shutdown()
        self.process_pool.close()
        self.process_pool.join()

class ResourceManager:
    """Manages system resources."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_metrics(self) -> ResourceMetrics:
        """Get current resource metrics."""
        try:
            return ResourceMetrics(
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                network_usage=self._get_network_usage()
            )
        except Exception as e:
            self.logger.error(f"Failed to get resource metrics: {str(e)}")
            raise
    
    def _get_network_usage(self) -> float:
        """Get network usage percentage."""
        net_io = psutil.net_io_counters()
        # Simple metric: bytes sent + received
        total_bytes = net_io.bytes_sent + net_io.bytes_recv
        # Convert to percentage (assuming 1Gbps network)
        max_bytes = 125000000  # 1Gbps in bytes/s
        return (total_bytes / max_bytes) * 100

class LoadBalancer:
    """Manages load balancing."""
    
    def __init__(self):
        self.workers: Dict[str, Dict] = {}
        self.resource_manager = ResourceManager()
        self.logger = logging.getLogger(__name__)
    
    def register_worker(self, worker_id: str, capacity: float):
        """Register new worker."""
        self.workers[worker_id] = {
            'capacity': capacity,
            'current_load': 0.0,
            'tasks': []
        }
    
    def remove_worker(self, worker_id: str):
        """Remove worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
    
    def get_best_worker(self) -> Optional[str]:
        """Get worker with lowest load."""
        if not self.workers:
            return None
        
        return min(
            self.workers.items(),
            key=lambda x: x[1]['current_load'] / x[1]['capacity']
        )[0]
    
    def update_worker_load(self, worker_id: str, load: float):
        """Update worker's current load."""
        if worker_id in self.workers:
            self.workers[worker_id]['current_load'] = load
    
    def get_system_load(self) -> Dict:
        """Get overall system load."""
        metrics = self.resource_manager.get_metrics()
        return {
            'cpu': metrics.cpu_usage,
            'memory': metrics.memory_usage,
            'disk': metrics.disk_usage,
            'network': metrics.network_usage,
            'workers': len(self.workers),
            'total_capacity': sum(w['capacity'] for w in self.workers.values()),
            'total_load': sum(w['current_load'] for w in self.workers.values())
        }

class PerformanceSystem:
    """Manages performance optimization system."""
    
    def __init__(self):
        self.cache = CacheManager()
        self.parallel = ParallelProcessor()
        self.resources = ResourceManager()
        self.load_balancer = LoadBalancer()
        self.logger = logging.getLogger(__name__)
    
    async def optimize_task(self, task_id: str, func: Callable, *args, **kwargs):
        """Optimize task execution."""
        # Check cache
        cache_key = f"{task_id}:{args}:{kwargs}"
        result = self.cache.get(cache_key)
        if result is not None:
            return result
        
        # Get best worker
        worker_id = self.load_balancer.get_best_worker()
        if not worker_id:
            self.logger.warning("No workers available")
            # Execute locally
            result = await func(*args, **kwargs)
        else:
            # Execute on worker
            try:
                # Update worker load
                metrics = self.resources.get_metrics()
                self.load_balancer.update_worker_load(
                    worker_id,
                    metrics.cpu_usage
                )
                
                # Execute task
                result = await func(*args, **kwargs)
                
            finally:
                # Update worker load
                metrics = self.resources.get_metrics()
                self.load_balancer.update_worker_load(
                    worker_id,
                    metrics.cpu_usage
                )
        
        # Cache result
        self.cache.set(cache_key, result)
        return result
    
    def get_performance_metrics(self) -> Dict:
        """Get performance metrics."""
        return {
            'cache': self.cache.get_stats(),
            'system': self.load_balancer.get_system_load()
        }
    
    def shutdown(self):
        """Shutdown performance system."""
        self.parallel.shutdown()
