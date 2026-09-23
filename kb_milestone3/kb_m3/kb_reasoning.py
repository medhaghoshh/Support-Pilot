"""
Milestone 3 - Knowledge Base / Data Engineer (Member 4)
Reasoning layer over the KB articles.

Milestone 2 supported single-shot retrieval: query in, one article out.
An agent workflow needs more than that. For each article this layer adds:

  symptoms          - structured symptom list (feeds the Diagnosis Agent)
  prerequisites     - what must be checked/true before the steps apply
  resolution_steps  - ordered, individually addressable steps, each with
                      an expected outcome so the Resolution Agent can
                      walk them one at a time instead of dumping prose
  related_articles  - cross-references, enabling multi-hop reasoning
                      ("tried this, still broken -> now look here")
  next_if_unresolved- explicit next hop when the steps do not fix it
  escalate_to       - which team owns it once self-service is exhausted
  escalate_when     - the condition that should trigger escalation
  auto_resolvable   - whether the agent may resolve without a human

Keyed by kb_id so it stays decoupled from the article prose itself.
"""

REASONING = {

"KB-101": {
    "symptoms": [
        "VPN client fails to connect",
        "VPN connects then drops repeatedly",
        "Connected to VPN but internal resources unreachable",
        "Certificate error on VPN client",
    ],
    "prerequisites": [
        "User has a working internet connection outside the VPN",
        "User has valid, non-expired network credentials",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Load any external website with the VPN disconnected",
         "expected": "Confirms the underlying internet connection is stable"},
        {"step": 2, "action": "Fully close the VPN client from the system tray and reopen it",
         "expected": "Clears cached session state that a reconnect does not"},
        {"step": 3, "action": "Check the VPN client version and update if outdated",
         "expected": "Client can negotiate current gateway security settings"},
        {"step": 4, "action": "Retry on a mobile hotspot instead of the current network",
         "expected": "Identifies whether the network is blocking VPN ports"},
        {"step": 5, "action": "Clear the VPN configuration cache and re-enter credentials",
         "expected": "Resolves certificate errors caused by stale local config"},
    ],
    "related_articles": ["KB-108", "KB-103", "KB-102"],
    "next_if_unresolved": "KB-103",
    "escalate_to": "Network Administration",
    "escalate_when": "Steps complete and the gateway still refuses the connection, "
                     "or colleagues on the same gateway are also affected",
    "auto_resolvable": True,
},

"KB-102": {
    "symptoms": [
        "Password expired message",
        "Repeated login failures with a believed-correct password",
        "Account locked after failed attempts",
        "Reset link not arriving",
    ],
    "prerequisites": [
        "User can access their registered email address",
        "User knows their employee ID",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Open the self-service password portal and choose forgot password",
         "expected": "Reset flow starts without needing IT involvement"},
        {"step": 2, "action": "Enter employee ID and the currently registered email address",
         "expected": "Reset link is dispatched within a few minutes"},
        {"step": 3, "action": "Check spam and junk folders if the link has not arrived",
         "expected": "Locates a link caught by corporate mail filtering"},
        {"step": 4, "action": "Set a new password meeting complexity rules and not reusing the last five",
         "expected": "New password is accepted by the portal"},
        {"step": 5, "action": "Wait up to fifteen minutes before testing email, VPN and applications",
         "expected": "Credential propagates across all connected systems"},
    ],
    "related_articles": ["KB-109", "KB-101"],
    "next_if_unresolved": "KB-109",
    "escalate_to": "Identity & Access Team",
    "escalate_when": "Still locked out after the fifteen minute sync window, "
                     "or the account has administrator privileges",
    "auto_resolvable": True,
},

"KB-103": {
    "symptoms": [
        "Application times out to a specific external service",
        "Internal server unreachable while other traffic works",
        "Tool worked yesterday and is blocked today",
    ],
    "prerequisites": [
        "The affected application and destination are identified",
        "General network connectivity is otherwise working",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Identify the exact application, destination and port affected",
         "expected": "Gives the specificity a firewall exception requires"},
        {"step": 2, "action": "Check whether teammates hit the same block",
         "expected": "Distinguishes a policy rule from a local misconfiguration"},
        {"step": 3, "action": "Review recent firewall policy announcements",
         "expected": "Identifies a recent change as the cause"},
        {"step": 4, "action": "Compare required ports against the current whitelist",
         "expected": "Confirms whether the tool's ports are approved"},
    ],
    "related_articles": ["KB-101", "KB-108"],
    "next_if_unresolved": None,
    "escalate_to": "Network Administration",
    "escalate_when": "A legitimate business application is confirmed blocked and "
                     "needs a firewall exception request",
    "auto_resolvable": False,
},

