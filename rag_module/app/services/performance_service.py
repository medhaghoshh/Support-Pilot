"""
SupportPilot Performance Service

Provides performance-related metrics for the
analytics dashboard.
"""

from __future__ import annotations

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models import Ticket, TicketResponse


class PerformanceService:
    """
    Performance metrics for the analytics dashboard.
    """

    @staticmethod
    def get_average_response_time(db: Session) -> float:
        """
        Returns the average AI response generation time
        in seconds.
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
                Ticket.ticket_id == TicketResponse.ticket_id,
            )
            .scalar()
        )

        return round(float(avg_time or 0), 2)

    @staticmethod
    def get_email_delivery_time() -> dict:
        """
        Placeholder until email tracking
        is implemented.
        """

        return {
            "status": "Not Implemented",
            "average_time": None,
        }

    @staticmethod
    def get_jira_response_time() -> dict:
        """
        Placeholder until Jira response tracking
        is implemented.
        """

        return {
            "status": "Not Implemented",
            "average_time": None,
        }

    @staticmethod
    def get_performance_summary(db: Session) -> dict:
        """
        Returns all performance metrics.
        """

        return {
            "average_response_time": (
                PerformanceService.get_average_response_time(db)
            ),
            "email_delivery": (
                PerformanceService.get_email_delivery_time()
            ),
            "jira_response": (
                PerformanceService.get_jira_response_time()
            ),
        }