"""
Demo Environment Setup and Management Module.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os
import shutil
import docker
from pathlib import Path

@dataclass
class DemoConfig:
    """Demo environment configuration."""
    environment_id: str
    instance_type: str
    features: List[str]
    demo_data: Dict[str, str]
    created_at: datetime

@dataclass
class DemoInstance:
    """Demo instance information."""
    instance_id: str
    status: str
    url: str
    credentials: Dict[str, str]
    features: List[str]
    created_at: datetime
    expires_at: datetime

class DemoEnvironmentManager:
    """Manages demo environment setup and operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_file = "config/demo_config.json"
        self.config = self._load_config()
        self.docker_client = docker.from_env()
        self.instances: Dict[str, DemoInstance] = {}
    
    def _load_config(self) -> DemoConfig:
        """Load demo configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return DemoConfig(**data)
        
        # Default configuration
        return DemoConfig(
            environment_id="td-generator-demo",
            instance_type="cloud",
            features=[
                "documentation_generation",
                "multi_format_support",
                "collaboration",
                "version_control"
            ],
            demo_data={
                "project_templates": "data/demo/templates",
                "sample_docs": "data/demo/samples",
                "test_cases": "data/demo/tests"
            },
            created_at=datetime.now()
        )
    
    def _save_config(self):
        """Save demo configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(vars(self.config), f)
    
    def _setup_demo_data(self):
        """Set up demo data directories and content."""
        for purpose, path in self.config.demo_data.items():
            os.makedirs(path, exist_ok=True)
            
            # Create demo content based on purpose
            if purpose == "project_templates":
                self._create_project_templates(path)
            elif purpose == "sample_docs":
                self._create_sample_docs(path)
            elif purpose == "test_cases":
                self._create_test_cases(path)
    
    def _create_project_templates(self, path: str):
        """Create project templates for demo."""
        templates = {
            "api_docs": {
                "template.md": "# API Documentation\n\n## Endpoints\n\n### GET /api/v1/resource\n",
                "schema.json": '{"openapi": "3.0.0", "info": {"title": "Sample API", "version": "1.0.0"}}'
            },
            "user_guides": {
                "template.md": "# User Guide\n\n## Getting Started\n\n### Installation\n",
                "styles.css": "body { font-family: Arial, sans-serif; }"
            },
            "technical_specs": {
                "template.md": "# Technical Specification\n\n## System Architecture\n",
                "diagrams.svg": '<svg width="100" height="100"></svg>'
            }
        }
        
        for category, files in templates.items():
            category_path = os.path.join(path, category)
            os.makedirs(category_path, exist_ok=True)
            
            for filename, content in files.items():
                with open(os.path.join(category_path, filename), 'w') as f:
                    f.write(content)
    
    def _create_sample_docs(self, path: str):
        """Create sample documentation."""
        samples = {
            "rest_api.md": """# REST API Documentation

## Authentication
API uses JWT tokens for authentication.

## Endpoints

### GET /users
Retrieve list of users.

#### Parameters
- page: int
- limit: int

#### Response
```json
{
    "users": [],
    "total": 0
}
```
""",
            "deployment.md": """# Deployment Guide

## Prerequisites
- Docker
- Python 3.9+
- PostgreSQL

## Installation Steps
1. Clone repository
2. Install dependencies
3. Configure environment
4. Run migrations
5. Start server
""",
            "architecture.md": """# System Architecture

## Components
1. Frontend (React)
2. Backend (Python)
3. Database (PostgreSQL)
4. Cache (Redis)

## Data Flow
1. User request
2. Load balancer
3. Application server
4. Database
"""
        }
        
        for filename, content in samples.items():
            with open(os.path.join(path, filename), 'w') as f:
                f.write(content)
    
    def _create_test_cases(self, path: str):
        """Create test documentation cases."""
        test_cases = {
            "api_tests.md": """# API Documentation Tests

## Test Cases

### 1. Endpoint Documentation
- Verify all endpoints listed
- Check parameters documentation
- Validate response format

### 2. Authentication
- Test auth token documentation
- Verify error responses
- Check rate limiting info
""",
            "format_tests.md": """# Format Conversion Tests

## Test Cases

### 1. Markdown to HTML
- Headers conversion
- Code blocks formatting
- Table rendering

### 2. Code Documentation
- Function documentation
- Class documentation
- Module documentation
"""
        }
        
        for filename, content in test_cases.items():
            with open(os.path.join(path, filename), 'w') as f:
                f.write(content)
    
    def create_instance(self, name: str) -> DemoInstance:
        """Create new demo instance."""
        instance_id = f"demo-{name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create Docker container
        container = self.docker_client.containers.run(
            "python:3.9-slim",
            name=instance_id,
            detach=True,
            environment={
                "DEMO_ID": instance_id,
                "FEATURES": ",".join(self.config.features)
            },
            ports={'8000/tcp': None}
        )
        
        # Get container info
        container_info = container.attrs
        port = container_info['NetworkSettings']['Ports']['8000/tcp'][0]['HostPort']
        
        # Create instance record
        instance = DemoInstance(
            instance_id=instance_id,
            status="running",
            url=f"http://localhost:{port}",
            credentials={
                "username": "demo",
                "password": "demo123"
            },
            features=self.config.features.copy(),
            created_at=datetime.now(),
            expires_at=datetime.now().replace(hour=23, minute=59, second=59)
        )
        
        self.instances[instance_id] = instance
        self.logger.info(f"Created demo instance: {instance_id}")
        
        return instance
    
    def stop_instance(self, instance_id: str):
        """Stop demo instance."""
        if instance_id not in self.instances:
            raise ValueError(f"Instance not found: {instance_id}")
        
        try:
            container = self.docker_client.containers.get(instance_id)
            container.stop()
            container.remove()
            
            instance = self.instances[instance_id]
            instance.status = "stopped"
            
            self.logger.info(f"Stopped demo instance: {instance_id}")
            
        except docker.errors.NotFound:
            self.logger.warning(f"Container not found: {instance_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to stop instance: {str(e)}")
            raise
    
    def get_instance(self, instance_id: str) -> Optional[DemoInstance]:
        """Get demo instance information."""
        return self.instances.get(instance_id)
    
    def list_instances(self) -> List[DemoInstance]:
        """List all demo instances."""
        return list(self.instances.values())
    
    def cleanup_expired(self):
        """Clean up expired demo instances."""
        now = datetime.now()
        expired = [
            instance_id
            for instance_id, instance in self.instances.items()
            if instance.expires_at < now
        ]
        
        for instance_id in expired:
            self.stop_instance(instance_id)
            del self.instances[instance_id]
    
    def get_status(self) -> Dict:
        """Get demo environment status."""
        active_instances = len([
            i for i in self.instances.values()
            if i.status == "running"
        ])
        
        return {
            "status": "active" if active_instances > 0 else "idle",
            "instances": {
                "total": len(self.instances),
                "active": active_instances
            },
            "features": self.config.features,
            "demo_data": {
                path: os.path.exists(path)
                for path in self.config.demo_data.values()
            }
        }

class DemoOrchestrator:
    """Orchestrates demo environment operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.manager = DemoEnvironmentManager()
    
    def initialize(self):
        """Initialize demo environment."""
        self.logger.info("Initializing demo environment")
        
        # Set up demo data
        self._setup_demo_data()
        
        # Create initial instance
        self.manager.create_instance("initial")
        
        self.logger.info("Demo environment initialized")
    
    def _setup_demo_data(self):
        """Set up demo data and structure."""
        self.manager._setup_demo_data()
    
    def create_demo(self, name: str) -> Dict:
        """Create new demo instance."""
        instance = self.manager.create_instance(name)
        
        return {
            "instance_id": instance.instance_id,
            "url": instance.url,
            "credentials": instance.credentials
        }
    
    def cleanup(self):
        """Clean up demo environment."""
        self.manager.cleanup_expired()
    
    def get_status(self) -> Dict:
        """Get demo environment status."""
        return self.manager.get_status()