"KB-104": {
    "symptoms": [
        "Outlook shows connected but no new mail appears",
        "Outgoing mail stuck in sending",
        "Desktop and mobile mailboxes disagree",
    ],
    "prerequisites": [
        "User's account credentials are current",
        "Internet connectivity is confirmed working",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Close Outlook completely and reopen it rather than refreshing",
         "expected": "Clears a stuck sync process"},
        {"step": 2, "action": "Confirm internet connectivity independently of Outlook",
         "expected": "Rules out a broader network problem"},
        {"step": 3, "action": "Check the mailbox is not at or near its storage quota",
         "expected": "A full mailbox can silently block new mail delivery"},
        {"step": 4, "action": "Confirm credentials have not expired, especially after enabling MFA",
         "expected": "Re-authentication restores background sync"},
        {"step": 5, "action": "Request a local data file rebuild if corruption is suspected",
         "expected": "Resolves sync failures surviving a restart"},
    ],
    "related_articles": ["KB-109", "KB-107", "KB-102"],
    "next_if_unresolved": "KB-109",
    "escalate_to": "Collaboration Tools Team",
    "escalate_when": "Sync fails after a restart and a confirmed under-quota mailbox, "
                     "indicating a corrupted data file needing a rebuild",
    "auto_resolvable": True,
},

"KB-105": {
    "symptoms": [
        "Laptop shuts down without warning during intensive tasks",
        "Device hot to the touch during light use",
        "Fan running constantly at high speed",
        "Burning smell or unusual vibration",
    ],
    "prerequisites": [
        "Device is accessible for physical inspection",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Check task manager for runaway high-CPU background processes",
         "expected": "Identifies a software cause rather than a hardware fault"},
        {"step": 2, "action": "Move the laptop onto a hard flat surface, clear of vents",
         "expected": "Restores airflow blocked by soft surfaces"},
        {"step": 3, "action": "Update firmware and BIOS to the latest version for the model",
         "expected": "Applies any thermal management fixes"},
        {"step": 4, "action": "Note the device age; over two years suggests internal dust buildup",
         "expected": "Determines whether physical cleaning is required"},
    ],
    "related_articles": ["KB-110"],
    "next_if_unresolved": None,
    "escalate_to": "Hardware Support Team",
    "escalate_when": "Overheating persists after software and ventilation checks, or "
                     "there is a burning smell, vibration, or visible damage "
                     "(treat these as immediate, do not continue troubleshooting)",
    "auto_resolvable": False,
},

"KB-106": {
    "symptoms": [
        "Installation blocked by permission restrictions",
        "License activation error on launch",
        "Trial expired message despite a valid company licence",
    ],
    "prerequisites": [
        "A software request has been submitted and approved",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Confirm a software request was submitted through the internal portal",
         "expected": "Most applications require pre-approval before install is possible"},
        {"step": 2, "action": "Check whether the installer requires administrator rights",
         "expected": "Explains a permissions-based install failure"},
        {"step": 3, "action": "Connect to the company network or VPN, then relaunch the application",
         "expected": "License server becomes reachable and activation succeeds"},
    ],
    "related_articles": ["KB-101"],
    "next_if_unresolved": "KB-101",
    "escalate_to": "Application Support Team",
    "escalate_when": "Activation still fails with confirmed network connectivity, "
                     "suggesting the account is missing from the licence pool",
    "auto_resolvable": True,
},

"KB-107": {
    "symptoms": [
        "Email with urgent language demanding immediate action",
        "Request for login credentials or payment by email",
        "Unexpected attachment from a known contact",
        "Sender address closely mimicking a legitimate one",
    ],
    "prerequisites": [],
    "resolution_steps": [
        {"step": 1, "action": "Do not click links or open attachments from unexpected mail",
         "expected": "Prevents credential theft or malware execution"},
        {"step": 2, "action": "Hover over links to preview the true destination URL",
         "expected": "Reveals a mismatch with the expected domain"},
        {"step": 3, "action": "Check the sender's full address, not just the display name",
         "expected": "Exposes a spoofed display name"},
        {"step": 4, "action": "Use the Report Phishing button to forward it to security",
         "expected": "Message is analysed and safely removed from the inbox"},
        {"step": 5, "action": "If credentials were already entered, change the password immediately",
         "expected": "Limits the window of exposure"},
    ],
    "related_articles": ["KB-102", "KB-109", "KB-104"],
    "next_if_unresolved": "KB-102",
    "escalate_to": "Security Team",
    "escalate_when": "Credentials were entered, a link was clicked, or several "
                     "colleagues report similar messages (escalate immediately, "
                     "do not wait for self-service steps)",
    "auto_resolvable": False,
},

