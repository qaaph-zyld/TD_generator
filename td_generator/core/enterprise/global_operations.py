"""
Global Operations Management System for Enterprise Scale.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging
import json
import os
from pathlib import Path
import yaml
import asyncio
import statistics
from enum import Enum

class RegionCode(str, Enum):
    """Global region codes."""
    NA = "na"  # North America
    EU = "eu"  # Europe
    APAC = "apac"  # Asia Pacific
    LATAM = "latam"  # Latin America
    MEA = "mea"  # Middle East & Africa

class DataCenterTier(str, Enum):
    """Data center tier levels."""
    TIER_1 = "tier1"  # Basic
    TIER_2 = "tier2"  # Redundant Components
    TIER_3 = "tier3"  # Concurrent Maintainable
    TIER_4 = "tier4"  # Fault Tolerant

class LoadBalancerType(str, Enum):
    """Load balancer types."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONN = "least_connections"
    IP_HASH = "ip_hash"
    WEIGHTED = "weighted"
    DYNAMIC = "dynamic"

@dataclass
class DataCenter:
    """Data center definition."""
    id: str
    name: str
    region: RegionCode
    location: str
    tier: DataCenterTier
    capacity: Dict[str, float]  # Resource type to capacity
    utilization: Dict[str, float]  # Resource type to current usage
    status: str
    metrics: Dict[str, float]
    created_at: datetime
    updated_at: datetime

@dataclass
class LoadBalancer:
    """Load balancer definition."""
    id: str
    name: str
    type: LoadBalancerType
    region: RegionCode
    endpoints: List[str]
    health_checks: Dict[str, bool]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class DisasterRecovery:
    """Disaster recovery configuration."""
    id: str
    name: str
    primary_dc: str
    backup_dc: str
    rpo: int  # Recovery Point Objective (minutes)
    rto: int  # Recovery Time Objective (minutes)
    last_test: datetime
    test_result: Optional[bool]
    status: str
    created_at: datetime
    updated_at: datetime

