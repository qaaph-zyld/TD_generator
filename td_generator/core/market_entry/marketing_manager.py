"""
Marketing Foundation Management System.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os
import shutil
from pathlib import Path
import markdown
import jinja2
import yaml

@dataclass
class ContentItem:
    """Marketing content item."""
    id: str
    title: str
    type: str
    content: str
    metadata: Dict[str, str]
    channels: List[str]
    schedule: Dict[str, datetime]
    status: str
    created_at: datetime
    updated_at: datetime
    version: str

@dataclass
class Channel:
    """Marketing channel configuration."""
    id: str
    name: str
    type: str
    config: Dict[str, str]
    metrics: Dict[str, int]
    status: str
    created_at: datetime

@dataclass
class Campaign:
    """Marketing campaign definition."""
    id: str
    name: str
    description: str
    channels: List[str]
    content: List[str]
    schedule: Dict[str, datetime]
    metrics: Dict[str, int]
    status: str
    created_at: datetime
    updated_at: datetime

class MarketingManager:
    """Manages marketing content and campaigns."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.content: Dict[str, ContentItem] = {}
        self.channels: Dict[str, Channel] = {}
        self.campaigns: Dict[str, Campaign] = {}
        self.storage_path = "data/marketing"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates/marketing")
        )
        self._initialize_storage()
        self._load_channels()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "website",
            "blog",
            "social",
            "email",
            "analytics",
            "campaigns"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_channels(self):
        """Load marketing channels configuration."""
        config_path = os.path.join(self.storage_path, "channels.yaml")
        
        # Create default channels if config doesn't exist
        if not os.path.exists(config_path):
            self._create_default_channels()
        
        # Load channel configurations
        with open(config_path, 'r') as f:
            channels_data = yaml.safe_load(f)
            for channel_id, data in channels_data.items():
                channel = Channel(
                    id=channel_id,
                    created_at=datetime.now(),
                    **data
                )
                self.channels[channel_id] = channel
    
    def _create_default_channels(self):
        """Create default marketing channels."""
        default_channels = {
            "website": {
                "name": "TD Generator Website",
                "type": "web",
                "config": {
                    "domain": "tdgenerator.io",
                    "hosting": "cloud",
                    "analytics_id": ""
                },
                "metrics": {
                    "visitors": 0,
                    "conversions": 0
                },
                "status": "active"
            },
            "blog": {
                "name": "TD Generator Blog",
                "type": "content",
                "config": {
                    "platform": "hugo",
                    "domain": "blog.tdgenerator.io"
                },
                "metrics": {
                    "posts": 0,
                    "views": 0
                },
                "status": "active"
            },
            "linkedin": {
                "name": "LinkedIn",
                "type": "social",
                "config": {
                    "page_url": "linkedin.com/company/tdgenerator"
                },
                "metrics": {
                    "followers": 0,
                    "engagement": 0
                },
                "status": "active"
            },
            "twitter": {
                "name": "Twitter",
                "type": "social",
                "config": {
                    "handle": "@TDGenerator"
                },
                "metrics": {
                    "followers": 0,
                    "engagement": 0
                },
                "status": "active"
            },
            "email": {
                "name": "Email Marketing",
                "type": "email",
                "config": {
                    "platform": "mailchimp",
                    "list_id": ""
                },
                "metrics": {
                    "subscribers": 0,
                    "open_rate": 0
                },
                "status": "active"
            }
        }
        
        # Save channel configurations
        config_path = os.path.join(self.storage_path, "channels.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_channels, f)
    
    def create_content(
        self,
        title: str,
        type: str,
        content: str,
        metadata: Dict[str, str],
        channels: List[str]
    ) -> ContentItem:
        """Create new marketing content."""
        # Validate channels
        invalid_channels = set(channels) - set(self.channels.keys())
        if invalid_channels:
            raise ValueError(f"Invalid channels: {invalid_channels}")
        
        # Create content item
        item = ContentItem(
            id=f"content-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            type=type,
            content=content,
            metadata=metadata,
            channels=channels,
            schedule={},
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0"
        )
        
        # Save content
        self._save_content(item)
        self.content[item.id] = item
        
        self.logger.info(f"Created content: {item.id}")
        return item
    
    def _save_content(self, item: ContentItem):
        """Save content item to storage."""
        content_path = os.path.join(
            self.storage_path,
            item.type,
            f"{item.id}.json"
        )
        
        with open(content_path, 'w') as f:
            json.dump(vars(item), f, default=str)
    
    def update_content(
        self,
        content_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        channels: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> ContentItem:
        """Update existing content."""
        if content_id not in self.content:
            raise ValueError(f"Content not found: {content_id}")
        
        item = self.content[content_id]
        
        # Update fields
        if content is not None:
            item.content = content
        if metadata is not None:
            item.metadata.update(metadata)
        if channels is not None:
            invalid_channels = set(channels) - set(self.channels.keys())
            if invalid_channels:
                raise ValueError(f"Invalid channels: {invalid_channels}")
            item.channels = channels
        if status is not None:
            item.status = status
        
        # Update metadata
        item.updated_at = datetime.now()
        version_parts = item.version.split('.')
        item.version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2])+1}"
        
        # Save updates
        self._save_content(item)
        
        self.logger.info(f"Updated content: {content_id}")
        return item
    
    def create_campaign(
        self,
        name: str,
        description: str,
        channels: List[str],
        content: List[str],
        schedule: Dict[str, datetime]
    ) -> Campaign:
        """Create new marketing campaign."""
        # Validate channels
        invalid_channels = set(channels) - set(self.channels.keys())
        if invalid_channels:
            raise ValueError(f"Invalid channels: {invalid_channels}")
        
        # Validate content
        invalid_content = set(content) - set(self.content.keys())
        if invalid_content:
            raise ValueError(f"Invalid content: {invalid_content}")
        
        # Create campaign
        campaign = Campaign(
            id=f"campaign-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            description=description,
            channels=channels,
            content=content,
            schedule=schedule,
            metrics={
                "impressions": 0,
                "engagement": 0,
                "conversions": 0
            },
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save campaign
        self._save_campaign(campaign)
        self.campaigns[campaign.id] = campaign
        
        self.logger.info(f"Created campaign: {campaign.id}")
        return campaign
    
    def _save_campaign(self, campaign: Campaign):
        """Save campaign to storage."""
        campaign_path = os.path.join(
            self.storage_path,
            "campaigns",
            f"{campaign.id}.json"
        )
        
        with open(campaign_path, 'w') as f:
            json.dump(vars(campaign), f, default=str)
    
    def update_campaign(
        self,
        campaign_id: str,
        channels: Optional[List[str]] = None,
        content: Optional[List[str]] = None,
        schedule: Optional[Dict[str, datetime]] = None,
        metrics: Optional[Dict[str, int]] = None,
        status: Optional[str] = None
    ) -> Campaign:
        """Update existing campaign."""
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        campaign = self.campaigns[campaign_id]
        
        # Update fields
        if channels is not None:
            invalid_channels = set(channels) - set(self.channels.keys())
            if invalid_channels:
                raise ValueError(f"Invalid channels: {invalid_channels}")
            campaign.channels = channels
        
        if content is not None:
            invalid_content = set(content) - set(self.content.keys())
            if invalid_content:
                raise ValueError(f"Invalid content: {invalid_content}")
            campaign.content = content
        
        if schedule is not None:
            campaign.schedule = schedule
        
        if metrics is not None:
            campaign.metrics.update(metrics)
        
        if status is not None:
            campaign.status = status
        
        # Update metadata
        campaign.updated_at = datetime.now()
        
        # Save updates
        self._save_campaign(campaign)
        
        self.logger.info(f"Updated campaign: {campaign_id}")
        return campaign
    
    def get_channel_metrics(self, channel_id: str) -> Dict[str, int]:
        """Get metrics for a specific channel."""
        if channel_id not in self.channels:
            raise ValueError(f"Channel not found: {channel_id}")
        
        return self.channels[channel_id].metrics
    
    def update_channel_metrics(
        self,
        channel_id: str,
        metrics: Dict[str, int]
    ) -> Channel:
        """Update metrics for a specific channel."""
        if channel_id not in self.channels:
            raise ValueError(f"Channel not found: {channel_id}")
        
        channel = self.channels[channel_id]
        channel.metrics.update(metrics)
        
        # Save channel configurations
        config_path = os.path.join(self.storage_path, "channels.yaml")
        with open(config_path, 'r') as f:
            channels_data = yaml.safe_load(f)
        
        channels_data[channel_id]["metrics"] = channel.metrics
        
        with open(config_path, 'w') as f:
            yaml.dump(channels_data, f)
        
        self.logger.info(f"Updated metrics for channel: {channel_id}")
        return channel
    
    def get_campaign_metrics(self, campaign_id: str) -> Dict[str, int]:
        """Get metrics for a specific campaign."""
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campaign not found: {campaign_id}")
        
        return self.campaigns[campaign_id].metrics
    
    def get_status(self) -> Dict:
        """Get marketing system status."""
        return {
            "channels": {
                "total": len(self.channels),
                "active": len([c for c in self.channels.values() if c.status == "active"]),
                "metrics": {
                    channel_id: channel.metrics
                    for channel_id, channel in self.channels.items()
                }
            },
            "content": {
                "total": len(self.content),
                "by_type": {
                    type: len([c for c in self.content.values() if c.type == type])
                    for type in set(c.type for c in self.content.values())
                },
                "by_status": {
                    status: len([c for c in self.content.values() if c.status == status])
                    for status in set(c.status for c in self.content.values())
                }
            },
            "campaigns": {
                "total": len(self.campaigns),
                "active": len([c for c in self.campaigns.values() if c.status == "active"]),
                "metrics": {
                    campaign_id: campaign.metrics
                    for campaign_id, campaign in self.campaigns.items()
                }
            }
        }
