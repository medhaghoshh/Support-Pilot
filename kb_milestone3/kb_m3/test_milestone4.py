"""
Self-test for the Milestone 4 deliverables.
Run after `python ingest.py` to confirm everything is wired correctly.

Checks:
  1. KB expanded and every article is well-formed (300-500 words, all fields)
  2. New gap-filling articles exist and cover the identified gap topics
  3. official_coverage counts match/no-match correctly
  4. gap_analysis correctly separates strong / weak / no matches
  5. recommendations surface the seeded gap categories
  6. coverage report builds and is valid JSON-serializable
  7. SQL Knowledge_Base table still has exactly its 5 required columns
"""

import json
import sqlite3
import sys

from kb_articles import get_articles
from coverage_analyzer import (
    official_coverage,
    gap_analysis,
    recommend_gaps,
)
from coverage_report import build_report
from sample_ticket_data import get_sample_tickets

DB_PATH = "knowledge_base.db"
failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(label)


print("1. KB articles well-formed")
articles = get_articles()
required_fields = {"kb_id", "title", "category", "tags", "last_updated",
                   "priority", "version", "author", "content"}
all_fields_ok = all(required_fields <= set(a.keys()) for a in articles)
check(f"all {len(articles)} articles have required fields", all_fields_ok)
word_counts_ok = all(300 <= len(a["content"].split()) <= 500 for a in articles)
check("all articles are 300-500 words", word_counts_ok,
      str([(a["kb_id"], len(a["content"].split())) for a in articles
           if not (300 <= len(a["content"].split()) <= 500)]))

print("\n2. Gap-filling articles added")
ids = {a["kb_id"] for a in articles}
new_ids = {"KB-111", "KB-112", "KB-113", "KB-114", "KB-115", "KB-116", "KB-117"}
check("new gap-filling articles present", new_ids <= ids,
      f"missing: {sorted(new_ids - ids)}")
cats = {a["category"] for a in articles}
check("Human Resources category now covered", "Human Resources" in cats)

print("\n3. Official coverage metric")
tickets = get_sample_tickets()
oc = official_coverage(tickets)
manual_covered = sum(1 for t in tickets if t.get("retrieved_kb_id"))
check("covered count matches manual count", oc["covered"] == manual_covered)
check("covered + gaps == total",
      oc["covered"] + oc["gaps"] == oc["total_tickets"])

print("\n4. Gap analysis classification")
ga = gap_analysis(tickets)
total_classified = (ga["strong_match_count"] + ga["weak_match_count"]
                    + ga["no_match_count"])
check("every ticket classified exactly once",
      total_classified == ga["total_tickets"],
      f"{total_classified} vs {ga['total_tickets']}")
check("weak matches detected below threshold", ga["weak_match_count"] > 0)
check("no-matches detected", ga["no_match_count"] > 0)
check("effective coverage <= official coverage",
      ga["effective_coverage_pct"] <= oc["coverage_pct"])

print("\n5. Recommendations")
recs = recommend_gaps(tickets)
rec_cats = {r["category"] for r in recs}
check("recommendations generated", len(recs) > 0)
check("seeded gap categories surfaced (Email/Software/HR)",
      {"Email", "Software", "Human Resources"} & rec_cats != set())

print("\n6. Coverage report builds and serializes")
try:
    report = build_report()
    json.dumps(report)  # must be JSON-serializable
    check("report is JSON-serializable", True)
    check("report has all expected sections",
          all(k in report for k in
              ["kb_summary", "official_coverage", "deeper_gap_analysis",
               "gaps_by_category", "recommendations"]))
except (TypeError, ValueError) as e:
    check("report is JSON-serializable", False, str(e))

print("\n7. Knowledge_Base SQL schema intact")
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(Knowledge_Base)")
    cols = [row[1] for row in cur.fetchall()]
    expected = ["article_id", "title", "content", "category", "embedding_id"]
    check("Knowledge_Base has exactly the 5 required columns",
          cols == expected, f"got {cols}")
    cur.execute("SELECT COUNT(*) FROM Knowledge_Base")
    n = cur.fetchone()[0]
    check(f"Knowledge_Base populated with all articles ({n} rows)",
          n == len(articles))
    conn.close()
except sqlite3.OperationalError as e:
    check("database readable", False, f"{e} - run 'python ingest.py' first")

print("\n" + "=" * 55)
if failures:
    print(f"{len(failures)} CHECK(S) FAILED:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("ALL CHECKS PASSED")
