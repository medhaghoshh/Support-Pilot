"""
SupportPilot AI

Workflow Logger

Provides helper methods for recording and
retrieving AI workflow execution logs.
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models import WorkflowLog

logger = logging.getLogger(__name__)


class WorkflowLogger:
    """
    Utility class for storing and retrieving
    workflow execution logs.
    """

    # ---------------------------------------------------
    # Store Workflow Log
    # ---------------------------------------------------

    @staticmethod
    def log_workflow(
        db: Session,
        ticket_id: int,
        agent_name: str,
        status: str,
        message: str,
    ) -> WorkflowLog:
        """
        Save a workflow event to the database.

        Returns
        -------
        WorkflowLog
            Newly created workflow log entry.
        """

        logger.info(
            "Recording workflow log for ticket %s (%s).",
            ticket_id,
            agent_name,
        )

        try:

            log = WorkflowLog(
                ticket_id=ticket_id,
                agent_name=agent_name,
                status=status,
                message=message,
            )

            db.add(log)
            db.commit()
            db.refresh(log)

            logger.info(
                "Workflow log recorded successfully."
            )

            return log

        except Exception:

            db.rollback()

            logger.exception(
                "Failed to record workflow log."
            )

            raise

    # ---------------------------------------------------
    # Retrieve Workflow Logs
    # ---------------------------------------------------

    @staticmethod
    def get_ticket_logs(
        db: Session,
        ticket_id: int,
    ) -> list[WorkflowLog]:
        """
        Retrieve all workflow logs for a ticket.

        Parameters
        ----------
        ticket_id : int
            Support ticket ID.

        Returns
        -------
        list[WorkflowLog]
            Workflow log entries ordered by timestamp.
        """

        logger.info(
            "Retrieving workflow logs for ticket %s.",
            ticket_id,
        )

        return (
            db.query(WorkflowLog)
            .filter(
                WorkflowLog.ticket_id == ticket_id
            )
            .order_by(
                WorkflowLog.timestamp.asc()
            )
            .all()
        )


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "WorkflowLogger",
]