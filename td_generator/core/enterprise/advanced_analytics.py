"""
Advanced Analytics System for Enterprise Intelligence.
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
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd

class AnalyticsType(str, Enum):
    """Analytics types."""
    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    PREDICTIVE = "predictive"
    PRESCRIPTIVE = "prescriptive"

class MetricType(str, Enum):
    """Metric types."""
    USAGE = "usage"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    TECHNICAL = "technical"

class TimeFrame(str, Enum):
    """Time frames for analysis."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class AnalyticsConfig:
    """Analytics configuration."""
    id: str
    name: str
    type: AnalyticsType
    metrics: List[str]
    dimensions: List[str]
    filters: Dict[str, Any]
    aggregations: Dict[str, str]
    created_at: datetime
    updated_at: datetime

@dataclass
class MetricData:
    """Metric data point."""
    id: str
    metric: str
    type: MetricType
    value: float
    dimensions: Dict[str, str]
    timestamp: datetime
    source: str

@dataclass
class AnalyticsReport:
    """Analytics report."""
    id: str
    name: str
    type: AnalyticsType
    metrics: Dict[str, List[MetricData]]
    insights: List[Dict[str, Any]]
    predictions: Optional[Dict[str, Any]]
    created_at: datetime

class AdvancedAnalytics:
    """Manages advanced analytics and business intelligence."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analytics_configs: Dict[str, AnalyticsConfig] = {}
        self.metric_data: Dict[str, List[MetricData]] = {}
        self.reports: Dict[str, AnalyticsReport] = {}
        self.storage_path = "data/enterprise/analytics"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "configs",
            "metrics",
            "reports",
            "models",
            "insights"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load analytics configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default analytics configuration."""
        default_config = {
            "analytics_types": [
                {
                    "type": "descriptive",
                    "metrics": ["usage", "performance"]
                },
                {
                    "type": "diagnostic",
                    "metrics": ["errors", "latency"]
                },
                {
                    "type": "predictive",
                    "metrics": ["growth", "usage"]
                },
                {
                    "type": "prescriptive",
                    "metrics": ["optimization", "resource"]
                }
            ],
            "metric_types": [
                {
                    "type": "usage",
                    "dimensions": ["user", "feature"]
                },
                {
                    "type": "performance",
                    "dimensions": ["service", "region"]
                },
                {
                    "type": "business",
                    "dimensions": ["customer", "product"]
                },
                {
                    "type": "technical",
                    "dimensions": ["component", "resource"]
                }
            ],
            "time_frames": [
                {
                    "frame": "hourly",
                    "retention": "7days"
                },
                {
                    "frame": "daily",
                    "retention": "90days"
                },
                {
                    "frame": "weekly",
                    "retention": "1year"
                },
                {
                    "frame": "monthly",
                    "retention": "3years"
                }
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_analytics_config(
        self,
        name: str,
        type: AnalyticsType,
        metrics: List[str],
        dimensions: List[str],
        filters: Dict[str, Any],
        aggregations: Dict[str, str]
    ) -> AnalyticsConfig:
        """Create analytics configuration."""
        config = AnalyticsConfig(
            id=f"analytics-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            metrics=metrics,
            dimensions=dimensions,
            filters=filters,
            aggregations=aggregations,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.analytics_configs[config.id] = config
        
        # Save analytics config
        self._save_analytics_config(config)
        
        self.logger.info(f"Analytics config created: {config.id}")
        return config
    
    def _save_analytics_config(self, config: AnalyticsConfig):
        """Save analytics configuration to storage."""
        config_path = os.path.join(
            self.storage_path,
            "configs",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    async def record_metric(
        self,
        metric: str,
        type: MetricType,
        value: float,
        dimensions: Dict[str, str],
        source: str
    ) -> MetricData:
        """Record metric data point."""
        data = MetricData(
            id=f"metric-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            metric=metric,
            type=type,
            value=value,
            dimensions=dimensions,
            timestamp=datetime.now(),
            source=source
        )
        
        if metric not in self.metric_data:
            self.metric_data[metric] = []
        
        self.metric_data[metric].append(data)
        
        # Save metric data
        self._save_metric_data(data)
        
        self.logger.info(f"Metric recorded: {data.id}")
        return data
    
    def _save_metric_data(self, data: MetricData):
        """Save metric data to storage."""
        data_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{data.id}.json"
        )
        
        with open(data_path, 'w') as f:
            json.dump(vars(data), f, default=str)
    
    def generate_report(
        self,
        name: str,
        type: AnalyticsType,
        metrics: List[str],
        time_frame: TimeFrame,
        dimensions: Optional[List[str]] = None
    ) -> AnalyticsReport:
        """Generate analytics report."""
        report_metrics = {}
        insights = []
        predictions = None
        
        # Collect metric data
        for metric in metrics:
            if metric in self.metric_data:
                data = self.metric_data[metric]
                
                # Filter by time frame
                now = datetime.now()
                if time_frame == TimeFrame.HOURLY:
                    cutoff = now - timedelta(hours=24)
                elif time_frame == TimeFrame.DAILY:
                    cutoff = now - timedelta(days=30)
                elif time_frame == TimeFrame.WEEKLY:
                    cutoff = now - timedelta(weeks=12)
                elif time_frame == TimeFrame.MONTHLY:
                    cutoff = now - timedelta(days=365)
                else:
                    cutoff = now - timedelta(days=365*3)
                
                filtered_data = [
                    d for d in data
                    if d.timestamp >= cutoff
                ]
                
                report_metrics[metric] = filtered_data
                
                # Generate insights
                if filtered_data:
                    values = [d.value for d in filtered_data]
                    insights.append({
                        "metric": metric,
                        "avg": statistics.mean(values),
                        "min": min(values),
                        "max": max(values),
                        "std": statistics.stdev(values) if len(values) > 1 else 0
                    })
                
                # Generate predictions if needed
                if type == AnalyticsType.PREDICTIVE and len(filtered_data) > 10:
                    predictions = self._generate_predictions(filtered_data)
        
        report = AnalyticsReport(
            id=f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            metrics=report_metrics,
            insights=insights,
            predictions=predictions,
            created_at=datetime.now()
        )
        
        self.reports[report.id] = report
        
        # Save report
        self._save_report(report)
        
        self.logger.info(f"Report generated: {report.id}")
        return report
    
    def _save_report(self, report: AnalyticsReport):
        """Save report to storage."""
        report_path = os.path.join(
            self.storage_path,
            "reports",
            f"{report.id}.json"
        )
        
        with open(report_path, 'w') as f:
            json.dump(vars(report), f, default=str)
    
    def _generate_predictions(
        self,
        data: List[MetricData]
    ) -> Dict[str, Any]:
        """Generate predictions using linear regression."""
        # Prepare data
        df = pd.DataFrame([
            {
                'timestamp': (d.timestamp - datetime(1970, 1, 1)).total_seconds(),
                'value': d.value
            }
            for d in data
        ])
        
        X = df[['timestamp']].values
        y = df['value'].values
        
        # Train model
        model = LinearRegression()
        model.fit(X, y)
        
        # Make predictions
        future_timestamps = np.array([
            [
                (
                    data[-1].timestamp +
                    timedelta(days=i)
                ).timestamp()
            ]
            for i in range(1, 31)
        ])
        
        predictions = model.predict(future_timestamps)
        
        # Calculate error
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        
        return {
            "values": predictions.tolist(),
            "timestamps": [
                (
                    data[-1].timestamp +
                    timedelta(days=i)
                ).isoformat()
                for i in range(1, 31)
            ],
            "mse": mse,
            "confidence": 1.0 / (1.0 + mse)
        }
    
    def get_metrics_stats(
        self,
        type: Optional[MetricType] = None,
        time_frame: Optional[TimeFrame] = None
    ) -> Dict[str, Any]:
        """Get metrics statistics."""
        metrics = []
        for metric_list in self.metric_data.values():
            metrics.extend(metric_list)
        
        if type:
            metrics = [m for m in metrics if m.type == type]
        
        if time_frame:
            now = datetime.now()
            if time_frame == TimeFrame.HOURLY:
                cutoff = now - timedelta(hours=24)
            elif time_frame == TimeFrame.DAILY:
                cutoff = now - timedelta(days=30)
            elif time_frame == TimeFrame.WEEKLY:
                cutoff = now - timedelta(weeks=12)
            elif time_frame == TimeFrame.MONTHLY:
                cutoff = now - timedelta(days=365)
            else:
                cutoff = now - timedelta(days=365*3)
            
            metrics = [m for m in metrics if m.timestamp >= cutoff]
        
        if not metrics:
            return {
                "total": 0,
                "by_type": {},
                "by_source": {},
                "time_range": None
            }
        
        return {
            "total": len(metrics),
            "by_type": {
                type: len([
                    m for m in metrics
                    if m.type == type
                ])
                for type in {m.type for m in metrics}
            },
            "by_source": {
                source: len([
                    m for m in metrics
                    if m.source == source
                ])
                for source in {m.source for m in metrics}
            },
            "time_range": {
                "start": min(m.timestamp for m in metrics),
                "end": max(m.timestamp for m in metrics)
            }
        }
    
    def get_report_stats(
        self,
        type: Optional[AnalyticsType] = None
    ) -> Dict[str, Any]:
        """Get report statistics."""
        reports = self.reports.values()
        
        if type:
            reports = [r for r in reports if r.type == type]
        
        if not reports:
            return {
                "total": 0,
                "by_type": {},
                "metrics_coverage": {},
                "prediction_accuracy": None
            }
        
        # Calculate metrics coverage
        all_metrics = set()
        for report in reports:
            all_metrics.update(report.metrics.keys())
        
        metrics_coverage = {}
        for metric in all_metrics:
            metrics_coverage[metric] = len([
                r for r in reports
                if metric in r.metrics
            ])
        
        # Calculate prediction accuracy
        predictive_reports = [
            r for r in reports
            if r.type == AnalyticsType.PREDICTIVE and r.predictions
        ]
        
        if predictive_reports:
            avg_confidence = statistics.mean([
                r.predictions["confidence"]
                for r in predictive_reports
            ])
        else:
            avg_confidence = None
        
        return {
            "total": len(reports),
            "by_type": {
                type: len([
                    r for r in reports
                    if r.type == type
                ])
                for type in {r.type for r in reports}
            },
            "metrics_coverage": metrics_coverage,
            "prediction_accuracy": avg_confidence
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get advanced analytics status."""
        return {
            "metrics": self.get_metrics_stats(),
            "reports": self.get_report_stats(),
            "health_summary": {
                "data_health": bool(self.metric_data),
                "prediction_health": any(
                    r.type == AnalyticsType.PREDICTIVE
                    and r.predictions
                    and r.predictions["confidence"] > 0.8
                    for r in self.reports.values()
                ),
                "insight_health": any(
                    r.insights for r in self.reports.values()
                )
            }
        }
