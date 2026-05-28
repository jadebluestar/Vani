from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Progress(BaseModel):
    """Progress model for tracking user skill development."""
    
    id: str
    user_id: str
    skill: str
    score: float = 0.0
    trend: float = 0.0
    history: List[Dict[str, Any]] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    """Schema for updating progress scores."""
    
    fluency: Optional[float] = None
    pronunciation: Optional[float] = None
    grammar: Optional[float] = None
    vocabulary: Optional[float] = None
    speaking: Optional[float] = None
    listening: Optional[float] = None


class SkillScore(BaseModel):
    """Schema for individual skill score."""
    
    score: float
    trend: float
    history: List[Dict[str, Any]]


class DashboardResponse(BaseModel):
    """Schema for dashboard API response."""
    
    user_name: str
    preferred_language: str
    total_practice_minutes: int
    total_sessions: int
    confidence_score: float
    streak_days: int
    coins_balance: int
    weekly_activity: List[Dict[str, Any]]
    session_breakdown: Dict[str, int]
    skill_summary: Dict[str, float]


class ConfidenceTimelinePoint(BaseModel):
    """Schema for confidence timeline data point."""
    
    date: str
    confidence: Optional[float]
    sessions: int


class Recommendation(BaseModel):
    """Schema for AI-generated recommendation."""
    
    priority: str
    skill: str
    recommendation: str
    time_required: str
    exercise_type: str