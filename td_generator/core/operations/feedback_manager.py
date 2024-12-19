"""
User Feedback and Issue Management System.
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

@dataclass
class Feedback:
    """User feedback entry."""
    id: str
    user_id: str
    category: str
    subject: str
    content: str
    rating: Optional[int]
    tags: List[str]
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

@dataclass
class Issue:
    """System issue report."""
    id: str
    feedback_id: Optional[str]
    reporter_id: str
    category: str
    title: str
    description: str
    severity: str
    impact: str
    status: str
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

@dataclass
class FeatureRequest:
    """Feature request entry."""
    id: str
    feedback_id: Optional[str]
    requester_id: str
    title: str
    description: str
    use_case: str
    business_value: str
    priority: str
    status: str
    votes: int
    created_at: datetime
    updated_at: datetime
    implemented_at: Optional[datetime]

class FeedbackManager:
    """Manages user feedback and issue tracking."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feedback: Dict[str, Feedback] = {}
        self.issues: Dict[str, Issue] = {}
        self.features: Dict[str, FeatureRequest] = {}
        self.storage_path = "data/feedback"
        self._initialize_storage()
        self._load_categories()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "feedback",
            "issues",
            "features",
            "analytics",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_categories(self):
        """Load feedback categories."""
        categories_path = os.path.join(self.storage_path, "categories.yaml")
        
        # Create default categories if none exist
        if not os.path.exists(categories_path):
            self._create_default_categories()
    
    def _create_default_categories(self):
        """Create default feedback categories."""
        default_categories = {
            "feedback_categories": [
                {
                    "id": "usability",
                    "name": "Usability",
                    "description": "User experience and interface feedback"
                },
                {
                    "id": "performance",
                    "name": "Performance",
                    "description": "System performance and speed"
                },
                {
                    "id": "feature",
                    "name": "Feature Request",
                    "description": "New feature suggestions"
                },
                {
                    "id": "bug",
                    "name": "Bug Report",
                    "description": "System issues and bugs"
                },
                {
                    "id": "documentation",
                    "name": "Documentation",
                    "description": "Documentation clarity and completeness"
                }
            ],
            "issue_categories": [
                {
                    "id": "technical",
                    "name": "Technical",
                    "description": "Technical system issues"
                },
                {
                    "id": "functional",
                    "name": "Functional",
                    "description": "Functional behavior issues"
                },
                {
                    "id": "security",
                    "name": "Security",
                    "description": "Security-related issues"
                },
                {
                    "id": "performance",
                    "name": "Performance",
                    "description": "Performance-related issues"
                }
            ],
            "feature_categories": [
                {
                    "id": "core",
                    "name": "Core Functionality",
                    "description": "Core system features"
                },
                {
                    "id": "integration",
                    "name": "Integration",
                    "description": "System integration features"
                },
                {
                    "id": "automation",
                    "name": "Automation",
                    "description": "Process automation features"
                },
                {
                    "id": "reporting",
                    "name": "Reporting",
                    "description": "Reporting and analytics features"
                }
            ]
        }
        
        # Save categories
        categories_path = os.path.join(self.storage_path, "categories.yaml")
        with open(categories_path, 'w') as f:
            yaml.dump(default_categories, f)
    
    async def submit_feedback(
        self,
        user_id: str,
        category: str,
        subject: str,
        content: str,
        rating: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Feedback:
        """Submit user feedback."""
        feedback = Feedback(
            id=f"feedback-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            user_id=user_id,
            category=category,
            subject=subject,
            content=content,
            rating=rating,
            tags=tags or [],
            status="new",
            priority="medium",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None
        )
        
        self.feedback[feedback.id] = feedback
        
        # Save feedback
        self._save_feedback(feedback)
        
        # Create issue if bug report
        if category == "bug":
            await self.create_issue(
                feedback_id=feedback.id,
                reporter_id=user_id,
                category="functional",
                title=subject,
                description=content,
                severity="medium",
                impact="under_investigation"
            )
        
        # Create feature request if feature suggestion
        elif category == "feature":
            await self.create_feature_request(
                feedback_id=feedback.id,
                requester_id=user_id,
                title=subject,
                description=content,
                use_case="Under review",
                business_value="Under evaluation"
            )
        
        self.logger.info(f"Feedback submitted: {feedback.id}")
        return feedback
    
    def _save_feedback(self, feedback: Feedback):
        """Save feedback to storage."""
        feedback_path = os.path.join(
            self.storage_path,
            "feedback",
            f"{feedback.id}.json"
        )
        
        with open(feedback_path, 'w') as f:
            json.dump(vars(feedback), f, default=str)
    
    async def create_issue(
        self,
        reporter_id: str,
        category: str,
        title: str,
        description: str,
        severity: str,
        impact: str,
        feedback_id: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Issue:
        """Create system issue."""
        issue = Issue(
            id=f"issue-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            feedback_id=feedback_id,
            reporter_id=reporter_id,
            category=category,
            title=title,
            description=description,
            severity=severity,
            impact=impact,
            status="open",
            assignee=assignee,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            resolved_at=None
        )
        
        self.issues[issue.id] = issue
        
        # Save issue
        self._save_issue(issue)
        
        self.logger.info(f"Issue created: {issue.id}")
        return issue
    
    def _save_issue(self, issue: Issue):
        """Save issue to storage."""
        issue_path = os.path.join(
            self.storage_path,
            "issues",
            f"{issue.id}.json"
        )
        
        with open(issue_path, 'w') as f:
            json.dump(vars(issue), f, default=str)
    
    async def create_feature_request(
        self,
        requester_id: str,
        title: str,
        description: str,
        use_case: str,
        business_value: str,
        feedback_id: Optional[str] = None
    ) -> FeatureRequest:
        """Create feature request."""
        feature = FeatureRequest(
            id=f"feature-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            feedback_id=feedback_id,
            requester_id=requester_id,
            title=title,
            description=description,
            use_case=use_case,
            business_value=business_value,
            priority="medium",
            status="under_review",
            votes=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            implemented_at=None
        )
        
        self.features[feature.id] = feature
        
        # Save feature request
        self._save_feature(feature)
        
        self.logger.info(f"Feature request created: {feature.id}")
        return feature
    
    def _save_feature(self, feature: FeatureRequest):
        """Save feature request to storage."""
        feature_path = os.path.join(
            self.storage_path,
            "features",
            f"{feature.id}.json"
        )
        
        with open(feature_path, 'w') as f:
            json.dump(vars(feature), f, default=str)
    
    def update_feedback(
        self,
        feedback_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Feedback:
        """Update feedback entry."""
        if feedback_id not in self.feedback:
            raise ValueError(f"Feedback not found: {feedback_id}")
        
        feedback = self.feedback[feedback_id]
        
        if status:
            feedback.status = status
            if status == "resolved":
                feedback.resolved_at = datetime.now()
        
        if priority:
            feedback.priority = priority
        
        feedback.updated_at = datetime.now()
        
        # Save updated feedback
        self._save_feedback(feedback)
        
        self.logger.info(f"Feedback updated: {feedback_id}")
        return feedback
    
    def update_issue(
        self,
        issue_id: str,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assignee: Optional[str] = None
    ) -> Issue:
        """Update issue entry."""
        if issue_id not in self.issues:
            raise ValueError(f"Issue not found: {issue_id}")
        
        issue = self.issues[issue_id]
        
        if status:
            issue.status = status
            if status == "resolved":
                issue.resolved_at = datetime.now()
        
        if severity:
            issue.severity = severity
        
        if assignee:
            issue.assignee = assignee
        
        issue.updated_at = datetime.now()
        
        # Save updated issue
        self._save_issue(issue)
        
        self.logger.info(f"Issue updated: {issue_id}")
        return issue
    
    def update_feature(
        self,
        feature_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        votes: Optional[int] = None
    ) -> FeatureRequest:
        """Update feature request."""
        if feature_id not in self.features:
            raise ValueError(f"Feature request not found: {feature_id}")
        
        feature = self.features[feature_id]
        
        if status:
            feature.status = status
            if status == "implemented":
                feature.implemented_at = datetime.now()
        
        if priority:
            feature.priority = priority
        
        if votes is not None:
            feature.votes = votes
        
        feature.updated_at = datetime.now()
        
        # Save updated feature
        self._save_feature(feature)
        
        self.logger.info(f"Feature request updated: {feature_id}")
        return feature
    
    def get_feedback_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get feedback statistics."""
        end_time = end_time or datetime.now()
        
        # Filter feedback entries
        entries = [
            f for f in self.feedback.values()
            if start_time <= f.created_at <= end_time
        ]
        
        if not entries:
            return {
                "total": 0,
                "by_category": {},
                "by_status": {},
                "average_rating": None
            }
        
        # Calculate statistics
        ratings = [
            f.rating for f in entries
            if f.rating is not None
        ]
        
        return {
            "total": len(entries),
            "by_category": {
                category: len([
                    f for f in entries
                    if f.category == category
                ])
                for category in {f.category for f in entries}
            },
            "by_status": {
                status: len([
                    f for f in entries
                    if f.status == status
                ])
                for status in {f.status for f in entries}
            },
            "average_rating": (
                statistics.mean(ratings)
                if ratings else None
            )
        }
    
    def get_issue_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get issue statistics."""
        end_time = end_time or datetime.now()
        
        # Filter issues
        issues = [
            i for i in self.issues.values()
            if start_time <= i.created_at <= end_time
        ]
        
        if not issues:
            return {
                "total": 0,
                "by_category": {},
                "by_severity": {},
                "by_status": {}
            }
        
        return {
            "total": len(issues),
            "by_category": {
                category: len([
                    i for i in issues
                    if i.category == category
                ])
                for category in {i.category for i in issues}
            },
            "by_severity": {
                severity: len([
                    i for i in issues
                    if i.severity == severity
                ])
                for severity in {i.severity for i in issues}
            },
            "by_status": {
                status: len([
                    i for i in issues
                    if i.status == status
                ])
                for status in {i.status for i in issues}
            }
        }
    
    def get_feature_stats(
        self,
        start_time: datetime,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get feature request statistics."""
        end_time = end_time or datetime.now()
        
        # Filter feature requests
        features = [
            f for f in self.features.values()
            if start_time <= f.created_at <= end_time
        ]
        
        if not features:
            return {
                "total": 0,
                "by_status": {},
                "by_priority": {},
                "top_voted": []
            }
        
        return {
            "total": len(features),
            "by_status": {
                status: len([
                    f for f in features
                    if f.status == status
                ])
                for status in {f.status for f in features}
            },
            "by_priority": {
                priority: len([
                    f for f in features
                    if f.priority == priority
                ])
                for priority in {f.priority for f in features}
            },
            "top_voted": sorted(
                [
                    {
                        "id": f.id,
                        "title": f.title,
                        "votes": f.votes
                    }
                    for f in features
                ],
                key=lambda x: x["votes"],
                reverse=True
            )[:5]
        }
    
    def get_status(self) -> Dict:
        """Get feedback system status."""
        now = datetime.now()
        
        return {
            "feedback": self.get_feedback_stats(
                start_time=datetime.min,
                end_time=now
            ),
            "issues": self.get_issue_stats(
                start_time=datetime.min,
                end_time=now
            ),
            "features": self.get_feature_stats(
                start_time=datetime.min,
                end_time=now
            ),
            "recent_activity": {
                "feedback": len([
                    f for f in self.feedback.values()
                    if (now - f.updated_at).days <= 7
                ]),
                "issues": len([
                    i for i in self.issues.values()
                    if (now - i.updated_at).days <= 7
                ]),
                "features": len([
                    f for f in self.features.values()
                    if (now - f.updated_at).days <= 7
                ])
            }
        }
