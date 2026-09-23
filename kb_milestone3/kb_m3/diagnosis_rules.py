"""
Milestone 3 - Knowledge Base / Data Engineer (Member 4)
Ticket-analysis rules for the Diagnosis Agent.

Structure:
  SYMPTOM_RULES  -> per category, a set of weighted symptom indicators
  CATEGORY_KB    -> which KB articles cover each category
  SEVERITY_RULES -> urgency indicators, used to suggest a priority
  CLARIFYING_QUESTIONS -> what the agent should ask when confidence is low

Weights:
  3 = strong indicator (nearly always means this category)
  2 = moderate indicator
  1 = weak / supporting indicator (only meaningful alongside others)

All matching is done on lowercased ticket text. Multi-word phrases are
matched as substrings; single words are matched as whole words so that
"vpn" does not match inside an unrelated longer word.
"""

# ---------------------------------------------------------------------
# 1. SYMPTOM -> CATEGORY MAPPING
# ---------------------------------------------------------------------

SYMPTOM_RULES = {
    "Networking": {
        3: [
            "vpn", "firewall", "wifi", "wi-fi", "wireless network",
            "network drive", "cannot connect to the network",
            "no internet", "dns", "router", "ethernet",
        ],
        2: [
            "network", "connection drops", "keeps disconnecting",
            "disconnecting", "cannot reach", "unable to connect",
            "access point", "bandwidth", "latency", "packet loss",
            "shared drive", "intranet",
        ],
        1: [
            "slow", "timeout", "timed out", "offline", "remote",
            "working from home", "connectivity",
        ],
    },
    "Password Reset": {
        3: [
            "password", "locked out", "account locked", "reset my password",
            "forgot my password", "password expired", "cannot log in",
            "can't log in", "login failed",
        ],
        2: [
            "sign in", "signin", "log in", "login", "unlock my account",
            "account lockout", "reset link", "temporary password",
            "single sign-on", "sso",
            # "credentials" is deliberately weight 2, not 3: it appears
            # just as often in phishing reports as in genuine reset requests
            "credentials",
        ],
        1: [
            "access denied", "authentication", "username", "portal",
        ],
    },
    "Email": {
        3: [
            "outlook", "mailbox", "inbox", "email not", "emails not",
            "not receiving email", "cannot send email", "attachment",
            "distribution list", "shared mailbox",
        ],
        2: [
            "email", "mail", "sync", "not syncing", "bounce", "bounced",
            "calendar invite", "auto-reply", "out of office", "signature",
            "spam", "junk folder",
        ],
        1: [
            "message", "send", "receive", "quota", "storage full",
        ],
    },
    "Hardware": {
        3: [
            "laptop", "printer", "monitor", "keyboard", "mouse",
            "docking station", "webcam", "headset", "battery",
            "overheating", "blue screen", "won't turn on",
            "will not turn on", "not powering on",
        ],
        2: [
            "device", "screen", "display", "charger", "charging",
            "fan", "noise", "usb", "scanner", "hardware",
            "shutting down", "shuts down", "flickering", "cracked",
        ],
        1: [
            "hot", "slow", "not detected", "unresponsive", "port",
        ],
    },
    "Software": {
        3: [
            "install", "installation", "license", "activation",
            "application crash", "app crashes", "crashing on launch",
            "software", "uninstall", "update failed",
        ],
        2: [
            "application", "app", "program", "version", "compatibility",
            "trial expired", "won't open", "will not open",
            "keeps crashing", "freezing", "update",
        ],
        1: [
            "error message", "slow", "settings", "permission", "launch",
        ],
    },
    "Security": {
        3: [
            "phishing", "suspicious email", "malware", "virus",
            "ransomware", "data breach", "stolen", "hacked",
            "unauthorized access", "mfa", "multi-factor",
            "two-factor", "authenticator",
        ],
        2: [
            "security", "suspicious", "compromised", "antivirus",
            "quarantine", "lost my laptop", "lost device",
            "verification code", "security code", "encryption",
        ],
        1: [
            "warning", "alert", "policy", "confidential", "sensitive",
        ],
    },
}


