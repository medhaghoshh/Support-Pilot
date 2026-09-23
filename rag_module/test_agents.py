import logging
import sys

# Configure logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(levelname)s - %(message)s")

from app.agents.diagnose import diagnose_ticket
from app.agents.retrieval_agent import retrieval_agent
from app.agents.resolution_agent import ResolutionAgent
from app.agents.escalation_agent import EscalationAgent

ticket = "My VPN keeps disconnecting every few minutes when I work from home"

print("\n=== STEP 1: Running Diagnosis Agent ===")
diag = diagnose_ticket(ticket)
print("Diagnosis Output:")
print(f"  Category: {diag.get('predicted_category')}")
print(f"  Confidence: {diag.get('confidence')}")
print(f"  Suggested Priority: {diag.get('suggested_priority')}")

print("\n=== STEP 2: Running Retrieval Agent ===")
ret = retrieval_agent(ticket)
print("Retrieval Output:")
print(f"  Status: {ret.get('status')}")
print(f"  Retrieved Doc Title: {ret.get('retrieved_document', {}).get('title') if ret.get('retrieved_document') else 'None'}")

print("\n=== STEP 3: Running Resolution Agent ===")
res = ResolutionAgent().run(ticket, diag, ret)
print("Resolution Output:")
print(f"  Success: {res.get('success')}")
print(f"  Final Confidence: {res.get('confidence')}")
print(f"  Resolution Steps:")
print(res.get("resolution_steps"))

print("\n=== STEP 4: Running Escalation Agent ===")
esc = EscalationAgent().run(res, diag)
print("Escalation Output:")
print(f"  Escalate: {esc.get('escalated')}")
print(f"  Escalate To: {esc.get('assigned_team')}")
print(f"  Reason: {esc.get('reason')}")

