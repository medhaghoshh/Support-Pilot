"""
Milestone 3 - Member 5 (RAG / LLM Engineer)

Escalation Agent

Determines whether an AI-generated resolution
should be escalated to human support.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Configuration
# ---------------------------------------------------

MIN_CONFIDENCE = 0.70

# Categories that the AI can resolve autonomously.
# Tickets in these categories skip phrase-based escalation (Rule 5) because
# LLMs routinely write "contact support if unresolved" as a last-resort step —
# that is NOT a genuine escalation signal for these well-understood issues.
AUTO_RESOLVE_CATEGORIES = {
    "Networking",       # WiFi, Bluetooth, VPN, connectivity
    "Password Reset",   # Password, account lockout, MFA
    "Software",         # App crashes, installation, updates
    "Email",            # Outlook, mail client issues
    "Access & Permissions",
}

# Categories that ALWAYS require human hands — never auto-resolved.
# Hardware needs a physical technician; Security needs a human security review.
HUMAN_REQUIRED_CATEGORIES = {
    "Hardware",   # keyboard, laptop, printer, monitor — needs physical fix
    "Security",   # phishing, malware, breach — needs human security review
}

# Lower confidence floor for well-understood IT categories.
AUTO_RESOLVE_MIN_CONFIDENCE = 0.45

HIGH_PRIORITY = {"P1"}

HIGH_SEVERITY = {"CRITICAL"}

# Only escalate when the LLM output EXPLICITLY demands human intervention
# as the PRIMARY resolution — not as a routine last-resort fallback line.
ESCALATION_PHRASES = [
    "human support required",
    "level 2 support",
    "please escalate",
    "requires escalation",
    "escalate this ticket",
    "this issue requires human",
    "must be escalated",
]


class EscalationAgent:
    """
    Determines whether a support ticket should be
    escalated after AI resolution.
    """

    def run(
        self,
        resolution_output: dict[str, Any],
        diagnosis_output: dict[str, Any],
    ) -> dict[str, Any]:

        logger.info("Escalation Agent started.")

        try:

            confidence = resolution_output.get(
                "confidence",
                0.0,
            )

            success = resolution_output.get(
                "success",
                False,
            )

            priority = diagnosis_output.get(
                "suggested_priority",
                "P4",
            )

            severity = diagnosis_output.get(
                "severity",
                "LOW",
            )

            # Category drives all routing decisions
            predicted_category = diagnosis_output.get(
                "predicted_category",
                "",
            ) or ""

            is_human_required   = predicted_category in HUMAN_REQUIRED_CATEGORIES
            is_auto_resolve_category = predicted_category in AUTO_RESOLVE_CATEGORIES

            # Use a relaxed confidence floor for well-understood IT categories
            effective_min_confidence = (
                AUTO_RESOLVE_MIN_CONFIDENCE
                if is_auto_resolve_category
                else MIN_CONFIDENCE
            )

            resolution_text = (
                resolution_output.get(
                    "resolution_steps",
                    "",
                )
                .lower()
                .strip()
            )

            # -----------------------------------------
            # Rule 0
            # Hardware / Security — always escalate.
            # These require a physical technician or
            # a human security review respectively.
            # -----------------------------------------

            if is_human_required:

                team_map = {
                    "Hardware": "Hardware Support Team",
                    "Security": "Security Operations Team",
                }
                assigned = team_map.get(predicted_category, "Level 2 Support")

                logger.info(
                    "Escalating because category '%s' always requires human handling.",
                    predicted_category,
                )

                return {
                    "escalated": True,
                    "assigned_team": assigned,
                    "reason": (
                        f"{predicted_category} issues require human intervention."
                    ),
                    "status": "IN_PROGRESS",
                }

            # -----------------------------------------
            # Rule 1
            # Resolution generation failed
            # -----------------------------------------

            if not success:

                logger.info(
                    "Escalating because AI resolution failed."
                )

                return {
                    "escalated": True,
                    "assigned_team": "Level 2 Support",
                    "reason": "Resolution generation failed.",
                    "status": "IN_PROGRESS",
                }

            # -----------------------------------------
            # Rule 2
            # Low confidence
            # (relaxed threshold for routine IT categories)
            # -----------------------------------------

            if confidence < effective_min_confidence:

                logger.info(
                    "Escalating because confidence %.2f < %.2f (category=%s)",
                    confidence,
                    effective_min_confidence,
                    predicted_category,
                )

                return {
                    "escalated": True,
                    "assigned_team": "Level 2 Support",
                    "reason": (
                        f"Low AI confidence ({confidence:.2f})."
                    ),
                    "status": "IN_PROGRESS",
                }

            # -----------------------------------------
            # Rule 3
            # Critical Priority
            # -----------------------------------------

            if priority in HIGH_PRIORITY:

                logger.info(
                    "Escalating because priority=%s",
                    priority,
                )

                return {
                    "escalated": True,
                    "assigned_team": "Priority Support",
                    "reason": (
                        f"Priority {priority} requires review."
                    ),
                    "status": "IN_PROGRESS",
                }

            # -----------------------------------------
            # Rule 4
            # Critical Severity
            # -----------------------------------------

            if severity in HIGH_SEVERITY:

                logger.info(
                    "Escalating because severity=%s",
                    severity,
                )

                return {
                    "escalated": True,
                    "assigned_team": "Critical Incident Team",
                    "reason": "Critical severity issue.",
                    "status": "IN_PROGRESS",
                }

            # -----------------------------------------
            # Rule 5
            # Explicit LLM escalation recommendation
            # Skipped for auto-resolve categories: LLMs naturally write
            # "contact support if unresolved" in IT resolutions — that
            # is a fallback step, NOT a genuine escalation request.
            # -----------------------------------------

            if not is_auto_resolve_category:

                matched_phrase = next(
                    (
                        phrase
                        for phrase in ESCALATION_PHRASES
                        if phrase in resolution_text
                    ),
                    None,
                )

                if matched_phrase:

                    logger.info(
                        "Escalating because LLM suggested '%s'.",
                        matched_phrase,
                    )

                    return {
                        "escalated": True,
                        "assigned_team": "Level 2 Support",
                        "reason": (
                            "LLM recommended human escalation."
                        ),
                        "status": "IN_PROGRESS",
                    }
            else:
                logger.info(
                    "Skipping phrase-match escalation for auto-resolve category '%s'.",
                    predicted_category,
                )

            # -----------------------------------------
            # Ticket resolved automatically
            # -----------------------------------------

            logger.info(
                "Ticket resolved automatically."
            )

            return {
                "escalated": False,
                "assigned_team": None,
                "reason": None,
                "status": "RESOLVED",
            }

        except Exception as exc:

            logger.exception(
                "Escalation Agent failed."
            )

            return {
                "escalated": True,
                "assigned_team": "Level 2 Support",
                "reason": str(exc),
                "status": "IN_PROGRESS",
            }


__all__ = [
    "EscalationAgent",
]