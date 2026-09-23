"""
Self-test for the Milestone 3 deliverables.
Run this after `python ingest.py` to confirm everything is wired correctly.

Checks:
  1. Every article has reasoning data, and vice versa
  2. All cross-references point to real articles
  3. Resolution steps are numbered correctly and fully populated
  4. Diagnosis returns the expected category for known tickets
  5. Low-signal tickets correctly ask for clarification
  6. Reasoning chains resolve without infinite loops
  7. All SQL tables are populated
"""

import sqlite3
import sys

from kb_articles import get_articles
from kb_reasoning import REASONING, get_reasoning_chain
from diagnose import diagnose_ticket

DB_PATH = "knowledge_base.db"

failures = []


def check(label, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}" + (f" -- {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(label)


print("1. Article / reasoning coverage")
article_ids = {a["kb_id"] for a in get_articles()}
reasoning_ids = set(REASONING)
check("every article has reasoning data", article_ids <= reasoning_ids,
      f"missing: {sorted(article_ids - reasoning_ids)}")
check("no orphan reasoning entries", reasoning_ids <= article_ids,
      f"orphans: {sorted(reasoning_ids - article_ids)}")

print("\n2. Cross-reference integrity")
broken = []
for kb_id, r in REASONING.items():
    for rel in r["related_articles"]:
        if rel not in article_ids:
            broken.append((kb_id, "related", rel))
    nxt = r.get("next_if_unresolved")
    if nxt and nxt not in article_ids:
        broken.append((kb_id, "next_if_unresolved", nxt))
check("all cross-references resolve", not broken, str(broken))

print("\n3. Resolution step structure")
step_problems = []
for kb_id, r in REASONING.items():
    nums = [s["step"] for s in r["resolution_steps"]]
    if nums != list(range(1, len(nums) + 1)):
        step_problems.append((kb_id, "numbering", nums))
    for s in r["resolution_steps"]:
        if not s.get("action") or not s.get("expected"):
            step_problems.append((kb_id, "empty field", s))
check("steps numbered sequentially with all fields", not step_problems,
      str(step_problems))

print("\n4. Diagnosis accuracy on known tickets")
cases = [
    ("My VPN keeps disconnecting when working from home", "Networking"),
    ("I forgot my password and I am locked out", "Password Reset"),
    ("Outlook is not receiving emails", "Email"),
    ("My laptop is overheating and shutting down", "Hardware"),
    ("I got a suspicious email asking for credentials", "Security"),
    ("The printer is offline and jobs are stuck in the queue", "Hardware"),
    ("I need a licence activated for this application", "Software"),
]
correct = 0
for text, expected in cases:
    got = diagnose_ticket(text)["predicted_category"]
    ok = got == expected
    correct += ok
    if not ok:
        print(f"    expected {expected}, got {got}  <- '{text}'")
check(f"diagnosis correct on known tickets ({correct}/{len(cases)})",
      correct == len(cases))

print("\n5. Low-signal handling")
vague = diagnose_ticket("Something is broken please help")
check("vague ticket flags needs_clarification", vague["needs_clarification"])
check("vague ticket supplies clarifying questions",
      len(vague["clarifying_questions"]) > 0)

print("\n6. Reasoning chains terminate")
chain_ok = True
for kb_id in REASONING:
    chain = get_reasoning_chain(kb_id)
    ids = [c["kb_id"] for c in chain]
    if len(ids) != len(set(ids)) or not chain:
        chain_ok = False
        print(f"    problem chain from {kb_id}: {ids}")
check("all chains terminate without repeating", chain_ok)

print("\n7. SQL tables populated")
try:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    expected_tables = {
        "Knowledge_Base": 10,
        "KB_Symptoms": 1,
        "KB_Resolution_Steps": 1,
        "KB_Reasoning": 10,
        "Diagnosis_Rules": 1,
    }
    for table, minimum in expected_tables.items():
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        n = cur.fetchone()[0]
        check(f"{table} populated ({n} rows)", n >= minimum)
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
