"""
Unit tests for optimization configuration.
"""

from app.config import optimization_config as config


def test_similarity_threshold():
    assert config.DEFAULT_SIMILARITY_THRESHOLD == 0.45


def test_resolution_rate():
    assert config.MIN_RESOLUTION_SUCCESS_RATE == 80.0


def test_response_time():
    assert config.MAX_RESPONSE_TIME_SECONDS > 0


def test_retrieval_time():
    assert config.MAX_RETRIEVAL_TIME_SECONDS > 0


def test_flags():
    assert config.ENABLE_PERFORMANCE_LOGGING
    assert config.ENABLE_KB_ANALYSIS
    assert config.ENABLE_RECOMMENDATIONS