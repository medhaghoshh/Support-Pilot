"""
SupportPilot AI

Email Service

Provides helper functions for sending:

- Generic emails
- Ticket resolution notifications
- Escalation notifications
"""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

# ---------------------------------------------------
# Environment Variables
# ---------------------------------------------------

from app.config.dynamic_config import get_email_config


# ---------------------------------------------------
# Generic Email Sender
# ---------------------------------------------------

def send_email(
    to_email: str,
    subject: str,
    message: str,
) -> bool:
    """
    Send an email using Gmail SMTP.

    Returns
    -------
    bool
        True if email sent successfully.
    """
    config = get_email_config()
    sender_email = config.get("EMAIL_ADDRESS")
    app_password = config.get("EMAIL_APP_PASSWORD")

    if not sender_email or not app_password:
        logger.error(
            "EMAIL_ADDRESS or EMAIL_APP_PASSWORD is not configured."
        )
        return False

    email = EmailMessage()

    email["From"] = sender_email
    email["To"] = to_email
    email["Subject"] = subject
    email.set_content(message)

    try:

        with smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT,
        ) as smtp:

            smtp.login(
                sender_email,
                app_password,
            )

            smtp.send_message(email)

        logger.info(
            "Email sent successfully to %s",
            to_email,
        )

        return True

    except smtplib.SMTPAuthenticationError:

        logger.exception(
            "SMTP authentication failed."
        )

    except smtplib.SMTPException:

        logger.exception(
            "SMTP error while sending email."
        )

    except Exception:

        logger.exception(
            "Unexpected email error."
        )

    return False


# ---------------------------------------------------
# Resolution Notification
# ---------------------------------------------------

def send_resolved_notification(
    to_email: str,
    ticket_id: int,
) -> bool:
    """
    Notify the user that the ticket
    has been resolved.
    """

    subject = (
        f"SupportPilot - Ticket #{ticket_id} Resolved"
    )

    message = (
        f"Hello,\n\n"
        f"Your support ticket #{ticket_id} "
        f"has been resolved successfully.\n\n"
        f"Thank you,\n"
        f"SupportPilot Team"
    )

    return send_email(
        to_email,
        subject,
        message,
    )


# ---------------------------------------------------
# Escalation Notification
# ---------------------------------------------------

def send_escalation_notification(
    to_email: str,
    ticket_id: int,
    jira_ticket: str,
    subject_name: str,
    priority: str,
    jira_status: str,
    assigned_team: str,
    reason: str,
) -> bool:
    """
    Notify the user that the ticket
    has been escalated.
    """

    subject = (
        f"SupportPilot | Escalation Notification | "
        f"{jira_ticket}"
    )

    message = f"""
Hello,

Thank you for contacting SupportPilot.

Your support request has been successfully escalated
to our technical support team.

--------------------------------------------------
SUPPORT TICKET DETAILS
--------------------------------------------------

Original Ticket ID : {ticket_id}
Jira Ticket ID     : {jira_ticket}
Issue Subject      : {subject_name}
Priority           : {priority}
Current Status     : {jira_status}
Assigned Team      : {assigned_team}

--------------------------------------------------
Escalation Reason
--------------------------------------------------

{reason}

Generated On:
{datetime.now().strftime("%d %B %Y, %I:%M %p")}

--------------------------------------------------
NEXT STEPS
--------------------------------------------------

• Your ticket has been registered in Jira.
• The assigned support team will investigate it.
• You will receive status updates via email.
• Keep your Jira Ticket ID ({jira_ticket})
  for future communication.

Thank you for choosing SupportPilot.

Regards,

SupportPilot Support Team

Infosys Internship Project

Email:
supportpilotinfosys@gmail.com

--------------------------------------------------
This is an automated email.
Please do not reply.
--------------------------------------------------
"""

    return send_email(
        to_email,
        subject,
        message,
    )


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "send_email",
    "send_resolved_notification",
    "send_escalation_notification",
]