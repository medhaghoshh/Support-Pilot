# The 6 Tabs of SupportPilot — How Each One Works (Current Build)

The whole app lives inside `App.jsx`. Navigation is driven by a single `activeTab` state variable — clicking any sidebar item calls `setActiveTab`, and the main content area conditionally renders the matching component. Nothing reloads. No router. Pure client-side conditional rendering.

The sidebar is built from a `NAV_ITEMS` array with 6 entries: Dashboard, Tickets, AI Agent, Integrations, Analytics, Settings. A `Sidebar` component maps over that array and highlights the active item.

---

## 1. Dashboard Tab

**Renders:** `DashboardOptimization.jsx`  
**Receives:** `tickets` — the full live ticket array fetched from port 8000

This is the landing tab — what opens first. It receives the already-fetched ticket list from `App.jsx` (via `useQuery` polling `http://localhost:8000/api/tickets` every 30 seconds), so it doesn't make its own ticket fetch — it works off the shared state.

**What it shows:**

- **Total Tickets, Open Tickets, Resolved Tickets, Escalated Tickets** — computed from the ticket array directly in the component. Resolved = status `RESOLVED` or `CLOSED`. Escalated = status `IN_PROGRESS`.
- **Resolution Rate** — percentage of tickets that are resolved vs total. If all 7 tickets are resolved, this reads 100%. If 1 is open, it adjusts.
- **Severity Breakdown** — counts of Low / Medium / High / Critical tickets, pulled from the `severity` field stored in the DB.
- **Recent Activity Feed** — the ticket list sorted by most recent, showing subject, status badge, and requester email.

**The purpose** is a bird's-eye operational snapshot. An IT manager opens this and immediately knows: how many tickets are active, what's the AI resolution rate, are there any critical issues, and what came in recently — all without clicking into individual tickets.

---

## 2. Tickets Tab

**Renders:** Inline in `App.jsx` — a two-pane layout. No single component wraps it; the left pane and right pane are built directly in the JSX.  
**Sub-components used:** `TicketForm.jsx`, `ResolutionPanel.jsx`

This is the core workspace. Every ticket action — creating, viewing, classifying, resolving — happens here.

### Left Pane — Live Ticket List (fixed 320px width)

Pulls from the shared `tickets` state (same query as Dashboard). Three controls live above the list:

- **New Ticket button** — sets `isCreatingTicket = true` and clears `activeTicket`, which switches the right pane to the submission form
- **Search bar** — live filters the `filteredTickets` array by matching the search string against `t.subject` and `t.description`
- **Status filter pills** — four options: `ALL`, `OPEN`, `IN_PROGRESS`, `RESOLVED`. Resolved also catches `CLOSED` status. Selecting one updates `statusFilter` state, which re-filters the displayed list.

Each ticket card in the list shows: subject, a colored status badge (green for RESOLVED, amber for IN_PROGRESS, blue for OPEN), a 2-line preview of the description, the requester's username (email prefix before @), their department, and priority in red. Clicking a card calls `handleSelectRecentTicket(ticket)`.

### Right Pane — Three States

The right pane is a conditional render based on two state variables: `isCreatingTicket` and `activeTicket`.

**State 1 — Creating a new ticket (`isCreatingTicket = true`)**

