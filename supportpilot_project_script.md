# SupportPilot — Project Explanation Script
### AI-Powered Enterprise IT Helpdesk System | Infosys Internship Project

---

## PROJECT OVERVIEW

**SupportPilot** is an AI-powered enterprise IT helpdesk and ticket management system. It automates the process of receiving, classifying, diagnosing, resolving, and escalating IT support tickets using a multi-agent AI pipeline — reducing manual effort and resolution time for IT support teams.

The system consists of:
- A **React frontend** (SupportPilot Console) running on `localhost:5173`
- A **RAG (Retrieval-Augmented Generation) backend** running on `localhost:8000` — handles ticket workflows, email, and Jira
- A **Diagnosis/Classification API** running on `localhost:8001` — classifies ticket categories using rule-based NLP
- A **MySQL database** — stores tickets, responses, Jira records, and user data

---

## ARCHITECTURE — HOW IT WORKS

```
User Submits Ticket
        ↓
 [Diagnosis Agent]        → Classifies category (Networking, Hardware, Password Reset...)
        ↓
 [Retrieval Agent]        → Searches Knowledge Base for relevant KB articles
        ↓
 [Resolution Agent]       → Groq LLM generates a step-by-step resolution
        ↓
 [Escalation Agent]       → Decides: Auto-Resolve OR Escalate to human team
        ↓
    ┌───────────────────────────────────┐
    │  RESOLVED (IT/Network/Software)   │  → Email sent: "Ticket Resolved by AI"
    │  IN_PROGRESS (Hardware/Security)  │  → Jira ticket created + Escalation email sent
    └───────────────────────────────────┘
```

---

## PAGE-BY-PAGE EXPLANATION

---

### 1. DASHBOARD PAGE

**Navigation:** Sidebar → Dashboard

**Purpose:**
The Dashboard is the command center of the application. It gives a real-time summary of all support activity across the system.

**What it shows:**

| Section | Description |
|---|---|
| **Total Tickets** | Count of all tickets ever submitted |
| **Open Tickets** | Tickets not yet resolved or in progress |
| **Resolved Tickets** | Tickets successfully handled by AI |
| **Escalated Tickets** | Tickets handed off to a human support team |
| **Resolution Rate** | Percentage of tickets auto-resolved by AI |
| **Recent Activity Feed** | Live list of recently submitted or updated tickets |
| **Severity Breakdown** | Visual split of Low / Medium / High / Critical tickets |

**Value to the user:**
An IT manager can open the dashboard and instantly know:
- How many tickets are pending attention
- How effective the AI resolution is
- Whether there are any critical issues flagged today

---

### 2. TICKETS PAGE

**Navigation:** Sidebar → Tickets

**Purpose:**
This is where all ticket interactions happen. It has two sub-sections: the **Ticket List** (left panel) and the **AI Classification + Resolution Panel** (right panel).

---

#### 2A. TICKET LIST (Left Panel)

**What it shows:**
- All submitted tickets sorted by most recent
- Each ticket card shows: Ticket ID, Subject, Requester Email, Status badge, Priority, and Time

**Status Badges:**
- 🟡 `OPEN` — Ticket submitted, not yet processed
- 🔵 `IN_PROGRESS` — Being handled / escalated to a team
- 🟢 `RESOLVED` — Successfully resolved by AI
- ✅ `CLOSED` — Manually closed

**Filters available:**
- Search by subject or description keyword
- Filter by status: All / Open / In Progress / Resolved

**Actions:**
- Click any ticket → loads it into the right panel for AI analysis
- Click **"+ New Ticket"** → opens the ticket submission form

---

#### 2B. NEW TICKET FORM

**Triggered by:** "+ New Ticket" button

**Fields:**
| Field | Description |
|---|---|
| **Subject** | Short title of the issue |
| **Description** | Detailed explanation of the problem |
| **Requester Email** | User's email — used to send notifications |
| **Department** | User's work department (Finance, HR, IT...) |
| **Priority** | P1 (Critical) to P4 (Low) |
| **Severity** | Critical / High / Medium / Low |

**What happens after submission:**
1. Ticket is saved to the database with status `OPEN`
2. The AI Classification panel immediately runs — showing the predicted category and confidence score
3. The ticket appears at the top of the Ticket List

---

#### 2C. AI CLASSIFICATION PANEL (Right Panel — Top Section)

**Purpose:**
Shows the real-time AI diagnosis output for the selected ticket.

**What it shows:**
| Field | Example |
|---|---|
| **Category** | `Networking` / `Hardware` / `Password Reset` / `Software` |
| **Sub-Category** | `Network Connectivity` / `Hardware & Devices` |
| **Confidence Score** | `80%` — how confident the AI is in the classification |
| **Priority** | Suggested priority based on issue type |
| **Severity** | LOW / MEDIUM / HIGH / CRITICAL |

**How it works:**
- Sends the ticket description + subject to the Diagnosis API at `localhost:8001/diagnose`
- Uses keyword-matching and rule-based NLP to predict the IT category
- The confidence score reflects how many symptom keywords were matched

