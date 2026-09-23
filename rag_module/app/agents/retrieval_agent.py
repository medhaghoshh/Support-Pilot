"""
Milestone 4 - Member 3 (Retrieval Engineer)

Retrieval Agent

Receives the user query,
searches the Vector Database,
and returns the most relevant
Knowledge Base article(s).
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.vector_search import search_documents

logger = logging.getLogger(__name__)



def retrieval_agent(user_query: str) -> dict[str, Any]:
    """
    Execute a semantic search against the Knowledge Base.

    Parameters
    ----------
    user_query : str
        User support query.

    Returns
    -------
    dict
        Retrieval Agent output in the standard pipeline format.
    """

    logger.info("Retrieval Agent started.")

    try:
        result = search_documents(user_query)

        if result.get("status") != "Completed":
            logger.warning(
                "Retrieval completed without a successful match."
            )

        logger.info("Retrieval Agent completed successfully.")

        return result

    except Exception as exc:
        logger.exception(
            "Retrieval Agent failed: %s",
            exc,
        )

        return {
            "agent_name": "Retrieval Agent",
            "status": "Failed",
            "retrieved_docs": [],
            "error": str(exc),
        }


__all__ = ["retrieval_agent"]