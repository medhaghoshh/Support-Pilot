"""
Full escalation logic test covering all categories.
"""
from app.agents.escalation_agent import EscalationAgent

agent = EscalationAgent()

test_cases = [
    # Should AUTO-RESOLVE
    ("WiFi issue",          "Networking",     "P4", "LOW",    True,  0.62, "RESOLVED"),
    ("Bluetooth issue",     "Networking",     "P4", "LOW",    True,  0.55, "RESOLVED"),
    ("Password reset",      "Password Reset", "P4", "LOW",    True,  0.60, "RESOLVED"),
    ("App crash",           "Software",       "P4", "LOW",    True,  0.72, "RESOLVED"),
    ("Email not syncing",   "Email",          "P4", "LOW",    True,  0.65, "RESOLVED"),
    # Should ESCALATE
    ("Keyboard failure",    "Hardware",       "P4", "LOW",    True,  0.80, "IN_PROGRESS"),
    ("Laptop overheating",  "Hardware",       "P3", "MEDIUM", True,  0.75, "IN_PROGRESS"),
    ("Phishing email",      "Security",       "P2", "HIGH",   True,  0.85, "IN_PROGRESS"),
    ("Data breach",         "Security",       "P1", "CRITICAL",True, 0.90, "IN_PROGRESS"),
    ("Server outage P1",    "Infrastructure", "P1", "CRITICAL",True, 0.80, "IN_PROGRESS"),
    ("Low conf unknown",    "General",        "P3", "MEDIUM", True,  0.40, "IN_PROGRESS"),
]

print(f"{'Ticket':<28} {'Category':<18} {'Expected':<14} {'Got':<14} {'Pass'}")
print("-" * 90)
all_pass = True
for label, category, priority, severity, success, confidence, expected_status in test_cases:
    result = agent.run(
        resolution_output={
            "success": success,
            "resolution_steps": "Follow these steps. Contact IT support if unresolved.",
            "confidence": confidence,
        },
        diagnosis_output={
            "predicted_category": category,
            "suggested_priority": priority,
            "severity": severity,
        },
    )
    got = result["status"]
    ok = got == expected_status
    if not ok:
        all_pass = False
    print(f"{label:<28} {category:<18} {expected_status:<14} {got:<14} {'OK' if ok else 'FAIL  <---'}")

print()
print("All tests passed!" if all_pass else "SOME TESTS FAILED - review above.")
