from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """Conversation model for storing AI coaching sessions."""
    
    id: str
    user_id: str
    language: str = "en"
    user_message: str
    ai_response: str
    feedback: Optional[Dict[str, Any]] = None
    fluency_score: Optional[float] = None
    pronunciation_score: Optional[float] = None
    grammar_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation entry."""
    
    user_id: str
    language: str
    user_message: str
    ai_response: str
    feedback: Optional[Dict[str, Any]] = None
    fluency_score: Optional[float] = None
    pronunciation_score: Optional[float] = None
    grammar_score: Optional[float] = None


class ConversationResponse(BaseModel):
    """Schema for conversation API responses."""
    
    id: str
    language: str
    user_message: str
    ai_response: str
    feedback: Optional[Dict[str, Any]] = None
    fluency_score: Optional[float] = None
    pronunciation_score: Optional[float] = None
    grammar_score: Optional[float] = None
    created_at: datetime
    is_saved: bool = False


class ConversationHistoryResponse(BaseModel):
    """Schema for paginated conversation history."""
    
    conversations: List[ConversationResponse]
    total: int
    page: int
    per_page: int
    pages: int