Renders `TicketForm.jsx`. The form collects: Subject, Description, Requester Email, Department (the user's work department — Finance, HR, etc.), Priority (P1–P4), and Severity. On submit, it POSTs to `http://localhost:8000/api/tickets`. On success, the backend also calls the Diagnosis API on port 8001 to classify the ticket immediately, returns the classification result alongside the new ticket, and `handleTicketCreated(ticket, classification)` is called — which calls `classifyTicket(description)` to get the AI category and sets `activeTicket` with the real category and confidence. The new ticket then appears at the top of the left pane.

**State 2 — A ticket is selected (`activeTicket !== null`)**

This is the full ticket workspace. It's a vertical stack of blocks:

- **Ticket Header** — Ticket ID (styled as `T-7`), status badge, title, requester email, priority, and time label
- **Two-column grid:**
  - *Left block (3/5 width)* — the original ticket description in a scrollable card. Below the description are three mini-stats: Accuracy (94%), Processing time (1.2s), and Today's ticket count (live from `tickets.length`)
  - *Right block (2/5 width)* — the **AI Classification card**. Shows Category, Sub-Category, Severity, Priority, and a Confidence Score progress bar. The category and confidence come from `classifyTicket(description)` — a GET call to `http://localhost:8001/diagnose?text=<description>`. The category is the AI-predicted IT category (Networking, Hardware, Password Reset, Software, etc.), not the user's work department. The confidence bar animates from 0 to the real value.
- **Resolution Panel** — renders `ResolutionPanel.jsx`, which contains the "Resolve" button. Clicking it POSTs to `http://localhost:8000/api/tickets/{id}/resolve`, triggering the full 4-agent backend pipeline. The panel shows the generated resolution steps and has two tabs: **Resolution** (shows the step-by-step AI-generated fix) and **AI Agent** (shows the pipeline workflow visualization with Jira/email output).

**State 3 — Nothing selected, not creating**

An empty state with a centered icon, a prompt message ("Select a ticket from the left pane…"), and a shortcut button to create a new ticket.

---

## 3. AI Agent Tab

**Renders:** `AgentWorkflowPanel.jsx`  
**Receives:** `activeTicket` — whatever ticket is currently selected in the Tickets tab

This is a full-screen, dedicated view of the multi-agent pipeline for the active ticket. It's the same content as the "AI Agent" sub-tab inside `ResolutionPanel.jsx`, but surfaced as its own top-level tab so it can be viewed standalone without the ticket list in the way.

**What it shows:**

- **Pipeline Agent Topology** — four agent cards in a horizontal flow: Diagnosis → Retrieval → Resolution → Escalation. Each card has an icon and a live status label: `COMPLETED`, `ACTIVE`, or `STANDBY`. The status comes from polling `GET http://localhost:8000/api/tickets/{id}/workflow`.

- **Pipeline STDERR/STDOUT Logs** — a dark terminal-style log box showing the real backend log lines. Each line is timestamped. Shows entries like `AIClassification: Workflow started.`, `Retrieval Agent completed successfully.`, `Escalation Agent started.` — live output from the FastAPI backend.

- **Third-Party Connectors (right column):**
  - *Jira Integration* — shows "Connected - Standby" or "Connected - Identity". If the ticket was escalated, it shows the Jira issue key (e.g. `SCRUM-30`) and a link.
  - *Email Automation* — shows "Connected - Notification sent" once the email dispatch runs.

- **Jira Orchestrator Output** — a text block showing the Jira creation status and escalation state from the workflow response.

- **Automated Email Dispatch** — a preview card showing the exact email that was sent: Subject line, Sender address, Recipient email, and the first few lines of the email body.

If no ticket is active (user comes to this tab without selecting one first), the panel shows a placeholder prompting the user to select a ticket from the Tickets tab.

---

## 4. Integrations Tab

**Renders:** `IntegrationsPage.jsx`  
**No props passed** — manages its own state and API calls internally

Admin-only configuration panel. End users who submit tickets never need this page. It's for the system administrator who sets up the connections that power the backend workflow.

**Two integration blocks:**

### Jira Integration

Four input fields: Jira URL (e.g. `https://yourcompany.atlassian.net`), Jira Email (admin's Atlassian account), API Token (generated from Atlassian's API token settings page), and Project Key (e.g. `SCRUM`).

**Save** — POSTs to `http://localhost:8000/api/integrations/jira/config`. The backend writes this to a persistent config file (`integrations_config.json`). From that point forward, any escalated ticket (Hardware, Security, P1/CRITICAL) automatically creates a real Jira issue in that project using the Atlassian REST API v3.

**Test Connection** — POSTs to `http://localhost:8000/api/integrations/jira/test`. Verifies the credentials authenticate against Jira before saving, so the admin knows immediately if the token is wrong.

### Email Automation (Gmail SMTP)

Two input fields: Gmail Address and App Password (a 16-character Google App Password — not the regular Gmail login password; Google requires a dedicated app password when using SMTP from third-party code).

**Save** — POSTs to `http://localhost:8000/api/integrations/email/config`. Stored in the same config file. Once saved, the email service at `app/services/email_service.py` uses these credentials to send resolution and escalation emails via Gmail SMTP on SSL port 465.

**Test Connection** — POSTs to `http://localhost:8000/api/integrations/email/test`, which sends a real test email to the configured address to confirm SMTP works.

**The real-world impact:** Without this page being configured, the entire notification system is silent. Tickets can be resolved internally, but no user ever knows because no email goes out. Jira integration being unconfigured means escalated hardware tickets sit in the DB with no tracking in the engineering team's board.

---

## 5. Analytics Tab

**Renders:** `ClassificationResults.jsx`  
**No props** — completely self-contained, fetches its own data

This tab is different from the Dashboard tab. Dashboard shows operational health (how many open, how many resolved). Analytics shows **AI classification accuracy** — specifically, what category the AI assigned to each ticket and how confident it was.

**Data flow:**
1. Fetches the full ticket list from `http://localhost:8000/api/tickets`
2. For every ticket, calls `GET http://localhost:8001/diagnose?text=<subject + description combined>` — the Diagnosis API
3. If the API returns a real category (confidence > 0), uses it. If confidence is 0.0 or the API matched no keywords, falls back to a local `localInfer()` keyword heuristic built into the component
4. Displays the results in a table

**Header stats row:** Total Tickets, Open Tickets, Closed Tickets, High Severity count, Medium Severity count, Low Severity count.

**Table columns:** Ticket ID (clickable), Subject, Category (the AI-classified IT category — Networking, Hardware, Software, Password Reset, etc.), Severity badge, Priority, Confidence (progress bar + percentage), Status (Closed/Open badge), Action (View button).

**Search bar** — filters the table by ticket ID, subject, department, or status in real time.

**View modal** — clicking the View button on any row opens a detail slide-in panel showing the full ticket info: description, AI category, confidence, severity, priority, status, and created-at timestamp.

**Why this tab exists:** It lets an admin audit how well the AI classifier is actually performing. If the classifier consistently gets a category wrong (e.g., calling "System Server Outage" something other than IT Support), that's visible here and can be used to improve the Knowledge Base or diagnosis rules.

---

## 6. Settings Tab

**Renders:** `SettingsPage.jsx`  
**Receives:** `theme`, `setTheme`, `accentColor`, `setAccentColor`, `density`, `setDensity`, `refreshInterval`, `setRefreshInterval`, `language`, `setLanguage`, `notifications`, `setNotifications` — all from `App.jsx` state

Pure user preference panel. Every setting lives in `App.jsx` state and is also persisted to `localStorage`, so preferences survive a browser refresh.

**Sections:**

- **Theme** — Dark or Light mode. Toggles `dark` class on the root element. Most components are written with `dark:` Tailwind variants so the whole UI flips cleanly.
- **Accent Color** — Four options: Indigo (default), Violet, Emerald, Amber. Changes the primary color of buttons, badges, and highlights across the app.
- **Density** — Comfortable or Compact. Adjusts spacing classes on cards and list items.
- **Refresh Interval** — How often the ticket list auto-refreshes: 15s, 30s (default), 60s, or 5 minutes. Controls the `refetchInterval` on the `useQuery` call in `App.jsx`.
- **Language** — English, Spanish (`es`), French (`fr`), or German (`de`). The `TRANSLATIONS` object in `App.jsx` maps language keys to translated label strings. The `t` object (the active translation) is passed to the `Sidebar` component and used wherever nav labels appear.
- **Notifications** — Two toggles: Desktop Notifications (uses the browser `Notification` API to pop a system alert when a new ticket arrives) and Email Notifications (controls whether the user wants email alerts — stored as a preference flag).

---

## How It All Connects

```
App.jsx
  ├── useQuery → GET localhost:8000/api/tickets (polls every 30s)
  ├── activeTab state → controls which component renders
  ├── activeTicket state → shared between Tickets tab and AI Agent tab
  │
  ├── Dashboard tab   → DashboardOptimization.jsx     (receives tickets[])
  ├── Tickets tab     → Inline layout in App.jsx
  │     ├── Left pane  → ticket list from shared state
  │     └── Right pane → TicketForm.jsx | ResolutionPanel.jsx | empty state
  ├── AI Agent tab    → AgentWorkflowPanel.jsx          (receives activeTicket)
  │     └── polls      GET localhost:8000/api/tickets/{id}/workflow
  ├── Integrations tab→ IntegrationsPage.jsx
  │     ├── POST       localhost:8000/api/integrations/jira/config
  │     └── POST       localhost:8000/api/integrations/email/config
  ├── Analytics tab   → ClassificationResults.jsx
  │     ├── GET        localhost:8000/api/tickets
  │     └── GET        localhost:8001/diagnose?text=<subject+description>
  └── Settings tab    → SettingsPage.jsx               (receives all preference state)
```

---

*SupportPilot — React + FastAPI + Groq LLM + MySQL | Infosys Internship Project*
