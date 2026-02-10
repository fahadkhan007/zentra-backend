"""
Pydantic schemas for chat API endpoints
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# ============================================================================
# Request Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Request schema for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    include_sources: bool = Field(default=True, description="Whether to include source documents in response")


# ============================================================================
# Response Schemas - Sources
# ============================================================================

class Source(BaseModel):
    """Source document metadata"""
    name: str = Field(..., description="Source name (exercise name or document title)")
    type: str = Field(..., description="Source type (exercise, pdf, etc.)")
    body_part: Optional[str] = Field(None, description="Body part for exercises")
    equipment: Optional[str] = Field(None, description="Equipment needed for exercises")
    page: Optional[int] = Field(None, description="Page number for PDF sources")


# ============================================================================
# Response Schemas - Messages
# ============================================================================

class ChatMessageResponse(BaseModel):
    """Single chat message response"""
    id: UUID
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    sources: Optional[List[Source]] = Field(None, description="Sources (only for assistant messages)")
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Response for a single chat interaction"""
    message: ChatMessageResponse  # The AI's response message
    session_id: UUID
    
    class Config:
        from_attributes = True


# ============================================================================
# Response Schemas - Sessions
# ============================================================================

class ChatSessionSummary(BaseModel):
    """Summary of a chat session (for sidebar list)"""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = Field(None, description="Number of messages in session")
    
    class Config:
        from_attributes = True


class ChatSessionDetail(BaseModel):
    """Detailed chat session with all messages"""
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse]
    
    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    """Response for listing all chat sessions"""
    sessions: List[ChatSessionSummary]
    total: int


# ============================================================================
# Request Schemas - Session Management
# ============================================================================

class UpdateSessionTitleRequest(BaseModel):
    """Request to update session title"""
    title: str = Field(..., min_length=1, max_length=200)
