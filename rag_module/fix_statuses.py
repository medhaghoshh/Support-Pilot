"""
DB correction script:
- Ticket 5 (Password failure): OPEN → RESOLVED  (Password Reset = auto-resolve category)
- Ticket 7 (Keyboard keys failure): RESOLVED → IN_PROGRESS  (Hardware = always escalate)
"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("BEFORE:")
    rows = conn.execute(text("SELECT ticket_id, subject, status FROM tickets ORDER BY ticket_id")).fetchall()
    for r in rows:
        print(f"  ID={r[0]}  STATUS={r[2]}  SUBJ={r[1]}")

    # Ticket 5: Password Reset → auto-resolved by AI, has AI response
    conn.execute(text("UPDATE tickets SET status = 'RESOLVED' WHERE ticket_id = 5 AND status = 'OPEN'"))

    # Ticket 7: Hardware (Keyboard) → must be IN_PROGRESS (escalated to hardware team)
    conn.execute(text("UPDATE tickets SET status = 'IN_PROGRESS' WHERE ticket_id = 7"))

    conn.commit()

    print("\nAFTER:")
    rows = conn.execute(text("SELECT ticket_id, subject, status FROM tickets ORDER BY ticket_id")).fetchall()
    for r in rows:
        print(f"  ID={r[0]}  STATUS={r[2]}  SUBJ={r[1]}")

print("\nDone.")
