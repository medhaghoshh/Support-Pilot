"""
SupportPilot AI

Optimization Configuration

Central configuration values used by the
optimization layer.

These values are intentionally isolated to
avoid hardcoding thresholds throughout the
project.
"""

from __future__ import annotations

# ===================================================
# Knowledge Base
# ===================================================

DEFAULT_SIMILARITY_THRESHOLD: float = 0.45

# ===================================================
# Resolution
# ===================================================

MIN_RESOLUTION_SUCCESS_RATE: float = 80.0

# ===================================================
# Performance
# ===================================================

MAX_RESPONSE_TIME_SECONDS: float = 5.0

MAX_RETRIEVAL_TIME_SECONDS: float = 1.0

LATENCY_WARNING_THRESHOLD: float = 3.0

# ===================================================
# Feature Toggles
# ===================================================

ENABLE_PERFORMANCE_LOGGING: bool = True

ENABLE_KB_ANALYSIS: bool = True

ENABLE_RECOMMENDATIONS: bool = True

# ===================================================
# Public Exports
# ===================================================

__all__ = [
    "DEFAULT_SIMILARITY_THRESHOLD",
    "MIN_RESOLUTION_SUCCESS_RATE",
    "MAX_RESPONSE_TIME_SECONDS",
    "MAX_RETRIEVAL_TIME_SECONDS",
    "LATENCY_WARNING_THRESHOLD",
    "ENABLE_PERFORMANCE_LOGGING",
    "ENABLE_KB_ANALYSIS",
    "ENABLE_RECOMMENDATIONS",
]