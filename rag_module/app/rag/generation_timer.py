"""
SupportPilot AI

Generation Timer

Provides a specialized timer for measuring
Large Language Model (LLM) generation latency
within the RAG pipeline.
"""

from __future__ import annotations

from app.utils.timers import Timer


class GenerationTimer(Timer):
    """
    Specialized timer for measuring
    LLM response generation latency.
    """

    @property
    def latency_seconds(self) -> float:
        """
        Returns the elapsed generation
        time in seconds.
        """

        return self.elapsed_seconds

    @property
    def latency_ms(self) -> float:
        """
        Returns the elapsed generation
        time in milliseconds.
        """

        return self.elapsed_ms


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "GenerationTimer",
]