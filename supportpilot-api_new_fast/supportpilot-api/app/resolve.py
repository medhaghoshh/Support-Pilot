from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .mock_services import search_documents, generate_resolution  # swap later for real imports

router = APIRouter()


@router.post("/api/tickets/{ticket_id}/resolve", response_model=schemas.TicketResolveOut)
def resolve_ticket(ticket_id: int, db: Session = Depends(get_db)):
    # Step 1: Fetch the ticket
    ticket = db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Step 2: Call search (Member 3)
    retrieved_doc = search_documents(query=ticket.description)

    # Step 3: Call AI generation (Member 5)
    ai_result = generate_resolution(user_query=ticket.description, retrieved_documents=retrieved_doc)

    # Step 4: Save to DB
    resolution = models.TicketResponse(
        ticket_id=ticket.ticket_id,
        generated_response=ai_result["resolution"],
        confidence_score=ai_result["retrieval_confidence"]
    )
    db.add(resolution)

    # Mark the ticket as RESOLVED so the dashboard AI Resolve Index increments
    ticket.status = "RESOLVED"
    db.add(ticket)

    db.commit()
    db.refresh(resolution)

    # Step 5: Return to frontend
    return {
        "ticket_id": ticket.ticket_id,
        "generated_response": ai_result["resolution"],
        "confidence_score": ai_result["retrieval_confidence"],
        "articles_used": ai_result["sources"],
        "status": "resolved"
    }