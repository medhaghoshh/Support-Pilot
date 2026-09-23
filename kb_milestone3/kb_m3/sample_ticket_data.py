"""
Milestone 4 - Sample ticket data for coverage/gap analysis.

Each ticket mimics what the Retrieval Agent (Role 3) produces per query:
  ticket_text       - the raw ticket
  retrieved_kb_id   - the KB article retrieval returned, or None if nothing
  similarity_score  - normalized 0-1 relevance from ChromaDB, or None
  category          - the diagnosed category (from the M3 Diagnosis Agent)
  escalated         - whether the ticket ended up escalated

This is SAMPLE data so the analyzer can be demonstrated before the real
aggregated ticket feed from Backend (Role 2) is available. It is
deliberately built with three kinds of tickets:

  - strong matches  (score >= 0.60): topics the KB covers well
  - weak matches    (score <  0.45): topics where retrieval returns
                     something but it is a poor fit -> a real content gap
  - no matches      (retrieved_kb_id None): topics the KB has nothing for

The weak and no-match tickets cluster around a few topics on purpose
(mobile device setup, software-specific errors, HR/account topics) so the
gap analysis produces a clear, realistic recommendation.
"""


SAMPLE_TICKETS = [
    # ---- strong matches: KB covers these well ----
    {"ticket_text": "My VPN keeps disconnecting every few minutes from home",
     "retrieved_kb_id": "KB-101", "similarity_score": 0.71,
     "category": "Networking", "escalated": False},
    {"ticket_text": "I forgot my password and I'm locked out of my account",
     "retrieved_kb_id": "KB-102", "similarity_score": 0.68,
     "category": "Password Reset", "escalated": False},
    {"ticket_text": "Outlook is not receiving any new emails since this morning",
     "retrieved_kb_id": "KB-104", "similarity_score": 0.66,
     "category": "Email", "escalated": False},
    {"ticket_text": "My laptop overheats and shuts down during video calls",
     "retrieved_kb_id": "KB-105", "similarity_score": 0.73,
     "category": "Hardware", "escalated": False},
    {"ticket_text": "I got a suspicious phishing email asking for my login",
     "retrieved_kb_id": "KB-107", "similarity_score": 0.70,
     "category": "Security", "escalated": False},
    {"ticket_text": "The office wifi keeps dropping on my floor",
     "retrieved_kb_id": "KB-108", "similarity_score": 0.64,
     "category": "Networking", "escalated": False},
    {"ticket_text": "My MFA authenticator codes are being rejected",
     "retrieved_kb_id": "KB-109", "similarity_score": 0.67,
     "category": "Security", "escalated": False},
    {"ticket_text": "The printer shows offline and jobs are stuck",
     "retrieved_kb_id": "KB-110", "similarity_score": 0.69,
     "category": "Hardware", "escalated": False},
    {"ticket_text": "Firewall is blocking access to an external service",
     "retrieved_kb_id": "KB-103", "similarity_score": 0.62,
     "category": "Networking", "escalated": False},
    {"ticket_text": "I need a licence activated for my design software",
     "retrieved_kb_id": "KB-106", "similarity_score": 0.61,
     "category": "Software", "escalated": False},

    # ---- weak matches: retrieval returns something, but a poor fit ----
    # cluster 1: mobile device / email-on-phone setup (KB has no article for this)
    {"ticket_text": "How do I set up my work email on my personal iPhone?",
     "retrieved_kb_id": "KB-104", "similarity_score": 0.38,
     "category": "Email", "escalated": True},
    {"ticket_text": "Company email won't configure on my Android phone",
     "retrieved_kb_id": "KB-104", "similarity_score": 0.34,
     "category": "Email", "escalated": True},
    {"ticket_text": "Can't add my Outlook account to the mobile app",
     "retrieved_kb_id": "KB-104", "similarity_score": 0.41,
     "category": "Email", "escalated": False},

    # cluster 2: specific software crashes (KB only has generic licensing article)
    {"ticket_text": "Excel keeps crashing whenever I open a large spreadsheet",
     "retrieved_kb_id": "KB-106", "similarity_score": 0.29,
     "category": "Software", "escalated": True},
    {"ticket_text": "Teams call audio cuts out constantly during meetings",
     "retrieved_kb_id": "KB-106", "similarity_score": 0.26,
     "category": "Software", "escalated": True},
    {"ticket_text": "My browser freezes every time I open more than five tabs",
     "retrieved_kb_id": "KB-106", "similarity_score": 0.31,
     "category": "Software", "escalated": False},

    # ---- no matches: KB has nothing relevant at all ----
    # cluster 3: HR / account-lifecycle topics (outside current IT KB scope)
    {"ticket_text": "How do I update my direct deposit banking details?",
     "retrieved_kb_id": None, "similarity_score": None,
     "category": "Human Resources", "escalated": True},
    {"ticket_text": "I need to request additional annual leave days",
     "retrieved_kb_id": None, "similarity_score": None,
     "category": "Human Resources", "escalated": True},
    {"ticket_text": "Where do I submit my expense reimbursement claim?",
     "retrieved_kb_id": None, "similarity_score": None,
     "category": "Human Resources", "escalated": True},
    # ---- previously-flagged gaps, now covered by KB-116 and KB-117 ----
    # Role 3 reported these two as unmatched; they now retrieve strongly
    # after adding the Bluetooth and keyboard articles.
    {"ticket_text": "My Bluetooth headset won't connect to my laptop",
     "retrieved_kb_id": "KB-116", "similarity_score": 0.63,
     "category": "Hardware", "escalated": False},
    {"ticket_text": "Keyboard not responding, some keys stopped working",
     "retrieved_kb_id": "KB-117", "similarity_score": 0.65,
     "category": "Hardware", "escalated": False},
]


def get_sample_tickets():
    return SAMPLE_TICKETS
