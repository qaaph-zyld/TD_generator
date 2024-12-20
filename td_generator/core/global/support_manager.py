"""
International Support Management System for Global Customer Service.
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
import pytz
from babel import Locale, support
import schedule
import time
import threading
from queue import PriorityQueue
import jira
import zendesk
import freshdesk
import intercom

class SupportType(str, Enum):
    """Support types."""
    TECHNICAL = "technical"
    CUSTOMER = "customer"
    SALES = "sales"
    TRAINING = "training"

class RegionType(str, Enum):
    """Region types."""
    AMERICAS = "americas"
    EMEA = "emea"
    APAC = "apac"
    GLOBAL = "global"

class PriorityType(str, Enum):
    """Priority types."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TeamProfile:
    """Team profile definition."""
    id: str
    name: str
    type: SupportType
    region: RegionType
    languages: List[str]
    schedule: Dict[str, Any]
    capacity: Dict[str, float]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class SupportCase:
    """Support case definition."""
    id: str
    team_id: str
    type: SupportType
    priority: PriorityType
    language: str
    details: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

class SupportManager:
    """Manages international support and customer service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.teams: Dict[str, TeamProfile] = {}
        self.cases: Dict[str, List[SupportCase]] = {}
        self.storage_path = "data/global/support"
        self._initialize_storage()
        self._load_configuration()
        self._scheduler = schedule.Scheduler()
        self._case_queue = PriorityQueue()
        self._running = False
        self._schedule_thread = None
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "teams",
            "cases",
            "knowledge",
            "metrics",
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
            "support_types": [
                {
                    "type": "technical",
                    "skills": ["programming", "debugging"]
                },
                {
                    "type": "customer",
                    "skills": ["communication", "problem-solving"]
                },
                {
                    "type": "sales",
                    "skills": ["negotiation", "product-knowledge"]
                },
                {
                    "type": "training",
                    "skills": ["teaching", "documentation"]
                }
            ],
            "region_types": [
                {
                    "type": "americas",
                    "timezones": ["America/New_York", "America/Los_Angeles"]
                },
                {
                    "type": "emea",
                    "timezones": ["Europe/London", "Europe/Berlin"]
                },
                {
                    "type": "apac",
                    "timezones": ["Asia/Tokyo", "Asia/Singapore"]
                },
                {
                    "type": "global",
                    "timezones": ["all"]
                }
            ],
            "priority_types": [
                {
                    "type": "low",
                    "sla": "72h"
                },
                {
                    "type": "medium",
                    "sla": "24h"
                },
                {
                    "type": "high",
                    "sla": "4h"
                },
                {
                    "type": "critical",
                    "sla": "1h"
                }
            ],
            "language_support": {
                "americas": ["en", "es", "pt"],
                "emea": ["en", "fr", "de", "ar"],
                "apac": ["en", "zh", "ja", "ko"]
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_team(
        self,
        name: str,
        type: SupportType,
        region: RegionType,
        languages: List[str],
        schedule: Dict[str, Any]
    ) -> TeamProfile:
        """Create team profile."""
        # Validate languages
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        region_languages = config["language_support"][region]
        for lang in languages:
            if lang not in region_languages:
                raise ValueError(
                    f"Language {lang} not supported in region {region}"
                )
        
        # Create team profile
        profile = TeamProfile(
            id=f"team-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            region=region,
            languages=languages,
            schedule=schedule,
            capacity={
                "cases_per_hour": 5,
                "concurrent_cases": 10
            },
            metrics={},
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.teams[profile.id] = profile
        
        # Save team profile
        self._save_team(profile)
        
        # Schedule team shifts
        self._schedule_team(profile)
        
        self.logger.info(f"Team created: {profile.id}")
        return profile
    
    def _save_team(self, profile: TeamProfile):
        """Save team profile to storage."""
        profile_path = os.path.join(
            self.storage_path,
            "teams",
            f"{profile.id}.json"
        )
        
        with open(profile_path, 'w') as f:
            json.dump(vars(profile), f, default=str)
    
    def _schedule_team(self, profile: TeamProfile):
        """Schedule team shifts."""
        for day, shifts in profile.schedule.items():
            for shift in shifts:
                start_time = shift["start"]
                end_time = shift["end"]
                
                # Schedule shift start
                getattr(self._scheduler.every(), day.lower()).at(
                    start_time
                ).do(self._start_shift, profile.id)
                
                # Schedule shift end
                getattr(self._scheduler.every(), day.lower()).at(
                    end_time
                ).do(self._end_shift, profile.id)
    
    def _start_shift(self, team_id: str):
        """Start team shift."""
        team = self.teams[team_id]
        team.status = "active"
        team.updated_at = datetime.now()
        self._save_team(team)
        self.logger.info(f"Started shift for team: {team_id}")
    
    def _end_shift(self, team_id: str):
        """End team shift."""
        team = self.teams[team_id]
        team.status = "inactive"
        team.updated_at = datetime.now()
        self._save_team(team)
        self.logger.info(f"Ended shift for team: {team_id}")
    
    async def create_case(
        self,
        type: SupportType,
        priority: PriorityType,
        language: str,
        details: Dict[str, Any]
    ) -> SupportCase:
        """Create support case."""
        # Find available team
        team = await self._find_team(type, language)
        if not team:
            raise ValueError(
                f"No available team for {type} support in {language}"
            )
        
        # Create case
        case = SupportCase(
            id=f"case-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            team_id=team.id,
            type=type,
            priority=priority,
            language=language,
            details=details,
            status="open",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if team.id not in self.cases:
            self.cases[team.id] = []
        
        self.cases[team.id].append(case)
        
        # Save case
        self._save_case(case)
        
        # Add to priority queue
        self._case_queue.put((
            self._get_priority_value(priority),
            case.id,
            case
        ))
        
        self.logger.info(f"Case created: {case.id}")
        return case
    
    def _save_case(self, case: SupportCase):
        """Save support case to storage."""
        case_path = os.path.join(
            self.storage_path,
            "cases",
            f"{case.id}.json"
        )
        
        with open(case_path, 'w') as f:
            json.dump(vars(case), f, default=str)
    
    async def _find_team(
        self,
        type: SupportType,
        language: str
    ) -> Optional[TeamProfile]:
        """Find available team for case."""
        available_teams = [
            team for team in self.teams.values()
            if team.type == type
            and language in team.languages
            and team.status == "active"
            and len(self.cases.get(team.id, [])) < team.capacity["concurrent_cases"]
        ]
        
        if not available_teams:
            return None
        
        # Return team with lowest current load
        return min(
            available_teams,
            key=lambda t: len(self.cases.get(t.id, []))
        )
    
    def _get_priority_value(self, priority: PriorityType) -> int:
        """Get numeric priority value."""
        return {
            PriorityType.LOW: 3,
            PriorityType.MEDIUM: 2,
            PriorityType.HIGH: 1,
            PriorityType.CRITICAL: 0
        }[priority]
    
    def start(self):
        """Start support scheduler."""
        if not self._running:
            self._running = True
            self._schedule_thread = threading.Thread(
                target=self._run_scheduler
            )
            self._schedule_thread.start()
            self.logger.info("Support scheduler started")
    
    def stop(self):
        """Stop support scheduler."""
        if self._running:
            self._running = False
            if self._schedule_thread:
                self._schedule_thread.join()
            self.logger.info("Support scheduler stopped")
    
    def _run_scheduler(self):
        """Run scheduler loop."""
        while self._running:
            self._scheduler.run_pending()
            self._process_cases()
            time.sleep(1)
    
    def _process_cases(self):
        """Process support cases."""
        while not self._case_queue.empty():
            _, case_id, case = self._case_queue.get()
            
            # Check if case is still open
            if case.status != "open":
                continue
            
            # Check if assigned team is active
            team = self.teams.get(case.team_id)
            if not team or team.status != "active":
                # Reassign case
                self._reassign_case(case)
                continue
            
            # Process case based on type
            if case.type == SupportType.TECHNICAL:
                self._process_technical_case(case)
            elif case.type == SupportType.CUSTOMER:
                self._process_customer_case(case)
            elif case.type == SupportType.SALES:
                self._process_sales_case(case)
            elif case.type == SupportType.TRAINING:
                self._process_training_case(case)
    
    def _reassign_case(self, case: SupportCase):
        """Reassign case to new team."""
        asyncio.create_task(self._find_and_reassign(case))
    
    async def _find_and_reassign(self, case: SupportCase):
        """Find new team and reassign case."""
        new_team = await self._find_team(case.type, case.language)
        if new_team:
            # Update case
            case.team_id = new_team.id
            case.updated_at = datetime.now()
            self._save_case(case)
            
            # Add to new team's cases
            if new_team.id not in self.cases:
                self.cases[new_team.id] = []
            self.cases[new_team.id].append(case)
            
            # Add back to queue
            self._case_queue.put((
                self._get_priority_value(case.priority),
                case.id,
                case
            ))
    
    def _process_technical_case(self, case: SupportCase):
        """Process technical support case."""
        # Implement technical support workflow
        pass
    
    def _process_customer_case(self, case: SupportCase):
        """Process customer support case."""
        # Implement customer support workflow
        pass
    
    def _process_sales_case(self, case: SupportCase):
        """Process sales support case."""
        # Implement sales support workflow
        pass
    
    def _process_training_case(self, case: SupportCase):
        """Process training support case."""
        # Implement training support workflow
        pass
    
    def get_team_stats(
        self,
        type: Optional[SupportType] = None,
        region: Optional[RegionType] = None
    ) -> Dict[str, Any]:
        """Get team statistics."""
        teams = self.teams.values()
        
        if type:
            teams = [t for t in teams if t.type == type]
        
        if region:
            teams = [t for t in teams if t.region == region]
        
        if not teams:
            return {
                "total": 0,
                "by_type": {},
                "by_region": {},
                "by_status": {}
            }
        
        return {
            "total": len(teams),
            "by_type": {
                type: len([
                    t for t in teams
                    if t.type == type
                ])
                for type in {t.type for t in teams}
            },
            "by_region": {
                region: len([
                    t for t in teams
                    if t.region == region
                ])
                for region in {t.region for t in teams}
            },
            "by_status": {
                status: len([
                    t for t in teams
                    if t.status == status
                ])
                for status in {t.status for t in teams}
            }
        }
    
    def get_case_stats(
        self,
        team_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get case statistics."""
        if team_id:
            cases = self.cases.get(team_id, [])
        else:
            cases = []
            for case_list in self.cases.values():
                cases.extend(case_list)
        
        if not cases:
            return {
                "total": 0,
                "by_type": {},
                "by_priority": {},
                "by_status": {}
            }
        
        return {
            "total": len(cases),
            "by_type": {
                type: len([
                    c for c in cases
                    if c.type == type
                ])
                for type in {c.type for c in cases}
            },
            "by_priority": {
                priority: len([
                    c for c in cases
                    if c.priority == priority
                ])
                for priority in {c.priority for c in cases}
            },
            "by_status": {
                status: len([
                    c for c in cases
                    if c.status == status
                ])
                for status in {c.status for c in cases}
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get support manager status."""
        return {
            "teams": self.get_team_stats(),
            "cases": self.get_case_stats(),
            "health_summary": {
                "team_health": all(
                    team.status in ["active", "inactive"]
                    for team in self.teams.values()
                ),
                "case_health": all(
                    case.status != "error"
                    for cases in self.cases.values()
                    for case in cases
                ),
                "scheduler_health": self._running
            }
        }
