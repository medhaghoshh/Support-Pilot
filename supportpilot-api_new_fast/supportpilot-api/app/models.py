from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# -------------------------
# USERS TABLE
# -------------------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    department = Column(String(100))
    role = Column(
        Enum("EMPLOYEE", "SUPPORT_ENGINEER", "ADMIN"),
        nullable=False,
        default="EMPLOYEE"
    )
    created_at = Column(TIMESTAMP, server_default=func.now())

    tickets = relationship("Ticket", back_populates="user")


# -------------------------
# TICKETS TABLE
# -------------------------
class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    priority = Column(
        Enum("P1", "P2", "P3", "P4"),
        nullable=False,
        default="P4"
    )

    severity = Column(
        Enum("LOW", "MEDIUM", "HIGH", "CRITICAL"),
        nullable=False,
        default="LOW"
    )

    status = Column(
        Enum("OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"),
        nullable=False,
        default="OPEN"
    )

    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="tickets")


# -------------------------
# TICKET RESPONSES
# -------------------------
class TicketResponse(Base):
    __tablename__ = "ticket_responses"

    response_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)

    generated_response = Column(Text)
    confidence_score = Column(Float)
    generated_at = Column(TIMESTAMP, server_default=func.now())


# -------------------------
# ACTIVITY LOGS
# -------------------------
class ActivityLog(Base):
    __tablename__ = "activity_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)

    action = Column(String(255), nullable=False)
    performed_by = Column(String(100))
    timestamp = Column(TIMESTAMP, server_default=func.now())


# -------------------------
# ESCALATIONS
# -------------------------
class Escalation(Base):
    __tablename__ = "escalations"

    escalation_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)

    assigned_team = Column(String(100))
    escalation_reason = Column(String(255))

    status = Column(
        Enum("PENDING", "IN_PROGRESS", "RESOLVED"),
        nullable=False,
        default="PENDING"
    )

    created_at = Column(TIMESTAMP, server_default=func.now())


# -------------------------
# JIRA TICKETS
# -------------------------
class JiraTicket(Base):
    __tablename__ = "jira_tickets"

    jira_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.ticket_id"), nullable=False)

    jira_issue_key = Column(String(50), unique=True)
    jira_status = Column(String(50))
    last_updated = Column(TIMESTAMP, server_default=func.now())


# -------------------------
# KNOWLEDGE BASE
# -------------------------
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    article_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )