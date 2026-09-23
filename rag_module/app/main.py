"""
SupportPilot AI

Main FastAPI application.

Provides:
- Ticket Management APIs
- AI Resolution APIs
- Analytics APIs
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import analytics_router
from . import integrations_router
from . import models
from . import resolve
from . import schemas
from .database import Base, engine, get_db
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    force=True,
)
# ---------------------------------------------------
# Create Missing Database Tables
# ---------------------------------------------------

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------
# FastAPI Application
# ---------------------------------------------------

app = FastAPI(
    title="SupportPilot AI",
    description=(
        "AI-powered IT Helpdesk System built during the "
        "Infosys Internship Project."
    ),
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Tickets",
            "description": "Ticket creation and retrieval endpoints.",
        },
        {
            "name": "Analytics",
            "description": "Dashboard and optimization metrics.",
        },
    ],
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# Register Routers
# ---------------------------------------------------

app.include_router(resolve.router)
app.include_router(analytics_router.router)
app.include_router(integrations_router.router, prefix="/api")


# ---------------------------------------------------
# Startup Event
# ---------------------------------------------------

@app.on_event("startup")
def startup():
    print("=" * 60)
    print("SupportPilot AI started successfully.")
    print("Database connection established.")
    # Pre-warm the SentenceTransformer embedding model so the
    # first resolve call is instant instead of waiting 5-10s
    try:
        from app.services.vector_search import search_documents
        search_documents("warmup")
        print("Embedding model pre-warmed successfully.")
    except Exception as e:
        print(f"Warning: Embedding pre-warm failed: {e}")
    print("=" * 60)



# ---------------------------------------------------
# Root Endpoint
# ---------------------------------------------------

@app.get("/", tags=["System"])
def root():
    """
    Health check endpoint.
    """

    return {
        "message": "SupportPilot AI is running",
        "status": "OK",
    }


# ---------------------------------------------------
# Create Ticket
# ---------------------------------------------------

@app.post(
    "/api/tickets",
    response_model=schemas.TicketResponse,
    tags=["Tickets"],
)
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
):
    """
    Creates a new support ticket.
    """
    from app.agents.diagnose import diagnose_ticket

    # Use real Diagnosis Agent to categorize, set priority, and severity on intake
    try:
        diagnosis = diagnose_ticket(ticket.description)
        
        sev_map = {"Low": "LOW", "Medium": "MEDIUM", "High": "HIGH", "Critical": "CRITICAL"}
        prio_map = {"Low": "P4", "Medium": "P3", "High": "P2", "Critical": "P1"}
        
        suggested_priority = diagnosis.get("suggested_priority", "Medium")
        priority = prio_map.get(suggested_priority, "P4")
        severity = sev_map.get(suggested_priority, "LOW")
        
        predicted_category = diagnosis.get("predicted_category")
        if predicted_category:
            ticket.department = predicted_category
    except Exception as e:
        logging.error(f"Classification failed during ticket ingestion: {e}")
        priority = "P4"
        severity = "LOW"

    user = (
        db.query(models.User)
        .filter(
            models.User.email == ticket.requester_email
        )
        .first()
    )

    if user is None:

        user = models.User(
            name=ticket.requester_email.split("@")[0],
            email=ticket.requester_email,
            department=ticket.department or "IT Support",
            role="EMPLOYEE",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user department if it was classified
        if ticket.department and user.department != ticket.department:
            user.department = ticket.department
            db.commit()

    new_ticket = models.Ticket(
        user_id=user.user_id,
        subject=ticket.subject,
        description=ticket.description,
        priority=priority,
        severity=severity,
        status="OPEN",
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    # Send ticket-received acknowledgment email to the requester
    try:
        from app.services.email_service import send_email
        send_email(
            to_email=ticket.requester_email,
            subject=f"SupportPilot - Ticket #{new_ticket.ticket_id} Received",
            message=(
                f"Hello,\n\n"
                f"Thank you for contacting SupportPilot.\n\n"
                f"Your support ticket has been received and is now being processed by our AI system.\n\n"
                f"--------------------------------------------------\n"
                f"TICKET DETAILS\n"
                f"--------------------------------------------------\n"
                f"Ticket ID  : #{new_ticket.ticket_id}\n"
                f"Subject    : {new_ticket.subject}\n"
                f"Priority   : {new_ticket.priority}\n"
                f"Status     : OPEN\n"
                f"--------------------------------------------------\n\n"
                f"Our AI agent will analyze your issue and either resolve it automatically\n"
                f"or escalate it to the appropriate support team.\n\n"
                f"You will receive a follow-up email with the resolution or escalation details shortly.\n\n"
                f"Thank you,\n"
                f"SupportPilot Support Team\n"
            ),
        )
        logging.info("Ticket-received email sent to %s for ticket #%s", ticket.requester_email, new_ticket.ticket_id)
    except Exception as e:
        logging.warning("Failed to send ticket-received email: %s", e)

    return new_ticket


# ---------------------------------------------------
# Get Ticket
# ---------------------------------------------------

@app.get(
    "/api/tickets/{ticket_id}",
    response_model=schemas.TicketResponse,
    tags=["Tickets"],
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieves a ticket by its ID.
    """

    ticket = (
        db.query(models.Ticket)
        .filter(
            models.Ticket.ticket_id == ticket_id
        )
        .first()
    )

    if ticket is None:

        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


# ---------------------------------------------------
# List Tickets
# ---------------------------------------------------

@app.get(
    "/api/tickets",
    response_model=list[schemas.TicketResponse],
    tags=["Tickets"],
)
def list_tickets(
    db: Session = Depends(get_db),
):
    """
    Returns all support tickets.
    """

    return db.query(models.Ticket).all()


# ---------------------------------------------------
# Create Feedback
# ---------------------------------------------------

@app.post(
    "/api/tickets/{ticket_id}/feedback",
    tags=["Tickets"],
)
def create_ticket_feedback(
    ticket_id: int,
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
):
    """
    Submits feedback for a specific ticket.
    """
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.ticket_id == ticket_id)
        .first()
    )

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    db_feedback = models.Feedback(
        ticket_id=ticket_id,
        rating=feedback.rating,
        classification_correct=feedback.classification_correct,
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return {"status": "Feedback recorded successfully", "id": db_feedback.feedback_id}