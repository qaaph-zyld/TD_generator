"""
Security system for authentication and authorization.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import jwt
import bcrypt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

@dataclass
class User:
    id: str
    username: str
    password_hash: str
    role: str
    permissions: List[str]

@dataclass
class Session:
    id: str
    user_id: str
    token: str
    expires_at: datetime

class AuthenticationManager:
    """Manages user authentication."""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_user(self, username: str, password: str, role: str) -> User:
        """Register new user."""
        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )
        
        user = User(
            id=f"user_{len(self.users)}",
            username=username,
            password_hash=password_hash,
            role=role,
            permissions=self._get_role_permissions(role)
        )
        
        self.users[user.id] = user
        self.logger.info(f"Registered user {username}")
        return user
    
    def authenticate(self, username: str, password: str) -> Optional[Session]:
        """Authenticate user and create session."""
        user = next(
            (u for u in self.users.values() if u.username == username),
            None
        )
        
        if user and bcrypt.checkpw(
            password.encode('utf-8'),
            user.password_hash
        ):
            # Create JWT token
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'role': user.role,
                    'exp': datetime.utcnow() + timedelta(hours=1)
                },
                self.secret_key,
                algorithm='HS256'
            )
            
            session = Session(
                id=f"session_{len(self.sessions)}",
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            
            self.sessions[session.id] = session
            self.logger.info(f"User {username} authenticated")
            return session
        
        return None
    
    def validate_session(self, token: str) -> Optional[User]:
        """Validate session token."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=['HS256']
            )
            user_id = payload['user_id']
            
            if user_id in self.users:
                return self.users[user_id]
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Session token expired")
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid session token")
        
        return None
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for role."""
        permissions = {
            'admin': [
                'read', 'write', 'delete', 'manage_users'
            ],
            'editor': [
                'read', 'write'
            ],
            'viewer': [
                'read'
            ]
        }
        return permissions.get(role, [])

class AuthorizationManager:
    """Manages user authorization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has required permission."""
        return required_permission in user.permissions
    
    def validate_access(self,
                       user: User,
                       resource: str,
                       action: str) -> bool:
        """Validate user access to resource."""
        required_permission = f"{action}_{resource}"
        return self.check_permission(user, action)

class EncryptionManager:
    """Manages data encryption."""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.key = encryption_key.encode() if encryption_key else Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.logger = logging.getLogger(__name__)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data."""
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data."""
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise

class AuditLogger:
    """Manages security audit logging."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_auth_event(self, event_type: str, user_id: str, details: Dict):
        """Log authentication event."""
        self.logger.info(
            f"Auth event: {event_type}, User: {user_id}, Details: {details}"
        )
    
    def log_access_event(self,
                        event_type: str,
                        user_id: str,
                        resource: str,
                        action: str):
        """Log resource access event."""
        self.logger.info(
            f"Access event: {event_type}, User: {user_id}, "
            f"Resource: {resource}, Action: {action}"
        )

class SecuritySystem:
    """Manages security system."""
    
    def __init__(self, secret_key: str):
        self.auth = AuthenticationManager(secret_key)
        self.authz = AuthorizationManager()
        self.encryption = EncryptionManager()
        self.audit = AuditLogger()
        self.logger = logging.getLogger(__name__)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Session]:
        """Authenticate user."""
        try:
            session = self.auth.authenticate(username, password)
            if session:
                self.audit.log_auth_event(
                    'login_success',
                    session.user_id,
                    {'username': username}
                )
            else:
                self.audit.log_auth_event(
                    'login_failure',
                    'unknown',
                    {'username': username}
                )
            return session
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def validate_access(self,
                       token: str,
                       resource: str,
                       action: str) -> bool:
        """Validate user access."""
        try:
            user = self.auth.validate_session(token)
            if not user:
                return False
            
            has_access = self.authz.validate_access(user, resource, action)
            self.audit.log_access_event(
                'access_check',
                user.id,
                resource,
                action
            )
            
            return has_access
            
        except Exception as e:
            self.logger.error(f"Access validation failed: {str(e)}")
            raise
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            return self.encryption.encrypt(data)
        except Exception as e:
            self.logger.error(f"Data encryption failed: {str(e)}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            return self.encryption.decrypt(encrypted_data)
        except Exception as e:
            self.logger.error(f"Data decryption failed: {str(e)}")
            raise
