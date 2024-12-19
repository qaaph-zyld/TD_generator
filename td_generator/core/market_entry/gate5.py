"""
Gate 5: Market Entry Implementation
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os

@dataclass
class MarketMetrics:
    """Market performance metrics."""
    customer_count: int
    mrr: float
    cac: float
    ltv: float
    churn_rate: float
    nps_score: float

@dataclass
class SalesTarget:
    """Sales target definition."""
    company_name: str
    industry: str
    size: str
    priority: int
    status: str
    last_contact: Optional[datetime]
    next_action: Optional[str]

class MarketEntryManager:
    """Manages Gate 5: Market Entry implementation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = MarketMetrics(
            customer_count=0,
            mrr=0.0,
            cac=0.0,
            ltv=0.0,
            churn_rate=0.0,
            nps_score=0.0
        )
        self.targets: Dict[str, SalesTarget] = {}
        self._load_targets()
    
    def _load_targets(self):
        """Load sales targets from file."""
        target_file = "data/sales_targets.json"
        if os.path.exists(target_file):
            with open(target_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    self.targets[item['company_name']] = SalesTarget(**item)
    
    def _save_targets(self):
        """Save sales targets to file."""
        target_file = "data/sales_targets.json"
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, 'w') as f:
            json.dump([vars(t) for t in self.targets.values()], f)

    def add_target(self, target: SalesTarget):
        """Add new sales target."""
        self.targets[target.company_name] = target
        self.logger.info(f"Added target: {target.company_name}")
        self._save_targets()
    
    def update_target(self, company_name: str, **kwargs):
        """Update sales target status."""
        if company_name not in self.targets:
            raise ValueError(f"Target not found: {company_name}")
        
        target = self.targets[company_name]
        for key, value in kwargs.items():
            if hasattr(target, key):
                setattr(target, key, value)
        
        self.logger.info(f"Updated target: {company_name}")
        self._save_targets()
    
    def get_priority_targets(self, count: int = 10) -> List[SalesTarget]:
        """Get top priority targets."""
        return sorted(
            self.targets.values(),
            key=lambda x: (x.priority, -len(x.status))
        )[:count]
    
    def update_metrics(self, **kwargs):
        """Update market metrics."""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)
        
        self.logger.info("Updated market metrics")
    
    def get_metrics(self) -> MarketMetrics:
        """Get current market metrics."""
        return self.metrics
    
    def generate_report(self) -> Dict:
        """Generate market entry progress report."""
        active_targets = len([t for t in self.targets.values() if t.status != 'closed'])
        conversion_rate = (
            self.metrics.customer_count / len(self.targets)
            if self.targets else 0
        )
        
        return {
            'metrics': vars(self.metrics),
            'targets': {
                'total': len(self.targets),
                'active': active_targets,
                'conversion_rate': conversion_rate
            },
            'priorities': [
                vars(t) for t in self.get_priority_targets()
            ]
        }

