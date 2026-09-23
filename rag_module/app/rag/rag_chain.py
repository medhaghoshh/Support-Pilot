import logging
import time
from typing import Any

from app.rag.llm import llm
from app.rag.prompts import troubleshooting_prompt
from app.rag.formatter import format_response

logger = logging.getLogger(__name__)


def generate_resolution(
    user_query: str,
    retrieved_document: dict[str, Any] | None
) -> dict:
    """
    Generate an AI-powered troubleshooting response
    using the retrieved knowledge base article.
    """
    start_time = time.time()
    logger.info("Starting AI resolution generation")

    # ---------------------------------------------------
    # No matching KB article found
    # ---------------------------------------------------
    if not retrieved_document or not retrieved_document.get("content"):
        logger.warning("No relevant KB article found")
        return {
            "resolution": (
                "No relevant knowledge base article was found. "
                "Please escalate this issue to the IT support team."
            ),
            "sources": [],
            "documents_used": 0,
            "retrieval_distance": None,
            "response_time": round(time.time() - start_time, 3)
        }

    # ---------------------------------------------------
    # Build Context
    # ---------------------------------------------------
    context = (
        f"KB ID: {retrieved_document.get('kb_id')}\n"
        f"Title: {retrieved_document.get('title')}\n"
        f"Category: {retrieved_document.get('category')}\n"
        f"Tags: {retrieved_document.get('tags')}\n\n"
        f"{retrieved_document.get('content')}"
    )

    try:
        formatted_prompt = troubleshooting_prompt.format(
            context=context,
            question=user_query
        )
    except Exception:
        formatted_prompt = f"Knowledge Base Context:\n{context}\n\nUser Issue:\n{user_query}"

    # ---------------------------------------------------
    # LLM Generation
    # ---------------------------------------------------
    try:
        logger.info("Sending prompt to Groq / LLM chain")
        response = llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, "content") else str(response)
        logger.info("LLM response received successfully")
    except Exception as e:
        logger.exception(f"Groq/LLM invocation error ({e}). Returning structured RAG resolution.")
        response_text = (
            f"1. Verify corporate network firewall & settings for '{retrieved_document.get('title', 'Service')}'.\n"
            f"2. Inspect configuration & authentication for request: '{user_query}'.\n"
            "3. Restart the service dependencies and clear any cached credentials.\n"
            "4. If issue persists, escalate to IT support tier 2 queue."
        )

    # ---------------------------------------------------
    # Format Response
    # ---------------------------------------------------
    result = format_response(
        response_text,
        retrieved_document
    )

    result["response_time"] = round(time.time() - start_time, 3)
    logger.info(f"AI resolution generated in {result['response_time']} seconds")

    return result