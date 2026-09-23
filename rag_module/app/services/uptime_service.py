"""
SupportPilot AI

Uptime Service

Tracks application uptime for the
Milestone 4 analytics dashboard.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class UptimeService:
    """
    Provides application uptime statistics.

    The service records the application
    startup time and calculates the current
    uptime whenever requested.
    """

    # ---------------------------------------------------
    # Application Startup Time
    # ---------------------------------------------------

    START_TIME = datetime.now()

    # ---------------------------------------------------
    # Raw Uptime
    # ---------------------------------------------------

    @classmethod
    def get_uptime_duration(
        cls,
    ) -> timedelta:
        """
        Calculate the application's uptime.

        Returns
        -------
        timedelta
            Elapsed time since the application
            started.
        """

        logger.debug(
            "Calculating application uptime."
        )

        return datetime.now() - cls.START_TIME

    # ---------------------------------------------------
    # Dashboard Summary
    # ---------------------------------------------------

    @classmethod
    def get_system_uptime(
        cls,
    ) -> dict[str, Any]:
        """
        Build a dashboard-friendly uptime summary.

        Returns
        -------
        dict[str, Any]
            Structured uptime information.
        """

        logger.info(
            "Generating system uptime summary."
        )

        uptime = cls.get_uptime_duration()

        total_seconds = int(
            uptime.total_seconds()
        )

        days = total_seconds // 86400
        hours = (
            total_seconds % 86400
        ) // 3600
        minutes = (
            total_seconds % 3600
        ) // 60
        seconds = total_seconds % 60

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "uptime": (
                f"{days}d "
                f"{hours}h "
                f"{minutes}m "
                f"{seconds}s"
            ),
            "startup_time": (
                cls.START_TIME.isoformat()
            ),
        }


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "UptimeService",
]