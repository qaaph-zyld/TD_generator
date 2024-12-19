"""
Support Infrastructure and Community Management System.
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

class SupportLevel(str, Enum):
    """Support service levels."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ResourceType(str, Enum):
    """Training resource types."""
    DOCUMENTATION = "documentation"
    VIDEO = "video"
    WEBINAR = "webinar"
    WORKSHOP = "workshop"
    TUTORIAL = "tutorial"

@dataclass
class SupportTicket:
    """Support ticket definition."""
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    client: str
    assigned_to: Optional[str]
    resolution_time: Optional[int]
    satisfaction_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

@dataclass
class TrainingResource:
    """Training resource definition."""
    id: str
    title: str
    type: ResourceType
    description: str
    content_url: str
    language: str
    duration: int
    difficulty: str
    prerequisites: List[str]
    tags: List[str]
    views: int
    rating: float
    created_at: datetime
    updated_at: datetime

@dataclass
class CommunityPost:
    """Community post definition."""
    id: str
    title: str
    content: str
    author: str
    category: str
    tags: List[str]
    likes: int
    views: int
    status: str
    created_at: datetime
    updated_at: datetime

class SupportManager:
    """Manages support infrastructure and community engagement."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tickets: Dict[str, SupportTicket] = {}
        self.resources: Dict[str, TrainingResource] = {}
        self.posts: Dict[str, CommunityPost] = {}
        self.storage_path = "data/support_infrastructure"
        self._initialize_storage()
        self._load_configuration()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "tickets",
            "resources",
            "community",
            "analytics",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load support configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default support configuration."""
        default_config = {
            "support_levels": [
                {
                    "id": "basic",
                    "name": "Basic Support",
                    "response_time": 24,
                    "channels": ["email", "docs"]
                },
                {
                    "id": "standard",
                    "name": "Standard Support",
                    "response_time": 12,
                    "channels": ["email", "chat", "docs"]
                },
                {
                    "id": "premium",
                    "name": "Premium Support",
                    "response_time": 4,
                    "channels": ["email", "chat", "phone", "docs"]
                },
                {
                    "id": "enterprise",
                    "name": "Enterprise Support",
                    "response_time": 1,
                    "channels": ["email", "chat", "phone", "dedicated"]
                }
            ],
            "resource_types": [
                {
                    "id": "documentation",
                    "formats": ["md", "pdf", "html"]
                },
                {
                    "id": "video",
                    "formats": ["mp4", "webm"]
                },
                {
                    "id": "webinar",
                    "platforms": ["zoom", "teams"]
                },
                {
                    "id": "workshop",
                    "delivery": ["online", "onsite"]
                },
                {
                    "id": "tutorial",
                    "types": ["text", "interactive"]
                }
            ],
            "community_categories": [
                "discussion",
                "question",
                "tutorial",
                "showcase",
                "feedback"
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_ticket(
        self,
        title: str,
        description: str,
        category: str,
        priority: str,
        client: str
    ) -> SupportTicket:
        """Create support ticket."""
        ticket = SupportTicket(
            id=f"ticket-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="open",
            client=client,
            assigned_to=None,
            resolution_time=None,
            satisfaction_score=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None
        )
        
        self.tickets[ticket.id] = ticket
        
        # Save ticket
        self._save_ticket(ticket)
        
        self.logger.info(f"Support ticket created: {ticket.id}")
        return ticket
    
    def _save_ticket(self, ticket: SupportTicket):
        """Save support ticket to storage."""
        ticket_path = os.path.join(
            self.storage_path,
            "tickets",
            f"{ticket.id}.json"
        )
        
        with open(ticket_path, 'w') as f:
            json.dump(vars(ticket), f, default=str)
    
    async def create_resource(
        self,
        title: str,
        type: ResourceType,
        description: str,
        content_url: str,
        language: str,
        duration: int,
        difficulty: str,
        prerequisites: List[str],
        tags: List[str]
    ) -> TrainingResource:
        """Create training resource."""
        resource = TrainingResource(
            id=f"resource-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            type=type,
            description=description,
            content_url=content_url,
            language=language,
            duration=duration,
            difficulty=difficulty,
            prerequisites=prerequisites,
            tags=tags,
            views=0,
            rating=0.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.resources[resource.id] = resource
        
        # Save resource
        self._save_resource(resource)
        
        self.logger.info(f"Training resource created: {resource.id}")
        return resource
    
    def _save_resource(self, resource: TrainingResource):
        """Save training resource to storage."""
        resource_path = os.path.join(
            self.storage_path,
            "resources",
            f"{resource.id}.json"
        )
        
        with open(resource_path, 'w') as f:
            json.dump(vars(resource), f, default=str)
    
    async def create_post(
        self,
        title: str,
        content: str,
        author: str,
        category: str,
        tags: List[str]
    ) -> CommunityPost:
        """Create community post."""
        post = CommunityPost(
            id=f"post-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=title,
            content=content,
            author=author,
            category=category,
            tags=tags,
            likes=0,
            views=0,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.posts[post.id] = post
        
        # Save post
        self._save_post(post)
        
        self.logger.info(f"Community post created: {post.id}")
        return post
    
    def _save_post(self, post: CommunityPost):
        """Save community post to storage."""
        post_path = os.path.join(
            self.storage_path,
            "community",
            f"{post.id}.json"
        )
        
        with open(post_path, 'w') as f:
            json.dump(vars(post), f, default=str)
    
    def update_ticket(
        self,
        ticket_id: str,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        satisfaction_score: Optional[float] = None
    ) -> SupportTicket:
        """Update support ticket."""
        if ticket_id not in self.tickets:
            raise ValueError(f"Ticket not found: {ticket_id}")
        
        ticket = self.tickets[ticket_id]
        
        if status:
            ticket.status = status
            if status == "resolved":
                ticket.resolved_at = datetime.now()
                ticket.resolution_time = int(
                    (ticket.resolved_at - ticket.created_at).total_seconds() / 3600
                )
        
        if assigned_to:
            ticket.assigned_to = assigned_to
        
        if satisfaction_score is not None:
            ticket.satisfaction_score = satisfaction_score
        
        ticket.updated_at = datetime.now()
        
        # Save updated ticket
        self._save_ticket(ticket)
        
        self.logger.info(f"Ticket updated: {ticket_id}")
        return ticket
    
    def update_resource(
        self,
        resource_id: str,
        views: Optional[int] = None,
        rating: Optional[float] = None,
        content_url: Optional[str] = None
    ) -> TrainingResource:
        """Update training resource."""
        if resource_id not in self.resources:
            raise ValueError(f"Resource not found: {resource_id}")
        
        resource = self.resources[resource_id]
        
        if views is not None:
            resource.views = views
        
        if rating is not None:
            resource.rating = rating
        
        if content_url:
            resource.content_url = content_url
        
        resource.updated_at = datetime.now()
        
        # Save updated resource
        self._save_resource(resource)
        
        self.logger.info(f"Resource updated: {resource_id}")
        return resource
    
    def update_post(
        self,
        post_id: str,
        likes: Optional[int] = None,
        views: Optional[int] = None,
        status: Optional[str] = None
    ) -> CommunityPost:
        """Update community post."""
        if post_id not in self.posts:
            raise ValueError(f"Post not found: {post_id}")
        
        post = self.posts[post_id]
        
        if likes is not None:
            post.likes = likes
        
        if views is not None:
            post.views = views
        
        if status:
            post.status = status
        
        post.updated_at = datetime.now()
        
        # Save updated post
        self._save_post(post)
        
        self.logger.info(f"Post updated: {post_id}")
        return post
    
    def get_ticket_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get ticket statistics."""
        end_time = end_time or datetime.now()
        
        # Filter tickets
        tickets = [
            t for t in self.tickets.values()
            if start_time <= t.created_at <= end_time
        ]
        
        if not tickets:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "avg_resolution_time": None,
                "satisfaction": None
            }
        
        resolved = [
            t for t in tickets
            if t.resolution_time is not None
        ]
        
        rated = [
            t for t in tickets
            if t.satisfaction_score is not None
        ]
        
        return {
            "total": len(tickets),
            "by_status": {
                status: len([
                    t for t in tickets
                    if t.status == status
                ])
                for status in {t.status for t in tickets}
            },
            "by_priority": {
                priority: len([
                    t for t in tickets
                    if t.priority == priority
                ])
                for priority in {t.priority for t in tickets}
            },
            "avg_resolution_time": statistics.mean([
                t.resolution_time for t in resolved
            ]) if resolved else None,
            "satisfaction": statistics.mean([
                t.satisfaction_score for t in rated
            ]) if rated else None
        }
    
    def get_resource_stats(
        self,
        type: Optional[ResourceType] = None
    ) -> Dict[str, Any]:
        """Get resource statistics."""
        resources = self.resources.values()
        
        if type:
            resources = [
                r for r in resources
                if r.type == type
            ]
        
        if not resources:
            return {
                "total": 0,
                "by_type": {},
                "by_language": {},
                "avg_rating": None,
                "total_views": 0
            }
        
        return {
            "total": len(resources),
            "by_type": {
                rtype: len([
                    r for r in resources
                    if r.type == rtype
                ])
                for rtype in {r.type for r in resources}
            },
            "by_language": {
                lang: len([
                    r for r in resources
                    if r.language == lang
                ])
                for lang in {r.language for r in resources}
            },
            "avg_rating": statistics.mean([
                r.rating for r in resources
            ]),
            "total_views": sum(r.views for r in resources)
        }
    
    def get_community_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get community statistics."""
        end_time = end_time or datetime.now()
        
        # Filter posts
        posts = [
            p for p in self.posts.values()
            if start_time <= p.created_at <= end_time
        ]
        
        if not posts:
            return {
                "total": 0,
                "by_category": {},
                "total_views": 0,
                "total_likes": 0
            }
        
        return {
            "total": len(posts),
            "by_category": {
                category: len([
                    p for p in posts
                    if p.category == category
                ])
                for category in {p.category for p in posts}
            },
            "total_views": sum(p.views for p in posts),
            "total_likes": sum(p.likes for p in posts),
            "engagement_rate": (
                sum(p.likes for p in posts) /
                sum(p.views for p in posts)
                if sum(p.views for p in posts) > 0
                else 0
            )
        }
    
    def get_status(self) -> Dict:
        """Get support infrastructure status."""
        now = datetime.now()
        month_ago = now - timedelta(days=30)
        
        return {
            "tickets": self.get_ticket_stats(month_ago, now),
            "resources": {
                type.value: self.get_resource_stats(type)
                for type in ResourceType
            },
            "community": self.get_community_stats(month_ago, now),
            "recent_activity": {
                "tickets": len([
                    t for t in self.tickets.values()
                    if (now - t.updated_at).days <= 7
                ]),
                "resources": len([
                    r for r in self.resources.values()
                    if (now - r.updated_at).days <= 7
                ]),
                "posts": len([
                    p for p in self.posts.values()
                    if (now - p.updated_at).days <= 7
                ])
            }
        }
