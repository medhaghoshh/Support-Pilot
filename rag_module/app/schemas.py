"""
SupportPilot AI

Pydantic schemas used by the API.

Includes:
- Ticket Creation
- Ticket Responses
- Resolution Output
- Escalation Information
- Optimization Metrics
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ===================================================
# Ticket Creation
# ===================================================

class TicketCreate(BaseModel):
    """
    Request body for creating a support ticket.
    """

    subject: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str = Field(
        ...,
        min_length=1,
    )

    requester_email: EmailStr

    department: Optional[str] = None


# ===================================================
# Ticket Response
# ===================================================

class TicketResponse(BaseModel):
    """
    Returned after creating or retrieving a ticket.
    """

    ticket_id: int
    user_id: int
    subject: str
    description: str
    priority: str
    severity: str
    status: str
    created_at: datetime
    requester_email: Optional[str] = None
    department: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }


# ===================================================
# Knowledge Base Article Used
# ===================================================

class ArticleUsed(BaseModel):
    """
    Knowledge Base article used to generate
    the AI response.
    """

    kb_id: str

    title: str

    category: str

    tags: str

    similarity_score: float

    model_config = {
        "from_attributes": True,
    }


# ===================================================
# Ticket Resolution Response
# ===================================================

class TicketResolveOut(BaseModel):
    """
    Returned after the AI workflow completes.
    """

    ticket_id: int

    generated_response: str

    confidence_score: float

    articles_used: list[ArticleUsed]

    status: str

    escalated: bool

    assigned_team: Optional[str] = None

    escalation_reason: Optional[str] = None

    generation_time_seconds: Optional[float] = None

    model_config = {
        "from_attributes": True,
    }


# ===================================================
# Feedback Schemas
# ===================================================

class FeedbackCreate(BaseModel):
    """
    Schema for user feedback.
    """
    rating: int = Field(..., ge=1, le=5)
    classification_correct: bool = True