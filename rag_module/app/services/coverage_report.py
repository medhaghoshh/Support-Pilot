"""
Milestone 4 - Knowledge Base / Data Engineer (Member 4)
Coverage report generator.

Produces a single JSON summary of KB coverage that the Backend/Frontend
(Roles 2 and 1) can consume for the dashboard's "Knowledge Base Coverage"
metric and the System Optimization panel.

Imports are relative to the app.services package.
"""

import json
from collections import Counter

from app.services.coverage_analyzer import (
    official_coverage,
    gap_analysis,
    gaps_by_category,
    recommend_gaps,
    GAP_THRESHOLD,
)
from app.services.sample_ticket_data import get_sample_tickets
from app.services.kb_articles import get_articles


def build_report(tickets=None):
    if tickets is None:
        tickets = get_sample_tickets()

    articles = get_articles()
    category_counts = dict(Counter(a["category"] for a in articles))

    official = official_coverage(tickets)
    deeper = gap_analysis(tickets)
    by_cat = gaps_by_category(tickets)
    recs = recommend_gaps(tickets)

    report = {
        "kb_summary": {
            "total_articles": len(articles),
            "categories": len(category_counts),
            "articles_per_category": category_counts,
        },
        "official_coverage": {
            "definition": (
                "Any successfully retrieved document counts as a match "
                "(no similarity threshold). Matches Role 3's dashboard metric."
            ),
            "total_tickets": official["total_tickets"],
            "covered": official["covered"],
            "gaps": official["gaps"],
            "coverage_pct": official["coverage_pct"],
        },
        "deeper_gap_analysis": {
            "definition": (
                f"Uses similarity_score with a {GAP_THRESHOLD} threshold to "
                "surface weak matches as real content gaps."
            ),
            "threshold": GAP_THRESHOLD,
            "strong_matches": deeper["strong_match_count"],
            "weak_matches": deeper["weak_match_count"],
            "no_matches": deeper["no_match_count"],
            "effective_coverage_pct": deeper["effective_coverage_pct"],
        },
        "gaps_by_category": {
            cat: {"gap_tickets": d["count"], "avg_similarity": d["avg_score"]}
            for cat, d in by_cat.items()
        },
        "recommendations": recs,
    }
    return report
