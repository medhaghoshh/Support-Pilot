"""
SupportPilot AI

Timer Utilities

Provides a reusable high-precision timer for
measuring execution latency across the
SupportPilot AI pipeline.

Typical use cases
-----------------
- LLM response generation
- Retrieval latency
- Workflow execution time
- Analytics and optimization metrics
"""

from __future__ import annotations

import logging
import time
from types import TracebackType
from typing import Optional

logger = logging.getLogger(__name__)


class Timer:
    """
    High-precision execution timer.

    Example
    -------
    >>> timer = Timer()
    >>> timer.start()
    >>> # perform work
    >>> timer.stop()
    >>> print(timer.elapsed_ms)
    """

    def __init__(self) -> None:
        self._start: Optional[float] = None
        self._end: Optional[float] = None

    # ---------------------------------------------------
    # Start
    # ---------------------------------------------------

    def start(self) -> None:
        """
        Start the timer.
        """

        logger.debug("Timer started.")

        self._start = time.perf_counter()
        self._end = None

    # ---------------------------------------------------
    # Stop
    # ---------------------------------------------------

    def stop(self) -> float:
        """
        Stop the timer.

        Returns
        -------
        float
            Elapsed time in seconds.

        Raises
        ------
        RuntimeError
            If the timer has not been started.
        """

        if self._start is None:
            raise RuntimeError(
                "Timer has not been started."
            )

        self._end = time.perf_counter()

        logger.debug(
            "Timer stopped (%.6f seconds).",
            self.elapsed_seconds,
        )

        return self.elapsed_seconds

    # ---------------------------------------------------
    # Elapsed Seconds
    # ---------------------------------------------------

    @property
    def elapsed_seconds(self) -> float:
        """
        Return elapsed time in seconds.
        """

        if self._start is None:
            raise RuntimeError(
                "Timer has not been started."
            )

        end = (
            self._end
            if self._end is not None
            else time.perf_counter()
        )

        return end - self._start

    # ---------------------------------------------------
    # Elapsed Milliseconds
    # ---------------------------------------------------

    @property
    def elapsed_ms(self) -> float:
        """
        Return elapsed time in milliseconds.
        """

        return self.elapsed_seconds * 1000.0

    # ---------------------------------------------------
    # Reset
    # ---------------------------------------------------

    def reset(self) -> None:
        """
        Reset the timer.
        """

        logger.debug("Timer reset.")

        self._start = None
        self._end = None

    # ---------------------------------------------------
    # Running Status
    # ---------------------------------------------------

    @property
    def is_running(self) -> bool:
        """
        Returns
        -------
        bool
            True if the timer is currently
            running.
        """

        return (
            self._start is not None
            and self._end is None
        )

    # ---------------------------------------------------
    # Context Manager
    # ---------------------------------------------------

    def __enter__(self) -> "Timer":
        """
        Enter context manager.
        """

        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """
        Exit context manager.
        """

        self.stop()


# ---------------------------------------------------
# Public Exports
# ---------------------------------------------------

__all__ = [
    "Timer",
]