---

#### 2D. RESOLUTION PANEL (Right Panel — Bottom Section / AI Agent Tab)

**Purpose:**
Displays the full AI agent pipeline execution for a ticket when the "Resolve" button is clicked.

**Tabs inside:**

**→ Resolution Tab:**
Shows the AI-generated resolution steps.
- Step-by-step solution generated by the Groq LLM (Llama 3.3 70B)
- Based on Knowledge Base retrieval + AI reasoning
- Example for WiFi issue: "Step 1: Restart the router. Step 2: Forget and reconnect to the WiFi network..."

**→ AI Agent Tab (Workflow Panel):**
Shows the 4-agent pipeline execution in real time.

```
[ Diagnosis Agent ]  →  [ Retrieval Agent ]  →  [ Resolution Agent ]  →  [ Escalation Agent ]
    COMPLETED               COMPLETED               COMPLETED               COMPLETED / ACTIVE
```

Each agent card shows:
- Status: `COMPLETED` / `ACTIVE` / `STANDBY` / `FAILED`
- The agent's role in the pipeline
- Live terminal-style log output (PIPELINE STDERR/STDOUT LOGS)

**Third-Party Connectors (right side of AI Agent tab):**

| Connector | What it shows |
|---|---|
| **Jira Integration** | Whether a Jira ticket was created; shows the Jira issue key (e.g. `SCRUM-31`) |
| **Email Automation** | Confirms whether the notification email was sent to the requester |
| **Jira Orchestrator Output** | Displays the Jira ticket creation status and escalation state |
| **Automated Email Dispatch** | Shows the exact email subject, sender, recipient, and message body |

---

### 3. AI AGENT PAGE

**Navigation:** Sidebar → AI Agent

**Purpose:**
A dedicated full-screen view of the AI Orchestrator Workflow for the currently active ticket. This is the same pipeline view as the "AI Agent" tab inside the Tickets page — but displayed as a standalone focused page for presentation or deeper review.

**What it shows:**
- **Pipeline Agent Topology** — visual flow of all 4 agents
- **Pipeline Logs** — live stdout/stderr from the backend workflow execution
- **Third-Party Connectors** — Jira + Email status
- **Automated Email Dispatch** — full preview of the email that was sent

**When to use:**
When you want to demonstrate or review the AI decision-making process without the distraction of the ticket list.

---

### 4. INTEGRATIONS PAGE

**Navigation:** Sidebar → Integrations

**Purpose:**
Admin configuration panel for connecting SupportPilot to external services. This is a one-time setup done by the system administrator — not by end users.

**Two integration sections:**

---

#### 4A. JIRA INTEGRATION

**What it configures:**
| Field | Description |
|---|---|
| **Jira URL** | Your Atlassian instance URL (e.g. `https://company.atlassian.net`) |
| **Jira Email** | Admin's Atlassian account email |
| **API Token** | Generated from Atlassian → Security → API Tokens |
| **Project Key** | The Jira project where escalated issues go (e.g. `SCRUM`, `IT`, `HELP`) |

**What happens when configured:**
- Every escalated ticket (Hardware, Security, P1 issues) automatically creates a Jira issue
- The Jira issue key (e.g. `SCRUM-30`) is stored in the database and shown in the AI Agent workflow panel
- The escalation email sent to the user includes this Jira ticket ID for tracking

**Test Connection button:**
Verifies that the provided credentials can authenticate with the Jira API before saving.

---

#### 4B. EMAIL AUTOMATION (Gmail SMTP)

**What it configures:**
| Field | Description |
|---|---|
| **Gmail Address** | The support email account (e.g. `support@gmail.com`) |
| **App Password** | A Gmail App Password — generated from Google Account → Security → 2-Step Verification → App Passwords |

**What happens when configured:**
- **Resolution emails:** Sent automatically when AI resolves a ticket → "Your ticket #5 has been resolved"
- **Escalation emails:** Sent when a ticket is escalated → "Your ticket #7 has been escalated to Level 2 Support"

**Important:** A regular Gmail password does NOT work here. Google requires an "App Password" (a 16-character code) when SMTP is used by third-party apps.

**Test Connection button:**
Sends a real test email to verify the SMTP credentials work before saving.

---

### 5. ANALYTICS PAGE

**Navigation:** Sidebar → Analytics

**Purpose:**
The Analytics page is the **AI Ticket Classification Analytics** dashboard. It shows all tickets with their AI-classified IT categories, confidence scores, and statuses in a tabular format for analysis.

**Header Stats:**
| Stat | Description |
|---|---|
| **Total Tickets** | All tickets in the system |
| **Open Tickets** | Unresolved tickets |
| **Closed Tickets** | Resolved or closed tickets |
| **High Severity** | Count of high/critical severity tickets |
| **Medium Severity** | Count of medium severity tickets |
| **Low Severity** | Count of low severity tickets |

