"""
Market Analysis and Research System.
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
import numpy as np
from enum import Enum

class MarketSegment(str, Enum):
    """Market segment types."""
    ENTERPRISE = "enterprise"
    MID_MARKET = "mid_market"
    SMALL_BUSINESS = "small_business"
    STARTUP = "startup"

class CompetitorTier(str, Enum):
    """Competitor tier levels."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"

@dataclass
class MarketMetric:
    """Market analysis metric."""
    timestamp: datetime
    category: str
    metric_name: str
    value: float
    unit: str
    segment: Optional[MarketSegment]
    region: Optional[str]
    tags: Dict[str, str]

@dataclass
class Competitor:
    """Competitor analysis entry."""
    id: str
    name: str
    tier: CompetitorTier
    description: str
    strengths: List[str]
    weaknesses: List[str]
    market_share: float
    target_segments: List[MarketSegment]
    regions: List[str]
    products: List[Dict[str, Any]]
    pricing: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class MarketOpportunity:
    """Market opportunity analysis."""
    id: str
    title: str
    description: str
    segment: MarketSegment
    region: str
    potential_revenue: float
    market_size: int
    growth_rate: float
    competition_level: str
    entry_barriers: List[str]
    success_factors: List[str]
    risks: List[str]
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

class MarketAnalyzer:
    """Manages market analysis and research."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics: Dict[str, List[MarketMetric]] = {}
        self.competitors: Dict[str, Competitor] = {}
        self.opportunities: Dict[str, MarketOpportunity] = {}
        self.storage_path = "data/market_analysis"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "metrics",
            "competitors",
            "opportunities",
            "research",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load market analysis configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default market analysis configuration."""
        default_config = {
            "regions": [
                {
                    "id": "na",
                    "name": "North America",
                    "countries": ["US", "CA"]
                },
                {
                    "id": "eu",
                    "name": "Europe",
                    "countries": ["UK", "DE", "FR", "ES", "IT"]
                },
                {
                    "id": "apac",
                    "name": "Asia Pacific",
                    "countries": ["JP", "CN", "IN", "SG", "AU"]
                }
            ],
            "market_metrics": [
                {
                    "id": "market_size",
                    "name": "Market Size",
                    "unit": "USD",
                    "description": "Total addressable market size"
                },
                {
                    "id": "growth_rate",
                    "name": "Growth Rate",
                    "unit": "percent",
                    "description": "Year-over-year market growth"
                },
                {
                    "id": "penetration",
                    "name": "Market Penetration",
                    "unit": "percent",
                    "description": "Market penetration rate"
                }
            ],
            "competition_factors": [
                {
                    "id": "product",
                    "name": "Product Features",
                    "weight": 0.3
                },
                {
                    "id": "pricing",
                    "name": "Pricing Strategy",
                    "weight": 0.25
                },
                {
                    "id": "market_presence",
                    "name": "Market Presence",
                    "weight": 0.2
                },
                {
                    "id": "technology",
                    "name": "Technology Stack",
                    "weight": 0.15
                },
                {
                    "id": "support",
                    "name": "Customer Support",
                    "weight": 0.1
                }
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def track_market_metric(
        self,
        category: str,
        metric_name: str,
        value: float,
        unit: str,
        segment: Optional[MarketSegment] = None,
        region: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> MarketMetric:
        """Track market analysis metric."""
        metric = MarketMetric(
            timestamp=datetime.now(),
            category=category,
            metric_name=metric_name,
            value=value,
            unit=unit,
            segment=segment,
            region=region,
            tags=tags or {}
        )
        
        key = f"{category}_{metric_name}"
        if key not in self.metrics:
            self.metrics[key] = []
        
        self.metrics[key].append(metric)
        
        # Save metric
        self._save_metric(metric)
        
        self.logger.info(f"Market metric tracked: {category} - {metric_name}")
        return metric
    
    def _save_metric(self, metric: MarketMetric):
        """Save market metric to storage."""
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
                "segment": metric.segment,
                "region": metric.region,
                "tags": metric.tags
            }, f)
            f.write('\n')
    
    async def add_competitor(
        self,
        name: str,
        tier: CompetitorTier,
        description: str,
        strengths: List[str],
        weaknesses: List[str],
        market_share: float,
        target_segments: List[MarketSegment],
        regions: List[str],
        products: List[Dict[str, Any]],
        pricing: Dict[str, Any]
    ) -> Competitor:
        """Add competitor analysis."""
        competitor = Competitor(
            id=f"competitor-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            tier=tier,
            description=description,
            strengths=strengths,
            weaknesses=weaknesses,
            market_share=market_share,
            target_segments=target_segments,
            regions=regions,
            products=products,
            pricing=pricing,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.competitors[competitor.id] = competitor
        
        # Save competitor
        self._save_competitor(competitor)
        
        self.logger.info(f"Competitor added: {competitor.id}")
        return competitor
    
    def _save_competitor(self, competitor: Competitor):
        """Save competitor to storage."""
        competitor_path = os.path.join(
            self.storage_path,
            "competitors",
            f"{competitor.id}.json"
        )
        
        with open(competitor_path, 'w') as f:
            json.dump(vars(competitor), f, default=str)
    
    async def create_opportunity(
        self,
        title: str,
        description: str,
        segment: MarketSegment,
        region: str,
        potential_revenue: float,
        market_size: int,
        growth_rate: float,
        competition_level: str,
        entry_barriers: List[str],
        success_factors: List[str],
        risks: List[str]
    ) -> MarketOpportunity:
        """Create market opportunity."""
        # Calculate priority based on factors
        priority_score = (
            potential_revenue / market_size * 0.4 +
            growth_rate * 0.3 +
            (1 - len(entry_barriers) / 10) * 0.2 +
            (1 - len(risks) / 10) * 0.1
        )
        
        if priority_score >= 0.8:
            priority = "critical"
        elif priority_score >= 0.6:
            priority = "high"
        elif priority_score >= 0.4:
            priority = "medium"
        else:
            priority = "low"
        
        opportunity = MarketOpportunity(
            id=f"opportunity-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            description=description,
            segment=segment,
            region=region,
            potential_revenue=potential_revenue,
            market_size=market_size,
            growth_rate=growth_rate,
            competition_level=competition_level,
            entry_barriers=entry_barriers,
            success_factors=success_factors,
            risks=risks,
            priority=priority,
            status="identified",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.opportunities[opportunity.id] = opportunity
        
        # Save opportunity
        self._save_opportunity(opportunity)
        
        self.logger.info(f"Market opportunity created: {opportunity.id}")
        return opportunity
    
    def _save_opportunity(self, opportunity: MarketOpportunity):
        """Save market opportunity to storage."""
        opportunity_path = os.path.join(
            self.storage_path,
            "opportunities",
            f"{opportunity.id}.json"
        )
        
        with open(opportunity_path, 'w') as f:
            json.dump(vars(opportunity), f, default=str)
    
    def update_competitor(
        self,
        competitor_id: str,
        market_share: Optional[float] = None,
        tier: Optional[CompetitorTier] = None,
        products: Optional[List[Dict[str, Any]]] = None,
        pricing: Optional[Dict[str, Any]] = None
    ) -> Competitor:
        """Update competitor analysis."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor not found: {competitor_id}")
        
        competitor = self.competitors[competitor_id]
        
        if market_share is not None:
            competitor.market_share = market_share
        
        if tier:
            competitor.tier = tier
        
        if products:
            competitor.products = products
        
        if pricing:
            competitor.pricing = pricing
        
        competitor.updated_at = datetime.now()
        
        # Save updated competitor
        self._save_competitor(competitor)
        
        self.logger.info(f"Competitor updated: {competitor_id}")
        return competitor
    
    def update_opportunity(
        self,
        opportunity_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        potential_revenue: Optional[float] = None
    ) -> MarketOpportunity:
        """Update market opportunity."""
        if opportunity_id not in self.opportunities:
            raise ValueError(f"Opportunity not found: {opportunity_id}")
        
        opportunity = self.opportunities[opportunity_id]
        
        if status:
            opportunity.status = status
        
        if priority:
            opportunity.priority = priority
        
        if potential_revenue is not None:
            opportunity.potential_revenue = potential_revenue
        
        opportunity.updated_at = datetime.now()
        
        # Save updated opportunity
        self._save_opportunity(opportunity)
        
        self.logger.info(f"Opportunity updated: {opportunity_id}")
        return opportunity
    
    def get_market_stats(
        self,
        category: str,
        metric_name: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        segment: Optional[MarketSegment] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get market statistics for time period."""
        end_time = end_time or datetime.now()
        key = f"{category}_{metric_name}"
        
        if key not in self.metrics:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "trend": None
            }
        
        # Filter metrics
        metrics = [
            m for m in self.metrics[key]
            if start_time <= m.timestamp <= end_time
            and (not segment or m.segment == segment)
            and (not region or m.region == region)
        ]
        
        if not metrics:
            return {
                "count": 0,
                "min": None,
                "max": None,
                "avg": None,
                "trend": None
            }
        
        values = [m.value for m in metrics]
        
        # Calculate trend
        if len(values) >= 2:
            trend = (values[-1] - values[0]) / values[0] * 100
        else:
            trend = None
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "trend": trend
        }
    
    def get_competitor_analysis(
        self,
        segment: Optional[MarketSegment] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get competitor analysis."""
        competitors = self.competitors.values()
        
        if segment:
            competitors = [
                c for c in competitors
                if segment in c.target_segments
            ]
        
        if region:
            competitors = [
                c for c in competitors
                if region in c.regions
            ]
        
        if not competitors:
            return {
                "total": 0,
                "by_tier": {},
                "market_share": {},
                "top_competitors": []
            }
        
        return {
            "total": len(competitors),
            "by_tier": {
                tier.value: len([
                    c for c in competitors
                    if c.tier == tier
                ])
                for tier in CompetitorTier
            },
            "market_share": {
                c.name: c.market_share
                for c in sorted(
                    competitors,
                    key=lambda x: x.market_share,
                    reverse=True
                )[:5]
            },
            "top_competitors": [
                {
                    "id": c.id,
                    "name": c.name,
                    "tier": c.tier,
                    "market_share": c.market_share,
                    "strengths": c.strengths[:3]
                }
                for c in sorted(
                    competitors,
                    key=lambda x: x.market_share,
                    reverse=True
                )[:5]
            ]
        }
    
    def get_opportunity_analysis(
        self,
        segment: Optional[MarketSegment] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get opportunity analysis."""
        opportunities = self.opportunities.values()
        
        if segment:
            opportunities = [
                o for o in opportunities
                if o.segment == segment
            ]
        
        if region:
            opportunities = [
                o for o in opportunities
                if o.region == region
            ]
        
        if not opportunities:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "total_potential": 0
            }
        
        return {
            "total": len(opportunities),
            "by_status": {
                status: len([
                    o for o in opportunities
                    if o.status == status
                ])
                for status in {o.status for o in opportunities}
            },
            "by_priority": {
                priority: len([
                    o for o in opportunities
                    if o.priority == priority
                ])
                for priority in {o.priority for o in opportunities}
            },
            "total_potential": sum(
                o.potential_revenue
                for o in opportunities
            ),
            "top_opportunities": [
                {
                    "id": o.id,
                    "title": o.title,
                    "potential_revenue": o.potential_revenue,
                    "growth_rate": o.growth_rate,
                    "priority": o.priority
                }
                for o in sorted(
                    opportunities,
                    key=lambda x: x.potential_revenue,
                    reverse=True
                )[:5]
            ]
        }
    
    def get_status(self) -> Dict:
        """Get market analysis status."""
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        
        return {
            "metrics": {
                metric_key: self.get_market_stats(
                    *metric_key.split('_'),
                    start_time=month_ago,
                    end_time=now
                )
                for metric_key in self.metrics
            },
            "competitors": self.get_competitor_analysis(),
            "opportunities": self.get_opportunity_analysis(),
            "segments": {
                segment.value: {
                    "competitors": self.get_competitor_analysis(segment),
                    "opportunities": self.get_opportunity_analysis(segment)
                }
                for segment in MarketSegment
            },
            "recent_activity": {
                "metrics": len([
                    m for metrics in self.metrics.values()
                    for m in metrics
                    if (now - m.timestamp).days <= 7
                ]),
                "competitors": len([
                    c for c in self.competitors.values()
                    if (now - c.updated_at).days <= 7
                ]),
                "opportunities": len([
                    o for o in self.opportunities.values()
                    if (now - o.updated_at).days <= 7
                ])
            }
        }
