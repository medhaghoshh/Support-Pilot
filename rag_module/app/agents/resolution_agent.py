"""
Milestone 4 - Member 5 (RAG / LLM Engineer)

Resolution Agent

This agent receives:
- User Ticket
- Diagnosis Agent Output
- Retrieval Agent Output

It generates an AI-powered troubleshooting
response using the Groq LLM, computes
an overall confidence score, and records
LLM generation latency for optimization.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.agents.confidence import calculate_confidence
from app.agents.prompts import resolution_prompt
from app.rag.generation_timer import GenerationTimer
from app.rag.llm import llm

logger = logging.getLogger(__name__)



class ResolutionAgent:
    """
    Generates grounded troubleshooting responses
    using the Diagnosis Agent output and the
    retrieved Knowledge Base article.
    """

    def __init__(self) -> None:
        self.llm = llm

    def run(
        self,
        ticket: str,
        diagnosis_output: dict[str, Any],
        retrieval_output: dict[str, Any],
    ) -> dict[str, Any]:

        logger.info("Resolution Agent started.")

        try:

            # -----------------------------------------
            # Extract Retrieval Output
            # -----------------------------------------

            retrieved_docs = retrieval_output.get(
                "retrieved_docs",
                [],
            )

            if not retrieved_docs:

                logger.warning(
                    "No Knowledge Base article retrieved."
                )

                return {
                    "success": False,
                    "resolution_steps": (
                        "No relevant Knowledge Base article was found."
                    ),
                    "confidence": 0.0,
                    "resolution_id": None,
                    "sources": [],
                    "generation_time_seconds": 0.0,
                    "generation_time_ms": 0.0,
                    "error": None,
                }

            retrieved_document = retrieved_docs[0]

            # -----------------------------------------
            # Build Knowledge Base Context
            # -----------------------------------------

            knowledge_base = f"""
Title: {retrieved_document.get("title", "Unknown")}
Category: {retrieved_document.get("category", "Unknown")}
Tags: {retrieved_document.get("tags", "")}

Content:
{retrieved_document.get("content", "")}
""".strip()

            # -----------------------------------------
            # Build Prompt
            # -----------------------------------------

            prompt = resolution_prompt.format_messages(
                ticket=ticket,
                predicted_category=diagnosis_output.get(
                    "predicted_category",
                    "Unknown",
                ),
                diagnosis_confidence=diagnosis_output.get(
                    "confidence",
                    0.0,
                ),
                suggested_priority=diagnosis_output.get(
                    "suggested_priority",
                    "Medium",
                ),
                matched_symptoms=", ".join(
                    diagnosis_output.get(
                        "matched_symptoms",
                        [],
                    )
                ),
                knowledge_base=knowledge_base,
            )

            logger.info("Invoking Groq LLM...")

            # -----------------------------------------
            # Measure LLM Generation Time
            # -----------------------------------------

            timer = GenerationTimer()
            timer.start()

            response = self.llm.invoke(prompt)

            timer.stop()

            logger.info(
                "LLM generation completed in %.3f seconds",
                timer.latency_seconds,
            )

            # -----------------------------------------
            # Calculate Confidence
            # -----------------------------------------

            similarity_score = retrieved_document.get(
                "similarity_score",
                0.0,
            )

            confidence = calculate_confidence(
                diagnosis_confidence=diagnosis_output.get(
                    "confidence",
                    0.0,
                ),
                retrieval_confidence=similarity_score,
            )

            # -----------------------------------------
            # Resolution Metadata
            # -----------------------------------------

            resolution_id = (
                f"RES-{uuid.uuid4().hex[:8].upper()}"
            )

            sources = [
                {
                    "kb_id": retrieved_document.get("kb_id"),
                    "title": retrieved_document.get("title"),
                    "category": retrieved_document.get("category"),
                    "tags": retrieved_document.get("tags"),
                    "similarity_score": similarity_score,
                }
            ]

            logger.info(
                "Resolution generated successfully "
                "(confidence=%.2f)",
                confidence,
            )

            return {
                "success": True,
                "resolution_steps": response.content.strip(),
                "confidence": confidence,
                "resolution_id": resolution_id,
                "sources": sources,
                "generation_time_seconds": timer.latency_seconds,
                "generation_time_ms": timer.latency_ms,
                "error": None,
            }

        except Exception as exc:

            logger.exception(
                "Resolution Agent failed."
            )

            return {
                "success": False,
                "resolution_steps": (
                    "Unable to generate a resolution."
                ),
                "confidence": 0.0,
                "resolution_id": None,
                "sources": [],
                "generation_time_seconds": 0.0,
                "generation_time_ms": 0.0,
                "error": str(exc),
            }