# ---------------------------------------------------------------------
# 2. CATEGORY -> KB ARTICLES
#    Lets the Diagnosis Agent hand the Retrieval Agent a shortlist
#    instead of searching the whole KB blindly.
# ---------------------------------------------------------------------

CATEGORY_KB = {
    "Networking":     ["KB-101", "KB-103", "KB-108"],
    "Password Reset": ["KB-102"],
    "Email":          ["KB-104"],
    "Hardware":       ["KB-105", "KB-110"],
    "Software":       ["KB-106"],
    "Security":       ["KB-107", "KB-109"],
}


# ---------------------------------------------------------------------
# 3. SEVERITY / URGENCY INDICATORS
#    Suggests a priority the Escalation Agent can use as an input signal.
# ---------------------------------------------------------------------

SEVERITY_RULES = {
    "Critical": [
        "entire team", "everyone", "all users", "company wide",
        "company-wide", "production down", "cannot work at all",
        "data breach", "ransomware", "stolen", "hacked",
        "multiple people", "whole office",
    ],
    "High": [
        "urgent", "asap", "immediately", "blocked", "cannot work",
        "deadline", "client meeting", "presentation", "locked out",
        "not working at all", "completely",
    ],
    "Medium": [
        "intermittent", "sometimes", "occasionally", "slow",
        "workaround", "when possible", "affecting my work",
    ],
    "Low": [
        "question", "how do i", "how to", "request", "would like",
        "whenever you can", "no rush", "minor",
    ],
}


# ---------------------------------------------------------------------
# 4. CLARIFYING QUESTIONS
#    Used by the Diagnosis Agent when confidence is below threshold,
#    so the workflow can ask rather than guess.
# ---------------------------------------------------------------------

CLARIFYING_QUESTIONS = {
    "Networking": [
        "Are you connected via office WiFi, ethernet, or VPN from home?",
        "Is anyone else on your team seeing the same problem?",
    ],
    "Password Reset": [
        "Are you locked out entirely, or is the password being rejected?",
        "Is this a standard account or one with administrator access?",
    ],
    "Email": [
        "Is the problem with sending, receiving, or both?",
        "Does the issue appear on desktop, mobile, or both?",
    ],
    "Hardware": [
        "Which device is affected, and what is its asset tag?",
        "Is there any visible physical damage or unusual noise?",
    ],
    "Software": [
        "Which application and version are affected?",
        "Did this start after a recent update or installation?",
    ],
    "Security": [
        "Did you click any link or enter credentials before reporting this?",
        "Is any company data or device currently exposed?",
    ],
    "_generic": [
        "When did the issue first start?",
        "What is the exact error message shown, if any?",
        "Is this affecting only you or several colleagues?",
    ],
}


# Confidence below this means the Diagnosis Agent should ask rather than act.
CONFIDENCE_THRESHOLD = 0.45

# Tie-break order when two categories score identically.
# Security is first deliberately: misrouting a phishing or breach report
# is far more costly than misrouting a routine request, so an ambiguous
# ticket with any security signal should surface as Security.
TIEBREAK_PRIORITY = [
    "Security",
    "Password Reset",
    "Networking",
    "Email",
    "Hardware",
    "Software",
]


def get_rules():
    return SYMPTOM_RULES


def get_category_kb_map():
    return CATEGORY_KB


def get_severity_rules():
    return SEVERITY_RULES


def get_clarifying_questions(category=None):
    if category and category in CLARIFYING_QUESTIONS:
        return CLARIFYING_QUESTIONS[category] + CLARIFYING_QUESTIONS["_generic"]
    return CLARIFYING_QUESTIONS["_generic"]
