"""
SupportPilot AI

Analytics Router

Exposes analytics endpoints used by the
Milestone 4 dashboard.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics import (
    KPISummary,
    TicketVolumePoint,
    EscalationStageStatus,
)
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.coverage_analyzer import official_coverage, gap_analysis
from app.services.coverage_report import build_report
from app.services.sample_ticket_data import get_sample_tickets

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ---------------------------------------------------
# Dashboard Summary
# ---------------------------------------------------

@router.get(
    "/summary",
    response_model=dict,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """
    Returns the analytics dashboard summary.
    """

    return AnalyticsService.get_dashboard_summary(db)


# ---------------------------------------------------
# Ticket Volume
# ---------------------------------------------------

@router.get(
    "/ticket-volume",
    response_model=list[TicketVolumePoint],
)
def get_ticket_volume(
    db: Session = Depends(get_db),
):
    """
    Returns ticket volume statistics.

    Placeholder until historical
    ticket analytics are implemented.
    """

    return []


# ---------------------------------------------------
# Escalation Status
# ---------------------------------------------------

@router.get(
    "/escalation-status",
    response_model=list[EscalationStageStatus],
)
def get_escalation_status(
    db: Session = Depends(get_db),
):
    """
    Returns workflow stage counts.

    Placeholder until workflow
    aggregation is implemented.
    """

    return []


# ---------------------------------------------------
# KB Coverage (Milestone 4)
# ---------------------------------------------------

@router.get(
    "/kb-coverage",
    response_model=dict,
    summary="Knowledge Base Coverage",
)
def get_kb_coverage():
    """
    Knowledge Base Coverage metric for the dashboard.

    Returns both the official coverage number (any retrieval = a match,
    matching Role 3's definition) and the effective coverage after
    applying a similarity threshold, so the dashboard can show the honest
    picture alongside the headline number.
    """
    tickets = get_sample_tickets()
    official = official_coverage(tickets)
    deeper = gap_analysis(tickets)
    return {
        "official_coverage_pct": official["coverage_pct"],
        "effective_coverage_pct": deeper["effective_coverage_pct"],
        "total_tickets": official["total_tickets"],
        "covered": official["covered"],
        "gaps": official["gaps"],
        "weak_matches": deeper["weak_match_count"],
        "no_matches": deeper["no_match_count"],
    }


# ---------------------------------------------------
# KB Gaps (Milestone 4)
# ---------------------------------------------------

@router.get(
    "/kb-gaps",
    response_model=dict,
    summary="Knowledge Base Gap Analysis",
)
def get_kb_gaps():
    """
    The deeper gap analysis and prioritized content recommendations -
    which categories need new or expanded KB articles.
    """
    report = build_report()
    return {
        "gaps_by_category": report["gaps_by_category"],
        "recommendations": report["recommendations"],
    }