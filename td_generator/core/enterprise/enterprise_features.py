"""
Enterprise Features Management System.
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
import hashlib
import uuid

class SecurityLevel(str, Enum):
    """Security levels."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"

class ComplianceType(str, Enum):
    """Compliance types."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    PCI = "pci"

class WorkflowType(str, Enum):
    """Workflow types."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    CUSTOM = "custom"

@dataclass
class SecurityConfig:
    """Security configuration."""
    id: str
    name: str
    level: SecurityLevel
    features: Dict[str, bool]
    encryption: Dict[str, str]
    access_controls: Dict[str, List[str]]
    audit_logs: bool
    created_at: datetime
    updated_at: datetime

@dataclass
class WorkflowConfig:
    """Workflow configuration."""
    id: str
    name: str
    type: WorkflowType
    steps: List[Dict[str, Any]]
    conditions: Dict[str, Any]
    triggers: List[str]
    actions: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class ComplianceConfig:
    """Compliance configuration."""
    id: str
    name: str
    type: ComplianceType
    requirements: List[str]
    controls: Dict[str, Any]
    status: str
    audit_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class EnterpriseFeatures:
    """Manages enterprise features and configurations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_configs: Dict[str, SecurityConfig] = {}
        self.workflow_configs: Dict[str, WorkflowConfig] = {}
        self.compliance_configs: Dict[str, ComplianceConfig] = {}
        self.storage_path = "data/enterprise/features"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "security",
            "workflows",
            "compliance",
            "audit_logs",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load enterprise features configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default enterprise features configuration."""
        default_config = {
            "security_levels": [
                {
                    "level": "basic",
                    "features": {
                        "encryption": True,
                        "access_control": True,
                        "audit_logs": False
                    }
                },
                {
                    "level": "enhanced",
                    "features": {
                        "encryption": True,
                        "access_control": True,
                        "audit_logs": True
                    }
                },
                {
                    "level": "advanced",
                    "features": {
                        "encryption": True,
                        "access_control": True,
                        "audit_logs": True,
                        "mfa": True
                    }
                },
                {
                    "level": "enterprise",
                    "features": {
                        "encryption": True,
                        "access_control": True,
                        "audit_logs": True,
                        "mfa": True,
                        "sso": True
                    }
                }
            ],
            "workflow_types": [
                {
                    "type": "sequential",
                    "features": ["ordering", "dependencies"]
                },
                {
                    "type": "parallel",
                    "features": ["concurrent", "sync"]
                },
                {
                    "type": "conditional",
                    "features": ["rules", "branching"]
                },
                {
                    "type": "custom",
                    "features": ["templates", "actions"]
                }
            ],
            "compliance_types": [
                {
                    "type": "gdpr",
                    "features": ["data_protection", "consent"]
                },
                {
                    "type": "hipaa",
                    "features": ["health_data", "privacy"]
                },
                {
                    "type": "soc2",
                    "features": ["security", "availability"]
                },
                {
                    "type": "iso27001",
                    "features": ["risk", "controls"]
                },
                {
                    "type": "pci",
                    "features": ["payment", "security"]
                }
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_security_config(
        self,
        name: str,
        level: SecurityLevel,
        features: Dict[str, bool],
        encryption: Dict[str, str],
        access_controls: Dict[str, List[str]]
    ) -> SecurityConfig:
        """Create security configuration."""
        config = SecurityConfig(
            id=f"sec-{uuid.uuid4()}",
            name=name,
            level=level,
            features=features,
            encryption=encryption,
            access_controls=access_controls,
            audit_logs=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.security_configs[config.id] = config
        
        # Save security config
        self._save_security_config(config)
        
        self.logger.info(f"Security config created: {config.id}")
        return config
    
    def _save_security_config(self, config: SecurityConfig):
        """Save security configuration to storage."""
        config_path = os.path.join(
            self.storage_path,
            "security",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    async def create_workflow_config(
        self,
        name: str,
        type: WorkflowType,
        steps: List[Dict[str, Any]],
        conditions: Dict[str, Any],
        triggers: List[str],
        actions: List[str]
    ) -> WorkflowConfig:
        """Create workflow configuration."""
        config = WorkflowConfig(
            id=f"wf-{uuid.uuid4()}",
            name=name,
            type=type,
            steps=steps,
            conditions=conditions,
            triggers=triggers,
            actions=actions,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.workflow_configs[config.id] = config
        
        # Save workflow config
        self._save_workflow_config(config)
        
        self.logger.info(f"Workflow config created: {config.id}")
        return config
    
    def _save_workflow_config(self, config: WorkflowConfig):
        """Save workflow configuration to storage."""
        config_path = os.path.join(
            self.storage_path,
            "workflows",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    async def create_compliance_config(
        self,
        name: str,
        type: ComplianceType,
        requirements: List[str],
        controls: Dict[str, Any]
    ) -> ComplianceConfig:
        """Create compliance configuration."""
        config = ComplianceConfig(
            id=f"comp-{uuid.uuid4()}",
            name=name,
            type=type,
            requirements=requirements,
            controls=controls,
            status="pending",
            audit_date=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.compliance_configs[config.id] = config
        
        # Save compliance config
        self._save_compliance_config(config)
        
        self.logger.info(f"Compliance config created: {config.id}")
        return config
    
    def _save_compliance_config(self, config: ComplianceConfig):
        """Save compliance configuration to storage."""
        config_path = os.path.join(
            self.storage_path,
            "compliance",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    def update_security_config(
        self,
        config_id: str,
        features: Optional[Dict[str, bool]] = None,
        encryption: Optional[Dict[str, str]] = None,
        access_controls: Optional[Dict[str, List[str]]] = None
    ) -> SecurityConfig:
        """Update security configuration."""
        if config_id not in self.security_configs:
            raise ValueError(f"Security config not found: {config_id}")
        
        config = self.security_configs[config_id]
        
        if features:
            config.features = features
        
        if encryption:
            config.encryption = encryption
        
        if access_controls:
            config.access_controls = access_controls
        
        config.updated_at = datetime.now()
        
        # Save updated config
        self._save_security_config(config)
        
        self.logger.info(f"Security config updated: {config_id}")
        return config
    
    def update_workflow_config(
        self,
        config_id: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        conditions: Optional[Dict[str, Any]] = None,
        triggers: Optional[List[str]] = None,
        actions: Optional[List[str]] = None
    ) -> WorkflowConfig:
        """Update workflow configuration."""
        if config_id not in self.workflow_configs:
            raise ValueError(f"Workflow config not found: {config_id}")
        
        config = self.workflow_configs[config_id]
        
        if steps:
            config.steps = steps
        
        if conditions:
            config.conditions = conditions
        
        if triggers:
            config.triggers = triggers
        
        if actions:
            config.actions = actions
        
        config.updated_at = datetime.now()
        
        # Save updated config
        self._save_workflow_config(config)
        
        self.logger.info(f"Workflow config updated: {config_id}")
        return config
    
    def update_compliance_config(
        self,
        config_id: str,
        requirements: Optional[List[str]] = None,
        controls: Optional[Dict[str, Any]] = None,
        status: Optional[str] = None,
        audit_date: Optional[datetime] = None
    ) -> ComplianceConfig:
        """Update compliance configuration."""
        if config_id not in self.compliance_configs:
            raise ValueError(f"Compliance config not found: {config_id}")
        
        config = self.compliance_configs[config_id]
        
        if requirements:
            config.requirements = requirements
        
        if controls:
            config.controls = controls
        
        if status:
            config.status = status
        
        if audit_date:
            config.audit_date = audit_date
        
        config.updated_at = datetime.now()
        
        # Save updated config
        self._save_compliance_config(config)
        
        self.logger.info(f"Compliance config updated: {config_id}")
        return config
    
    def get_security_stats(
        self,
        level: Optional[SecurityLevel] = None
    ) -> Dict[str, Any]:
        """Get security statistics."""
        configs = self.security_configs.values()
        
        if level:
            configs = [c for c in configs if c.level == level]
        
        if not configs:
            return {
                "total": 0,
                "by_level": {},
                "feature_usage": {},
                "audit_enabled": 0
            }
        
        # Calculate feature usage
        all_features = set()
        for config in configs:
            all_features.update(config.features.keys())
        
        feature_usage = {}
        for feature in all_features:
            feature_usage[feature] = len([
                c for c in configs
                if c.features.get(feature, False)
            ])
        
        return {
            "total": len(configs),
            "by_level": {
                level: len([
                    c for c in configs
                    if c.level == level
                ])
                for level in {c.level for c in configs}
            },
            "feature_usage": feature_usage,
            "audit_enabled": len([
                c for c in configs
                if c.audit_logs
            ])
        }
    
    def get_workflow_stats(
        self,
        type: Optional[WorkflowType] = None
    ) -> Dict[str, Any]:
        """Get workflow statistics."""
        configs = self.workflow_configs.values()
        
        if type:
            configs = [c for c in configs if c.type == type]
        
        if not configs:
            return {
                "total": 0,
                "by_type": {},
                "avg_steps": None,
                "trigger_usage": {}
            }
        
        # Calculate trigger usage
        all_triggers = set()
        for config in configs:
            all_triggers.update(config.triggers)
        
        trigger_usage = {}
        for trigger in all_triggers:
            trigger_usage[trigger] = len([
                c for c in configs
                if trigger in c.triggers
            ])
        
        return {
            "total": len(configs),
            "by_type": {
                type: len([
                    c for c in configs
                    if c.type == type
                ])
                for type in {c.type for c in configs}
            },
            "avg_steps": statistics.mean([
                len(c.steps) for c in configs
            ]),
            "trigger_usage": trigger_usage
        }
    
    def get_compliance_stats(
        self,
        type: Optional[ComplianceType] = None
    ) -> Dict[str, Any]:
        """Get compliance statistics."""
        configs = self.compliance_configs.values()
        
        if type:
            configs = [c for c in configs if c.type == type]
        
        if not configs:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {},
                "audit_coverage": 0
            }
        
        return {
            "total": len(configs),
            "by_type": {
                type: len([
                    c for c in configs
                    if c.type == type
                ])
                for type in {c.type for c in configs}
            },
            "by_status": {
                status: len([
                    c for c in configs
                    if c.status == status
                ])
                for status in {c.status for c in configs}
            },
            "audit_coverage": len([
                c for c in configs
                if c.audit_date is not None
            ]) / len(configs)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get enterprise features status."""
        return {
            "security": self.get_security_stats(),
            "workflows": self.get_workflow_stats(),
            "compliance": self.get_compliance_stats(),
            "health_summary": {
                "security_health": all(
                    config.updated_at > (datetime.now() - timedelta(days=90))
                    for config in self.security_configs.values()
                ),
                "workflow_health": all(
                    config.updated_at > (datetime.now() - timedelta(days=90))
                    for config in self.workflow_configs.values()
                ),
                "compliance_health": all(
                    config.status != "failed"
                    for config in self.compliance_configs.values()
                )
            }
        }
