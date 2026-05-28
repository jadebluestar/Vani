from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Tutor(BaseModel):
    """Tutor model for peer tutoring platform."""
    
    id: str
    user_id: str
    languages: List[str] = []
    hourly_rate: int = 0
    rating: float = 0.0
    total_sessions: int = 0
    verified: bool = False
    bio: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class TutorCreate(BaseModel):
    """Schema for creating a new tutor profile."""
    
    user_id: str
    languages: List[str]
    hourly_rate: int
    bio: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None


class TutorUpdate(BaseModel):
    """Schema for updating tutor profile."""
    
    languages: Optional[List[str]] = None
    hourly_rate: Optional[int] = None
    bio: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None


class TutorResponse(BaseModel):
    """Schema for tutor API responses."""
    
    id: str
    user_id: str
    name: str
    languages: List[str]
    hourly_rate: int
    rating: float
    total_sessions: int
    verified: bool
    bio: Optional[str] = None
    district: Optional[str] = None


class TutorSession(BaseModel):
    """Tutor session model for booked sessions."""
    
    id: str
    tutor_id: str
    learner_id: str
    status: str = "scheduled"
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_minutes: int = 60
    amount_paid: int = 0
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class TutorSessionCreate(BaseModel):
    """Schema for creating a tutor session booking."""
    
    tutor_id: str
    scheduled_at: datetime
    duration_minutes: int = 60


class TutorSessionComplete(BaseModel):
    """Schema for completing a tutor session."""
    
    rating: float
    feedback: Optional[str] = None


class TutorSessionResponse(BaseModel):
    """Schema for tutor session API responses."""
    
    id: str
    tutor_name: str
    learner_name: str
    status: str
    scheduled_at: datetime
    duration_minutes: int
    amount_paid: int
    rating: Optional[float] = None
    feedback: Optional[str] = None