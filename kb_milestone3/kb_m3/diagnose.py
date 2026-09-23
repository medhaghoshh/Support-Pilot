"""
Milestone 3 - Knowledge Base / Data Engineer (Member 4)
Diagnosis engine: turns raw ticket text into a structured analysis the
Diagnosis Agent can act on.

Output shape (per ticket):
{
  "ticket_text": "...",
  "predicted_category": "Networking",
  "confidence": 0.71,
  "needs_clarification": False,
  "ranked_categories": [ {category, score, confidence, matched_symptoms}, ... ],
  "matched_symptoms": ["vpn", "keeps disconnecting"],
  "suggested_kb_ids": ["KB-101", "KB-103", "KB-108"],
  "suggested_priority": "High",
  "clarifying_questions": [...]
}

This is deterministic rule-based analysis, not an ML model. It is meant
to run BEFORE retrieval so the Retrieval Agent gets a category and a KB
shortlist instead of searching blind.
"""

import re

from diagnosis_rules import (
    SYMPTOM_RULES,
    CATEGORY_KB,
    SEVERITY_RULES,
    CONFIDENCE_THRESHOLD,
    TIEBREAK_PRIORITY,
    get_clarifying_questions,
)


def _matches(text, indicator):
    """
    Phrases (containing a space or hyphen) are matched as substrings.
    Single words are matched as whole words, so "vpn" does not match
    inside an unrelated longer token.
    """
    if " " in indicator or "-" in indicator:
        return indicator in text
    return re.search(r"\b" + re.escape(indicator) + r"\b", text) is not None


def score_categories(ticket_text):
    """Returns a list of category scores, highest first."""
    text = ticket_text.lower()
    results = []

    for category, weighted in SYMPTOM_RULES.items():
        score = 0
        matched = []
        for weight, indicators in weighted.items():
            for indicator in indicators:
                if _matches(text, indicator):
                    score += weight
                    matched.append(indicator)
        results.append({
            "category": category,
            "score": score,
            "matched_symptoms": matched,
        })

    # Sort by score, then by tie-break priority (Security first) so an
    # ambiguous ticket with a security signal is not lost to a tie.
    results.sort(
        key=lambda r: (-r["score"], TIEBREAK_PRIORITY.index(r["category"]))
    )
    return results


# Score at which we consider the evidence fully convincing. Chosen so a
# single strong indicator alone cannot produce a near-certain result.
FULL_EVIDENCE_SCORE = 9


def _confidence(ranked):
    """
    Confidence blends three things:
      share    - how much of the total evidence the winner holds
      margin   - how far clear of the runner-up it is
      evidence - how much absolute evidence was found at all

    The evidence term is what stops a single keyword match from
    reporting near-certainty. Returns 0.0 when nothing matched.
    """
    total = sum(r["score"] for r in ranked)
    if total == 0:
        return 0.0

    top = ranked[0]["score"]
    runner_up = ranked[1]["score"] if len(ranked) > 1 else 0

    share = top / total
    margin = (top - runner_up) / top if top else 0
    evidence = min(top / FULL_EVIDENCE_SCORE, 1.0)

    confidence = (share * 0.5) + (margin * 0.2) + (evidence * 0.3)
    return round(min(confidence, 0.95), 2)


def detect_severity(ticket_text):
    """Suggests a priority based on urgency wording in the ticket."""
    text = ticket_text.lower()
    for level in ["Critical", "High", "Medium", "Low"]:
        for indicator in SEVERITY_RULES[level]:
            if _matches(text, indicator):
                return level
    return "Medium"  # sensible default when nothing signals urgency


def diagnose_ticket(ticket_text, top_n=3):
    """Main entry point for the Diagnosis Agent."""
    ranked = score_categories(ticket_text)
    confidence = _confidence(ranked)

    scored = [r for r in ranked if r["score"] > 0][:top_n]
    for r in scored:
        total = sum(x["score"] for x in ranked) or 1
        r["confidence"] = round(r["score"] / total, 2)

    if scored:
        predicted = scored[0]["category"]
        matched = scored[0]["matched_symptoms"]
        suggested_kb = CATEGORY_KB.get(predicted, [])
    else:
        predicted = None
        matched = []
        suggested_kb = []

    needs_clarification = confidence < CONFIDENCE_THRESHOLD

    return {
        "ticket_text": ticket_text,
        "predicted_category": predicted,
        "confidence": confidence,
        "needs_clarification": needs_clarification,
        "ranked_categories": scored,
        "matched_symptoms": matched,
        "suggested_kb_ids": suggested_kb,
        "suggested_priority": detect_severity(ticket_text),
        "clarifying_questions": (
            get_clarifying_questions(predicted) if needs_clarification else []
        ),
    }


if __name__ == "__main__":
    samples = [
        "My VPN keeps disconnecting every few minutes when I work from home",
        "I forgot my password and I am locked out of my account",
        "Outlook is not receiving emails since this morning",
        "My laptop keeps shutting down and getting really hot",
        "I received a suspicious email asking for my login credentials",
        "The printer shows offline and my print jobs are stuck",
        "Something is wrong",
    ]
    for s in samples:
        d = diagnose_ticket(s)
        print(f"\nTicket: {s}")
        print(f"  Category   : {d['predicted_category']} "
              f"(confidence {d['confidence']})")
        print(f"  Priority   : {d['suggested_priority']}")
        print(f"  Symptoms   : {d['matched_symptoms'][:5]}")
        print(f"  KB shortlist: {d['suggested_kb_ids']}")
        if d["needs_clarification"]:
            print(f"  NEEDS CLARIFICATION -> {d['clarifying_questions'][0]}")
