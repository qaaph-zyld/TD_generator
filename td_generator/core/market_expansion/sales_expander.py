"""
Sales Expansion and Partner Management System.
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

class PartnerType(str, Enum):
    """Partner types."""
    RESELLER = "reseller"
    INTEGRATOR = "integrator"
    CONSULTANT = "consultant"
    TECHNOLOGY = "technology"
    STRATEGIC = "strategic"

class MarketType(str, Enum):
    """Market types."""
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"

@dataclass
class Partner:
    """Partner definition."""
    id: str
    name: str
    type: PartnerType
    description: str
    regions: List[str]
    markets: List[MarketType]
    capabilities: List[str]
    certifications: List[str]
    tier: str
    status: str
    performance: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    activated_at: Optional[datetime]

@dataclass
class Market:
    """Market definition."""
    id: str
    name: str
    type: MarketType
    region: str
    description: str
    size: int
    growth_rate: float
    competition_level: str
    entry_barriers: List[str]
    requirements: List[str]
    partners: List[str]
    status: str
    created_at: datetime
    updated_at: datetime
    entered_at: Optional[datetime]

@dataclass
class SalesMetric:
    """Sales performance metric."""
    timestamp: datetime
    category: str
    metric_name: str
    value: float
    unit: str
    market: Optional[str]
    partner: Optional[str]
    tags: Dict[str, str]

class SalesExpander:
    """Manages sales expansion and partner relationships."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.partners: Dict[str, Partner] = {}
        self.markets: Dict[str, Market] = {}
        self.metrics: Dict[str, List[SalesMetric]] = {}
        self.storage_path = "data/sales_expansion"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "partners",
            "markets",
            "metrics",
            "contracts",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load sales expansion configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default sales expansion configuration."""
        default_config = {
            "partner_tiers": [
                {
                    "id": "platinum",
                    "name": "Platinum Partner",
                    "requirements": {
                        "revenue": 1000000,
                        "certifications": 5,
                        "customers": 50
                    }
                },
                {
                    "id": "gold",
                    "name": "Gold Partner",
                    "requirements": {
                        "revenue": 500000,
                        "certifications": 3,
                        "customers": 25
                    }
                },
                {
                    "id": "silver",
                    "name": "Silver Partner",
                    "requirements": {
                        "revenue": 100000,
                        "certifications": 1,
                        "customers": 10
                    }
                }
            ],
            "market_metrics": [
                {
                    "id": "revenue",
                    "name": "Revenue",
                    "unit": "USD"
                },
                {
                    "id": "customers",
                    "name": "Customers",
                    "unit": "count"
                },
                {
                    "id": "growth",
                    "name": "Growth Rate",
                    "unit": "percent"
                }
            ],
            "performance_thresholds": {
                "partner": {
                    "revenue_growth": 20,
                    "customer_satisfaction": 4.5,
                    "certification_completion": 90
                },
                "market": {
                    "market_share": 10,
                    "customer_acquisition": 100,
                    "revenue_target": 1000000
                }
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def add_partner(
        self,
        name: str,
        type: PartnerType,
        description: str,
        regions: List[str],
        markets: List[MarketType],
        capabilities: List[str],
        certifications: List[str]
    ) -> Partner:
        """Add partner."""
        # Calculate initial tier based on certifications
        if len(certifications) >= 5:
            tier = "platinum"
        elif len(certifications) >= 3:
            tier = "gold"
        else:
            tier = "silver"
        
        partner = Partner(
            id=f"partner-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            description=description,
            regions=regions,
            markets=markets,
            capabilities=capabilities,
            certifications=certifications,
            tier=tier,
            status="onboarding",
            performance={
                "revenue": 0.0,
                "satisfaction": 0.0,
                "certification": 0.0
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            activated_at=None
        )
        
        self.partners[partner.id] = partner
        
        # Save partner
        self._save_partner(partner)
        
        self.logger.info(f"Partner added: {partner.id}")
        return partner
    
    def _save_partner(self, partner: Partner):
        """Save partner to storage."""
        partner_path = os.path.join(
            self.storage_path,
            "partners",
            f"{partner.id}.json"
        )
        
        with open(partner_path, 'w') as f:
            json.dump(vars(partner), f, default=str)
    
    async def create_market(
        self,
        name: str,
        type: MarketType,
        region: str,
        description: str,
        size: int,
        growth_rate: float,
        competition_level: str,
        entry_barriers: List[str],
        requirements: List[str]
    ) -> Market:
        """Create market."""
        market = Market(
            id=f"market-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            region=region,
            description=description,
            size=size,
            growth_rate=growth_rate,
            competition_level=competition_level,
            entry_barriers=entry_barriers,
            requirements=requirements,
            partners=[],
            status="analysis",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            entered_at=None
        )
        
        self.markets[market.id] = market
        
        # Save market
        self._save_market(market)
        
        self.logger.info(f"Market created: {market.id}")
        return market
    
    def _save_market(self, market: Market):
        """Save market to storage."""
        market_path = os.path.join(
            self.storage_path,
            "markets",
            f"{market.id}.json"
        )
        
        with open(market_path, 'w') as f:
            json.dump(vars(market), f, default=str)
    
    async def track_sales_metric(
        self,
        category: str,
        metric_name: str,
        value: float,
        unit: str,
        market: Optional[str] = None,
        partner: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> SalesMetric:
        """Track sales metric."""
        metric = SalesMetric(
            timestamp=datetime.now(),
            category=category,
            metric_name=metric_name,
            value=value,
            unit=unit,
            market=market,
            partner=partner,
            tags=tags or {}
        )
        
        key = f"{category}_{metric_name}"
        if key not in self.metrics:
            self.metrics[key] = []
        
        self.metrics[key].append(metric)
        
        # Save metric
        self._save_metric(metric)
        
        self.logger.info(f"Sales metric tracked: {category} - {metric_name}")
        return metric
    
    def _save_metric(self, metric: SalesMetric):
        """Save sales metric to storage."""
        metric_path = os.path.join(
            self.storage_path,
            "metrics",
            f"{metric.category}_{metric.metric_name}_{metric.timestamp.strftime('%Y%m%d')}.json"
        )
        
        with open(metric_path, 'a') as f:
            json.dump({
                "timestamp": metric.timestamp.isoformat(),
                "category": metric.category,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "market": metric.market,
                "partner": metric.partner,
                "tags": metric.tags
            }, f)
            f.write('\n')
    
    def update_partner(
        self,
        partner_id: str,
        status: Optional[str] = None,
        tier: Optional[str] = None,
        performance: Optional[Dict[str, float]] = None
    ) -> Partner:
        """Update partner."""
        if partner_id not in self.partners:
            raise ValueError(f"Partner not found: {partner_id}")
        
        partner = self.partners[partner_id]
        
        if status:
            partner.status = status
            if status == "active" and not partner.activated_at:
                partner.activated_at = datetime.now()
        
        if tier:
            partner.tier = tier
        
        if performance:
            partner.performance.update(performance)
        
        partner.updated_at = datetime.now()
        
        # Save updated partner
        self._save_partner(partner)
        
        self.logger.info(f"Partner updated: {partner_id}")
        return partner
    
    def update_market(
        self,
        market_id: str,
        status: Optional[str] = None,
        partners: Optional[List[str]] = None,
        size: Optional[int] = None,
        growth_rate: Optional[float] = None
    ) -> Market:
        """Update market."""
        if market_id not in self.markets:
            raise ValueError(f"Market not found: {market_id}")
        
        market = self.markets[market_id]
        
        if status:
            market.status = status
            if status == "active" and not market.entered_at:
                market.entered_at = datetime.now()
        
        if partners:
            # Validate partners
            for partner_id in partners:
                if partner_id not in self.partners:
                    raise ValueError(f"Partner not found: {partner_id}")
            market.partners = partners
        
        if size is not None:
            market.size = size
        
        if growth_rate is not None:
            market.growth_rate = growth_rate
        
        market.updated_at = datetime.now()
        
        # Save updated market
        self._save_market(market)
        
        self.logger.info(f"Market updated: {market_id}")
        return market
    
    def get_partner_stats(
        self,
        type: Optional[PartnerType] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get partner statistics."""
        partners = self.partners.values()
        
        if type:
            partners = [
                p for p in partners
                if p.type == type
            ]
        
        if region:
            partners = [
                p for p in partners
                if region in p.regions
            ]
        
        if not partners:
            return {
                "total": 0,
                "by_tier": {},
                "by_status": {},
                "performance": {}
            }
        
        return {
            "total": len(partners),
            "by_tier": {
                tier: len([
                    p for p in partners
                    if p.tier == tier
                ])
                for tier in {p.tier for p in partners}
            },
            "by_status": {
                status: len([
                    p for p in partners
                    if p.status == status
                ])
                for status in {p.status for p in partners}
            },
            "performance": {
                metric: statistics.mean([
                    p.performance[metric]
                    for p in partners
                    if metric in p.performance
                ])
                for metric in ["revenue", "satisfaction", "certification"]
            }
        }
    
    def get_market_stats(
        self,
        type: Optional[MarketType] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get market statistics."""
        markets = self.markets.values()
        
        if type:
            markets = [
                m for m in markets
                if m.type == type
            ]
        
        if region:
            markets = [
                m for m in markets
                if m.region == region
            ]
        
        if not markets:
            return {
                "total": 0,
                "by_status": {},
                "total_size": 0,
                "avg_growth": None
            }
        
        return {
            "total": len(markets),
            "by_status": {
                status: len([
                    m for m in markets
                    if m.status == status
                ])
                for status in {m.status for m in markets}
            },
            "total_size": sum(m.size for m in markets),
            "avg_growth": statistics.mean([
                m.growth_rate for m in markets
            ])
        }
    
    def get_status(self) -> Dict:
        """Get sales expansion status."""
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        
        return {
            "partners": {
                type.value: self.get_partner_stats(type)
                for type in PartnerType
            },
            "markets": {
                type.value: self.get_market_stats(type)
                for type in MarketType
            },
            "metrics": {
                metric_key: {
                    "total": len(metrics),
                    "recent": len([
                        m for m in metrics
                        if (now - m.timestamp).days <= 30
                    ])
                }
                for metric_key, metrics in self.metrics.items()
            },
            "recent_activity": {
                "partners": len([
                    p for p in self.partners.values()
                    if (now - p.updated_at).days <= 7
                ]),
                "markets": len([
                    m for m in self.markets.values()
                    if (now - m.updated_at).days <= 7
                ])
            }
        }
