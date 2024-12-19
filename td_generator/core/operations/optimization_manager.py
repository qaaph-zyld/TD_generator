"""
System Optimization and Resource Management.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path
import yaml
import psutil
import docker
import asyncio
import aiohttp
import statistics
import numpy as np
from concurrent.futures import ThreadPoolExecutor

@dataclass
class ResourceMetric:
    """Resource utilization metric."""
    timestamp: datetime
    resource_type: str
    metric_name: str
    value: float
    unit: str
    source: str
    tags: Dict[str, str]

@dataclass
class PerformanceTest:
    """Performance test definition."""
    id: str
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    baseline: Optional[Dict[str, float]]
    results: List[Dict[str, Any]]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class OptimizationTask:
    """System optimization task."""
    id: str
    category: str
    target: str
    description: str
    current_value: float
    target_value: float
    strategy: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class OptimizationManager:
    """Manages system optimization and performance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[ResourceMetric]] = {}
        self.tests: Dict[str, PerformanceTest] = {}
        self.tasks: Dict[str, OptimizationTask] = {}
        self.storage_path = "data/optimization"
        self.docker_client = docker.from_env()
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "metrics",
            "tests",
            "tasks",
            "reports",
            "baselines"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load optimization configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default optimization configuration."""
        default_config = {
            "resource_thresholds": {
                "cpu": {
                    "warning": 70,
                    "critical": 90
                },
                "memory": {
                    "warning": 80,
                    "critical": 95
                },
                "disk": {
                    "warning": 85,
                    "critical": 95
                }
            },
            "performance_targets": {
                "api_latency": {
                    "target": 200,
                    "unit": "ms"
                },
                "document_processing": {
                    "target": 15,
                    "unit": "seconds"
                },
                "concurrent_users": {
                    "target": 100,
                    "unit": "users"
                }
            },
            "optimization_strategies": {
                "resource_allocation": [
                    "scale_up",
                    "load_balancing",
                    "caching"
                ],
                "performance_tuning": [
                    "query_optimization",
                    "code_profiling",
                    "async_processing"
                ],
                "cost_management": [
                    "resource_scheduling",
                    "capacity_planning",
                    "usage_optimization"
                ]
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def collect_resource_metrics(self):
        """Collect current resource metrics."""
        timestamp = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = [
            ResourceMetric(
                timestamp=timestamp,
                resource_type="system",
                metric_name="cpu_usage",
                value=cpu_percent,
                unit="percent",
                source="host",
                tags={"type": "system"}
            ),
            ResourceMetric(
                timestamp=timestamp,
                resource_type="system",
                metric_name="memory_usage",
                value=memory.percent,
                unit="percent",
                source="host",
                tags={"type": "system"}
            ),
            ResourceMetric(
                timestamp=timestamp,
                resource_type="system",
                metric_name="disk_usage",
                value=disk.percent,
                unit="percent",
                source="host",
                tags={"type": "system"}
            )
        ]
        
        # Container metrics
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                stats = container.stats(stream=False)
                
                # Calculate container metrics
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                             stats["precpu_stats"]["system_cpu_usage"]
                cpu_usage = (cpu_delta / system_delta) * 100
                
                metrics.append(
                    ResourceMetric(
                        timestamp=timestamp,
                        resource_type="container",
                        metric_name="cpu_usage",
                        value=cpu_usage,
                        unit="percent",
                        source=container.id[:12],
                        tags={
                            "type": "container",
                            "name": container.name
                        }
                    )
                )
        
        except Exception as e:
            self.logger.error(f"Failed to collect container metrics: {str(e)}")
        
        # Store metrics
        for metric in metrics:
            key = f"{metric.resource_type}_{metric.metric_name}"
            if key not in self.metrics:
                self.metrics[key] = []
            self.metrics[key].append(metric)
            
            # Save metric
            self._save_metric(metric)
    
    def _save_metric(self, metric: ResourceMetric):
        """Save resource metric to storage."""
        metric_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{metric.resource_type}_{metric.metric_name}_{metric.timestamp.strftime('%Y%m%d')}.json"
        )
        
        with open(metric_path, 'a') as f:
            json.dump({
                "timestamp": metric.timestamp.isoformat(),
                "resource_type": metric.resource_type,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "source": metric.source,
                "tags": metric.tags
            }, f)
            f.write('\n')
    
    async def create_performance_test(
        self,
        name: str,
        category: str,
        description: str,
        parameters: Dict[str, Any]
    ) -> PerformanceTest:
        """Create performance test."""
        test = PerformanceTest(
            id=f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            category=category,
            description=description,
            parameters=parameters,
            baseline=None,
            results=[],
            status="created",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.tests[test.id] = test
        
        # Save test
        self._save_test(test)
        
        self.logger.info(f"Performance test created: {test.id}")
        return test
    
    def _save_test(self, test: PerformanceTest):
        """Save performance test to storage."""
        test_path = os.path.join(
            self.storage_path,
            "tests",
            f"{test.id}.json"
        )
        
        with open(test_path, 'w') as f:
            json.dump(vars(test), f, default=str)
    
    async def run_performance_test(
        self,
        test_id: str,
        iterations: int = 1
    ) -> Dict[str, Any]:
        """Run performance test."""
        if test_id not in self.tests:
            raise ValueError(f"Test not found: {test_id}")
        
        test = self.tests[test_id]
        test.status = "running"
        test.updated_at = datetime.now()
        
        results = []
        for i in range(iterations):
            # Simulate test execution
            await asyncio.sleep(1)
            
            # Record test results
            result = {
                "iteration": i + 1,
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "latency": np.random.normal(200, 20),
                    "throughput": np.random.normal(1000, 100),
                    "cpu_usage": np.random.normal(50, 5),
                    "memory_usage": np.random.normal(60, 5)
                }
            }
            results.append(result)
        
        # Update test
        test.results.extend(results)
        test.status = "completed"
        test.updated_at = datetime.now()
        
        # Save updated test
        self._save_test(test)
        
        # Calculate statistics
        latencies = [r["metrics"]["latency"] for r in results]
        throughputs = [r["metrics"]["throughput"] for r in results]
        
        stats = {
            "latency": {
                "min": min(latencies),
                "max": max(latencies),
                "avg": statistics.mean(latencies),
                "p95": np.percentile(latencies, 95)
            },
            "throughput": {
                "min": min(throughputs),
                "max": max(throughputs),
                "avg": statistics.mean(throughputs),
                "p95": np.percentile(throughputs, 95)
            }
        }
        
        self.logger.info(f"Performance test completed: {test_id}")
        return stats
    
    async def create_optimization_task(
        self,
        category: str,
        target: str,
        description: str,
        current_value: float,
        target_value: float,
        strategy: str
    ) -> OptimizationTask:
        """Create optimization task."""
        task = OptimizationTask(
            id=f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            category=category,
            target=target,
            description=description,
            current_value=current_value,
            target_value=target_value,
            strategy=strategy,
            status="pending",
            priority="medium",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            completed_at=None
        )
        
        self.tasks[task.id] = task
        
        # Save task
        self._save_task(task)
        
        self.logger.info(f"Optimization task created: {task.id}")
        return task
    
    def _save_task(self, task: OptimizationTask):
        """Save optimization task to storage."""
        task_path = os.path.join(
            self.storage_path,
            "tasks",
            f"{task.id}.json"
        )
        
        with open(task_path, 'w') as f:
            json.dump(vars(task), f, default=str)
    
    def update_task(
        self,
        task_id: str,
        status: Optional[str] = None,
        current_value: Optional[float] = None,
        priority: Optional[str] = None
    ) -> OptimizationTask:
        """Update optimization task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        if status:
            task.status = status
            if status == "completed":
                task.completed_at = datetime.now()
        
        if current_value is not None:
            task.current_value = current_value
        
        if priority:
            task.priority = priority
        
        task.updated_at = datetime.now()
        
        # Save updated task
        self._save_task(task)
        
        self.logger.info(f"Task updated: {task_id}")
        return task
    
    def get_resource_stats(
        self,
        resource_type: str,
        metric_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get resource statistics for time period."""
        end_time = end_time or datetime.now()
        key = f"{resource_type}_{metric_name}"
        
        if key not in self.metrics:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "p95": None
            }
        
        # Filter metrics
        metrics = [
            m for m in self.metrics[key]
            if start_time <= m.timestamp <= end_time
        ]
        
        if not metrics:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "p95": None
            }
        
        values = [m.value for m in metrics]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "p95": np.percentile(values, 95)
        }
    
    def get_optimization_progress(
        self,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get optimization progress."""
        tasks = self.tasks.values()
        if category:
            tasks = [t for t in tasks if t.category == category]
        
        if not tasks:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "improvement": None
            }
        
        # Calculate improvement
        completed = [
            t for t in tasks
            if t.status == "completed"
        ]
        
        if completed:
            initial_values = [t.current_value for t in completed]
            final_values = [t.target_value for t in completed]
            improvement = (
                sum(final_values) - sum(initial_values)
            ) / sum(initial_values) * 100
        else:
            improvement = None
        
        return {
            "total": len(tasks),
            "by_status": {
                status: len([
                    t for t in tasks
                    if t.status == status
                ])
                for status in {t.status for t in tasks}
            },
            "by_priority": {
                priority: len([
                    t for t in tasks
                    if t.priority == priority
                ])
                for priority in {t.priority for t in tasks}
            },
            "improvement": improvement
        }
    
    def get_status(self) -> Dict:
        """Get optimization system status."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        return {
            "resources": {
                "system": {
                    "cpu": self.get_resource_stats(
                        "system", "cpu_usage",
                        hour_ago, now
                    ),
                    "memory": self.get_resource_stats(
                        "system", "memory_usage",
                        hour_ago, now
                    ),
                    "disk": self.get_resource_stats(
                        "system", "disk_usage",
                        hour_ago, now
                    )
                },
                "containers": {
                    "cpu": self.get_resource_stats(
                        "container", "cpu_usage",
                        hour_ago, now
                    )
                }
            },
            "tests": {
                "total": len(self.tests),
                "by_status": {
                    status: len([
                        t for t in self.tests.values()
                        if t.status == status
                    ])
                    for status in {
                        t.status for t in self.tests.values()
                    }
                }
            },
            "optimization": {
                "tasks": self.get_optimization_progress(),
                "by_category": {
                    category: self.get_optimization_progress(category)
                    for category in {
                        t.category for t in self.tasks.values()
                    }
                }
            }
        }
