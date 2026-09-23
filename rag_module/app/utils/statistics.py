"""
SupportPilot AI

Statistics Utilities

Provides reusable statistical helper functions
used by analytics, optimization, monitoring,
and reporting components.
"""

from __future__ import annotations

import logging
from statistics import mean
from typing import Iterable

logger = logging.getLogger(__name__)


# ---------------------------------------------------
# Average
# ---------------------------------------------------

def calculate_average(
    values: Iterable[float],
) -> float:
    """
    Calculate the arithmetic mean.

    Parameters
    ----------
    values : Iterable[float]
        Collection of numeric values.

    Returns
    -------
    float
        Mean value, or 0.0 if the collection
        is empty.
    """

    values = list(values)

    if not values:

        logger.debug(
            "Average requested for an empty collection."
        )

        return 0.0

    return float(mean(values))


# ---------------------------------------------------
# Success Rate
# ---------------------------------------------------

def calculate_success_rate(
    success: int,
    total: int,
) -> float:
    """
    Calculate the success percentage.

    Parameters
    ----------
    success : int
        Number of successful operations.

    total : int
        Total number of operations.

    Returns
    -------
    float
        Success percentage between
        0.0 and 100.0.
    """

    if total <= 0:

        logger.debug(
            "Success rate requested with total <= 0."
        )

        return 0.0

    return (success / total) * 100.0


# ---------------------------------------------------
# Failure Rate
# ---------------------------------------------------

def calculate_failure_rate(
    failures: int,
    total: int,
) -> float:
    """
    Calculate the failure percentage.

    Parameters
    ----------
    failures : int
        Number of failed operations.

    total : int
        Total number of operations.

    Returns
    -------
    float
        Failure percentage between
        0.0 and 100.0.
    """

    if total <= 0:

        logger.debug(
            "Failure rate requested with total <= 0."
        )

        return 0.0

    return (failures / total) * 100.0


# ---------------------------------------------------
# Generic Percentage
# ---------------------------------------------------

def calculate_percentage(
    part: float,
    whole: float,
) -> float:
    """
    Calculate a percentage.

    Parameters
    ----------
    part : float
        Numerator.

    whole : float
        Denominator.

    Returns
    -------
    float
        Percentage between
        0.0 and 100.0.
    """

    if whole <= 0:

        logger.debug(
            "Percentage requested with whole <= 0."
        )

        return 0.0

    return (part / whole) * 100.0


# ---------------------------------------------------
# Latency Improvement
# ---------------------------------------------------

def calculate_latency_improvement(
    previous_latency: float,
    current_latency: float,
) -> float:
    """
    Calculate latency improvement.

    Positive values indicate an improvement.

    Negative values indicate slower
    performance compared to the previous
    measurement.

    Parameters
    ----------
    previous_latency : float
        Previous execution time.

    current_latency : float
        Current execution time.

    Returns
    -------
    float
        Percentage improvement.
    """

    if previous_latency <= 0:

        logger.debug(
            "Latency improvement requested "
            "with previous latency <= 0."
        )

        return 0.0

    return (
        (
            previous_latency
            - current_latency
        )
        / previous_latency
    ) * 100.0


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "calculate_average",
    "calculate_success_rate",
    "calculate_failure_rate",
    "calculate_percentage",
    "calculate_latency_improvement",
]