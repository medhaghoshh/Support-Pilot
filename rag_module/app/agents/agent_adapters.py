"""
Milestone 4 - Member 2 & Member 5 Integration

Agent Adapters

Normalizes the outputs of the Diagnosis, Retrieval,
Resolution, and Escalation Agents into a consistent
format for the orchestration layer.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------
# Diagnosis Adapter
# ---------------------------------------------------

def adapt_diagnosis_output(
    raw: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize Diagnosis Agent output.
    """

    return {
        "predicted_category": raw.get(
            "predicted_category"
        ),
        "confidence": raw.get(
            "confidence",
            0.0,
        ),
        "suggested_priority": raw.get(
            "suggested_priority",
            "Medium",
        ),
        "matched_symptoms": raw.get(
            "matched_symptoms",
            [],
        ),
        "needs_clarification": raw.get(
            "needs_clarification",
            False,
        ),
        "clarifying_questions": raw.get(
            "clarifying_questions",
            [],
        ),
    }


# ---------------------------------------------------
# Retrieval Adapter
# ---------------------------------------------------

def adapt_retrieval_output(
    raw: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize Retrieval Agent output.

    Member 3 already returns the expected
    `retrieved_docs` structure, so preserve it.
    """

    docs = raw.get(
        "retrieved_docs",
        [],
    )

    if not docs:
        return {
            "retrieved_docs": []
        }

    normalized_docs = []

    for doc in docs:

        normalized_docs.append(
            {
                "doc_id": doc.get(
                    "doc_id",
                    doc.get("kb_id"),
                ),
                "title": doc.get("title"),
                "category": doc.get("category"),
                "tags": doc.get("tags"),
                "content": doc.get("content"),
                "similarity_score": doc.get(
                    "similarity_score",
                    0.0,
                ),
            }
        )

    return {
        "retrieved_docs": normalized_docs
    }


# ---------------------------------------------------
# Resolution Adapter
# ---------------------------------------------------

def adapt_resolution_output(
    raw: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize Resolution Agent output.
    """

    return {
        "success": raw.get(
            "success",
            False,
        ),
        "resolution_steps": raw.get(
            "resolution_steps",
            "",
        ),
        "confidence": raw.get(
            "confidence",
            0.0,
        ),
        "resolution_id": raw.get(
            "resolution_id",
        ),
        "sources": raw.get(
            "sources",
            [],
        ),
        "generation_time_seconds": raw.get(
            "generation_time_seconds",
            0.0,
        ),
        "generation_time_ms": raw.get(
            "generation_time_ms",
            0.0,
        ),
        "error": raw.get(
            "error",
        ),
    }


# ---------------------------------------------------
# Escalation Adapter
# ---------------------------------------------------

def adapt_escalation_output(
    raw: dict[str, Any],
) -> dict[str, Any]:
    """
    Normalize Escalation Agent output.
    """

    return {
        "escalated": raw.get(
            "escalated",
            False,
        ),
        "assigned_team": raw.get(
            "assigned_team",
        ),
        "reason": raw.get(
            "reason",
        ),
        "status": raw.get(
            "status",
            "OPEN",
        ),
    }