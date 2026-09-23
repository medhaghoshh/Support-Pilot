"""
SupportPilot AI

Resolve Router

Thin API layer that delegates the complete
ticket resolution workflow to the
ResolutionWorkflowService.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.resolution_workflow_service import (
    ResolutionWorkflowService,
)

logger = logging.getLogger(__name__)


router = APIRouter(
    tags=["Resolution"],
)


@router.post(
    "/api/tickets/{ticket_id}/resolve",
    response_model=schemas.TicketResolveOut,
)
def resolve_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Resolve a support ticket using the complete
    AI workflow.

    Workflow
    --------
    Ticket
        ↓
    Retrieval Agent
        ↓
    Resolution Agent
        ↓
    Escalation Agent
        ↓
    Jira Integration
        ↓
    Email Notification
        ↓
    Database Updates
        ↓
    Workflow Logging
        ↓
    API Response
    """

    logger.info(
        "Received resolve request for ticket %s",
        ticket_id,
    )

    try:

        result = ResolutionWorkflowService.resolve(
            ticket_id=ticket_id,
            db=db,
        )

        logger.info(
            "Ticket %s resolved successfully.",
            ticket_id,
        )

        return result

    except ValueError as exc:

        logger.warning(
            "Ticket %s not found.",
            ticket_id,
        )

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:

        logger.exception(
            "Resolution workflow failed for ticket %s.",
            ticket_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal Server Error",
        ) from exc


@router.get(
    "/api/tickets/{ticket_id}/workflow",
    tags=["Resolution"],
)
def get_ticket_workflow(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve logs, status, email, and integration cards for a ticket's workflow.
    """
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    logs = (
        db.query(models.WorkflowLog)
        .filter(models.WorkflowLog.ticket_id == ticket_id)
        .order_by(models.WorkflowLog.timestamp.asc())
        .all()
    )

    esc = db.query(models.Escalation).filter(models.Escalation.ticket_id == ticket_id).first()
    jira = db.query(models.JiraTicket).filter(models.JiraTicket.ticket_id == ticket_id).first()
    resolution = db.query(models.TicketResponse).filter(models.TicketResponse.ticket_id == ticket_id).first()

    has_logs = len(logs) > 0
    has_resolution = resolution is not None
    has_escalation = esc is not None


    # -----------------------------------------------------------------
    # Use ticket.status as source of truth for all display signals.
    # A ticket may have an old escalation record but now be RESOLVED —
    # in that case we must NOT show "Escalation ACTIVE".
    # -----------------------------------------------------------------
    is_resolved   = ticket.status in ("RESOLVED", "CLOSED")
    is_escalated  = ticket.status == "IN_PROGRESS"   # handed to a team
    # "Active" only while genuinely in-flight; "Completed" once done
    escalation_display = (
        "Completed" if is_resolved
        else ("Active" if (has_escalation and is_escalated) else "Standby")
    )

    agents = [
        {
            "key": "diagnosis",
            "label": "Diagnosis",
            "status": "Completed" if has_logs else "Active",
            "icon": "Stethoscope",
            "color": "bg-blue-500",
        },
        {
            "key": "retrieval",
            "label": "Retrieval",
            "status": "Completed" if has_resolution else ("Active" if has_logs else "Standby"),
            "icon": "Search",
            "color": "bg-green-500",
        },
        {
            "key": "resolution",
            "label": "Resolution",
            "status": "Completed" if has_resolution else ("Active" if has_logs else "Standby"),
            "icon": "Wrench",
            "color": "bg-orange-500",
        },
        {
            "key": "escalation",
            "label": "Escalation",
            "status": escalation_display,
            "icon": "ArrowUpCircle",
            "color": "bg-red-500",
        },
    ]

    workflowActivity = []
    for log in logs:
        workflowActivity.append({
            "time": log.timestamp.strftime("%I:%M %p") if log.timestamp else "",
            "actor": log.agent_name,
            "action": log.message,
        })

    integrations = [
        {
            "key": "jira",
            "name": "Jira Integration",
            "detail": f"Connected • Ticket {jira.jira_issue_key} created" if jira else "Connected • Standby",
            # Show Active only while genuinely escalated/in-progress
            "status": "Active" if (has_escalation and is_escalated) else ("Completed" if (jira and is_resolved) else "Standby"),
            "icon": "FileCode2",
            "color": "text-blue-600 bg-blue-50",
        },
        {
            "key": "email",
            "name": "Email Automation",
            "detail": "Connected • Notification sent" if has_logs else "Connected",
            "status": "Active" if has_logs else "Standby",
            "icon": "Mail",
            "color": "text-green-600 bg-green-50",
        },
    ]

    jiraTicket = None
    if jira:
        # Reflect actual ticket status in Jira card — not hardcoded "In Progress"
        jira_display_status = "Resolved" if is_resolved else (jira.jira_status or "In Progress")
        jiraTicket = {
            "ticketId": jira.jira_issue_key,
            "status": jira_display_status,
            "assignee": esc.assigned_team if esc else "Support Team",
            "priority": ticket.priority,
        }
    elif has_escalation:
        jiraTicket = {
            "ticketId": f"JIRA-{ticket_id}",
            "status": "Resolved" if is_resolved else "In Progress",
            "assignee": esc.assigned_team if esc else "Support Team",
            "priority": ticket.priority,
        }

    emailNotification = None
    if has_logs:
        # Use ticket.status as the ONLY source of truth for the message.
        # OPEN   → workflow ran but outcome undetermined (e.g. hardware/pending)
        # RESOLVED → AI handled it
        # IN_PROGRESS → escalated to a human team
        if is_resolved and resolution:
            message = (
                f"Your support ticket #{ticket.ticket_id} has been Resolved by AI. "
                f"Resolution: {resolution.generated_response[:200]}..."
            )
        elif is_escalated and esc:
            message = (
                f"Your support ticket #{ticket.ticket_id} has been escalated to "
                f"{esc.assigned_team}. Reason: {esc.escalation_reason}"
            )
        else:
            # OPEN — workflow ran but ticket is still pending
            message = (
                f"Your support ticket #{ticket.ticket_id} has been received and "
                f"is currently under review by our support team."
            )
        emailNotification = {
            "title": "Email Notification Sent",
            "message": message,
        }

    return {
        "agents": agents,
        "workflowActivity": workflowActivity,
        "integrations": integrations,
        "jiraTicket": jiraTicket,
        "emailNotification": emailNotification,
        "resolution": {
            "generated_response": resolution.generated_response if resolution else None,
            "confidence_score": float(resolution.confidence_score) if resolution else None,
        } if resolution else None,
    }