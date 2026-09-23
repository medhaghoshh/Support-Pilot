"""
Unit tests for statistics utilities.
"""

from app.utils.statistics import (
    calculate_average,
    calculate_failure_rate,
    calculate_latency_improvement,
    calculate_percentage,
    calculate_success_rate,
)


def test_average():
    assert calculate_average([1, 2, 3]) == 2.0


def test_average_empty():
    assert calculate_average([]) == 0.0


def test_success_rate():
    assert calculate_success_rate(8, 10) == 80.0


def test_failure_rate():
    assert calculate_failure_rate(2, 10) == 20.0


def test_percentage():
    assert calculate_percentage(25, 100) == 25.0


def test_zero_total():
    assert calculate_success_rate(0, 0) == 0.0


def test_latency_improvement():
    assert calculate_latency_improvement(10.0, 8.0) == 20.0


def test_latency_regression():
    assert calculate_latency_improvement(10.0, 12.0) == -20.0