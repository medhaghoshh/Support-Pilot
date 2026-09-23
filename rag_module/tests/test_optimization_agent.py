"""
Unit tests for OptimizationAgent.
"""

from app.agents.optimization_agent import OptimizationAgent


def test_optimization_agent():
    agent = OptimizationAgent()

    metrics = {
        "knowledge_base_coverage": 85.0,
        "average_similarity_score": 0.62,
        "average_retrieval_time": 0.03,
    }

    result = agent.run(
        kb_metrics=metrics,
        resolution_success_rate=90.0,
        avg_generation_time=1.5,
        previous_generation_time=2.0,
    )

    assert result["knowledge_base_coverage"] == 85.0
    assert result["resolution_success_rate"] == 90.0
    assert result["average_generation_time"] == 1.5
    assert result["latency_improvement"] == 25.0