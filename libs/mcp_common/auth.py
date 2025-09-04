"""
Authentication utilities for MCP servers.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet

from .exceptions import AuthenticationError, ConfigurationError
from .config import get_config


class AuthConfig:
    """Authentication configuration."""
    
    def __init__(self, secret_key: Optional[str] = None):
        """Initialize auth configuration."""
        config = get_config()
        self.secret_key = secret_key or config.secret_key
        self.jwt_expiration = config.jwt_expiration
    
    def get_secret_key(self) -> str:
        """Get the secret key for JWT signing."""
        if not self.secret_key:
            raise ConfigurationError("Secret key not configured")
        return self.secret_key


class AuthenticationManager:
    """Manages authentication for MCP servers."""
    
    def __init__(self, config: Optional[AuthConfig] = None):
        """Initialize authentication manager."""
        self.config = config or AuthConfig()
        self._encryption_key = None
    
    def get_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        if self._encryption_key is None:
            # Use the secret key to derive an encryption key
            secret = self.config.get_secret_key().encode()
            # Pad or truncate to 32 bytes for Fernet
            key = secret[:32].ljust(32, b'0')
            self._encryption_key = Fernet.generate_key()
        return self._encryption_key
    
    def create_token(self, user_id: str, **claims) -> str:
        """Create a JWT token for a user."""
        try:
            payload = {
                'user_id': user_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.config.jwt_expiration),
                **claims
            }
            
            token = jwt.encode(
                payload,
                self.config.get_secret_key(),
                algorithm='HS256'
            )
            return token
            
        except Exception as e:
            raise AuthenticationError(f"Failed to create token: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.config.get_secret_key(),
                algorithms=['HS256']
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        try:
            f = Fernet(self.get_encryption_key())
            encrypted_data = f.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            raise AuthenticationError(f"Failed to encrypt data: {str(e)}")
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        try:
            f = Fernet(self.get_encryption_key())
            decrypted_data = f.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            raise AuthenticationError(f"Failed to decrypt data: {str(e)}")
    
    def validate_api_key(self, api_key: str, service: str) -> bool:
        """Validate an API key for a service."""
        if not api_key:
            return False
        
        # Check if it's a valid format (basic validation)
        if len(api_key) < 10:
            return False
        
        # Service-specific validation could be added here
        return True
