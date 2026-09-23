from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from . import resolve
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SupportPilot - Ticket Intake API")

app.include_router(resolve.router)
@app.get("/")
def root():
    return {"messhow toage": "SupportPilot Ticket Intake API is running"}


@app.post("/api/tickets", response_model=schemas.TicketResponse)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(
        models.User.email == ticket.requester_email
    ).first()

    if not user:
        user = models.User(
            name=ticket.requester_email.split("@")[0],
            email=ticket.requester_email,
            department=ticket.department,
            role="EMPLOYEE",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    new_ticket = models.Ticket(
        user_id=user.user_id,
        subject=ticket.subject,
        description=ticket.description,
        priority="P4",
        severity="LOW",
        status="OPEN",
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    return new_ticket


@app.get("/api/tickets/{ticket_id}", response_model=schemas.TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return ticket


@app.get("/api/tickets", response_model=list[schemas.TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()