"""
SupportPilot Integration Service

Handles external integrations required when
a ticket is escalated.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.email_service import (
    send_escalation_notification,
)
from app.services.jira_service import (
    create_jira_ticket,
    get_jira_ticket_status,
)

logger = logging.getLogger(__name__)


def handle_escalation(
    ticket_id: int,
    user_email: str,
    subject: str,
    description: str,
    reason: str,
    priority: str = "High",
    assigned_team: str = "Support Team",
) -> dict[str, Any]:
    """
    Creates a Jira ticket and notifies the user via email.

    Parameters
    ----------
    ticket_id : int
        Original SupportPilot ticket ID.

    user_email : str
        Email address of the requester.

    subject : str
        Ticket subject.

    description : str
        Ticket description.

    reason : str
        Escalation reason.

    priority : str, optional
        Ticket priority.

    assigned_team : str, optional
        Team responsible for handling the escalation.

    Returns
    -------
    dict[str, Any]
        Escalation result.
    """

    logger.info(
        "Starting external integrations for ticket %s.",
        ticket_id,
    )

    # ---------------------------------------------------
    # Step 1 - Create Jira Ticket
    # ---------------------------------------------------

    try:

        jira_result = create_jira_ticket(
            summary=(
                f"SupportPilot Ticket #{ticket_id} - "
                f"{subject}"
            ),
            description=f"""
Original Ticket ID: {ticket_id}

Issue:
{description}

Escalation Reason:
{reason}
""",
        )

    except Exception:

        logger.exception(
            "Exception occurred while creating Jira ticket."
        )

        return {
            "ticket_id": ticket_id,
            "jira_ticket": None,
            "jira_created": False,
            "email_sent": False,
            "status": "JIRA_FAILED",
        }

    if not jira_result:

        logger.error(
            "Failed to create Jira ticket."
        )

        return {
            "ticket_id": ticket_id,
            "jira_ticket": None,
            "jira_created": False,
            "email_sent": False,
            "status": "JIRA_FAILED",
        }

    jira_key = jira_result.get("key")

    logger.info(
        "Jira ticket created successfully: %s",
        jira_key,
    )

    # ---------------------------------------------------
    # Step 2 - Fetch Jira Status
    # ---------------------------------------------------

    try:

        jira_status = get_jira_ticket_status(
            jira_key,
        )

    except Exception:

        logger.exception(
            "Unable to retrieve Jira ticket status."
        )

        jira_status = None

    if not jira_status:

        jira_status = "To Do"

    logger.info(
        "Jira Status: %s",
        jira_status,
    )

    # ---------------------------------------------------
    # Step 3 - Send Email
    # ---------------------------------------------------

    try:

        email_sent = send_escalation_notification(
            to_email=user_email,
            ticket_id=ticket_id,
            jira_ticket=jira_key,
            subject_name=subject,
            priority=priority,
            jira_status=jira_status,
            assigned_team=assigned_team,
            reason=reason,
        )

    except Exception:

        logger.exception(
            "Unexpected error while sending email."
        )

        email_sent = False

    if email_sent:

        logger.info(
            "Escalation email sent to %s",
            user_email,
        )

    else:

        logger.warning(
            "Escalation email could not be sent."
        )

    # ---------------------------------------------------
    # Step 4 - Build Result
    # ---------------------------------------------------

    result = {
        "ticket_id": ticket_id,
        "jira_ticket": jira_key,
        "jira_created": True,
        "email_sent": email_sent,
        "status": (
            "ESCALATED"
            if email_sent
            else "PARTIAL_FAILURE"
        ),
    }

    logger.info(
        "External integrations completed for ticket %s.",
        ticket_id,
    )

    logger.info(
        "Integration Result: %s",
        result,
    )

    return result


__all__ = [
    "handle_escalation",
]