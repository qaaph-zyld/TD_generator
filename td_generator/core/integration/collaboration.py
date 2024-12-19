"""
Collaboration system for multi-user support.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import asyncio
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    role: str
    active: bool
    last_active: datetime

@dataclass
class Comment:
    id: str
    user_id: str
    content: str
    timestamp: datetime
    resolved: bool
    replies: List['Comment']

@dataclass
class Change:
    id: str
    user_id: str
    file_path: str
    content: str
    timestamp: datetime
    status: str  # pending, approved, rejected

class Session:
    """Manages a collaborative editing session."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.users: Dict[str, User] = {}
        self.changes: List[Change] = []
        self.comments: Dict[str, Comment] = {}
        self.locks: Dict[str, str] = {}  # file_path -> user_id
        self.logger = logging.getLogger(__name__)
    
    def add_user(self, user: User):
        """Add user to session."""
        self.users[user.id] = user
        self.logger.info(f"User {user.name} joined session {self.session_id}")
    
    def remove_user(self, user_id: str):
        """Remove user from session."""
        if user_id in self.users:
            user = self.users.pop(user_id)
            self.logger.info(f"User {user.name} left session {self.session_id}")
            
            # Release any locks held by user
            self._release_user_locks(user_id)
    
    def add_comment(self, comment: Comment):
        """Add comment to session."""
        self.comments[comment.id] = comment
        self.logger.info(f"Comment added by user {comment.user_id}")
    
    def resolve_comment(self, comment_id: str):
        """Mark comment as resolved."""
        if comment_id in self.comments:
            self.comments[comment_id].resolved = True
            self.logger.info(f"Comment {comment_id} marked as resolved")
    
    def propose_change(self, change: Change):
        """Propose a change for review."""
        self.changes.append(change)
        self.logger.info(f"Change proposed by user {change.user_id}")
    
    def approve_change(self, change_id: str):
        """Approve a proposed change."""
        for change in self.changes:
            if change.id == change_id:
                change.status = 'approved'
                self.logger.info(f"Change {change_id} approved")
                break
    
    def reject_change(self, change_id: str):
        """Reject a proposed change."""
        for change in self.changes:
            if change.id == change_id:
                change.status = 'rejected'
                self.logger.info(f"Change {change_id} rejected")
                break
    
    def acquire_lock(self, user_id: str, file_path: str) -> bool:
        """Attempt to acquire lock on file."""
        if file_path not in self.locks:
            self.locks[file_path] = user_id
            self.logger.info(f"User {user_id} acquired lock on {file_path}")
            return True
        return False
    
    def release_lock(self, user_id: str, file_path: str) -> bool:
        """Release lock on file."""
        if file_path in self.locks and self.locks[file_path] == user_id:
            del self.locks[file_path]
            self.logger.info(f"User {user_id} released lock on {file_path}")
            return True
        return False
    
    def _release_user_locks(self, user_id: str):
        """Release all locks held by user."""
        locked_files = [
            file_path
            for file_path, lock_holder in self.locks.items()
            if lock_holder == user_id
        ]
        
        for file_path in locked_files:
            self.release_lock(user_id, file_path)

class CollaborationSystem:
    """Manages collaborative editing sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_session(self, session_id: str) -> Session:
        """Create new collaborative session."""
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        session = Session(session_id)
        self.sessions[session_id] = session
        self.logger.info(f"Created new session {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Session:
        """Get existing session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.sessions[session_id]
    
    def close_session(self, session_id: str):
        """Close and cleanup session."""
        if session_id in self.sessions:
            session = self.sessions.pop(session_id)
            self.logger.info(f"Closed session {session_id}")
    
    def list_sessions(self) -> List[str]:
        """List all active sessions."""
        return list(self.sessions.keys())
    
    async def monitor_sessions(self):
        """Monitor and cleanup inactive sessions."""
        while True:
            try:
                current_time = datetime.now()
                
                for session_id, session in list(self.sessions.items()):
                    # Remove inactive users
                    inactive_users = [
                        user_id
                        for user_id, user in session.users.items()
                        if (current_time - user.last_active).total_seconds() > 3600
                    ]
                    
                    for user_id in inactive_users:
                        session.remove_user(user_id)
                    
                    # Close empty sessions
                    if not session.users:
                        self.close_session(session_id)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Session monitoring error: {str(e)}")
                await asyncio.sleep(60)  # Retry after 1 minute
