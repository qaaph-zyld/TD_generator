"""
Performance Monitoring and Analytics System.
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
import aiohttp
import asyncio
import statistics

@dataclass
class MetricPoint:
    """Single metric measurement."""
    timestamp: datetime
    value: Union[int, float]
    unit: str
    tags: Dict[str, str]

@dataclass
class Metric:
    """Performance metric definition."""
    id: str
    name: str
    category: str
    description: str
    unit: str
    threshold: Optional[Dict[str, float]]
    data: List[MetricPoint]
    created_at: datetime
    updated_at: datetime

@dataclass
class Alert:
    """System alert definition."""
    id: str
    metric_id: str
    severity: str
    condition: str
    threshold: float
    current_value: float
    message: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

class MonitoringManager:
    """Manages system monitoring and analytics."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, Metric] = {}
        self.alerts: Dict[str, Alert] = {}
        self.storage_path = "data/monitoring"
        self.docker_client = docker.from_env()
        self._initialize_storage()
        self._load_metrics()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "metrics",
            "alerts",
            "analytics",
            "reports",
            "dashboards"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_metrics(self):
        """Load metric definitions."""
        metrics_path = os.path.join(self.storage_path, "metrics.yaml")
        
        # Create default metrics if none exist
        if not os.path.exists(metrics_path):
            self._create_default_metrics()
        
        # Load existing metrics
        with open(metrics_path, 'r') as f:
            metrics_data = yaml.safe_load(f)
            for metric_id, data in metrics_data.items():
                metric = Metric(
                    id=metric_id,
                    data=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    **data
                )
                self.metrics[metric_id] = metric
    
    def _create_default_metrics(self):
        """Create default monitoring metrics."""
        default_metrics = {
            "system_cpu": {
                "name": "CPU Usage",
                "category": "system",
                "description": "System CPU utilization",
                "unit": "percent",
                "threshold": {
                    "warning": 70,
                    "critical": 90
                }
            },
            "system_memory": {
                "name": "Memory Usage",
                "category": "system",
                "description": "System memory utilization",
                "unit": "percent",
                "threshold": {
                    "warning": 80,
                    "critical": 95
                }
            },
            "api_latency": {
                "name": "API Latency",
                "category": "performance",
                "description": "API endpoint response time",
                "unit": "milliseconds",
                "threshold": {
                    "warning": 500,
                    "critical": 1000
                }
            },
            "document_processing": {
                "name": "Document Processing Time",
                "category": "performance",
                "description": "Time to process a document",
                "unit": "seconds",
                "threshold": {
                    "warning": 30,
                    "critical": 60
                }
            },
            "active_users": {
                "name": "Active Users",
                "category": "usage",
                "description": "Number of active users",
                "unit": "count",
                "threshold": None
            },
            "error_rate": {
                "name": "Error Rate",
                "category": "reliability",
                "description": "System error rate",
                "unit": "percent",
                "threshold": {
                    "warning": 1,
                    "critical": 5
                }
            }
        }
        
        # Save metric definitions
        metrics_path = os.path.join(self.storage_path, "metrics.yaml")
        with open(metrics_path, 'w') as f:
            yaml.dump(default_metrics, f)
    
    async def collect_metrics(self):
        """Collect current system metrics."""
        timestamp = datetime.now()
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        await self.record_metric(
            "system_cpu",
            cpu_percent,
            tags={"type": "system"}
        )
        
        await self.record_metric(
            "system_memory",
            memory.percent,
            tags={"type": "system"}
        )
        
        # Container metrics
        try:
            containers = self.docker_client.containers.list()
            for container in containers:
                stats = container.stats(stream=False)
                
                # Calculate container CPU usage
                cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                           stats["precpu_stats"]["cpu_usage"]["total_usage"]
                system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                             stats["precpu_stats"]["system_cpu_usage"]
                cpu_usage = (cpu_delta / system_delta) * 100
                
                await self.record_metric(
                    "system_cpu",
                    cpu_usage,
                    tags={
                        "type": "container",
                        "container_id": container.id[:12]
                    }
                )
        
        except Exception as e:
            self.logger.error(f"Failed to collect container metrics: {str(e)}")
    
    async def record_metric(
        self,
        metric_id: str,
        value: Union[int, float],
        tags: Optional[Dict[str, str]] = None
    ):
        """Record metric measurement."""
        if metric_id not in self.metrics:
            raise ValueError(f"Metric not found: {metric_id}")
        
        metric = self.metrics[metric_id]
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            unit=metric.unit,
            tags=tags or {}
        )
        
        metric.data.append(point)
        metric.updated_at = datetime.now()
        
        # Check thresholds and create alerts
        if metric.threshold:
            await self._check_thresholds(metric, point)
        
        # Save metric data
        self._save_metric_point(metric, point)
    
    async def _check_thresholds(self, metric: Metric, point: MetricPoint):
        """Check metric thresholds and create alerts."""
        if "critical" in metric.threshold and point.value >= metric.threshold["critical"]:
            await self.create_alert(
                metric_id=metric.id,
                severity="critical",
                condition=f">= {metric.threshold['critical']}",
                current_value=point.value,
                message=f"{metric.name} exceeded critical threshold"
            )
        
        elif "warning" in metric.threshold and point.value >= metric.threshold["warning"]:
            await self.create_alert(
                metric_id=metric.id,
                severity="warning",
                condition=f">= {metric.threshold['warning']}",
                current_value=point.value,
                message=f"{metric.name} exceeded warning threshold"
            )
    
    def _save_metric_point(self, metric: Metric, point: MetricPoint):
        """Save metric point to storage."""
        point_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{metric.id}-{point.timestamp.strftime('%Y%m%d')}.json"
        )
        
        # Append to daily file
        with open(point_path, 'a') as f:
            json.dump({
                "timestamp": point.timestamp.isoformat(),
                "value": point.value,
                "unit": point.unit,
                "tags": point.tags
            }, f)
            f.write('\n')
    
    async def create_alert(
        self,
        metric_id: str,
        severity: str,
        condition: str,
        current_value: float,
        message: str
    ) -> Alert:
        """Create system alert."""
        alert = Alert(
            id=f"alert-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            metric_id=metric_id,
            severity=severity,
            condition=condition,
            threshold=self.metrics[metric_id].threshold[severity],
            current_value=current_value,
            message=message,
            status="active",
            created_at=datetime.now(),
            resolved_at=None
        )
        
        self.alerts[alert.id] = alert
        
        # Save alert
        self._save_alert(alert)
        
        self.logger.warning(f"Alert created: {alert.id} - {message}")
        return alert
    
    def _save_alert(self, alert: Alert):
        """Save alert to storage."""
        alert_path = os.path.join(
            self.storage_path,
            "alerts",
            f"{alert.id}.json"
        )
        
        with open(alert_path, 'w') as f:
            json.dump(vars(alert), f, default=str)
    
    def resolve_alert(self, alert_id: str):
        """Resolve active alert."""
        if alert_id not in self.alerts:
            raise ValueError(f"Alert not found: {alert_id}")
        
        alert = self.alerts[alert_id]
        if alert.status == "resolved":
            return
        
        alert.status = "resolved"
        alert.resolved_at = datetime.now()
        
        # Save updated alert
        self._save_alert(alert)
        
        self.logger.info(f"Alert resolved: {alert_id}")
    
    def get_metric_stats(
        self,
        metric_id: str,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get metric statistics for time period."""
        if metric_id not in self.metrics:
            raise ValueError(f"Metric not found: {metric_id}")
        
        end_time = end_time or datetime.now()
        metric = self.metrics[metric_id]
        
        # Filter data points
        points = [
            p for p in metric.data
            if start_time <= p.timestamp <= end_time
        ]
        
        if not points:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "median": None
            }
        
        values = [p.value for p in points]
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values)
        }
    
    def get_active_alerts(
        self,
        severity: Optional[str] = None
    ) -> List[Alert]:
        """Get active system alerts."""
        alerts = [
            alert for alert in self.alerts.values()
            if alert.status == "active"
        ]
        
        if severity:
            alerts = [
                alert for alert in alerts
                if alert.severity == severity
            ]
        
        return sorted(
            alerts,
            key=lambda x: x.created_at,
            reverse=True
        )
    
    def get_status(self) -> Dict:
        """Get monitoring system status."""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        return {
            "metrics": {
                "total": len(self.metrics),
                "by_category": {
                    category: len([
                        m for m in self.metrics.values()
                        if m.category == category
                    ])
                    for category in {
                        m.category for m in self.metrics.values()
                    }
                },
                "last_hour": {
                    metric_id: self.get_metric_stats(
                        metric_id, hour_ago, now
                    )
                    for metric_id in self.metrics
                }
            },
            "alerts": {
                "total": len(self.alerts),
                "active": len([
                    a for a in self.alerts.values()
                    if a.status == "active"
                ]),
                "by_severity": {
                    severity: len([
                        a for a in self.alerts.values()
                        if a.severity == severity
                        and a.status == "active"
                    ])
                    for severity in {"warning", "critical"}
                }
            },
            "system": {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent
            }
        }
