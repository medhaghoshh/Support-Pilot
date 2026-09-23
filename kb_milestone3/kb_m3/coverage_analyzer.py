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
    The official metric as defined by Role 3: a ticket is 'covered' if the
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

    Returns the counts plus the list of weak/no-match tickets, which are
    the ones worth acting on for KB improvement.
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

    actionable = no_match + weak_match
    return {
        "total_tickets": total,
        "threshold": threshold,
        "no_match_count": len(no_match),
        "weak_match_count": len(weak_match),
        "strong_match_count": len(strong_match),
        "effective_coverage_pct": round(
            len(strong_match) / total * 100, 1
        ) if total else 0.0,
        "actionable_gaps": actionable,
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
        # running average of the (low) scores, treating no-match as 0
        b["_scores"] = b.get("_scores", []) + [score if score is not None else 0.0]

    # finalize averages
    result = {}
    for cat, b in buckets.items():
        scores = b.pop("_scores", [])
        b["avg_score"] = round(sum(scores) / len(scores), 3) if scores else 0.0
        b["examples"] = b["examples"][:3]  # keep it readable
        result[cat] = b

    # sort so the biggest gaps come first
    return dict(sorted(result.items(), key=lambda kv: kv[1]["count"], reverse=True))


def recommend_gaps(tickets, threshold=GAP_THRESHOLD, min_occurrences=2):
    """
    Turns the analysis into a prioritized, human-readable recommendation:
    which categories have repeated weak/no-match tickets and therefore
    genuinely need new or expanded KB content.

    min_occurrences avoids over-reacting to a single odd ticket - a real
    gap shows up more than once.
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


if __name__ == "__main__":
    from sample_ticket_data import get_sample_tickets

    tickets = get_sample_tickets()

    print("=" * 60)
    print("1. OFFICIAL COVERAGE (Role 3's definition: any doc returned)")
    print("=" * 60)
    off = official_coverage(tickets)
    for k, v in off.items():
        print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print(f"2. DEEPER GAP ANALYSIS (similarity threshold = {GAP_THRESHOLD})")
    print("=" * 60)
    ga = gap_analysis(tickets)
    print(f"  total tickets       : {ga['total_tickets']}")
    print(f"  strong matches      : {ga['strong_match_count']}")
    print(f"  weak matches        : {ga['weak_match_count']}  <- officially 'covered', actually gaps")
    print(f"  no matches          : {ga['no_match_count']}")
    print(f"  effective coverage  : {ga['effective_coverage_pct']}%  (vs official {off['coverage_pct']}%)")

    print("\n" + "=" * 60)
    print("3. GAPS BY CATEGORY")
    print("=" * 60)
    for cat, data in gaps_by_category(tickets).items():
        print(f"  {cat:16} {data['count']} gap ticket(s), avg score {data['avg_score']}")

    print("\n" + "=" * 60)
    print("4. RECOMMENDATIONS (what content to add)")
    print("=" * 60)
    recs = recommend_gaps(tickets)
    if not recs:
        print("  No repeated gaps found - KB coverage looks healthy.")
    for r in recs:
        print(f"\n  [{r['priority']}] {r['category']} "
              f"({r['gap_tickets']} tickets, avg sim {r['avg_similarity']})")
        print(f"    -> {r['suggested_action']}")
        for ex in r["example_tickets"]:
            print(f"       e.g. \"{ex}\"")