**Table Columns:**
| Column | Description |
|---|---|
| **Ticket ID** | Unique ticket number (clickable) |
| **Subject** | The issue title |
| **Category** | AI-classified IT category (Networking, Hardware, Software, Password Reset, etc.) — derived from the Diagnosis API |
| **Severity** | LOW / MEDIUM / HIGH badge |
| **Priority** | P1–P4 |
| **Confidence** | Progress bar + percentage showing how confident the AI is in the category |
| **Status** | Closed (Resolved) / Open / In Progress |
| **Action** | "View" button → opens a detail modal for the ticket |

**Search:**
Filter tickets in real time by Ticket ID, subject, department, or status.

**View Modal (clicking "View"):**
A slide-in detail panel showing full ticket info:
- Ticket ID, Subject, Description
- AI Category + Confidence
- Severity, Priority, Status
- Created At timestamp
- Clarifying questions the AI generated (if any)

**Key difference from Tickets page:**
The Tickets page is for **actions** (create, resolve). The Analytics page is for **review and reporting** — seeing patterns, high-severity issues, and confidence scores across all tickets.

---

### 6. SETTINGS PAGE

**Navigation:** Sidebar → Settings

**Purpose:**
User preferences and system configuration.

**Sections:**

| Section | Options |
|---|---|
| **Appearance** | Dark Mode / Light Mode toggle |
| **Language** | English / Spanish / French / German |
| **Notifications** | Desktop notifications ON/OFF, Email notifications ON/OFF |
| **Account** | Display name, role |

**Impact:**
- Language changes translate all UI labels across the entire application
- Dark/Light mode persists across sessions
- Desktop notifications alert the admin when a new ticket arrives

---

## ESCALATION LOGIC — HOW AGENTS DECIDE

| Ticket Category | Action | Reason |
|---|---|---|
| Networking (WiFi, Bluetooth, VPN) | ✅ Auto-Resolve | AI can provide KB-based solutions |
| Password Reset | ✅ Auto-Resolve | Standard procedure, AI handles it |
| Software / Email / Apps | ✅ Auto-Resolve | KB articles available |
| **Hardware** (Keyboard, Laptop, Monitor, Printer) | ❌ Escalate → Hardware Team | Requires physical technician |
| **Security** (Phishing, Virus, Data Breach) | ❌ Escalate → Security Operations | Requires human security review |
| **P1 / CRITICAL severity** (any category) | ❌ Escalate | Business impact too high for AI alone |
| **Low confidence** (< 45% for IT, < 70% for others) | ❌ Escalate | AI is uncertain — human must review |

---

## EMAIL NOTIFICATIONS — WHAT THE USER RECEIVES

### Resolution Email (Auto-Resolved Ticket):
```
Subject: SupportPilot - Ticket #5 Resolved

Hello,

Your support ticket #5 has been resolved successfully.

Thank you,
SupportPilot Team
```

### Escalation Email (Hardware/Security Ticket):
```
Subject: SupportPilot | Escalation Notification | SCRUM-30

Hello,

Your support request has been escalated to our technical support team.

SUPPORT TICKET DETAILS
──────────────────────────────
Original Ticket ID : 7
Jira Ticket ID     : SCRUM-30
Issue Subject      : Keyboard keys failure
Priority           : P4
Current Status     : In Progress
Assigned Team      : Hardware Support Team

ESCALATION REASON
──────────────────────────────
Hardware issues require physical inspection by a technician.

NEXT STEPS
──────────────────────────────
• Your ticket has been registered in Jira.
• The assigned support team will investigate it.
• You will receive status updates via email.
```

---

## TECHNOLOGY STACK

| Layer | Technology |
|---|---|
| **Frontend** | React + Vite, TanStack Query, Lucide Icons, Vanilla CSS |
| **Backend (RAG)** | FastAPI (Python), Uvicorn |
| **AI / LLM** | Groq API — Llama 3.3 70B Versatile |
| **Embeddings / RAG** | Sentence Transformers (`all-MiniLM-L6-v2`) |
| **Classification API** | FastAPI + Rule-based NLP (diagnosis_rules.py) |
| **Database** | MySQL + SQLAlchemy ORM |
| **Email** | Gmail SMTP (smtplib, SSL port 465) |
| **Jira** | Atlassian REST API v3 |
| **Environment** | Python venv, dotenv for credentials |

---

## SUMMARY — VALUE DELIVERED

| Feature | Before SupportPilot | After SupportPilot |
|---|---|---|
| Ticket Classification | Manual — agent reads and categorizes | Automatic — AI classifies in < 1 second |
| Resolution | Agent researches and replies manually | AI generates step-by-step resolution instantly |
| Escalation Decision | Human judgment — inconsistent | Rule-based + confidence scoring — consistent |
| Jira Ticket Creation | Manual copy-paste | Automatic on escalation |
| User Notification | Manual email | Automatic — resolution or escalation email |
| Reporting | Spreadsheet | Real-time Analytics dashboard |

---

*SupportPilot — Built with FastAPI, React, Groq LLM, and MySQL | Infosys Internship Project*
