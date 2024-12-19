"""
Scalability system for distributed processing.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
import logging
import asyncio
import aiohttp
from datetime import datetime

@dataclass
class Node:
    id: str
    address: str
    status: str
    capacity: float
    load: float
    last_heartbeat: datetime

@dataclass
class Task:
    id: str
    type: str
    data: Dict
    node_id: Optional[str]
    status: str
    result: Optional[Any]
    created_at: datetime
    completed_at: Optional[datetime]

class ClusterManager:
    """Manages distributed processing cluster."""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.tasks: Dict[str, Task] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_node(self, node: Node):
        """Register new node in cluster."""
        self.nodes[node.id] = node
        self.logger.info(f"Registered node {node.id}")
    
    def remove_node(self, node_id: str):
        """Remove node from cluster."""
        if node_id in self.nodes:
            node = self.nodes.pop(node_id)
            self.logger.info(f"Removed node {node_id}")
            
            # Reassign tasks from removed node
            self._reassign_node_tasks(node_id)
    
    def update_node_status(self, node_id: str, status: str):
        """Update node status."""
        if node_id in self.nodes:
            self.nodes[node_id].status = status
            self.nodes[node_id].last_heartbeat = datetime.now()
    
    def get_available_nodes(self) -> List[Node]:
        """Get list of available nodes."""
        return [
            node for node in self.nodes.values()
            if node.status == 'active' and node.load < node.capacity
        ]
    
    def add_task(self, task: Task):
        """Add new task to cluster."""
        self.tasks[task.id] = task
        self.logger.info(f"Added task {task.id}")
        
        # Assign task to node
        if not task.node_id:
            self._assign_task(task.id)
    
    def update_task_status(self, task_id: str, status: str, result: Optional[Any] = None):
        """Update task status."""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            if result is not None:
                task.result = result
            if status in ['completed', 'failed']:
                task.completed_at = datetime.now()
    
    def _assign_task(self, task_id: str):
        """Assign task to available node."""
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        available_nodes = self.get_available_nodes()
        
        if available_nodes:
            # Assign to node with lowest load
            best_node = min(available_nodes, key=lambda n: n.load)
            task.node_id = best_node.id
            task.status = 'assigned'
            self.logger.info(f"Assigned task {task_id} to node {best_node.id}")
        else:
            self.logger.warning(f"No available nodes for task {task_id}")
    
    def _reassign_node_tasks(self, node_id: str):
        """Reassign tasks from failed node."""
        reassigned_tasks = [
            task_id for task_id, task in self.tasks.items()
            if task.node_id == node_id and task.status not in ['completed', 'failed']
        ]
        
        for task_id in reassigned_tasks:
            self.tasks[task_id].node_id = None
            self.tasks[task_id].status = 'pending'
            self._assign_task(task_id)

class DistributedProcessor:
    """Manages distributed task processing."""
    
    def __init__(self):
        self.cluster = ClusterManager()
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start distributed processor."""
        self.session = aiohttp.ClientSession()
        asyncio.create_task(self._monitor_nodes())
    
    async def stop(self):
        """Stop distributed processor."""
        if self.session:
            await self.session.close()
    
    async def process_task(self, task_type: str, data: Dict) -> Any:
        """Process task in distributed system."""
        task = Task(
            id=f"{task_type}_{datetime.now().timestamp()}",
            type=task_type,
            data=data,
            node_id=None,
            status='pending',
            result=None,
            created_at=datetime.now(),
            completed_at=None
        )
        
        self.cluster.add_task(task)
        
        # Wait for task completion
        while task.status not in ['completed', 'failed']:
            await asyncio.sleep(0.1)
        
        if task.status == 'failed':
            raise Exception(f"Task {task.id} failed: {task.result}")
        
        return task.result
    
    async def _monitor_nodes(self):
        """Monitor node health."""
        while True:
            try:
                current_time = datetime.now()
                
                # Check node heartbeats
                for node_id, node in list(self.cluster.nodes.items()):
                    if (current_time - node.last_heartbeat).total_seconds() > 30:
                        self.logger.warning(f"Node {node_id} heartbeat timeout")
                        self.cluster.remove_node(node_id)
                
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.error(f"Node monitoring error: {str(e)}")
                await asyncio.sleep(10)

class LoadDistributor:
    """Manages load distribution across nodes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_node_weights(self, nodes: List[Node]) -> Dict[str, float]:
        """Calculate weight for each node."""
        total_capacity = sum(node.capacity for node in nodes)
        if total_capacity == 0:
            return {node.id: 0 for node in nodes}
        
        return {
            node.id: node.capacity / total_capacity
            for node in nodes
        }
    
    def should_scale(self, nodes: List[Node], threshold: float = 0.8) -> bool:
        """Check if cluster should scale."""
        if not nodes:
            return True
        
        avg_load = sum(node.load for node in nodes) / len(nodes)
        return avg_load > threshold
    
    def get_optimal_distribution(self,
                               tasks: List[Task],
                               nodes: List[Node]) -> Dict[str, List[str]]:
        """Get optimal task distribution."""
        if not nodes:
            return {}
        
        weights = self.calculate_node_weights(nodes)
        distribution: Dict[str, List[str]] = {node.id: [] for node in nodes}
        
        # Distribute tasks based on node weights
        for task in tasks:
            if task.status != 'pending':
                continue
            
            # Find node with lowest relative load
            best_node = min(
                nodes,
                key=lambda n: len(distribution[n.id]) / weights[n.id]
                if weights[n.id] > 0 else float('inf')
            )
            
            distribution[best_node.id].append(task.id)
        
        return distribution

class ScalabilitySystem:
    """Manages scalability system."""
    
    def __init__(self):
        self.processor = DistributedProcessor()
        self.distributor = LoadDistributor()
        self.logger = logging.getLogger(__name__)
    
    async def start(self):
        """Start scalability system."""
        await self.processor.start()
    
    async def stop(self):
        """Stop scalability system."""
        await self.processor.stop()
    
    async def process_distributed(self, task_type: str, data: Dict) -> Any:
        """Process task in distributed system."""
        return await self.processor.process_task(task_type, data)
    
    def get_cluster_status(self) -> Dict:
        """Get cluster status."""
        nodes = list(self.processor.cluster.nodes.values())
        tasks = list(self.processor.cluster.tasks.values())
        
        return {
            'nodes': len(nodes),
            'active_nodes': len([n for n in nodes if n.status == 'active']),
            'total_tasks': len(tasks),
            'pending_tasks': len([t for t in tasks if t.status == 'pending']),
            'should_scale': self.distributor.should_scale(nodes)
        }
