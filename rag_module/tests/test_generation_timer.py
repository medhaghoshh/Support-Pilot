"""
Unit tests for GenerationTimer.
"""

from __future__ import annotations

import time

from app.rag.generation_timer import GenerationTimer


def test_generation_timer() -> None:
    timer = GenerationTimer()

    timer.start()
    time.sleep(0.01)
    timer.stop()

    assert timer.latency_ms > 0
    assert timer.latency_seconds > 0


def test_generation_timer_context() -> None:
    with GenerationTimer() as timer:
        time.sleep(0.01)

    assert timer.latency_ms > 0