class GlobalOperations:
    """Manages global operations and infrastructure."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_centers: Dict[str, DataCenter] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.dr_configs: Dict[str, DisasterRecovery] = {}
        self.storage_path = "data/enterprise/global_ops"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "data_centers",
            "load_balancers",
            "dr_configs",
            "metrics",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load global operations configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default global operations configuration."""
        default_config = {
            "regions": [
                {
                    "code": "na",
                    "name": "North America",
                    "primary_dc": "dc-na-1",
                    "backup_dc": "dc-na-2"
                },
                {
                    "code": "eu",
                    "name": "Europe",
                    "primary_dc": "dc-eu-1",
                    "backup_dc": "dc-eu-2"
                },
                {
                    "code": "apac",
                    "name": "Asia Pacific",
                    "primary_dc": "dc-ap-1",
                    "backup_dc": "dc-ap-2"
                }
            ],
            "load_balancing": {
                "health_check_interval": 60,
                "retry_count": 3,
                "timeout": 30
            },
            "disaster_recovery": {
                "default_rpo": 15,
                "default_rto": 60,
                "test_interval": 90
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_data_center(
        self,
        name: str,
        region: RegionCode,
        location: str,
        tier: DataCenterTier,
        capacity: Dict[str, float]
    ) -> DataCenter:
        """Create data center."""
        dc = DataCenter(
            id=f"dc-{region}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            region=region,
            location=location,
            tier=tier,
            capacity=capacity,
            utilization={k: 0.0 for k in capacity.keys()},
            status="initializing",
            metrics={},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.data_centers[dc.id] = dc
        
        # Save data center
        self._save_data_center(dc)
        
        self.logger.info(f"Data center created: {dc.id}")
        return dc
    
    def _save_data_center(self, dc: DataCenter):
        """Save data center to storage."""
        dc_path = os.path.join(
            self.storage_path,
            "data_centers",
            f"{dc.id}.json"
        )
        
        with open(dc_path, 'w') as f:
            json.dump(vars(dc), f, default=str)
    
    async def create_load_balancer(
        self,
        name: str,
        type: LoadBalancerType,
        region: RegionCode,
        endpoints: List[str]
    ) -> LoadBalancer:
        """Create load balancer."""
        lb = LoadBalancer(
            id=f"lb-{region}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            region=region,
            endpoints=endpoints,
            health_checks={endpoint: True for endpoint in endpoints},
            metrics={},
            status="initializing",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.load_balancers[lb.id] = lb
        
        # Save load balancer
        self._save_load_balancer(lb)
        
        self.logger.info(f"Load balancer created: {lb.id}")
        return lb
    
    def _save_load_balancer(self, lb: LoadBalancer):
        """Save load balancer to storage."""
        lb_path = os.path.join(
            self.storage_path,
            "load_balancers",
            f"{lb.id}.json"
        )
        
        with open(lb_path, 'w') as f:
            json.dump(vars(lb), f, default=str)
    
    async def create_dr_config(
        self,
        name: str,
        primary_dc: str,
        backup_dc: str,
        rpo: int,
        rto: int
    ) -> DisasterRecovery:
        """Create disaster recovery configuration."""
        dr = DisasterRecovery(
            id=f"dr-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            primary_dc=primary_dc,
            backup_dc=backup_dc,
            rpo=rpo,
            rto=rto,
            last_test=datetime.now(),
            test_result=None,
            status="configured",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.dr_configs[dr.id] = dr
        
        # Save DR config
        self._save_dr_config(dr)
        
        self.logger.info(f"DR config created: {dr.id}")
        return dr
    
    def _save_dr_config(self, dr: DisasterRecovery):
        """Save DR config to storage."""
        dr_path = os.path.join(
            self.storage_path,
            "dr_configs",
            f"{dr.id}.json"
        )
        
        with open(dr_path, 'w') as f:
            json.dump(vars(dr), f, default=str)
    
    def update_data_center(
        self,
        dc_id: str,
        utilization: Optional[Dict[str, float]] = None,
        status: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None
    ) -> DataCenter:
        """Update data center."""
        if dc_id not in self.data_centers:
            raise ValueError(f"Data center not found: {dc_id}")
        
        dc = self.data_centers[dc_id]
        
        if utilization:
            dc.utilization = utilization
        
        if status:
            dc.status = status
        
        if metrics:
            dc.metrics = metrics
        
        dc.updated_at = datetime.now()
        
        # Save updated data center
        self._save_data_center(dc)
        
        self.logger.info(f"Data center updated: {dc_id}")
        return dc
    
    def update_load_balancer(
        self,
        lb_id: str,
        health_checks: Optional[Dict[str, bool]] = None,
        metrics: Optional[Dict[str, float]] = None,
        status: Optional[str] = None
    ) -> LoadBalancer:
        """Update load balancer."""
        if lb_id not in self.load_balancers:
            raise ValueError(f"Load balancer not found: {lb_id}")
        
        lb = self.load_balancers[lb_id]
        
        if health_checks:
            lb.health_checks = health_checks
        
        if metrics:
            lb.metrics = metrics
        
        if status:
            lb.status = status
        
        lb.updated_at = datetime.now()
        
        # Save updated load balancer
        self._save_load_balancer(lb)
        
        self.logger.info(f"Load balancer updated: {lb_id}")
        return lb
    
    def update_dr_config(
        self,
        dr_id: str,
        test_result: Optional[bool] = None,
        status: Optional[str] = None
    ) -> DisasterRecovery:
        """Update DR config."""
        if dr_id not in self.dr_configs:
            raise ValueError(f"DR config not found: {dr_id}")
        
        dr = self.dr_configs[dr_id]
        
        if test_result is not None:
            dr.test_result = test_result
            dr.last_test = datetime.now()
        
        if status:
            dr.status = status
        
        dr.updated_at = datetime.now()
        
        # Save updated DR config
        self._save_dr_config(dr)
        
        self.logger.info(f"DR config updated: {dr_id}")
        return dr
    
    def get_dc_metrics(
        self,
        region: Optional[RegionCode] = None
    ) -> Dict[str, Any]:
        """Get data center metrics."""
        dcs = self.data_centers.values()
        
        if region:
            dcs = [dc for dc in dcs if dc.region == region]
        
        if not dcs:
            return {
                "total": 0,
                "by_region": {},
                "by_tier": {},
                "avg_utilization": {}
            }
        
        # Calculate average utilization by resource type
        resource_types = set()
        for dc in dcs:
            resource_types.update(dc.utilization.keys())
        
        avg_utilization = {}
        for resource in resource_types:
            values = [
                dc.utilization.get(resource, 0)
                for dc in dcs
                if resource in dc.utilization
            ]
            if values:
                avg_utilization[resource] = statistics.mean(values)
        
        return {
            "total": len(dcs),
            "by_region": {
                region: len([
                    dc for dc in dcs
                    if dc.region == region
                ])
                for region in {dc.region for dc in dcs}
            },
            "by_tier": {
                tier: len([
                    dc for dc in dcs
                    if dc.tier == tier
                ])
                for tier in {dc.tier for dc in dcs}
            },
            "avg_utilization": avg_utilization
        }
    
    def get_lb_metrics(
        self,
        region: Optional[RegionCode] = None
    ) -> Dict[str, Any]:
        """Get load balancer metrics."""
        lbs = self.load_balancers.values()
        
        if region:
            lbs = [lb for lb in lbs if lb.region == region]
        
        if not lbs:
            return {
                "total": 0,
                "by_region": {},
                "by_type": {},
                "health_status": {}
            }
        
        # Calculate health status
        total_endpoints = sum(
            len(lb.endpoints)
            for lb in lbs
        )
        healthy_endpoints = sum(
            sum(1 for healthy in lb.health_checks.values() if healthy)
            for lb in lbs
        )
        
        return {
            "total": len(lbs),
            "by_region": {
                region: len([
                    lb for lb in lbs
                    if lb.region == region
                ])
                for region in {lb.region for lb in lbs}
            },
            "by_type": {
                type: len([
                    lb for lb in lbs
                    if lb.type == type
                ])
                for type in {lb.type for lb in lbs}
            },
            "health_status": {
                "total_endpoints": total_endpoints,
                "healthy_endpoints": healthy_endpoints,
                "health_rate": (
                    healthy_endpoints / total_endpoints
                    if total_endpoints > 0
                    else 0
                )
            }
        }
    
    def get_dr_metrics(self) -> Dict[str, Any]:
        """Get disaster recovery metrics."""
        drs = self.dr_configs.values()
        
        if not drs:
            return {
                "total": 0,
                "avg_rpo": None,
                "avg_rto": None,
                "test_results": {}
            }
        
        # Calculate test results
        tested = [dr for dr in drs if dr.test_result is not None]
        
        return {
            "total": len(drs),
            "avg_rpo": statistics.mean(dr.rpo for dr in drs),
            "avg_rto": statistics.mean(dr.rto for dr in drs),
            "test_results": {
                "total_tested": len(tested),
                "successful": len([
                    dr for dr in tested
                    if dr.test_result
                ]),
                "failed": len([
                    dr for dr in tested
                    if not dr.test_result
                ])
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get global operations status."""
        return {
            "data_centers": self.get_dc_metrics(),
            "load_balancers": self.get_lb_metrics(),
            "disaster_recovery": self.get_dr_metrics(),
            "health_summary": {
                "dc_health": all(
                    dc.status == "operational"
                    for dc in self.data_centers.values()
                ),
                "lb_health": all(
                    lb.status == "operational"
                    for lb in self.load_balancers.values()
                ),
                "dr_health": all(
                    dr.status == "configured"
                    for dr in self.dr_configs.values()
                )
            }
        }
