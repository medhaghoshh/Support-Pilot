"""
SupportPilot AI

Analytics Schemas

Pydantic models used by the
Analytics Dashboard (Milestone 4).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------
# Dashboard KPI Summary
# ---------------------------------------------------

class KPISummary(BaseModel):
    """
    High-level dashboard KPIs.
    """

    total_tickets_today: int = Field(
        ...,
        description="Total tickets currently recorded.",
    )

    ai_resolution_rate: float = Field(
        ...,
        description="Percentage of tickets resolved by AI.",
    )

    avg_resolution_time_minutes: float = Field(
        ...,
        description="Average ticket resolution time in minutes.",
    )

    user_satisfaction: Optional[float] = Field(
        default=None,
        description="Average user satisfaction score.",
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------
# Ticket Volume
# ---------------------------------------------------

class TicketVolumePoint(BaseModel):
    """
    Daily ticket volume.
    """

    day: str = Field(
        ...,
        description="Day label.",
    )

    received: int = Field(
        ...,
        description="Tickets received.",
    )

    resolved: int = Field(
        ...,
        description="Tickets resolved.",
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------
# Workflow / Escalation
# ---------------------------------------------------

class EscalationStageStatus(BaseModel):
    """
    Number of tickets in each workflow stage.
    """

    stage: str = Field(
        ...,
        description="Workflow stage.",
    )

    count: int = Field(
        ...,
        description="Number of tickets.",
    )

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------
# Optimization Metrics
# ---------------------------------------------------

class OptimizationMetrics(BaseModel):
    """
    Metrics produced by the optimization
    and analytics layer.
    """

    classification_accuracy: Optional[float] = Field(
        default=None,
        description="Diagnosis classification accuracy (%).",
    )

    resolution_success_rate: float = Field(
        ...,
        description="Resolution success rate (%).",
    )

    knowledge_base_coverage: float = Field(
        ...,
        description="Knowledge Base coverage (%).",
    )

    system_uptime: Optional[dict] = Field(
        default=None,
        description="Application uptime information.",
    )

    avg_response_generation_time_minutes: float = Field(
        ...,
        description="Average AI response generation time in minutes.",
    )

    user_satisfaction_score: Optional[float] = Field(
        default=None,
        description="Average user satisfaction score.",
    )

    model_config = ConfigDict(from_attributes=True)