"KB-108": {
    "symptoms": [
        "Office WiFi not appearing in the network list",
        "Connected but showing limited connectivity",
        "Frequent wireless disconnections through the day",
    ],
    "prerequisites": [
        "User is within range of an office access point",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Toggle WiFi off and on to force a network rescan",
         "expected": "Resolves many detection failures on its own"},
        {"step": 2, "action": "Forget the network and reconnect with fresh credentials",
         "expected": "Clears a corrupted saved network profile"},
        {"step": 3, "action": "Move closer to a known access point, away from weak-coverage areas",
         "expected": "Confirms whether the cause is coverage rather than configuration"},
        {"step": 4, "action": "Restart the network adapter via device manager",
         "expected": "Clears driver-level state a toggle does not reach"},
    ],
    "related_articles": ["KB-101", "KB-103"],
    "next_if_unresolved": "KB-101",
    "escalate_to": "Network Administration",
    "escalate_when": "Multiple users in the same physical area lose connectivity "
                     "simultaneously, indicating an access point failure",
    "auto_resolvable": True,
},

"KB-109": {
    "symptoms": [
        "Authenticator app not generating valid codes",
        "Codes rejected as expired immediately after generation",
        "SMS verification codes never arriving",
    ],
    "prerequisites": [
        "User has access to their enrolled authentication device",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Set the mobile device clock to automatic and let it resync",
         "expected": "Fixes the clock drift that invalidates generated codes"},
        {"step": 2, "action": "Remove and re-add the account in the authenticator app",
         "expected": "Regenerates a clean secret key"},
        {"step": 3, "action": "Confirm the registered phone number is current for SMS codes",
         "expected": "A single wrong digit causes silent delivery failure"},
    ],
    "related_articles": ["KB-102", "KB-107"],
    "next_if_unresolved": "KB-102",
    "escalate_to": "Security Team",
    "escalate_when": "The authenticator device is lost or wiped entirely - this "
                     "cannot be self-serviced and needs manual identity verification",
    "auto_resolvable": True,
},

"KB-110": {
    "symptoms": [
        "Print jobs stuck in the queue indefinitely",
        "Printer shows offline while powered on",
        "Documents printing with formatting errors",
    ],
    "prerequisites": [
        "Printer is powered on and physically connected",
    ],
    "resolution_steps": [
        {"step": 1, "action": "Clear the print queue completely and resend the job",
         "expected": "Removes a stuck job blocking all subsequent prints"},
        {"step": 2, "action": "Confirm printer and device are on the same network segment",
         "expected": "Rules out a network mismatch after any recent change"},
        {"step": 3, "action": "Restart the print spooler service",
         "expected": "Resolves most queue-related freezes"},
        {"step": 4, "action": "Update or reinstall the printer driver",
         "expected": "Fixes formatting errors across multiple documents"},
    ],
    "related_articles": ["KB-105", "KB-108"],
    "next_if_unresolved": "KB-108",
    "escalate_to": "Hardware Support Team",
    "escalate_when": "Printer remains offline after clearing the queue and "
                     "restarting the spooler, indicating a printer-side fault",
    "auto_resolvable": True,
},

}


def get_reasoning(kb_id=None):
    """Reasoning data for one article, or the whole map if kb_id is None."""
    if kb_id is None:
        return REASONING
    return REASONING.get(kb_id)


def get_related(kb_id):
    """Cross-referenced articles, for multi-hop reasoning."""
    entry = REASONING.get(kb_id)
    return entry["related_articles"] if entry else []


def get_reasoning_chain(kb_id, max_hops=4):
    """
    Follows next_if_unresolved to build an escalation-aware reasoning path.
    This is what turns single-shot retrieval into a multi-step plan:
    "try this article, and if it does not resolve, try this one next".
    """
    chain = []
    seen = set()
    current = kb_id

    while current and current not in seen and len(chain) < max_hops:
        entry = REASONING.get(current)
        if not entry:
            break
        seen.add(current)
        chain.append({
            "kb_id": current,
            "step_count": len(entry["resolution_steps"]),
            "auto_resolvable": entry["auto_resolvable"],
            "escalate_to": entry["escalate_to"],
        })
        current = entry.get("next_if_unresolved")

    return chain
