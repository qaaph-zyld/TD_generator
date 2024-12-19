"""
Product Enhancement and Customization System.
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

class FeatureCategory(str, Enum):
    """Feature categories."""
    CORE = "core"
    INTEGRATION = "integration"
    AUTOMATION = "automation"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class IntegrationType(str, Enum):
    """Integration types."""
    API = "api"
    PLUGIN = "plugin"
    WEBHOOK = "webhook"
    DATABASE = "database"
    CUSTOM = "custom"

@dataclass
class EnhancedFeature:
    """Enhanced feature definition."""
    id: str
    name: str
    category: FeatureCategory
    description: str
    requirements: List[str]
    dependencies: List[str]
    target_segments: List[str]
    development_status: str
    technical_specs: Dict[str, Any]
    test_coverage: float
    performance_impact: Dict[str, float]
    created_at: datetime
    updated_at: datetime
    released_at: Optional[datetime]

@dataclass
class Integration:
    """Integration definition."""
    id: str
    name: str
    type: IntegrationType
    description: str
    provider: str
    api_version: str
    endpoints: List[Dict[str, Any]]
    auth_method: str
    rate_limits: Dict[str, Any]
    documentation: str
    status: str
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]

@dataclass
class CustomSolution:
    """Custom solution definition."""
    id: str
    name: str
    client: str
    description: str
    features: List[str]
    integrations: List[str]
    requirements: Dict[str, Any]
    deployment_config: Dict[str, Any]
    support_level: str
    status: str
    created_at: datetime
    updated_at: datetime
    deployed_at: Optional[datetime]

class ProductEnhancer:
    """Manages product enhancements and customizations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.features: Dict[str, EnhancedFeature] = {}
        self.integrations: Dict[str, Integration] = {}
        self.solutions: Dict[str, CustomSolution] = {}
        self.storage_path = "data/product_enhancement"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "features",
            "integrations",
            "solutions",
            "documentation",
            "testing"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load product enhancement configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default product enhancement configuration."""
        default_config = {
            "feature_categories": [
                {
                    "id": "core",
                    "name": "Core Features",
                    "priority": 1
                },
                {
                    "id": "integration",
                    "name": "Integration Features",
                    "priority": 2
                },
                {
                    "id": "automation",
                    "name": "Automation Features",
                    "priority": 3
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise Features",
                    "priority": 4
                },
                {
                    "id": "custom",
                    "name": "Custom Features",
                    "priority": 5
                }
            ],
            "integration_types": [
                {
                    "id": "api",
                    "name": "API Integration",
                    "auth_methods": ["oauth2", "api_key"]
                },
                {
                    "id": "plugin",
                    "name": "Plugin Integration",
                    "platforms": ["web", "desktop"]
                },
                {
                    "id": "webhook",
                    "name": "Webhook Integration",
                    "methods": ["push", "pull"]
                },
                {
                    "id": "database",
                    "name": "Database Integration",
                    "types": ["sql", "nosql"]
                }
            ],
            "development_standards": {
                "test_coverage": 0.8,
                "performance_thresholds": {
                    "latency": 200,
                    "throughput": 1000
                },
                "documentation": {
                    "required_sections": [
                        "overview",
                        "setup",
                        "usage",
                        "api"
                    ]
                }
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_feature(
        self,
        name: str,
        category: FeatureCategory,
        description: str,
        requirements: List[str],
        dependencies: List[str],
        target_segments: List[str],
        technical_specs: Dict[str, Any]
    ) -> EnhancedFeature:
        """Create enhanced feature."""
        feature = EnhancedFeature(
            id=f"feature-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            category=category,
            description=description,
            requirements=requirements,
            dependencies=dependencies,
            target_segments=target_segments,
            development_status="planned",
            technical_specs=technical_specs,
            test_coverage=0.0,
            performance_impact={
                "latency": 0.0,
                "throughput": 0.0,
                "memory": 0.0
            },
            created_at=datetime.now(),
            updated_at=datetime.now(),
            released_at=None
        )
        
        self.features[feature.id] = feature
        
        # Save feature
        self._save_feature(feature)
        
        self.logger.info(f"Enhanced feature created: {feature.id}")
        return feature
    
    def _save_feature(self, feature: EnhancedFeature):
        """Save enhanced feature to storage."""
        feature_path = os.path.join(
            self.storage_path,
            "features",
            f"{feature.id}.json"
        )
        
        with open(feature_path, 'w') as f:
            json.dump(vars(feature), f, default=str)
    
    async def create_integration(
        self,
        name: str,
        type: IntegrationType,
        description: str,
        provider: str,
        api_version: str,
        endpoints: List[Dict[str, Any]],
        auth_method: str,
        rate_limits: Dict[str, Any],
        documentation: str
    ) -> Integration:
        """Create integration."""
        integration = Integration(
            id=f"integration-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            description=description,
            provider=provider,
            api_version=api_version,
            endpoints=endpoints,
            auth_method=auth_method,
            rate_limits=rate_limits,
            documentation=documentation,
            status="development",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deployed_at=None
        )
        
        self.integrations[integration.id] = integration
        
        # Save integration
        self._save_integration(integration)
        
        self.logger.info(f"Integration created: {integration.id}")
        return integration
    
    def _save_integration(self, integration: Integration):
        """Save integration to storage."""
        integration_path = os.path.join(
            self.storage_path,
            "integrations",
            f"{integration.id}.json"
        )
        
        with open(integration_path, 'w') as f:
            json.dump(vars(integration), f, default=str)
    
    async def create_solution(
        self,
        name: str,
        client: str,
        description: str,
        features: List[str],
        integrations: List[str],
        requirements: Dict[str, Any],
        deployment_config: Dict[str, Any],
        support_level: str
    ) -> CustomSolution:
        """Create custom solution."""
        # Validate features and integrations
        for feature_id in features:
            if feature_id not in self.features:
                raise ValueError(f"Feature not found: {feature_id}")
        
        for integration_id in integrations:
            if integration_id not in self.integrations:
                raise ValueError(f"Integration not found: {integration_id}")
        
        solution = CustomSolution(
            id=f"solution-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            client=client,
            description=description,
            features=features,
            integrations=integrations,
            requirements=requirements,
            deployment_config=deployment_config,
            support_level=support_level,
            status="planning",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deployed_at=None
        )
        
        self.solutions[solution.id] = solution
        
        # Save solution
        self._save_solution(solution)
        
        self.logger.info(f"Custom solution created: {solution.id}")
        return solution
    
    def _save_solution(self, solution: CustomSolution):
        """Save custom solution to storage."""
        solution_path = os.path.join(
            self.storage_path,
            "solutions",
            f"{solution.id}.json"
        )
        
        with open(solution_path, 'w') as f:
            json.dump(vars(solution), f, default=str)
    
    def update_feature(
        self,
        feature_id: str,
        development_status: Optional[str] = None,
        test_coverage: Optional[float] = None,
        performance_impact: Optional[Dict[str, float]] = None
    ) -> EnhancedFeature:
        """Update enhanced feature."""
        if feature_id not in self.features:
            raise ValueError(f"Feature not found: {feature_id}")
        
        feature = self.features[feature_id]
        
        if development_status:
            feature.development_status = development_status
            if development_status == "released":
                feature.released_at = datetime.now()
        
        if test_coverage is not None:
            feature.test_coverage = test_coverage
        
        if performance_impact:
            feature.performance_impact.update(performance_impact)
        
        feature.updated_at = datetime.now()
        
        # Save updated feature
        self._save_feature(feature)
        
        self.logger.info(f"Feature updated: {feature_id}")
        return feature
    
    def update_integration(
        self,
        integration_id: str,
        status: Optional[str] = None,
        api_version: Optional[str] = None,
        endpoints: Optional[List[Dict[str, Any]]] = None
    ) -> Integration:
        """Update integration."""
        if integration_id not in self.integrations:
            raise ValueError(f"Integration not found: {integration_id}")
        
        integration = self.integrations[integration_id]
        
        if status:
            integration.status = status
            if status == "deployed":
                integration.deployed_at = datetime.now()
        
        if api_version:
            integration.api_version = api_version
        
        if endpoints:
            integration.endpoints = endpoints
        
        integration.updated_at = datetime.now()
        
        # Save updated integration
        self._save_integration(integration)
        
        self.logger.info(f"Integration updated: {integration_id}")
        return integration
    
    def update_solution(
        self,
        solution_id: str,
        status: Optional[str] = None,
        features: Optional[List[str]] = None,
        integrations: Optional[List[str]] = None
    ) -> CustomSolution:
        """Update custom solution."""
        if solution_id not in self.solutions:
            raise ValueError(f"Solution not found: {solution_id}")
        
        solution = self.solutions[solution_id]
        
        if status:
            solution.status = status
            if status == "deployed":
                solution.deployed_at = datetime.now()
        
        if features:
            # Validate features
            for feature_id in features:
                if feature_id not in self.features:
                    raise ValueError(f"Feature not found: {feature_id}")
            solution.features = features
        
        if integrations:
            # Validate integrations
            for integration_id in integrations:
                if integration_id not in self.integrations:
                    raise ValueError(f"Integration not found: {integration_id}")
            solution.integrations = integrations
        
        solution.updated_at = datetime.now()
        
        # Save updated solution
        self._save_solution(solution)
        
        self.logger.info(f"Solution updated: {solution_id}")
        return solution
    
    def get_feature_stats(
        self,
        category: Optional[FeatureCategory] = None
    ) -> Dict[str, Any]:
        """Get feature statistics."""
        features = self.features.values()
        
        if category:
            features = [
                f for f in features
                if f.category == category
            ]
        
        if not features:
            return {
                "total": 0,
                "by_status": {},
                "avg_coverage": None,
                "performance": {}
            }
        
        return {
            "total": len(features),
            "by_status": {
                status: len([
                    f for f in features
                    if f.development_status == status
                ])
                for status in {f.development_status for f in features}
            },
            "avg_coverage": statistics.mean([
                f.test_coverage for f in features
            ]),
            "performance": {
                metric: statistics.mean([
                    f.performance_impact[metric]
                    for f in features
                    if metric in f.performance_impact
                ])
                for metric in ["latency", "throughput", "memory"]
            }
        }
    
    def get_integration_stats(
        self,
        type: Optional[IntegrationType] = None
    ) -> Dict[str, Any]:
        """Get integration statistics."""
        integrations = self.integrations.values()
        
        if type:
            integrations = [
                i for i in integrations
                if i.type == type
            ]
        
        if not integrations:
            return {
                "total": 0,
                "by_status": {},
                "by_auth_method": {},
                "deployment_rate": None
            }
        
        deployed = [
            i for i in integrations
            if i.deployed_at
        ]
        
        return {
            "total": len(integrations),
            "by_status": {
                status: len([
                    i for i in integrations
                    if i.status == status
                ])
                for status in {i.status for i in integrations}
            },
            "by_auth_method": {
                method: len([
                    i for i in integrations
                    if i.auth_method == method
                ])
                for method in {i.auth_method for i in integrations}
            },
            "deployment_rate": len(deployed) / len(integrations) * 100
        }
    
    def get_solution_stats(
        self,
        support_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get solution statistics."""
        solutions = self.solutions.values()
        
        if support_level:
            solutions = [
                s for s in solutions
                if s.support_level == support_level
            ]
        
        if not solutions:
            return {
                "total": 0,
                "by_status": {},
                "avg_features": None,
                "avg_integrations": None
            }
        
        return {
            "total": len(solutions),
            "by_status": {
                status: len([
                    s for s in solutions
                    if s.status == status
                ])
                for status in {s.status for s in solutions}
            },
            "avg_features": statistics.mean([
                len(s.features) for s in solutions
            ]),
            "avg_integrations": statistics.mean([
                len(s.integrations) for s in solutions
            ])
        }
    
    def get_status(self) -> Dict:
        """Get product enhancement status."""
        return {
            "features": {
                category.value: self.get_feature_stats(category)
                for category in FeatureCategory
            },
            "integrations": {
                type.value: self.get_integration_stats(type)
                for type in IntegrationType
            },
            "solutions": self.get_solution_stats(),
            "development": {
                "features": len([
                    f for f in self.features.values()
                    if f.development_status == "development"
                ]),
                "integrations": len([
                    i for i in self.integrations.values()
                    if i.status == "development"
                ]),
                "solutions": len([
                    s for s in self.solutions.values()
                    if s.status == "development"
                ])
            }
        }
