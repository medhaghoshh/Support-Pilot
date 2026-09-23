"""
Milestone 4 - Optimization Agent

Builds optimization metrics and recommendations for
the analytics dashboard.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import optimization_config as config
from app.utils.statistics import calculate_latency_improvement

logger = logging.getLogger(__name__)


class OptimizationAgent:
    """
    Produces optimization metrics for dashboard reporting.
    """

    def run(
        self,
        kb_metrics: dict[str, Any],
        resolution_success_rate: float,
        avg_generation_time: float,
        previous_generation_time: float | None = None,
    ) -> dict[str, Any]:
        """
        Generate optimization metrics.

        Parameters
        ----------
        kb_metrics
            Metrics supplied by the retrieval layer.

        resolution_success_rate
            AI resolution success percentage.

        avg_generation_time
            Average LLM generation latency.

        previous_generation_time
            Previous latency for comparison.

        Returns
        -------
        dict
            Dashboard optimization report.
        """

        logger.info("Optimization Agent started.")

        latency_change = None

        if previous_generation_time is not None:
            latency_change = calculate_latency_improvement(
                previous_generation_time,
                avg_generation_time,
            )

        recommendations = []

        if (
            kb_metrics["knowledge_base_coverage"]
            < config.MIN_RESOLUTION_SUCCESS_RATE
        ):
            recommendations.append(
                "Increase Knowledge Base coverage."
            )

        if (
            avg_generation_time
            > config.MAX_RESPONSE_TIME_SECONDS
        ):
            recommendations.append(
                "Reduce LLM response latency."
            )

        if (
            resolution_success_rate
            < config.MIN_RESOLUTION_SUCCESS_RATE
        ):
            recommendations.append(
                "Improve AI resolution quality."
            )

        logger.info("Optimization Agent completed.")

        return {
            "resolution_success_rate": resolution_success_rate,
            "knowledge_base_coverage": kb_metrics.get(
                "knowledge_base_coverage",
                0.0,
            ),
            "average_similarity_score": kb_metrics.get(
                "average_similarity_score",
                0.0,
            ),
            "average_retrieval_time": kb_metrics.get(
                "average_retrieval_time",
                0.0,
            ),
            "average_generation_time": avg_generation_time,
            "latency_improvement": latency_change,
            "recommendations": recommendations,
        }