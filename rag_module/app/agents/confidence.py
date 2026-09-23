"""
Milestone 3 - Member 5 (RAG / LLM Engineer)

Confidence Scoring Module

Computes the overall confidence score for the
generated troubleshooting response.

The final confidence is derived from:

1. Diagnosis Agent confidence
2. Retrieval Agent confidence

The resulting score is normalized to the range
[0.0, 1.0] and is consumed by both the
Resolution Agent and the Escalation Agent.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# Weight Configuration
# ---------------------------------------------------

DIAGNOSIS_WEIGHT = 0.50
RETRIEVAL_WEIGHT = 0.50


def _clamp(value: float) -> float:
    """
    Clamp a floating-point value to the range [0.0, 1.0].
    """
    return max(0.0, min(1.0, value))


# ---------------------------------------------------
# Final Confidence Calculation
# ---------------------------------------------------

def calculate_confidence(
    diagnosis_confidence: float,
    retrieval_confidence: float,
) -> float:
    """
    Calculate the overall confidence score.

    The score combines the Diagnosis Agent's
    confidence with the Retrieval Agent's
    normalized retrieval confidence.

    Parameters
    ----------
    diagnosis_confidence
        Confidence produced by the Diagnosis Agent
        in the range [0.0, 1.0].

    retrieval_confidence
        Normalized confidence produced by the
        Retrieval Agent in the range [0.0, 1.0].

    Returns
    -------
    float
        Final confidence score in the range
        [0.0, 1.0].
    """

    diagnosis_confidence = _clamp(diagnosis_confidence)
    retrieval_confidence = _clamp(retrieval_confidence)

    final_score = (
        diagnosis_confidence * DIAGNOSIS_WEIGHT
        + retrieval_confidence * RETRIEVAL_WEIGHT
    )

    final_score = round(_clamp(final_score), 2)

    logger.info(
        (
            "Confidence calculated | "
            "Diagnosis=%.2f | "
            "Retrieval=%.2f | "
            "Final=%.2f"
        ),
        diagnosis_confidence,
        retrieval_confidence,
        final_score,
    )

    return final_score