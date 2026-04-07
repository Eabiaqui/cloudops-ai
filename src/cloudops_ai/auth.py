"""Authentication and JWT token handling."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os
from uuid import UUID

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

# Use argon2 (no byte limit like bcrypt), fallback to bcrypt
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65540,
    argon2__time_cost=3,
    argon2__parallelism=2,
)

class TokenData(BaseModel):
    tenant_id: str
    user_id: Optional[str] = None
    exp: datetime

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(tenant_id: UUID, user_id: Optional[UUID] = None, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "tenant_id": str(tenant_id),
        "user_id": str(user_id) if user_id else None,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[TokenData]:
    """Decode JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tenant_id: str = payload.get("tenant_id")
        user_id: Optional[str] = payload.get("user_id")
        
        if tenant_id is None:
            return None
        
        return TokenData(
            tenant_id=tenant_id,
            user_id=user_id,
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        )
    except JWTError:
        return None

def hash_api_key(api_key: str) -> str:
    """Hash API key for storage."""
    return pwd_context.hash(api_key)

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify API key."""
    return pwd_context.verify(plain_key, hashed_key)
