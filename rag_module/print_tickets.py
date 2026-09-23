import os
from app.database import SessionLocal
from app.models import Ticket

db = SessionLocal()
try:
    tickets = db.query(Ticket).all()
    print(f"Total tickets in database: {len(tickets)}")
    for t in tickets:
        print(f"Ticket ID: {t.ticket_id} | Subject: '{t.subject}' | Priority: {t.priority} | Severity: {t.severity} | Status: {t.status}")
finally:
    db.close()
