"""
SupportPilot

Metrics Service

Provides ticket-level metrics used by the
Milestone 4 analytics dashboard.
"""

from __future__ import annotations

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models import Escalation, Ticket, TicketResponse


class MetricsService:
    """
    Computes ticket statistics and
    resolution metrics.
    """

    @staticmethod
    def get_total_tickets(
        db: Session,
    ) -> int:
        """
        Returns the total number of tickets.
        """

        return db.query(Ticket).count()

    @staticmethod
    def get_total_escalations(
        db: Session,
    ) -> int:
        """
        Returns the total number of escalated tickets.
        """

        return db.query(Escalation).count()

    @staticmethod
    def get_resolution_success_rate(
        db: Session,
    ) -> float:
        """
        Resolution Success Rate

        (Resolved Tickets / Total Tickets) × 100
        """

        total = db.query(Ticket).count()

        if total == 0:
            return 0.0

        resolved = (
            db.query(Ticket)
            .filter(
                Ticket.status == "RESOLVED"
            )
            .count()
        )

        return round(
            (resolved / total) * 100,
            2,
        )

    @staticmethod
    def get_average_response_time(
        db: Session,
    ) -> float:
        """
        Returns the average AI response
        generation time in seconds.
        """

        avg_time = (
            db.query(
                func.avg(
                    func.timestampdiff(
                        text("SECOND"),
                        Ticket.created_at,
                        TicketResponse.generated_at,
                    )
                )
            )
            .join(
                TicketResponse,
                Ticket.ticket_id
                == TicketResponse.ticket_id,
            )
            .scalar()
        )

        return round(float(avg_time or 0), 2)


__all__ = [
    "MetricsService",
]