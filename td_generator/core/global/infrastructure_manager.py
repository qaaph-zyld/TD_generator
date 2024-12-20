"""
Global Infrastructure Management System for Worldwide Deployment.
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
from enum import Enum
import aiohttp
import dns.resolver
import geoip2.database
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import socket
import ssl
import boto3
import azure.mgmt.cdn
from google.cloud import cdn

class ServerType(str, Enum):
    """Server types."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    EDGE = "edge"
    CACHE = "cache"

class RegionType(str, Enum):
    """Region types."""
    AMERICAS = "americas"
    EMEA = "emea"
    APAC = "apac"
    GLOBAL = "global"

class ServiceType(str, Enum):
    """Service types."""
    CDN = "cdn"
    DNS = "dns"
    LOAD_BALANCER = "load_balancer"
    EDGE_COMPUTE = "edge_compute"

@dataclass
class ServerProfile:
    """Server profile definition."""
    id: str
    name: str
    type: ServerType
    region: RegionType
    location: str
    capacity: Dict[str, float]
    services: List[str]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class ServiceConfig:
    """Service configuration."""
    id: str
    server_id: str
    type: ServiceType
    settings: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

class InfrastructureManager:
    """Manages global infrastructure and deployment."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, ServerProfile] = {}
        self.services: Dict[str, List[ServiceConfig]] = {}
        self.storage_path = "data/global/infrastructure"
        self._initialize_storage()
        self._load_configuration()
        self.app = FastAPI()
        self._setup_api()
        self.dns_resolver = dns.resolver.Resolver()
        self.geoip_reader = geoip2.database.Reader('data/geoip/GeoLite2-City.mmdb')
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "profiles",
            "services",
            "metrics",
            "logs",
            "configs"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load infrastructure configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default infrastructure configuration."""
        default_config = {
            "server_types": [
                {
                    "type": "primary",
                    "requirements": ["high_availability", "redundancy"]
                },
                {
                    "type": "secondary",
                    "requirements": ["failover", "backup"]
                },
                {
                    "type": "edge",
                    "requirements": ["low_latency", "caching"]
                },
                {
                    "type": "cache",
                    "requirements": ["fast_access", "replication"]
                }
            ],
            "region_types": [
                {
                    "type": "americas",
                    "locations": ["us-east", "us-west", "br-south"]
                },
                {
                    "type": "emea",
                    "locations": ["eu-west", "eu-central", "me-south"]
                },
                {
                    "type": "apac",
                    "locations": ["ap-east", "ap-south", "ap-southeast"]
                },
                {
                    "type": "global",
                    "locations": ["all"]
                }
            ],
            "service_types": [
                {
                    "type": "cdn",
                    "providers": ["cloudflare", "akamai", "fastly"]
                },
                {
                    "type": "dns",
                    "providers": ["route53", "cloudflare", "azure"]
                },
                {
                    "type": "load_balancer",
                    "providers": ["aws", "gcp", "azure"]
                },
                {
                    "type": "edge_compute",
                    "providers": ["cloudflare", "lambda", "functions"]
                }
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    def _setup_api(self):
        """Setup FastAPI application."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}
        
        @self.app.get("/servers")
        async def list_servers():
            return {"servers": list(self.servers.values())}
        
        @self.app.get("/services")
        async def list_services():
            return {"services": self.services}
    
    async def create_server(
        self,
        name: str,
        type: ServerType,
        region: RegionType,
        location: str,
        capacity: Dict[str, float]
    ) -> ServerProfile:
        """Create server profile."""
        # Validate location
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        region_config = next(
            r for r in config["region_types"]
            if r["type"] == region
        )
        
        if location not in region_config["locations"] and location != "all":
            raise ValueError(f"Invalid location for region: {location}")
        
        # Create server profile
        profile = ServerProfile(
            id=f"server-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            region=region,
            location=location,
            capacity=capacity,
            services=[],
            metrics={},
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.servers[profile.id] = profile
        
        # Save server profile
        self._save_server(profile)
        
        # Create default services
        await self._create_default_services(profile)
        
        self.logger.info(f"Server created: {profile.id}")
        return profile
    
    def _save_server(self, profile: ServerProfile):
        """Save server profile to storage."""
        profile_path = os.path.join(
            self.storage_path,
            "profiles",
            f"{profile.id}.json"
        )
        
        with open(profile_path, 'w') as f:
            json.dump(vars(profile), f, default=str)
    
    async def _create_default_services(
        self,
        profile: ServerProfile
    ):
        """Create default services for server."""
        # CDN service
        if profile.type in [ServerType.EDGE, ServerType.CACHE]:
            await self.create_service(
                profile.id,
                ServiceType.CDN,
                {
                    "provider": "cloudflare",
                    "zone": profile.location,
                    "caching": "aggressive"
                }
            )
        
        # DNS service
        if profile.type in [ServerType.PRIMARY, ServerType.SECONDARY]:
            await self.create_service(
                profile.id,
                ServiceType.DNS,
                {
                    "provider": "route53",
                    "zone": f"{profile.location}.td-generator.com",
                    "ttl": 300
                }
            )
        
        # Load balancer service
        if profile.type in [ServerType.PRIMARY, ServerType.EDGE]:
            await self.create_service(
                profile.id,
                ServiceType.LOAD_BALANCER,
                {
                    "provider": "aws",
                    "algorithm": "least_connections",
                    "health_check": {
                        "protocol": "https",
                        "port": 443,
                        "path": "/health",
                        "interval": 30
                    }
                }
            )
        
        # Edge compute service
        if profile.type == ServerType.EDGE:
            await self.create_service(
                profile.id,
                ServiceType.EDGE_COMPUTE,
                {
                    "provider": "cloudflare",
                    "runtime": "python",
                    "memory": 128,
                    "timeout": 30
                }
            )
    
    async def create_service(
        self,
        server_id: str,
        type: ServiceType,
        settings: Dict[str, Any]
    ) -> ServiceConfig:
        """Create service configuration."""
        config = ServiceConfig(
            id=f"service-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            server_id=server_id,
            type=type,
            settings=settings,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if server_id not in self.services:
            self.services[server_id] = []
        
        self.services[server_id].append(config)
        
        # Update server profile
        server = self.servers[server_id]
        server.services.append(type)
        server.updated_at = datetime.now()
        self._save_server(server)
        
        # Save service
        self._save_service(config)
        
        self.logger.info(f"Service created: {config.id}")
        return config
    
    def _save_service(self, config: ServiceConfig):
        """Save service configuration to storage."""
        config_path = os.path.join(
            self.storage_path,
            "services",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    async def route_request(
        self,
        client_ip: str,
        service_type: ServiceType
    ) -> ServerProfile:
        """Route request to appropriate server."""
        try:
            # Get client location
            response = self.geoip_reader.city(client_ip)
            client_region = self._get_region_for_location(
                response.location.latitude,
                response.location.longitude
            )
            
            # Find servers in the same region
            regional_servers = [
                server for server in self.servers.values()
                if server.region == client_region
                and service_type in server.services
                and server.status == "active"
            ]
            
            if not regional_servers:
                # Fallback to global servers
                regional_servers = [
                    server for server in self.servers.values()
                    if server.region == RegionType.GLOBAL
                    and service_type in server.services
                    and server.status == "active"
                ]
            
            if not regional_servers:
                raise ValueError("No available servers")
            
            # Select server with lowest load
            return min(
                regional_servers,
                key=lambda s: s.metrics.get("load", 0)
            )
        
        except Exception as e:
            self.logger.error(f"Error routing request: {str(e)}")
            # Return any available server as fallback
            return next(
                server for server in self.servers.values()
                if service_type in server.services
                and server.status == "active"
            )
    
    def _get_region_for_location(
        self,
        latitude: float,
        longitude: float
    ) -> RegionType:
        """Get region type for geographical location."""
        # Simple region determination based on longitude
        if -165 <= longitude <= -30:  # Americas
            return RegionType.AMERICAS
        elif -30 < longitude <= 60:   # EMEA
            return RegionType.EMEA
        else:                         # APAC
            return RegionType.APAC
    
    async def check_cdn_status(
        self,
        service_config: ServiceConfig
    ) -> bool:
        """Check CDN service status."""
        provider = service_config.settings["provider"]
        
        if provider == "cloudflare":
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.cloudflare.com/client/v4/zones/{service_config.settings['zone']}"
                ) as response:
                    return response.status == 200
        
        elif provider == "akamai":
            # Implement Akamai status check
            pass
        
        elif provider == "fastly":
            # Implement Fastly status check
            pass
        
        return False
    
    async def check_dns_status(
        self,
        service_config: ServiceConfig
    ) -> bool:
        """Check DNS service status."""
        try:
            answers = self.dns_resolver.resolve(
                service_config.settings["zone"],
                "A"
            )
            return len(answers) > 0
        except Exception:
            return False
    
    async def check_load_balancer_status(
        self,
        service_config: ServiceConfig
    ) -> bool:
        """Check load balancer service status."""
        try:
            health_check = service_config.settings["health_check"]
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{health_check['protocol']}://{service_config.settings['zone']}:{health_check['port']}{health_check['path']}"
                ) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def check_edge_compute_status(
        self,
        service_config: ServiceConfig
    ) -> bool:
        """Check edge compute service status."""
        provider = service_config.settings["provider"]
        
        if provider == "cloudflare":
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{service_config.settings['account_id']}/workers"
                ) as response:
                    return response.status == 200
        
        elif provider == "lambda":
            # Implement Lambda status check
            pass
        
        elif provider == "functions":
            # Implement Cloud Functions status check
            pass
        
        return False
    
    def get_server_stats(
        self,
        type: Optional[ServerType] = None,
        region: Optional[RegionType] = None
    ) -> Dict[str, Any]:
        """Get server statistics."""
        servers = self.servers.values()
        
        if type:
            servers = [s for s in servers if s.type == type]
        
        if region:
            servers = [s for s in servers if s.region == region]
        
        if not servers:
            return {
                "total": 0,
                "by_type": {},
                "by_region": {},
                "by_status": {}
            }
        
        return {
            "total": len(servers),
            "by_type": {
                type: len([
                    s for s in servers
                    if s.type == type
                ])
                for type in {s.type for s in servers}
            },
            "by_region": {
                region: len([
                    s for s in servers
                    if s.region == region
                ])
                for region in {s.region for s in servers}
            },
            "by_status": {
                status: len([
                    s for s in servers
                    if s.status == status
                ])
                for status in {s.status for s in servers}
            }
        }
    
    def get_service_stats(
        self,
        server_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get service statistics."""
        if server_id:
            services = self.services.get(server_id, [])
        else:
            services = []
            for configs in self.services.values():
                services.extend(configs)
        
        if not services:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {},
                "coverage": {}
            }
        
        return {
            "total": len(services),
            "by_type": {
                type: len([
                    s for s in services
                    if s.type == type
                ])
                for type in {s.type for s in services}
            },
            "by_status": {
                status: len([
                    s for s in services
                    if s.status == status
                ])
                for status in {s.status for s in services}
            },
            "coverage": {
                server_id: len(configs)
                for server_id, configs in self.services.items()
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get infrastructure manager status."""
        return {
            "servers": self.get_server_stats(),
            "services": self.get_service_stats(),
            "health_summary": {
                "server_health": all(
                    server.status == "active"
                    for server in self.servers.values()
                ),
                "service_health": all(
                    config.status == "active"
                    for configs in self.services.values()
                    for config in configs
                ),
                "api_health": True
            }
        }
