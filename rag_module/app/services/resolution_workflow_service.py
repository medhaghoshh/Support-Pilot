"""
SupportPilot AI

Resolution Workflow Service

Coordinates the complete AI workflow:

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
Workflow Logging
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app import models
from app.agents.retrieval_agent import retrieval_agent
from app.agents.resolution_agent import ResolutionAgent
from app.agents.escalation_agent import EscalationAgent
from app.services.integration_service import handle_escalation

logger = logging.getLogger(__name__)


class ResolutionWorkflowService:
    """
    Coordinates the complete ticket resolution workflow.
    """

    # -----------------------------------------
    # Initialize AI Agents
    # -----------------------------------------

    resolution_agent = ResolutionAgent()
    escalation_agent = EscalationAgent()

    # -----------------------------------------
    # Workflow Logger
    # -----------------------------------------

    @staticmethod
    def _log(
        db: Session,
        ticket_id: int,
        agent_name: str,
        status: str,
        message: str,
    ) -> None:
        """
        Save workflow activity.
        """

        log = models.WorkflowLog(
            ticket_id=ticket_id,
            agent_name=agent_name,
            status=status,
            message=message,
        )

        db.add(log)
        db.commit()

    # -----------------------------------------
    # Get Ticket
    # -----------------------------------------

    @staticmethod
    def _get_ticket(
        db: Session,
        ticket_id: int,
    ) -> models.Ticket:
        """
        Retrieve ticket from database.
        """

        ticket = (
            db.query(models.Ticket)
            .filter(
                models.Ticket.ticket_id == ticket_id
            )
            .first()
        )

        if ticket is None:
            raise ValueError(
                f"Ticket {ticket_id} not found."
            )

        return ticket

    # -----------------------------------------
    # Get Ticket Owner
    # -----------------------------------------

    @staticmethod
    def _get_ticket_owner(
        db: Session,
        ticket: models.Ticket,
    ) -> models.User:
        """
        Returns the owner of a ticket.
        """

        user = (
            db.query(models.User)
            .filter(
                models.User.user_id == ticket.user_id
            )
            .first()
        )

        if user is None:
            raise ValueError(
                "Ticket owner not found."
            )

        return user

    # -----------------------------------------
    # Save AI Response
    # -----------------------------------------

    @staticmethod
    def _save_ticket_response(
        db: Session,
        ticket_id: int,
        resolution_output: dict[str, Any],
    ) -> models.TicketResponse:
        """
        Stores the generated AI response.
        """

        # Check if response already exists
        existing = (
            db.query(models.TicketResponse)
            .filter(models.TicketResponse.ticket_id == ticket_id)
            .first()
        )
        if existing:
            logger.info("Ticket response already exists for ticket %s.", ticket_id)
            return existing

        response = models.TicketResponse(
            ticket_id=ticket_id,
            generated_response=resolution_output[
                "resolution_steps"
            ],
            confidence_score=resolution_output[
                "confidence"
            ],
        )

        db.add(response)
        db.commit()
        db.refresh(response)

        return response

        # -----------------------------------------
    # Run Retrieval Agent
    # -----------------------------------------

    @staticmethod
    def _run_retrieval(
        ticket: models.Ticket,
    ) -> dict[str, Any]:
        """
        Executes the Retrieval Agent.
        """

        logger.info(
            "Running Retrieval Agent for ticket %s",
            ticket.ticket_id,
        )

        # Combine subject + description for better KB semantic match
        combined_query = f"{ticket.subject} {ticket.description}".strip()

        retrieval_output = retrieval_agent(
            combined_query,
        )

        if retrieval_output.get("status") != "Completed":

            raise RuntimeError(
                "Retrieval Agent failed to find a suitable "
                "Knowledge Base article."
            )

        return retrieval_output

    # -----------------------------------------
    # Build Diagnosis Output
    # -----------------------------------------

    @staticmethod
    def _build_diagnosis_output(
        ticket: models.Ticket,
    ) -> dict[str, Any]:
        """
        Runs the real Diagnosis Agent.
        """
        from app.agents.diagnose import diagnose_ticket

        try:
            diagnosis = diagnose_ticket(ticket.description)
            sev_map = {"Low": "LOW", "Medium": "MEDIUM", "High": "HIGH", "Critical": "CRITICAL"}
            prio_map = {"Low": "P4", "Medium": "P3", "High": "P2", "Critical": "P1"}
            
            suggested_priority = diagnosis.get("suggested_priority", "Medium")
            priority = prio_map.get(suggested_priority, "P3")
            severity = sev_map.get(suggested_priority, "MEDIUM")
            
            return {
                "predicted_category": diagnosis.get("predicted_category") or "General Support",
                "confidence": diagnosis.get("confidence", 0.95),
                "suggested_priority": priority,
                "matched_symptoms": diagnosis.get("matched_symptoms", []),
                "severity": severity,
            }
        except Exception as e:
            logger.error(f"Diagnosis Agent execution failed: {e}")
            return {
                "predicted_category": "General Support",
                "confidence": 0.95,
                "suggested_priority": ticket.priority,
                "matched_symptoms": [],
                "severity": ticket.severity,
            }

    # -----------------------------------------
    # Run Resolution Agent
    # -----------------------------------------

    @classmethod
    def _run_resolution(
        cls,
        ticket: models.Ticket,
        retrieval_output: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Executes the Resolution Agent.

        Returns
        -------
        tuple
            (
                diagnosis_output,
                resolution_output,
            )
        """

        logger.info(
            "Running Resolution Agent for ticket %s",
            ticket.ticket_id,
        )

        diagnosis_output = cls._build_diagnosis_output(
            ticket,
        )

        resolution_output = cls.resolution_agent.run(
            ticket=ticket.description,
            diagnosis_output=diagnosis_output,
            retrieval_output=retrieval_output,
        )

        if not resolution_output.get("success"):

            raise RuntimeError(
                resolution_output.get(
                    "error",
                    "Resolution Agent failed.",
                )
            )

        logger.info(
            "Resolution completed successfully."
        )

        return (
            diagnosis_output,
            resolution_output,
        )

    # -----------------------------------------
    # Convert Sources for API
    # -----------------------------------------

    @staticmethod
    def _format_articles_used(
        resolution_output: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Converts Resolution Agent output into the
        API response schema.
        """

        articles = []

        for source in resolution_output.get(
            "sources",
            [],
        ):

            articles.append(
                {
                    "kb_id": source.get(
                        "kb_id",
                        "",
                    ),
                    "title": source.get(
                        "title",
                        "Unknown",
                    ),
                    "category": source.get(
                        "category",
                        "",
                    ),
                    "tags": source.get(
                        "tags",
                        "",
                    ),
                    "similarity_score": float(
                        source.get(
                            "similarity_score",
                            0.0,
                        )
                    ),
                }
            )

        return articles

        # -----------------------------------------
    # Run Escalation Agent
    # -----------------------------------------

    @classmethod
    def _run_escalation(
        cls,
        diagnosis_output: dict[str, Any],
        resolution_output: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Executes the Escalation Agent.
        """

        logger.info("Running Escalation Agent.")

        escalation_output = cls.escalation_agent.run(
            resolution_output=resolution_output,
            diagnosis_output=diagnosis_output,
        )

        logger.info(
            "Escalation decision: %s",
            "ESCALATED"
            if escalation_output["escalated"]
            else "RESOLVED",
        )

        return escalation_output

    # -----------------------------------------
    # Save Escalation
    # -----------------------------------------

    @staticmethod
    def _save_escalation(
        db: Session,
        ticket_id: int,
        escalation_output: dict[str, Any],
    ) -> None:
        """
        Stores escalation details in the database.
        """

        if not escalation_output["escalated"]:
            return

        # Check if escalation already exists
        existing = (
            db.query(models.Escalation)
            .filter(models.Escalation.ticket_id == ticket_id)
            .first()
        )
        if existing:
            logger.info("Escalation already exists for ticket %s.", ticket_id)
            return

        escalation = models.Escalation(
            ticket_id=ticket_id,
            assigned_team=escalation_output["assigned_team"],
            escalation_reason=escalation_output["reason"],
            status="OPEN",
        )

        db.add(escalation)
        db.commit()

    # -----------------------------------------
    # Handle External Integrations
    # -----------------------------------------

    @classmethod
    def _handle_integrations(
        cls,
        db: Session,
        ticket: models.Ticket,
        user: models.User,
        escalation_output: dict[str, Any],
    ) -> dict[str, Any] | None:
        """
        Creates Jira ticket and sends
        escalation email.
        """

        if not escalation_output["escalated"]:
            # Ticket resolved by AI — always notify the user.
            try:
                from app.services.email_service import send_resolved_notification
                send_resolved_notification(
                    to_email=user.email,
                    ticket_id=ticket.ticket_id,
                )
                logger.info("Resolution email sent to %s for ticket %s.", user.email, ticket.ticket_id)
            except Exception:
                logger.exception("Failed to send resolution email notification.")
            return None

        # Check if a Jira ticket already exists for this ticket to prevent duplicate creation & emails
        existing_jira = (
            db.query(models.JiraTicket)
            .filter(models.JiraTicket.ticket_id == ticket.ticket_id)
            .first()
        )
        if existing_jira:
            logger.info("Jira ticket %s already exists for ticket %s. Skipping integrations and duplicate email.", existing_jira.jira_issue_key, ticket.ticket_id)
            return {
                "ticket_id": ticket.ticket_id,
                "jira_ticket": existing_jira.jira_issue_key,
                "jira_created": True,
                "email_sent": True,
                "status": "ESCALATED",
            }

        logger.info(
            "Creating Jira ticket and sending email."
        )

        result = handle_escalation(
            ticket_id=ticket.ticket_id,
            user_email=user.email,
            subject=ticket.subject,
            description=ticket.description,
            reason=escalation_output["reason"],
            priority=ticket.priority,
            assigned_team=escalation_output.get("assigned_team", "Support Team"),
        )

        # Save Jira ticket status/key to database
        if result and result.get("jira_created") and result.get("jira_ticket"):
            try:
                jira_db = models.JiraTicket(
                    ticket_id=ticket.ticket_id,
                    jira_issue_key=result["jira_ticket"],
                    jira_status="In Progress",
                )
                db.add(jira_db)
                db.commit()
                db.refresh(jira_db)
                logger.info("Saved JiraTicket model to DB.")
            except Exception:
                db.rollback()
                logger.exception("Failed to save JiraTicket to database.")

        logger.info(
            "Integration completed."
        )

        return result

    # -----------------------------------------
    # Update Ticket Status
    # -----------------------------------------

    @staticmethod
    def _update_ticket(
        db: Session,
        ticket: models.Ticket,
        escalation_output: dict[str, Any],
    ) -> None:
        """
        Updates ticket status after workflow completion.

        Rules
        -----
        - Already RESOLVED/CLOSED → never downgrade, skip.
        - Escalated               → set IN_PROGRESS (handed to a team).
        - Not escalated           → set RESOLVED (AI handled it).
        """

        # Never overwrite a terminal status
        if ticket.status in ("RESOLVED", "CLOSED"):
            logger.info(
                "Ticket %s is already %s — skipping status update.",
                ticket.ticket_id,
                ticket.status,
            )
            return

        if escalation_output["escalated"]:
            ticket.status = "IN_PROGRESS"
        else:
            ticket.status = "RESOLVED"

        db.commit()

    # -----------------------------------------
    # Final Workflow Log
    # -----------------------------------------

    @classmethod
    def _complete_workflow(
        cls,
        db: Session,
        ticket_id: int,
        escalation_output: dict[str, Any],
    ) -> None:
        """
        Writes the final workflow log.
        """

        if escalation_output["escalated"]:

            cls._log(
                db=db,
                ticket_id=ticket_id,
                agent_name="Human Agent Review",
                status="Escalated",
                message=escalation_output["reason"],
            )

        cls._log(
            db=db,
            ticket_id=ticket_id,
            agent_name="Resolution Validation",
            status="Completed",
            message=(
                f"Ticket marked as "
                f"{escalation_output['status']}."
            ),
        )

        # -----------------------------------------
    # Public Workflow
    # -----------------------------------------

    @classmethod
    def resolve(
        cls,
        ticket_id: int,
        db: Session,
    ) -> dict[str, Any]:
        """
        Executes the complete SupportPilot
        ticket resolution workflow.
        """

        logger.info(
            "Starting workflow for ticket %s",
            ticket_id,
        )

        # -----------------------------------------
        # Load Ticket & User
        # -----------------------------------------

        ticket = cls._get_ticket(
            db=db,
            ticket_id=ticket_id,
        )

        user = cls._get_ticket_owner(
            db=db,
            ticket=ticket,
        )

        # -----------------------------------------
        # Workflow Started
        # -----------------------------------------

        cls._log(
            db=db,
            ticket_id=ticket.ticket_id,
            agent_name="AI Classification",
            status="Completed",
            message="Workflow started.",
        )

        # -----------------------------------------
        # Retrieval Agent
        # -----------------------------------------

        retrieval_output = cls._run_retrieval(
            ticket,
        )

        # -----------------------------------------
        # Resolution Agent
        # -----------------------------------------

        (
            diagnosis_output,
            resolution_output,
        ) = cls._run_resolution(
            ticket,
            retrieval_output,
        )

        cls._log(
            db=db,
            ticket_id=ticket.ticket_id,
            agent_name="AI Resolution Attempt",
            status="Completed",
            message="Resolution generated successfully.",
        )

        # -----------------------------------------
        # Save AI Response
        # -----------------------------------------

        cls._save_ticket_response(
            db=db,
            ticket_id=ticket.ticket_id,
            resolution_output=resolution_output,
        )

        # -----------------------------------------
        # Escalation Decision
        # -----------------------------------------

        escalation_output = cls._run_escalation(
            diagnosis_output,
            resolution_output,
        )

        # -----------------------------------------
        # Save Escalation
        # -----------------------------------------

        cls._save_escalation(
            db=db,
            ticket_id=ticket.ticket_id,
            escalation_output=escalation_output,
        )

        # -----------------------------------------
        # External Integrations
        # -----------------------------------------

        cls._handle_integrations(
            db=db,
            ticket=ticket,
            user=user,
            escalation_output=escalation_output,
        )

        # -----------------------------------------
        # Update Ticket
        # -----------------------------------------

        cls._update_ticket(
            db=db,
            ticket=ticket,
            escalation_output=escalation_output,
        )

        # -----------------------------------------
        # Final Workflow Log
        # -----------------------------------------

        cls._complete_workflow(
            db=db,
            ticket_id=ticket.ticket_id,
            escalation_output=escalation_output,
        )

        logger.info(
            "Workflow completed successfully."
        )

        # -----------------------------------------
        # Build API Response
        # -----------------------------------------

        return {
            "ticket_id": ticket.ticket_id,
            "generated_response": resolution_output[
                "resolution_steps"
            ],
            "confidence_score": resolution_output[
                "confidence"
            ],
            "articles_used": cls._format_articles_used(
                resolution_output
            ),
            "status": ticket.status,
            "escalated": escalation_output[
                "escalated"
            ],
            "assigned_team": escalation_output.get(
                "assigned_team"
            ),
            "escalation_reason": escalation_output.get(
                "reason"
            ),
            "generation_time_seconds": (
                resolution_output.get(
                    "generation_time_seconds"
                )
            ),
        }


__all__ = [
    "ResolutionWorkflowService",
]