class SalesInfrastructureManager:
    """Manages sales infrastructure setup and maintenance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.components = {
            'crm': {'status': 'pending', 'details': {}},
            'demo': {'status': 'pending', 'details': {}},
            'collateral': {'status': 'pending', 'details': {}},
            'analytics': {'status': 'pending', 'details': {}}
        }
    
    def setup_crm(self, system: str, config: Dict):
        """Set up CRM system."""
        self.components['crm'] = {
            'status': 'active',
            'details': {
                'system': system,
                'config': config,
                'setup_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"CRM system set up: {system}")
    
    def setup_demo(self, environment: str, features: List[str]):
        """Set up demo environment."""
        self.components['demo'] = {
            'status': 'active',
            'details': {
                'environment': environment,
                'features': features,
                'setup_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"Demo environment set up: {environment}")
    
    def add_collateral(self, name: str, type: str, content: str):
        """Add sales collateral."""
        if 'items' not in self.components['collateral']['details']:
            self.components['collateral']['details']['items'] = []
        
        self.components['collateral']['details']['items'].append({
            'name': name,
            'type': type,
            'content': content,
            'created_at': datetime.now().isoformat()
        })
        
        self.components['collateral']['status'] = 'active'
        self.logger.info(f"Added sales collateral: {name}")
    
    def setup_analytics(self, platform: str, metrics: List[str]):
        """Set up sales analytics."""
        self.components['analytics'] = {
            'status': 'active',
            'details': {
                'platform': platform,
                'metrics': metrics,
                'setup_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"Analytics set up: {platform}")
    
    def get_status(self) -> Dict:
        """Get infrastructure status."""
        return {
            'components': self.components,
            'readiness': all(
                c['status'] == 'active'
                for c in self.components.values()
            )
        }

class MarketingFoundationManager:
    """Manages marketing foundation setup and operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.channels = {
            'website': {'status': 'pending', 'metrics': {}},
            'content': {'status': 'pending', 'metrics': {}},
            'social': {'status': 'pending', 'metrics': {}},
            'email': {'status': 'pending', 'metrics': {}}
        }
    
    def setup_website(self, domain: str, pages: List[str]):
        """Set up product website."""
        self.channels['website'] = {
            'status': 'active',
            'metrics': {
                'domain': domain,
                'pages': pages,
                'launch_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"Website set up: {domain}")
    
    def add_content(self, title: str, type: str, content: str):
        """Add marketing content."""
        if 'items' not in self.channels['content']['metrics']:
            self.channels['content']['metrics']['items'] = []
        
        self.channels['content']['metrics']['items'].append({
            'title': title,
            'type': type,
            'content': content,
            'created_at': datetime.now().isoformat()
        })
        
        self.channels['content']['status'] = 'active'
        self.logger.info(f"Added content: {title}")
    
    def setup_social(self, platforms: List[str]):
        """Set up social media presence."""
        self.channels['social'] = {
            'status': 'active',
            'metrics': {
                'platforms': platforms,
                'setup_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"Social media set up: {platforms}")
    
    def setup_email(self, platform: str, templates: List[str]):
        """Set up email marketing."""
        self.channels['email'] = {
            'status': 'active',
            'metrics': {
                'platform': platform,
                'templates': templates,
                'setup_date': datetime.now().isoformat()
            }
        }
        self.logger.info(f"Email marketing set up: {platform}")
    
    def get_status(self) -> Dict:
        """Get marketing status."""
        return {
            'channels': self.channels,
            'readiness': all(
                c['status'] == 'active'
                for c in self.channels.values()
            )
        }

class Gate5Manager:
    """Main manager for Gate 5: Market Entry."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market = MarketEntryManager()
        self.sales = SalesInfrastructureManager()
        self.marketing = MarketingFoundationManager()
    
    def initialize(self):
        """Initialize Gate 5 components."""
        self.logger.info("Initializing Gate 5: Market Entry")
        
        # Set up basic sales infrastructure
        self.sales.setup_crm(
            system="hubspot",
            config={
                "pipeline": "td_generator",
                "stages": ["lead", "contact", "demo", "trial", "negotiation", "closed"]
            }
        )
        
        # Set up demo environment
        self.sales.setup_demo(
            environment="cloud",
            features=[
                "documentation_generation",
                "multi_format_support",
                "collaboration",
                "version_control"
            ]
        )
        
        # Set up marketing channels
        self.marketing.setup_website(
            domain="tdgenerator.com",
            pages=["home", "features", "pricing", "docs", "blog"]
        )
        
        self.marketing.setup_social(
            platforms=["github", "linkedin", "twitter"]
        )
    
    def get_status(self) -> Dict:
        """Get comprehensive Gate 5 status."""
        return {
            'market_metrics': vars(self.market.get_metrics()),
            'sales_status': self.sales.get_status(),
            'marketing_status': self.marketing.get_status(),
            'readiness': all([
                self.sales.get_status()['readiness'],
                self.marketing.get_status()['readiness']
            ])
        }
