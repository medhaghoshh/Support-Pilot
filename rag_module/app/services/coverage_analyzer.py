"""
Milestone 4 - Knowledge Base / Data Engineer (Member 4)
KB Coverage and Gap Analysis.

Role 3 (Vector DB) confirmed the interface:
  - The Retrieval Agent returns a similarity_score (0-1) per ticket,
    normalized from the ChromaDB distance.
  - The OFFICIAL Knowledge Base Coverage metric currently counts any
    successful retrieval as a match (no threshold). A gap = nothing
    returned at all.

This tool does two things:
  1. Reports the official coverage number (match = a document was returned)
  2. Runs a DEEPER gap analysis using similarity_score with a threshold,
     so weak/irrelevant matches are surfaced as real content gaps even
     when they officially count as "covered".

The point of part 2: because retrieval almost always returns *something*,
the official metric can read close to 100% while real gaps still exist.
similarity_score is what lets us find those.
"""

from collections import defaultdict

# Below this, a returned document is treated as a weak match / real gap
# for content-planning purposes. Starting point agreed with Role 3;
# tune as real ticket data comes in.
GAP_THRESHOLD = 0.45

# At or above this, the match is considered genuinely strong.
STRONG_MATCH = 0.60


def official_coverage(tickets):
    """
    The official metric as defined by Role 3: a ticket is "covered" if the
    Retrieval Agent returned any document at all (retrieved_kb_id is not None).
    No similarity threshold applied.
    """
    total = len(tickets)
    if total == 0:
        return {"total_tickets": 0, "covered": 0, "gaps": 0, "coverage_pct": 0.0}

    covered = sum(1 for t in tickets if t.get("retrieved_kb_id"))
    gaps = total - covered
    return {
        "total_tickets": total,
        "covered": covered,
        "gaps": gaps,
        "coverage_pct": round(covered / total * 100, 1),
    }


def gap_analysis(tickets, threshold=GAP_THRESHOLD):
    """
    Deeper analysis using similarity_score. Classifies every ticket as:
      - no_match     : retrieval returned nothing (a true/official gap)
      - weak_match   : returned something, but below threshold (a real
                       content gap the official metric misses)
      - strong_match : returned something at or above threshold

    Returns the counts plus the list of weak/no-match tickets.
    """
    total = len(tickets)
    no_match = []
    weak_match = []
    strong_match = []

    for t in tickets:
        kb_id = t.get("retrieved_kb_id")
        score = t.get("similarity_score")

        if not kb_id or score is None:
            no_match.append(t)
        elif score < threshold:
            weak_match.append(t)
        else:
            strong_match.append(t)

    return {
        "total_tickets": total,
        "threshold": threshold,
        "no_match_count": len(no_match),
        "weak_match_count": len(weak_match),
        "strong_match_count": len(strong_match),
        "effective_coverage_pct": round(
            len(strong_match) / total * 100, 1
        ) if total else 0.0,
        "actionable_gaps": no_match + weak_match,
    }


def gaps_by_category(tickets, threshold=GAP_THRESHOLD):
    """
    Groups the weak/no-match tickets by their category so we can see WHICH
    topics need more KB content, not just how many gaps exist overall.
    """
    buckets = defaultdict(lambda: {"count": 0, "avg_score": 0.0, "examples": []})

    for t in tickets:
        kb_id = t.get("retrieved_kb_id")
        score = t.get("similarity_score")
        is_gap = (not kb_id) or (score is None) or (score < threshold)
        if not is_gap:
            continue

        cat = t.get("category", "Uncategorized")
        b = buckets[cat]
        b["count"] += 1
        b["examples"].append(t.get("ticket_text", "")[:80])
        b["_scores"] = b.get("_scores", []) + [score if score is not None else 0.0]

    result = {}
    for cat, b in buckets.items():
        scores = b.pop("_scores", [])
        b["avg_score"] = round(sum(scores) / len(scores), 3) if scores else 0.0
        b["examples"] = b["examples"][:3]
        result[cat] = b

    return dict(sorted(result.items(), key=lambda kv: kv[1]["count"], reverse=True))


def recommend_gaps(tickets, threshold=GAP_THRESHOLD, min_occurrences=2):
    """
    Turns the analysis into a prioritized recommendation:
    which categories have repeated weak/no-match tickets and therefore
    genuinely need new or expanded KB content.
    """
    by_cat = gaps_by_category(tickets, threshold)
    recommendations = []

    for cat, data in by_cat.items():
        if data["count"] >= min_occurrences:
            recommendations.append({
                "category": cat,
                "gap_tickets": data["count"],
                "avg_similarity": data["avg_score"],
                "priority": "High" if data["count"] >= 4 else "Medium",
                "example_tickets": data["examples"],
                "suggested_action": (
                    f"Add or expand KB articles for '{cat}' - "
                    f"{data['count']} tickets matched weakly or not at all "
                    f"(avg similarity {data['avg_score']})."
                ),
            })

    return recommendations
