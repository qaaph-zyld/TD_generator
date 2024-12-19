"""
Launch Preparation and Management System.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import os
from pathlib import Path
import yaml
import asyncio
import aiohttp

@dataclass
class LaunchTask:
    """Launch preparation task."""
    id: str
    name: str
    category: str
    description: str
    owner: str
    dependencies: List[str]
    checklist: List[Dict[str, bool]]
    status: str
    priority: str
    due_date: datetime
    created_at: datetime
    updated_at: datetime

@dataclass
class LaunchPhase:
    """Launch phase definition."""
    id: str
    name: str
    description: str
    tasks: List[str]
    dependencies: List[str]
    metrics: Dict[str, Any]
    status: str
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_at: datetime

@dataclass
class LaunchMetric:
    """Launch metric tracking."""
    id: str
    name: str
    category: str
    value: Any
    target: Any
    unit: str
    status: str
    timestamp: datetime

class LaunchManager:
    """Manages launch preparation and execution."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tasks: Dict[str, LaunchTask] = {}
        self.phases: Dict[str, LaunchPhase] = {}
        self.metrics: Dict[str, List[LaunchMetric]] = {}
        self.storage_path = "data/launch"
        self._initialize_storage()
        self._load_launch_plan()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "tasks",
            "phases",
            "metrics",
            "documentation",
            "training",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_launch_plan(self):
        """Load launch plan configuration."""
        plan_path = os.path.join(self.storage_path, "launch_plan.yaml")
        
        # Create default plan if none exists
        if not os.path.exists(plan_path):
            self._create_default_plan()
        
        # Load existing plan
        with open(plan_path, 'r') as f:
            plan_data = yaml.safe_load(f)
            
            # Load tasks
            for task_id, task_data in plan_data["tasks"].items():
                task = LaunchTask(
                    id=task_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    **task_data
                )
                self.tasks[task_id] = task
            
            # Load phases
            for phase_id, phase_data in plan_data["phases"].items():
                phase = LaunchPhase(
                    id=phase_id,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    **phase_data
                )
                self.phases[phase_id] = phase
    
    def _create_default_plan(self):
        """Create default launch plan."""
        default_plan = {
            "tasks": {
                "final_validation": {
                    "name": "Final System Validation",
                    "category": "validation",
                    "description": "Complete system-wide validation of all components",
                    "owner": "QA Team",
                    "dependencies": [],
                    "checklist": [
                        {"CRM Integration": False},
                        {"Demo Environment": False},
                        {"Sales Collateral": False},
                        {"Marketing System": False}
                    ],
                    "status": "pending",
                    "priority": "high",
                    "due_date": "2024-12-26T00:00:00Z"
                },
                "documentation": {
                    "name": "Documentation Review",
                    "category": "documentation",
                    "description": "Review and update all system documentation",
                    "owner": "Documentation Team",
                    "dependencies": ["final_validation"],
                    "checklist": [
                        {"User Guide": False},
                        {"API Documentation": False},
                        {"Deployment Guide": False},
                        {"Training Materials": False}
                    ],
                    "status": "pending",
                    "priority": "high",
                    "due_date": "2024-12-27T00:00:00Z"
                },
                "team_training": {
                    "name": "Team Training",
                    "category": "training",
                    "description": "Conduct training sessions for all teams",
                    "owner": "Training Team",
                    "dependencies": ["documentation"],
                    "checklist": [
                        {"Sales Team": False},
                        {"Support Team": False},
                        {"Marketing Team": False},
                        {"Development Team": False}
                    ],
                    "status": "pending",
                    "priority": "medium",
                    "due_date": "2024-12-28T00:00:00Z"
                },
                "launch_planning": {
                    "name": "Launch Planning",
                    "category": "planning",
                    "description": "Finalize launch strategy and timeline",
                    "owner": "Product Team",
                    "dependencies": ["team_training"],
                    "checklist": [
                        {"Marketing Plan": False},
                        {"Sales Strategy": False},
                        {"Support Plan": False},
                        {"Rollout Schedule": False}
                    ],
                    "status": "pending",
                    "priority": "high",
                    "due_date": "2024-12-29T00:00:00Z"
                }
            },
            "phases": {
                "preparation": {
                    "name": "Launch Preparation",
                    "description": "Prepare all components for launch",
                    "tasks": ["final_validation", "documentation"],
                    "dependencies": [],
                    "metrics": {
                        "completion_rate": 0,
                        "quality_score": 0
                    },
                    "status": "pending",
                    "start_date": "2024-12-26T00:00:00Z",
                    "end_date": "2024-12-27T00:00:00Z"
                },
                "readiness": {
                    "name": "Team Readiness",
                    "description": "Ensure team readiness for launch",
                    "tasks": ["team_training"],
                    "dependencies": ["preparation"],
                    "metrics": {
                        "training_completion": 0,
                        "team_confidence": 0
                    },
                    "status": "pending",
                    "start_date": "2024-12-28T00:00:00Z",
                    "end_date": "2024-12-28T00:00:00Z"
                },
                "execution": {
                    "name": "Launch Execution",
                    "description": "Execute launch plan",
                    "tasks": ["launch_planning"],
                    "dependencies": ["readiness"],
                    "metrics": {
                        "milestone_completion": 0,
                        "risk_score": 0
                    },
                    "status": "pending",
                    "start_date": "2024-12-29T00:00:00Z",
                    "end_date": "2024-12-29T00:00:00Z"
                }
            }
        }
        
        # Save launch plan
        plan_path = os.path.join(self.storage_path, "launch_plan.yaml")
        with open(plan_path, 'w') as f:
            yaml.dump(default_plan, f)
    
    def update_task(
        self,
        task_id: str,
        checklist: Optional[List[Dict[str, bool]]] = None,
        status: Optional[str] = None
    ) -> LaunchTask:
        """Update launch task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task not found: {task_id}")
        
        task = self.tasks[task_id]
        
        # Update fields
        if checklist is not None:
            task.checklist = checklist
        if status is not None:
            task.status = status
        
        # Update metadata
        task.updated_at = datetime.now()
        
        # Save task
        self._save_task(task)
        
        # Update phase metrics
        self._update_phase_metrics()
        
        self.logger.info(f"Updated task: {task_id}")
        return task
    
    def _save_task(self, task: LaunchTask):
        """Save task to storage."""
        task_path = os.path.join(
            self.storage_path,
            "tasks",
            f"{task.id}.json"
        )
        
        with open(task_path, 'w') as f:
            json.dump(vars(task), f, default=str)
    
    def _update_phase_metrics(self):
        """Update metrics for all phases."""
        for phase in self.phases.values():
            # Calculate completion rate
            total_items = sum(
                len(self.tasks[task_id].checklist)
                for task_id in phase.tasks
            )
            completed_items = sum(
                sum(1 for item in self.tasks[task_id].checklist
                    if list(item.values())[0])
                for task_id in phase.tasks
            )
            
            phase.metrics["completion_rate"] = (
                completed_items / total_items
                if total_items > 0 else 0
            )
            
            # Calculate quality score
            completed_tasks = len([
                task_id for task_id in phase.tasks
                if self.tasks[task_id].status == "completed"
            ])
            phase.metrics["quality_score"] = (
                completed_tasks / len(phase.tasks)
                if phase.tasks else 0
            )
            
            # Update phase
            phase.updated_at = datetime.now()
            self._save_phase(phase)
    
    def _save_phase(self, phase: LaunchPhase):
        """Save phase to storage."""
        phase_path = os.path.join(
            self.storage_path,
            "phases",
            f"{phase.id}.json"
        )
        
        with open(phase_path, 'w') as f:
            json.dump(vars(phase), f, default=str)
    
    def track_metric(
        self,
        name: str,
        category: str,
        value: Any,
        target: Any,
        unit: str
    ) -> LaunchMetric:
        """Track launch metric."""
        metric = LaunchMetric(
            id=f"metric-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            category=category,
            value=value,
            target=target,
            unit=unit,
            status="on_track" if value >= target else "at_risk",
            timestamp=datetime.now()
        )
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append(metric)
        
        # Save metric
        self._save_metric(metric)
        
        self.logger.info(f"Tracked metric: {metric.id}")
        return metric
    
    def _save_metric(self, metric: LaunchMetric):
        """Save metric to storage."""
        metric_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{metric.id}.json"
        )
        
        with open(metric_path, 'w') as f:
            json.dump(vars(metric), f, default=str)
    
    def get_phase_status(self, phase_id: str) -> Dict:
        """Get detailed phase status."""
        if phase_id not in self.phases:
            raise ValueError(f"Phase not found: {phase_id}")
        
        phase = self.phases[phase_id]
        
        return {
            "name": phase.name,
            "status": phase.status,
            "progress": {
                "tasks": {
                    task_id: {
                        "status": self.tasks[task_id].status,
                        "checklist_completion": sum(
                            1 for item in self.tasks[task_id].checklist
                            if list(item.values())[0]
                        ) / len(self.tasks[task_id].checklist)
                    }
                    for task_id in phase.tasks
                },
                "metrics": phase.metrics
            },
            "timeline": {
                "start": phase.start_date,
                "end": phase.end_date,
                "updated": phase.updated_at
            }
        }
    
    def get_status(self) -> Dict:
        """Get launch preparation status."""
        return {
            "tasks": {
                "total": len(self.tasks),
                "by_status": {
                    status: len([
                        t for t in self.tasks.values()
                        if t.status == status
                    ])
                    for status in {"pending", "in_progress", "completed"}
                },
                "by_priority": {
                    priority: len([
                        t for t in self.tasks.values()
                        if t.priority == priority
                    ])
                    for priority in {"high", "medium", "low"}
                }
            },
            "phases": {
                "total": len(self.phases),
                "by_status": {
                    status: len([
                        p for p in self.phases.values()
                        if p.status == status
                    ])
                    for status in {"pending", "in_progress", "completed"}
                },
                "metrics": {
                    phase_id: phase.metrics
                    for phase_id, phase in self.phases.items()
                }
            },
            "metrics": {
                name: {
                    "current": metrics[-1].value if metrics else None,
                    "target": metrics[-1].target if metrics else None,
                    "status": metrics[-1].status if metrics else None
                }
                for name, metrics in self.metrics.items()
            },
            "timeline": {
                "start": min(
                    phase.start_date
                    for phase in self.phases.values()
                ),
                "end": max(
                    phase.end_date
                    for phase in self.phases.values()
                )
            }
        }
