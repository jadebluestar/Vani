from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class User(BaseModel):
    """User model for Vani platform."""
    
    id: str
    phone: str
    name: Optional[str] = None
    preferred_language: str = "kn"
    district: Optional[str] = None
    is_tutor: bool = False
    tutor_verified: bool = False
    coins_balance: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    
    phone: str
    name: Optional[str] = None
    preferred_language: str = "kn"
    district: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating an existing user."""
    
    name: Optional[str] = None
    preferred_language: Optional[str] = None
    district: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user API responses."""
    
    id: str
    phone: str
    name: Optional[str] = None
    preferred_language: str
    district: Optional[str] = None
    is_tutor: bool
    tutor_verified: bool
    coins_balance: int
    created_at: datetime
    last_active: datetime