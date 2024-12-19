"""
Feature Enhancement and Release Management System.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path
import yaml
import asyncio
import statistics
from enum import Enum

class Priority(str, Enum):
    """Feature priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Status(str, Enum):
    """Feature status states."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    COMPLETED = "completed"
    RELEASED = "released"

@dataclass
class Feature:
    """Feature enhancement definition."""
    id: str
    title: str
    description: str
    category: str
    priority: Priority
    status: Status
    requester: str
    assignee: Optional[str]
    dependencies: List[str]
    estimated_effort: int
    business_value: int
    technical_complexity: int
    risk_level: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    released_at: Optional[datetime]

@dataclass
class Release:
    """Release version definition."""
    id: str
    version: str
    name: str
    description: str
    features: List[str]
    dependencies: List[str]
    status: str
    release_notes: str
    created_at: datetime
    updated_at: datetime
    released_at: Optional[datetime]

@dataclass
class ReleaseMetric:
    """Release performance metric."""
    timestamp: datetime
    release_id: str
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]

class EnhancementManager:
    """Manages feature enhancements and releases."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.features: Dict[str, Feature] = {}
        self.releases: Dict[str, Release] = {}
        self.metrics: Dict[str, List[ReleaseMetric]] = {}
        self.storage_path = "data/enhancement"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "features",
            "releases",
            "metrics",
            "documentation",
            "planning"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load enhancement configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default enhancement configuration."""
        default_config = {
            "feature_categories": [
                {
                    "id": "core",
                    "name": "Core Functionality",
                    "description": "Essential system features"
                },
                {
                    "id": "integration",
                    "name": "Integration",
                    "description": "External system integration"
                },
                {
                    "id": "automation",
                    "name": "Automation",
                    "description": "Process automation features"
                },
                {
                    "id": "ui",
                    "name": "User Interface",
                    "description": "UI/UX improvements"
                },
                {
                    "id": "performance",
                    "name": "Performance",
                    "description": "Performance enhancements"
                }
            ],
            "release_types": [
                {
                    "id": "major",
                    "name": "Major Release",
                    "description": "Significant new features"
                },
                {
                    "id": "minor",
                    "name": "Minor Release",
                    "description": "Minor features and improvements"
                },
                {
                    "id": "patch",
                    "name": "Patch Release",
                    "description": "Bug fixes and small updates"
                }
            ],
            "priority_weights": {
                "business_value": 0.4,
                "technical_complexity": 0.3,
                "risk_level": 0.3
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_feature(
        self,
        title: str,
        description: str,
        category: str,
        requester: str,
        estimated_effort: int,
        business_value: int,
        technical_complexity: int,
        risk_level: int,
        dependencies: Optional[List[str]] = None
    ) -> Feature:
        """Create feature enhancement."""
        # Calculate priority based on metrics
        priority_score = (
            business_value * 0.4 +
            (10 - technical_complexity) * 0.3 +
            (10 - risk_level) * 0.3
        )
        
        if priority_score >= 8:
            priority = Priority.CRITICAL
        elif priority_score >= 6:
            priority = Priority.HIGH
        elif priority_score >= 4:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW
        
        feature = Feature(
            id=f"feature-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            description=description,
            category=category,
            priority=priority,
            status=Status.PROPOSED,
            requester=requester,
            assignee=None,
            dependencies=dependencies or [],
            estimated_effort=estimated_effort,
            business_value=business_value,
            technical_complexity=technical_complexity,
            risk_level=risk_level,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            started_at=None,
            completed_at=None,
            released_at=None
        )
        
        self.features[feature.id] = feature
        
        # Save feature
        self._save_feature(feature)
        
        self.logger.info(f"Feature created: {feature.id}")
        return feature
    
    def _save_feature(self, feature: Feature):
        """Save feature to storage."""
        feature_path = os.path.join(
            self.storage_path,
            "features",
            f"{feature.id}.json"
        )
        
        with open(feature_path, 'w') as f:
            json.dump(vars(feature), f, default=str)
    
    async def create_release(
        self,
        version: str,
        name: str,
        description: str,
        features: List[str],
        dependencies: Optional[List[str]] = None
    ) -> Release:
        """Create release version."""
        # Validate features
        for feature_id in features:
            if feature_id not in self.features:
                raise ValueError(f"Feature not found: {feature_id}")
        
        release = Release(
            id=f"release-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            version=version,
            name=name,
            description=description,
            features=features,
            dependencies=dependencies or [],
            status="planned",
            release_notes="",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            released_at=None
        )
        
        self.releases[release.id] = release
        
        # Save release
        self._save_release(release)
        
        self.logger.info(f"Release created: {release.id}")
        return release
    
    def _save_release(self, release: Release):
        """Save release to storage."""
        release_path = os.path.join(
            self.storage_path,
            "releases",
            f"{release.id}.json"
        )
        
        with open(release_path, 'w') as f:
            json.dump(vars(release), f, default=str)
    
    def update_feature(
        self,
        feature_id: str,
        status: Optional[Status] = None,
        assignee: Optional[str] = None,
        priority: Optional[Priority] = None
    ) -> Feature:
        """Update feature status."""
        if feature_id not in self.features:
            raise ValueError(f"Feature not found: {feature_id}")
        
        feature = self.features[feature_id]
        
        if status:
            feature.status = status
            if status == Status.IN_PROGRESS and not feature.started_at:
                feature.started_at = datetime.now()
            elif status == Status.COMPLETED:
                feature.completed_at = datetime.now()
            elif status == Status.RELEASED:
                feature.released_at = datetime.now()
        
        if assignee:
            feature.assignee = assignee
        
        if priority:
            feature.priority = priority
        
        feature.updated_at = datetime.now()
        
        # Save updated feature
        self._save_feature(feature)
        
        self.logger.info(f"Feature updated: {feature_id}")
        return feature
    
    def update_release(
        self,
        release_id: str,
        status: Optional[str] = None,
        release_notes: Optional[str] = None
    ) -> Release:
        """Update release status."""
        if release_id not in self.releases:
            raise ValueError(f"Release not found: {release_id}")
        
        release = self.releases[release_id]
        
        if status:
            release.status = status
            if status == "released":
                release.released_at = datetime.now()
                
                # Update feature statuses
                for feature_id in release.features:
                    self.update_feature(
                        feature_id,
                        status=Status.RELEASED
                    )
        
        if release_notes:
            release.release_notes = release_notes
        
        release.updated_at = datetime.now()
        
        # Save updated release
        self._save_release(release)
        
        self.logger.info(f"Release updated: {release_id}")
        return release
    
    def track_release_metric(
        self,
        release_id: str,
        metric_name: str,
        value: float,
        unit: str,
        tags: Optional[Dict[str, str]] = None
    ) -> ReleaseMetric:
        """Track release metric."""
        if release_id not in self.releases:
            raise ValueError(f"Release not found: {release_id}")
        
        metric = ReleaseMetric(
            timestamp=datetime.now(),
            release_id=release_id,
            metric_name=metric_name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append(metric)
        
        # Save metric
        self._save_metric(metric)
        
        self.logger.info(f"Release metric tracked: {release_id} - {metric_name}")
        return metric
    
    def _save_metric(self, metric: ReleaseMetric):
        """Save release metric to storage."""
        metric_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{metric.release_id}_{metric.metric_name}_{metric.timestamp.strftime('%Y%m%d')}.json"
        )
        
        with open(metric_path, 'a') as f:
            json.dump({
                "timestamp": metric.timestamp.isoformat(),
                "release_id": metric.release_id,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "tags": metric.tags
            }, f)
            f.write('\n')
    
    def get_feature_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get feature statistics."""
        end_time = end_time or datetime.now()
        
        # Filter features
        features = [
            f for f in self.features.values()
            if start_time <= f.created_at <= end_time
        ]
        
        if not features:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "by_category": {}
            }
        
        return {
            "total": len(features),
            "by_status": {
                status.value: len([
                    f for f in features
                    if f.status == status
                ])
                for status in Status
            },
            "by_priority": {
                priority.value: len([
                    f for f in features
                    if f.priority == priority
                ])
                for priority in Priority
            },
            "by_category": {
                category: len([
                    f for f in features
                    if f.category == category
                ])
                for category in {f.category for f in features}
            }
        }
    
    def get_release_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get release statistics."""
        end_time = end_time or datetime.now()
        
        # Filter releases
        releases = [
            r for r in self.releases.values()
            if start_time <= r.created_at <= end_time
        ]
        
        if not releases:
            return {
                "total": 0,
                "by_status": {},
                "features_per_release": None,
                "avg_development_time": None
            }
        
        # Calculate development time for completed releases
        completed = [
            r for r in releases
            if r.released_at
        ]
        
        if completed:
            dev_times = [
                (r.released_at - r.created_at).days
                for r in completed
            ]
            avg_dev_time = statistics.mean(dev_times)
        else:
            avg_dev_time = None
        
        return {
            "total": len(releases),
            "by_status": {
                status: len([
                    r for r in releases
                    if r.status == status
                ])
                for status in {r.status for r in releases}
            },
            "features_per_release": statistics.mean([
                len(r.features) for r in releases
            ]),
            "avg_development_time": avg_dev_time
        }
    
    def get_status(self) -> Dict:
        """Get enhancement system status."""
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        
        return {
            "features": self.get_feature_stats(month_ago, now),
            "releases": self.get_release_stats(month_ago, now),
            "current_release": next(
                (r for r in self.releases.values()
                 if r.status == "in_progress"),
                None
            ),
            "upcoming_releases": [
                r for r in self.releases.values()
                if r.status == "planned"
            ][:3],
            "recent_activity": {
                "features": len([
                    f for f in self.features.values()
                    if (now - f.updated_at).days <= 7
                ]),
                "releases": len([
                    r for r in self.releases.values()
                    if (now - r.updated_at).days <= 7
                ])
            }
        }
