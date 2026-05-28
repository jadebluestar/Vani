from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Interview(BaseModel):
    """Interview model for storing mock interview attempts."""
    
    id: str
    user_id: str
    question: str
    user_answer: str
    ai_feedback: Optional[Dict[str, Any]] = None
    question_category: str = "behavioral"
    difficulty_level: int = 1
    score: Optional[float] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class InterviewCreate(BaseModel):
    """Schema for creating a new interview entry."""
    
    user_id: str
    question: str
    user_answer: str
    ai_feedback: Optional[Dict[str, Any]] = None
    question_category: str = "behavioral"
    difficulty_level: int = 1
    score: Optional[float] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None


class InterviewResponse(BaseModel):
    """Schema for interview API responses."""
    
    id: str
    question: str
    user_answer: str
    ai_feedback: Optional[Dict[str, Any]] = None
    question_category: str
    difficulty_level: int
    score: Optional[float] = None
    strengths: Optional[List[str]] = None
    improvements: Optional[List[str]] = None
    created_at: datetime


class InterviewQuestion(BaseModel):
    """Schema for interview question."""
    
    id: str
    question: str
    category: str
    difficulty: int
    ai_generated: bool = False


class InterviewEvaluationResponse(BaseModel):
    """Schema for interview evaluation API response."""
    
    success: bool
    interview_id: Optional[str] = None
    score: float
    evaluation: Dict[str, Any]
    question: str