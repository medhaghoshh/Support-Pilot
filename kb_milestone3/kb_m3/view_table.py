"""
Views the populated SQL tables.
Useful for verifying ingestion and for demoing to mentors/teammates.
"""

import sqlite3

DB_PATH = "knowledge_base.db"


def view_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ---- Knowledge_Base (Milestone 2, required schema) ----
    cur.execute(
        "SELECT article_id, title, category, embedding_id FROM Knowledge_Base"
    )
    rows = cur.fetchall()
    print(f"Knowledge_Base - {len(rows)} rows\n")
    print(f"{'article_id':10} | {'category':14} | {'embedding_id':14} | title")
    print("-" * 92)
    for r in rows:
        print(f"{r[0]:10} | {r[2]:14} | {r[3]:14} | {r[1]}")

    # ---- Milestone 3 tables ----
    print("\n")
    cur.execute("SELECT kb_id, COUNT(*) FROM KB_Symptoms GROUP BY kb_id")
    sym = cur.fetchall()
    cur.execute("SELECT kb_id, COUNT(*) FROM KB_Resolution_Steps GROUP BY kb_id")
    steps = dict(cur.fetchall())

    print("KB_Symptoms / KB_Resolution_Steps per article\n")
    print(f"{'kb_id':10} | {'symptoms':9} | steps")
    print("-" * 34)
    for kb_id, n in sym:
        print(f"{kb_id:10} | {n:^9} | {steps.get(kb_id, 0)}")

    print("\n")
    cur.execute(
        "SELECT kb_id, escalate_to, auto_resolvable, next_if_unresolved "
        "FROM KB_Reasoning"
    )
    print("KB_Reasoning\n")
    print(f"{'kb_id':10} | {'escalate_to':26} | {'auto':5} | next_if_unresolved")
    print("-" * 76)
    for r in cur.fetchall():
        auto = "yes" if r[2] else "no"
        nxt = r[3] or "-"
        print(f"{r[0]:10} | {r[1]:26} | {auto:5} | {nxt}")

    print("\n")
    cur.execute(
        "SELECT category, COUNT(*) FROM Diagnosis_Rules GROUP BY category"
    )
    print("Diagnosis_Rules - symptom indicators per category\n")
    for cat, n in cur.fetchall():
        print(f"  {cat:16} {n} indicators")

    conn.close()


if __name__ == "__main__":
    view_table()
