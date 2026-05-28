from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Credential(BaseModel):
    """Credential model for blockchain-verified certificates."""
    
    id: str
    user_id: str
    certificate_id: str
    blockchain_tx_hash: Optional[str] = None
    level: str = "Beginner"
    skills: List[str] = []
    issued_at: datetime = Field(default_factory=datetime.utcnow)
    verified: bool = False

    class Config:
        from_attributes = True


class CredentialCreate(BaseModel):
    """Schema for creating a new credential."""
    
    user_id: str
    certificate_id: str
    level: str = "Beginner"
    skills: List[str] = []


class CredentialResponse(BaseModel):
    """Schema for credential API responses."""
    
    id: str
    certificate_id: str
    level: str
    skills: List[str]
    overall_score: Optional[float] = None
    issued_at: datetime
    blockchain_tx_hash: Optional[str] = None
    verified: bool


class CredentialVerificationResponse(BaseModel):
    """Schema for public credential verification."""
    
    verified: bool
    certificate_id: Optional[str] = None
    user_name: Optional[str] = None
    level: Optional[str] = None
    skills: Optional[List[str]] = None
    issued_at: Optional[datetime] = None
    blockchain_tx_hash: Optional[str] = None
    verification_url: Optional[str] = None
    message: Optional[str] = None


class GenerateCredentialResponse(BaseModel):
    """Schema for generate credential API response."""
    
    success: bool
    credential: CredentialResponse