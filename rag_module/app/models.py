"""
SupportPilot AI

Database Models

Defines all SQLAlchemy ORM models used by
SupportPilot.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# ===================================================
# USERS
# ===================================================

class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    email = Column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    department = Column(
        String(100),
        nullable=True,
    )

    role = Column(
        Enum(
            "EMPLOYEE",
            "SUPPORT_ENGINEER",
            "ADMIN",
        ),
        nullable=False,
        default="EMPLOYEE",
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    tickets = relationship(
        "Ticket",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<User "
            f"{self.user_id}: "
            f"{self.email}>"
        )


# ===================================================
# TICKETS
# ===================================================

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True,
    )

    subject = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    priority = Column(
        Enum(
            "P1",
            "P2",
            "P3",
            "P4",
        ),
        nullable=False,
        default="P4",
    )

    severity = Column(
        Enum(
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ),
        nullable=False,
        default="LOW",
    )

    status = Column(
        Enum(
            "OPEN",
            "IN_PROGRESS",
            "RESOLVED",
            "CLOSED",
        ),
        nullable=False,
        default="OPEN",
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    # ---------------------------------------------------
    # Relationships
    # ---------------------------------------------------

    user = relationship(
        "User",
        back_populates="tickets",
    )

    responses = relationship(
        "TicketResponse",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    activity_logs = relationship(
        "ActivityLog",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    escalations = relationship(
        "Escalation",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    jira_tickets = relationship(
        "JiraTicket",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    workflow_logs = relationship(
        "WorkflowLog",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    feedbacks = relationship(
        "Feedback",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )

    @property
    def requester_email(self) -> str:
        return self.user.email if self.user else ""

    @property
    def department(self) -> str:
        return self.user.department if self.user else ""

    def __repr__(self) -> str:
        return (
            f"<Ticket "
            f"{self.ticket_id}: "
            f"{self.subject}>"
        )

# ===================================================
# AI RESPONSES
# ===================================================

class TicketResponse(Base):
    __tablename__ = "ticket_responses"

    response_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    generated_response = Column(
        Text,
        nullable=False,
    )

    confidence_score = Column(
        Float,
        nullable=False,
    )

    generated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="responses",
    )


# ===================================================
# ACTIVITY LOGS
# ===================================================

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    log_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    action = Column(
        String(255),
        nullable=False,
    )

    performed_by = Column(
        String(100),
        nullable=True,
    )

    timestamp = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="activity_logs",
    )


# ===================================================
# ESCALATIONS
# ===================================================

class Escalation(Base):
    __tablename__ = "escalations"

    escalation_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    assigned_team = Column(
        String(100),
        nullable=False,
    )

    escalation_reason = Column(
        String(255),
        nullable=False,
    )

    status = Column(
        Enum(
            "OPEN",
            "IN_PROGRESS",
            "RESOLVED",
            "CLOSED",
        ),
        nullable=False,
        default="OPEN",
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="escalations",
    )


# ===================================================
# JIRA
# ===================================================

class JiraTicket(Base):
    __tablename__ = "jira_tickets"

    jira_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    jira_issue_key = Column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    jira_status = Column(
        String(50),
        nullable=False,
    )

    last_updated = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="jira_tickets",
    )

# ===================================================
# KNOWLEDGE BASE
# ===================================================

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    article_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeBase "
            f"{self.article_id}: "
            f"{self.title}>"
        )


# ===================================================
# WORKFLOW LOGS
# ===================================================

class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    agent_name = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
    )

    message = Column(
        String(500),
        nullable=False,
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="workflow_logs",
    )

    def __repr__(self) -> str:
        return (
            f"<WorkflowLog "
            f"{self.id} "
            f"Ticket={self.ticket_id} "
            f"Agent={self.agent_name}>"
        )


# ===================================================
# FEEDBACK
# ===================================================

class Feedback(Base):
    __tablename__ = "feedbacks"

    feedback_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.ticket_id"),
        nullable=False,
        index=True,
    )

    rating = Column(
        Integer,
        nullable=False,
    )

    classification_correct = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    ticket = relationship(
        "Ticket",
        back_populates="feedbacks",
    )

    def __repr__(self) -> str:
        return (
            f"<Feedback "
            f"{self.feedback_id} "
            f"Ticket={self.ticket_id} "
            f"Rating={self.rating}>"
        )


# ===================================================
# Public Exports
# ===================================================

__all__ = [
    "User",
    "Ticket",
    "TicketResponse",
    "ActivityLog",
    "Escalation",
    "JiraTicket",
    "KnowledgeBase",
    "WorkflowLog",
    "Feedback",
]