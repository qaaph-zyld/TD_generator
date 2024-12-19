"""
CRM Setup and Management Module for TD Generator.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging
import requests
import os
import json

@dataclass
class CRMConfig:
    """CRM configuration settings."""
    api_key: str
    pipeline_id: str
    portal_id: str
    stages: List[Dict[str, str]]

@dataclass
class Contact:
    """CRM contact information."""
    email: str
    first_name: str
    last_name: str
    company: str
    title: str
    status: str
    created_at: datetime
    last_contact: Optional[datetime] = None

class HubSpotManager:
    """Manages HubSpot CRM integration."""
    
    def __init__(self, config: CRMConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_pipeline(self) -> str:
        """Create sales pipeline in HubSpot."""
        endpoint = f"{self.base_url}/crm/v3/pipelines/deals"
        
        pipeline_data = {
            "name": "TD Generator Sales Pipeline",
            "stages": [
                {
                    "label": stage["label"],
                    "displayOrder": idx,
                    "probability": stage.get("probability", 0)
                }
                for idx, stage in enumerate(self.config.stages)
            ]
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=pipeline_data
            )
            response.raise_for_status()
            
            pipeline_id = response.json()["id"]
            self.config.pipeline_id = pipeline_id
            self.logger.info(f"Created pipeline: {pipeline_id}")
            return pipeline_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create pipeline: {str(e)}")
            raise
    
    def create_contact(self, contact: Contact) -> str:
        """Create new contact in HubSpot."""
        endpoint = f"{self.base_url}/crm/v3/objects/contacts"
        
        contact_data = {
            "properties": {
                "email": contact.email,
                "firstname": contact.first_name,
                "lastname": contact.last_name,
                "company": contact.company,
                "jobtitle": contact.title,
                "lifecyclestage": contact.status
            }
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=contact_data
            )
            response.raise_for_status()
            
            contact_id = response.json()["id"]
            self.logger.info(f"Created contact: {contact_id}")
            return contact_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create contact: {str(e)}")
            raise
    
    def create_deal(self, contact_id: str, amount: float, stage: str) -> str:
        """Create new deal in HubSpot."""
        endpoint = f"{self.base_url}/crm/v3/objects/deals"
        
        deal_data = {
            "properties": {
                "dealname": f"TD Generator - {datetime.now().strftime('%Y%m%d')}",
                "pipeline": self.config.pipeline_id,
                "dealstage": stage,
                "amount": amount
            },
            "associations": [
                {
                    "to": {"id": contact_id},
                    "types": [{"category": "HUBSPOT_DEFINED", "typeId": 3}]
                }
            ]
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=deal_data
            )
            response.raise_for_status()
            
            deal_id = response.json()["id"]
            self.logger.info(f"Created deal: {deal_id}")
            return deal_id
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create deal: {str(e)}")
            raise
    
    def update_deal_stage(self, deal_id: str, stage: str):
        """Update deal stage in HubSpot."""
        endpoint = f"{self.base_url}/crm/v3/objects/deals/{deal_id}"
        
        deal_data = {
            "properties": {
                "dealstage": stage
            }
        }
        
        try:
            response = requests.patch(
                endpoint,
                headers=self.headers,
                json=deal_data
            )
            response.raise_for_status()
            self.logger.info(f"Updated deal {deal_id} to stage: {stage}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update deal: {str(e)}")
            raise
    
    def get_pipeline_metrics(self) -> Dict:
        """Get pipeline performance metrics."""
        endpoint = f"{self.base_url}/crm/v3/pipelines/{self.config.pipeline_id}/stages"
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            
            stages = response.json()["results"]
            metrics = {
                stage["label"]: {
                    "deals": len(stage.get("deals", [])),
                    "value": sum(d.get("amount", 0) for d in stage.get("deals", []))
                }
                for stage in stages
            }
            
            return metrics
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get pipeline metrics: {str(e)}")
            raise

class CRMSetupManager:
    """Manages CRM setup and configuration."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config_file = "config/crm_config.json"
        self.config = self._load_config()
        self.hubspot = HubSpotManager(self.config)
    
    def _load_config(self) -> CRMConfig:
        """Load CRM configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return CRMConfig(**data)
        
        # Default configuration
        return CRMConfig(
            api_key=os.getenv("HUBSPOT_API_KEY", ""),
            pipeline_id="",
            portal_id=os.getenv("HUBSPOT_PORTAL_ID", ""),
            stages=[
                {"label": "Lead", "probability": 0.2},
                {"label": "Contact Made", "probability": 0.4},
                {"label": "Demo Scheduled", "probability": 0.6},
                {"label": "Trial", "probability": 0.8},
                {"label": "Negotiation", "probability": 0.9},
                {"label": "Closed Won", "probability": 1.0},
                {"label": "Closed Lost", "probability": 0.0}
            ]
        )
    
    def _save_config(self):
        """Save CRM configuration."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(vars(self.config), f)
    
    def initialize(self):
        """Initialize CRM setup."""
        self.logger.info("Initializing CRM setup")
        
        # Create pipeline if not exists
        if not self.config.pipeline_id:
            self.config.pipeline_id = self.hubspot.create_pipeline()
            self._save_config()
        
        # Validate configuration
        self._validate_setup()
        
        self.logger.info("CRM setup completed")
    
    def _validate_setup(self):
        """Validate CRM setup."""
        if not self.config.api_key:
            raise ValueError("HubSpot API key not configured")
        
        if not self.config.portal_id:
            raise ValueError("HubSpot portal ID not configured")
        
        if not self.config.pipeline_id:
            raise ValueError("Sales pipeline not created")
    
    def get_status(self) -> Dict:
        """Get CRM setup status."""
        try:
            metrics = self.hubspot.get_pipeline_metrics()
            return {
                "status": "active",
                "pipeline_id": self.config.pipeline_id,
                "metrics": metrics
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_test_data(self):
        """Create test data in CRM."""
        test_contact = Contact(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Corp",
            title="CTO",
            status="LEAD",
            created_at=datetime.now()
        )
        
        contact_id = self.hubspot.create_contact(test_contact)
        deal_id = self.hubspot.create_deal(contact_id, 5000.0, "Lead")
        
        return {
            "contact_id": contact_id,
            "deal_id": deal_id
        }
