"""
Unit tests for app.utils.timers.
"""

from __future__ import annotations

import time

import pytest

from app.utils.timers import Timer


def test_timer_start_stop() -> None:
    """
    Timer should measure elapsed time.
    """
    timer = Timer()

    timer.start()
    time.sleep(0.01)
    elapsed = timer.stop()

    assert elapsed > 0
    assert timer.elapsed_ms > 0


def test_timer_running_state() -> None:
    """
    Timer should correctly report running state.
    """
    timer = Timer()

    assert not timer.is_running

    timer.start()

    assert timer.is_running

    timer.stop()

    assert not timer.is_running


def test_timer_reset() -> None:
    """
    Reset should clear timer state.
    """
    timer = Timer()

    timer.start()
    timer.stop()

    timer.reset()

    assert not timer.is_running

    with pytest.raises(RuntimeError):
        _ = timer.elapsed_seconds


def test_timer_without_start() -> None:
    """
    Accessing elapsed time before starting should fail.
    """
    timer = Timer()

    with pytest.raises(RuntimeError):
        timer.stop()


def test_context_manager() -> None:
    """
    Timer should support context manager usage.
    """
    with Timer() as timer:
        time.sleep(0.01)

    assert timer.elapsed_ms > 0


def test_elapsed_increases_while_running() -> None:
    """
    Elapsed time should increase while timer is running.
    """
    timer = Timer()

    timer.start()

    first = timer.elapsed_ms

    time.sleep(0.01)

    second = timer.elapsed_ms

    timer.stop()

    assert second > first