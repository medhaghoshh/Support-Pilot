import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_response(
    llm_response: str,
    retrieved_document: dict[str, Any] | None
) -> dict:
    """
    Format the final RAG response with retrieved
    knowledge base metadata.
    """

    logger.info("Formatting AI response")

    # ---------------------------------------------------
    # No retrieved KB document
    # ---------------------------------------------------
    if not retrieved_document:
        logger.warning("No source document available")

        return {
            "resolution": llm_response.strip(),
            "sources": [],
            "documents_used": 0,
            "retrieval_distance": None
        }

    # ---------------------------------------------------
    # Safe retrieval distance
    # ---------------------------------------------------
    retrieval_distance = retrieved_document.get(
        "retrieval_distance"
    )

    try:
        retrieval_distance = (
            round(float(retrieval_distance), 3)
            if retrieval_distance is not None
            else None
        )
    except (TypeError, ValueError):
        logger.warning("Invalid retrieval distance")
        retrieval_distance = None

    # ---------------------------------------------------
    # Build formatted response
    # ---------------------------------------------------
    return {
        "resolution": llm_response.strip(),

        "sources": [
            {
                "kb_id": retrieved_document.get("kb_id"),
                "title": retrieved_document.get("title"),
                "category": retrieved_document.get("category"),
                "tags": retrieved_document.get("tags")
            }
        ],

        "documents_used": 1,

        "retrieval_distance": retrieval_distance
    }