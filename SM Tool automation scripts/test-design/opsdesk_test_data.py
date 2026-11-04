"""Single source of truth for the OpsDesk test design.

Requirements, scenarios and test cases defined here feed:
  * test-design/build_test_design.py  -> deliverables/OpsDesk_Test_Design_RTM.xlsx
  * reporting/generate_reports.py     -> defect summary + QA status report

Sources: OpsDesk_Application_Documentation.docx (build 28-Oct-2026), referenced as
"Doc §n", and the ticket-flow description supplied by the project team ("Flow step n").
"""

# ---------------------------------------------------------------------------
# Requirements
# ---------------------------------------------------------------------------
REQUIREMENTS = [
    # id, title, description, source, priority
    ("FR-01", "Authentication", "Users sign in with email and password; failed attempts are throttled; optional two-step verification; logout ends the session.", "Doc §7 (Configuration console)", "High"),
    ("FR-02", "Role-based access", "Customer, Employee, Team lead, Manager and Super admin see and do only what their role allows; only Super admin opens Administration.", "Doc §2", "High"),
    ("FR-03", "Ticket intake channels", "Tickets arrive via portal, email (webhook/IMAP), WhatsApp, monitoring alerts and API; inbound messages are queued and can be re-queued; replies thread into existing tickets.", "Doc §1, §4; Flow step 1", "High"),
    ("FR-04", "Ticket types and forms", "Customers raise Incidents and Service Requests only; Changes are staff-only. Default type-specific fields are shown.", "Doc §3; Flow step 1", "High"),
    ("FR-05", "Ticket numbering", "System assigns a gap-free ticket number with the type prefix (INC/REQ/CHG).", "Doc §3, §4; Flow step 2", "High"),
    ("FR-06", "Priority calculation", "Priority P1–P4 is calculated from impact and urgency (1–4) using the priority matrix; staff can override, which recalculates SLA due dates.", "Doc §4, §6; Flow step 2", "High"),
    ("FR-07", "SLA policy application", "Standard or Premium policy applied from the account, else the workspace default; targets per priority; business hours/holidays respected; Changes have no SLA.", "Doc §4, §6; Flow step 3", "High"),
    ("FR-08", "Routing and assignment", "Team chosen by category/service/CI; assignment manual, round-robin or least-loaded, skipping unavailable people; assignee list filtered by team.", "Doc §4, §7; Flow step 4", "High"),
    ("FR-09", "Unassigned ticket handling", "Employees cannot see unassigned tickets; a Team lead or Manager assigns them.", "Doc §2, §4; Flow step 5", "High"),
    ("FR-10", "Support work", "Staff investigate, update fields, send public replies, add internal notes, attach files and use AI suggestions.", "Doc §4; Flow step 6", "High"),
    ("FR-11", "Waiting states and SLA pause", "Waiting on customer and Awaiting approval pause the SLA; Waiting on third party does not; a customer reply returns the ticket to work.", "Doc §4, §6; Flow step 7", "High"),
    ("FR-12", "SLA alerts", "At-risk alert at 75% (per-policy threshold) and breach alert, to assignee and team, plus in-app notification to assignee.", "Doc §6; Flow step 8", "High"),
    ("FR-13", "Resolution and CSAT", "Resolution needs a resolution code and notes; a CSAT survey can be sent and answered without signing in.", "Doc §4, §5.1, §7; Flow step 9", "High"),
    ("FR-14", "Closure and auto-close", "Customer can reopen or confirm-close; resolved tickets auto-close after 5 days (workspace setting, checked hourly).", "Doc §4, §5.1; Flow step 10", "High"),
    ("FR-15", "Incident workflow", "New → In progress → Waiting → Resolved → Closed; cancel with comment by staff; resolve from any open state.", "Doc §5.1", "High"),
    ("FR-16", "Service request workflow", "New → (Awaiting approval) → In fulfilment → Fulfilled → Closed; reject by lead/manager with comment; fulfil requires notes.", "Doc §5.2", "High"),
    ("FR-17", "Change workflow", "Draft → Assessment → CAB → Scheduled → Implementing → PIR → Closed with stage field gates; reject/close by lead/manager.", "Doc §5.4", "Medium"),
    ("FR-18", "Problem workflow", "Staff-only; known error/resolve need root cause and resolution notes; close restricted to lead/manager.", "Doc §5.3", "Medium"),
    ("FR-19", "History and audit", "All changes recorded in ticket history and an append-only, searchable audit log.", "Doc §4; Flow step 11", "High"),
    ("FR-20", "Dashboard KPIs", "Open, breached, at-risk, SLA met %, avg first response, MTTR, CSAT, AI accepted; period 7/30/90 and account filter.", "Doc §8; Monitoring", "High"),
    ("FR-21", "Dashboard charts", "Created vs resolved, backlog age, intake by channel, open by priority; Accounts this period and Open by team for lead/manager/super admin only.", "Doc §8; Monitoring", "Medium"),
    ("FR-22", "Report exports", "Overview, Tickets, Major Incidents, Team Workload as CSV or PDF, respecting viewer visibility.", "Doc §8; Monitoring", "Medium"),
    ("FR-23", "Customer portal", "Customer sees requested/watched/company tickets, public replies only, can reply, edit subject/description/customer fields, rate service; portal is installable (PWA).", "Doc §1, §2", "High"),
    ("FR-24", "Knowledge base", "Customers read and vote on public articles; staff create/edit/delete and convert resolved tickets to drafts; suggestions on tickets and while typing.", "Doc §7", "Medium"),
    ("FR-25", "Administration console", "Super admin manages users (edit/deactivate/reset, no create), teams, SLA, business hours, workflows, types, priorities, categories, automation, accounts, channels, canned responses, outbox, audit log.", "Doc §2, §7", "Medium"),
    ("FR-26", "Multi-tenant isolation", "Each workspace is isolated in the application and by database row-level security.", "Doc §1", "High"),
    ("FR-27", "Notifications", "Requester acknowledgement and resolution messages; staff assignment, SLA and in-app notifications; live event stream.", "Doc §7", "Medium"),
    ("FR-28", "AI assistance", "Similar tickets/articles, duplicate merge, triage suggestions, summary, draft reply; PII masked; acceptance tracked.", "Doc §7", "Medium"),
    ("FR-29", "Major incidents", "Team leads and managers declare and coordinate major incidents; Major Incidents report.", "Doc §2, §8", "Medium"),
    ("NFR-01", "Security", "HTTPS, secure session handling, protection against XSS/IDOR/CSV injection, security headers.", "Doc §1, §7 (implied)", "High"),
    ("NFR-02", "Performance & compatibility", "Key pages load promptly; works on supported browsers and mobile viewport.", "Doc §1 (installable web app)", "Medium"),
]

# ---------------------------------------------------------------------------
# Scenarios (one per module)
# ---------------------------------------------------------------------------
MODULES = {
    "AUTH": ("Authentication & session", "Verify sign-in, sign-out, throttling and session protection for every role."),
    "RBAC": ("Role-based access control", "Verify each role sees only permitted screens, tickets and actions."),
    "TKT": ("Ticket creation & numbering", "Verify ticket creation per type and role, form fields, validation and gap-free numbering."),
    "PRI": ("Priority calculation", "Verify the impact × urgency matrix and priority override behaviour."),
    "SLA": ("SLA policies & timers", "Verify policy selection, targets, business hours and pause rules."),
    "WAIT": ("Waiting states", "Verify SLA pause/resume and automatic return to work."),
    "ALR": ("SLA alerts", "Verify at-risk (75%) and breach notifications."),
    "ASG": ("Routing & assignment", "Verify auto-routing, assignment methods and manual assignment of unassigned tickets."),
    "WRK": ("Support work", "Verify replies, internal notes, attachments and field edits."),
    "INC": ("Incident lifecycle", "Verify incident state transitions, resolution, closure and auto-close."),
    "REQ": ("Service request lifecycle", "Verify request fulfilment, approval and rejection rules."),
    "CHG": ("Change lifecycle", "Verify change stage gates and lead/manager-only actions."),
    "PRB": ("Problem lifecycle", "Verify problem workflow restrictions."),
    "MI": ("Major incidents", "Verify declaration and coordination of major incidents."),
    "AUD": ("History & audit", "Verify ticket history and the tamper-proof audit log."),
    "DSH": ("Dashboard", "Verify KPIs, charts, filters and visibility rules."),
    "RPT": ("Report exports", "Verify CSV/PDF exports and their visibility rules."),
    "CUS": ("Customer portal", "Verify customer self-service capabilities."),
    "KB": ("Knowledge base", "Verify article visibility, voting and staff management."),
    "ADM": ("Administration", "Verify Super admin configuration console."),
    "MT": ("Multi-tenancy", "Verify workspace isolation."),
    "CHN": ("Intake channels", "Verify email, WhatsApp, monitoring and API intake."),
    "NTF": ("Notifications", "Verify email, in-app and live notifications."),
    "AI": ("AI assistance", "Verify AI suggestions, masking and acceptance tracking."),
    "NFR": ("Non-functional", "Verify security, performance, compatibility and accessibility basics."),
}

# Automation status values
AUTO = "Automated"
MANUAL = "Manual"
BLOCKED = "Automation blocked"     # automatable but blocked by data/feature/credential gap

TEST_CASES = []


def tc(id_, req, title, role, pre, steps, data, expected, pri, typ, tech, auto, spec="", note=""):
    TEST_CASES.append({
        "id": id_, "req": req, "module": id_.split("-")[1], "title": title, "role": role,
        "pre": pre, "steps": steps, "data": data, "expected": expected, "priority": pri,
        "type": typ, "technique": tech, "automation": auto, "spec": spec, "note": note,
    })


LOGGED_OUT = "User is signed out; application reachable."
CUST_TKT = "Customer has at least one open ticket."

# --- AUTH -------------------------------------------------------------------
S = "tests/auth.spec.ts"
tc("TC-AUTH-001", "FR-01", "Customer signs in with valid credentials", "Customer", LOGGED_OUT,
   "1. Open the application\n2. Enter customer email and password\n3. Click Sign in",
   "Customer credential", "Customer lands on the self-service portal (ticket list / new request); no Dashboard or Administration menu.", "High", "Positive", "Use case", AUTO, S)
tc("TC-AUTH-002", "FR-01", "Employee signs in with valid credentials", "Employee", LOGGED_OUT,
   "1. Open the application\n2. Enter employee credentials\n3. Click Sign in",
   "Employee credential", "Employee lands on the Dashboard.", "High", "Positive", "Use case", AUTO, S)
tc("TC-AUTH-003", "FR-01", "Manager signs in with valid credentials", "Manager", LOGGED_OUT,
   "1. Open the application\n2. Enter manager credentials\n3. Click Sign in",
   "Manager credential", "User lands on the full Dashboard; Administration entry is NOT shown (Super admin only).", "High", "Positive", "Use case", AUTO, S)
tc("TC-AUTH-004", "FR-01", "Sign-in rejected with wrong password", "Any", LOGGED_OUT,
   "1. Enter a valid email and an incorrect password\n2. Click Sign in",
   "valid email / 'Wrong!Pass123'", "Generic error shown; user stays on sign-in page; no session created.", "High", "Negative", "Equivalence partitioning", AUTO, S)
tc("TC-AUTH-005", "FR-01", "Sign-in with unregistered email gives same generic error", "Any", LOGGED_OUT,
   "1. Enter an unregistered email and any password\n2. Click Sign in\n3. Compare message with TC-AUTH-004",
   "nobody.qa@example.com", "Same generic message as wrong password (no user enumeration).", "Medium", "Security", "Equivalence partitioning", AUTO, S)
tc("TC-AUTH-006", "FR-01", "Sign-in validation for empty fields", "Any", LOGGED_OUT,
   "1. Leave email and password empty and submit\n2. Fill email only and submit\n3. Enter malformed email 'abc@' and submit",
   "'', 'abc@'", "Form is not submitted; field-level validation messages shown.", "Medium", "Negative", "Boundary value analysis", AUTO, S)
tc("TC-AUTH-007", "FR-01", "Login throttling after repeated failures", "Any", "Dedicated throw-away test account (do NOT use shared accounts).",
   "1. Submit wrong password repeatedly (e.g. 10 times)\n2. Submit the correct password",
   "Dedicated account", "After the threshold, further attempts are throttled with a clear message; correct password is refused until the window expires.", "High", "Security", "Boundary value analysis", MANUAL, "",
   "Manual to avoid locking the shared project accounts.")
tc("TC-AUTH-008", "FR-01", "Sign-out ends the session", "Employee", "Employee signed in.",
   "1. Click Sign out\n2. Press browser Back\n3. Reload a protected URL",
   "-", "User is returned to sign-in; protected pages are not shown after Back or reload.", "High", "Security", "Use case", AUTO, S)
tc("TC-AUTH-009", "FR-01", "Protected URL without session redirects to sign-in", "Anonymous", LOGGED_OUT,
   "1. Open /dashboard and /tickets directly in a fresh browser",
   "-", "Redirected to sign-in; no data rendered.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-AUTH-010", "FR-01", "Two-step verification challenge when enabled", "Any", "2FA enabled for a test account.",
   "1. Sign in with valid password\n2. Enter wrong code, then correct code",
   "TOTP code", "Wrong code is rejected; correct code completes sign-in.", "Medium", "Security", "State transition", MANUAL, "",
   "Requires an authenticator on a 2FA-enabled account.")
tc("TC-AUTH-011", "FR-01", "Email is case-insensitive and password is masked", "Customer", LOGGED_OUT,
   "1. Check the password field type\n2. Sign in with the email in upper case",
   "SAKTHIBALAJI.M@...", "Password input is masked; sign-in succeeds with upper-case email.", "Low", "Positive", "Equivalence partitioning", AUTO, S)

# --- RBAC -------------------------------------------------------------------
S = "tests/rbac.spec.ts"
tc("TC-RBAC-001", "FR-02", "Customer cannot open the Dashboard", "Customer", "Customer signed in.",
   "1. Check navigation for Dashboard\n2. Open /dashboard directly",
   "-", "No Dashboard link; direct URL is denied or redirected.", "High", "Security", "Decision table (role × screen)", AUTO, S)
tc("TC-RBAC-002", "FR-02", "Customer cannot open Administration", "Customer", "Customer signed in.",
   "1. Open /admin directly", "-", "Access denied / redirected; no admin data rendered.", "High", "Security", "Decision table (role × screen)", AUTO, S)
tc("TC-RBAC-003", "FR-02", "Employee cannot open Administration", "Employee", "Employee signed in.",
   "1. Check navigation for Administration\n2. Open /admin directly", "-", "No Administration link; direct URL denied.", "High", "Security", "Decision table (role × screen)", AUTO, S)
tc("TC-RBAC-004", "FR-02, FR-09", "Employee ticket list excludes unassigned and others' tickets", "Employee", "Unassigned tickets and tickets of other employees exist.",
   "1. Open the ticket list\n2. Inspect the Assignee column and filters\n3. Look for an 'Unassigned' view",
   "-", "Every row is assigned to / raised by the employee; no unassigned queue is offered.", "High", "Security", "Decision table (role × visibility)", AUTO, S)
tc("TC-RBAC-005", "FR-02", "Team lead sees all tickets but not Administration", "Team lead", "Team lead account available.",
   "1. Sign in as Team lead\n2. Open ticket list incl. unassigned\n3. Open /admin",
   "-", "All workspace tickets visible; Administration denied.", "High", "Security", "Decision table (role × screen)", BLOCKED, S,
   "No Team lead credential supplied — set OPSDESK_TEAMLEAD_* in .env to enable.")
tc("TC-RBAC-006", "FR-02, FR-09", "Manager/Super admin sees unassigned tickets", "Manager", "Unassigned ticket exists.",
   "1. Sign in as Manager/Super admin\n2. Open the unassigned queue/filter",
   "-", "Unassigned tickets are listed.", "High", "Positive", "Decision table (role × visibility)", AUTO, S)
tc("TC-RBAC-007", "FR-02", "Super admin opens every Administration section", "Manager", "Super admin signed in.",
   "1. Open Administration\n2. Visit Users, Teams, SLA policies, Business hours, Configuration, Outbox, Audit log",
   "-", "All sections load without error.", "High", "Positive", "Use case", BLOCKED, S,
   "No Super admin credential supplied (shared admin login is a Manager) — set OPSDESK_SUPERADMIN_* in .env.")
tc("TC-RBAC-012", "FR-02", "Manager cannot open Administration", "Manager", "Manager signed in.",
   "1. Check navigation for Administration\n2. Open /admin directly", "-", "No Administration link; direct URL denied.", "High", "Security", "Decision table (role × screen)", AUTO, S)
tc("TC-RBAC-008", "NFR-01, FR-23", "Customer cannot open another customer's ticket by URL (IDOR)", "Customer", "Staff-created ticket of another account known.",
   "1. As staff, note the URL of a ticket not belonging to the customer's account\n2. As customer, open that URL",
   "Foreign ticket URL", "Not found / access denied; no ticket data shown.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-RBAC-009", "NFR-01, FR-02", "Employee cannot open an unassigned ticket by URL (IDOR)", "Employee", "Unassigned ticket URL known.",
   "1. As Manager, create/locate an unassigned ticket and note its URL\n2. As Employee, open the URL",
   "Unassigned ticket URL", "Not found / access denied.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-RBAC-010", "FR-02, FR-25", "Super admin account cannot be edited, deactivated, assigned or reset", "Manager", "Super admin signed in.",
   "1. Open Users\n2. Locate the Super admin row\n3. Look for Edit/Deactivate/Reset actions\n4. Try assigning a ticket to Super admin",
   "-", "No edit/deactivate/reset actions for the Super admin; not offered as an assignee.", "Medium", "Negative", "Error guessing", AUTO, S)
tc("TC-RBAC-011", "FR-02", "Manager vs Team lead privilege differences", "Manager / Team lead", "Both accounts available; list of 'minor privileges' confirmed by BA.",
   "1. Execute each documented privilege difference for both roles",
   "-", "Only the Manager can perform the Manager-only privileges.", "Low", "Positive", "Decision table", MANUAL, "",
   "Requirement not specified (see DOC-05).")

# --- TKT --------------------------------------------------------------------
S = "tests/tickets.spec.ts"
tc("TC-TKT-001", "FR-04, FR-05", "Customer raises an Incident from the portal", "Customer", "Customer signed in.",
   "1. Click New request\n2. Choose Incident\n3. Enter subject, description, environment, error message\n4. Submit",
   "Subject 'QA-AUTO INC <timestamp>'", "Ticket created; number starts with INC; status New; channel Portal.", "High", "Positive", "Use case", AUTO, S)
tc("TC-TKT-002", "FR-04, FR-05", "Customer raises a Service Request from the portal", "Customer", "Customer signed in.",
   "1. Click New request\n2. Choose Service Request\n3. Enter subject, description, requested for, needed by\n4. Submit",
   "Subject 'QA-AUTO REQ <timestamp>'", "Ticket created; number starts with REQ; status New.", "High", "Positive", "Use case", AUTO, S)
tc("TC-TKT-003", "FR-04", "Customer cannot choose Change or Problem", "Customer", "Customer signed in.",
   "1. Open New request\n2. Inspect ticket type options", "-", "Only Incident and Service Request are offered.", "High", "Negative", "Equivalence partitioning", AUTO, S)
tc("TC-TKT-004", "FR-04", "Incident form shows Environment and Error message", "Customer", "Customer signed in.",
   "1. Open New request → Incident", "-", "Environment and Error message fields are present.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-TKT-005", "FR-04", "Service Request form shows Requested for and Needed by", "Customer", "Customer signed in.",
   "1. Open New request → Service Request", "-", "Requested for and Needed by fields are present.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-TKT-006", "FR-04, FR-05", "Staff raises a Change with change-specific fields", "Manager", "Staff signed in.",
   "1. New ticket → Change\n2. Inspect fields\n3. Enter subject and save as Draft",
   "Subject 'QA-AUTO CHG <timestamp>'", "Change type, Risk, Implementation window, Back-out plan and Outcome fields exist; number starts with CHG; status Draft.", "High", "Positive", "Use case", AUTO, S)
tc("TC-TKT-007", "FR-04", "Mandatory field validation on new ticket", "Customer", "Customer signed in.",
   "1. Open New request → Incident\n2. Submit with empty subject/description", "Empty values",
   "Submission blocked; required-field messages shown; no ticket number consumed.", "High", "Negative", "Boundary value analysis", AUTO, S)
tc("TC-TKT-008", "FR-04", "Subject length boundaries", "Customer", "Max length confirmed with BA.",
   "1. Submit subjects of max-1, max and max+1 characters", "Max length per spec", "max-1 and max accepted; max+1 rejected or truncated with message.", "Low", "Boundary", "Boundary value analysis", MANUAL, "",
   "Maximum length not documented.")
tc("TC-TKT-009", "FR-04, FR-10", "Attachment rules on new ticket", "Customer", "Allowed types/size confirmed with BA.",
   "1. Attach an allowed file\n2. Attach an executable\n3. Attach an over-size file", "sample.pdf, test.exe, 30MB file",
   "Allowed file stored; disallowed/over-size rejected with message.", "Medium", "Negative", "Equivalence partitioning", MANUAL, "",
   "Allowed types/size not documented.")
tc("TC-TKT-010", "FR-24", "Knowledge articles suggested while customer types", "Customer", "Published public article exists.",
   "1. Open New request\n2. Type keywords that match a public article in the subject", "Article keyword",
   "Matching articles are suggested before submission.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-TKT-011", "NFR-01", "Script in ticket subject is rendered as text (XSS)", "Customer", "Customer signed in.",
   "1. Create incident with subject <img src=x onerror=alert(1)>\n2. Open the ticket as customer and as staff", "XSS payload",
   "No script executes / no dialog; payload displayed as plain text.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-TKT-012", "FR-05", "Ticket numbers are sequential per type", "Customer", "Quiet environment (no parallel creators).",
   "1. Create three incidents in a row\n2. Compare the numeric parts", "3 incidents",
   "Numbers are strictly increasing; in a quiet environment they are consecutive (gap-free).", "High", "Positive", "Boundary value analysis", AUTO, S)
tc("TC-TKT-013", "FR-05", "Concurrent creation never duplicates numbers", "Customer", "Load tool available.",
   "1. Create 20 incidents concurrently via portal/API\n2. Inspect numbers", "20 parallel requests",
   "All numbers unique and gap-free.", "Medium", "Performance", "Error guessing", MANUAL, "")

# --- PRI --------------------------------------------------------------------
S = "tests/priority.spec.ts"
tc("TC-PRI-001", "FR-06", "Priority matrix — all 16 impact × urgency combinations", "Manager", "Default priority matrix in place; staff can set impact/urgency.",
   "For each combination in sheet 'Priority Decision Table':\n1. Create/edit an incident with that impact and urgency\n2. Read the calculated priority",
   "Impact 1–4 × Urgency 1–4", "Priority matches the decision table (sum ≤3 → P1, 4 → P2, 5–6 → P3, 7–8 → P4).", "High", "Positive", "Decision table", AUTO, S)
tc("TC-PRI-002", "FR-06", "Priority band boundaries", "Manager", "Default matrix.",
   "1. Set sums 3,4,5,6,7 (e.g. 1+2, 2+2, 2+3, 3+3, 3+4)", "Boundary sums", "3→P1, 4→P2, 5→P3, 6→P3, 7→P4.", "High", "Boundary", "Boundary value analysis", AUTO, S)
tc("TC-PRI-003", "FR-06, FR-07", "Priority override recalculates SLA due dates", "Manager", "Incident at P4 with SLA timers.",
   "1. Note response/resolution due dates\n2. Override priority to P1\n3. Note due dates again", "P4 → P1",
   "Due dates are recalculated earlier per P1 targets; change recorded in history.", "High", "Positive", "State transition", AUTO, S)
tc("TC-PRI-004", "FR-06, FR-02", "Customer cannot set or override priority", "Customer", "Customer signed in.",
   "1. Open New request and an existing own ticket\n2. Look for an editable Priority field", "-", "Priority is not editable by customer.", "Medium", "Negative", "Decision table (role × field)", AUTO, S)
tc("TC-PRI-005", "FR-06", "Out-of-range impact/urgency rejected", "API client", "API access.",
   "1. Submit impact 0 and urgency 5 via API", "0, 5", "Request rejected with validation error.", "Low", "Negative", "Boundary value analysis", MANUAL, "",
   "API contract not documented.")

# --- SLA --------------------------------------------------------------------
S = "tests/sla.spec.ts"
tc("TC-SLA-001", "FR-07", "Standard policy P1 targets (15 min / 4 h, business hours)", "Manager", "Standard account; created inside business hours.",
   "1. Create P1 incident for a Standard account at a known time\n2. Read response and resolution due", "Standard account",
   "Response due = created + 15 min; resolution due = created + 4 business hours.", "High", "Positive", "Decision table", MANUAL, "",
   "Requires knowing the account's policy; verify manually then promote to automation.")
tc("TC-SLA-002", "FR-07", "Premium policy P1 targets (10 min / 2 h, 24×7)", "Manager", "Premium account.",
   "1. Create P1 incident for a Premium account\n2. Read due dates", "Premium account", "Response +10 min; resolution +2 h calendar time.", "High", "Positive", "Decision table", MANUAL, "")
tc("TC-SLA-003", "FR-07", "Full SLA target table (8 targets × 2 policies)", "Manager", "Standard and Premium accounts.",
   "1. Create P1–P4 for each policy\n2. Compare due dates with Doc §6 table", "8 tickets", "All targets match the table.", "High", "Positive", "Decision table", MANUAL, "")
tc("TC-SLA-004", "FR-07", "Account without policy falls back to workspace default", "Manager", "Account with no policy.",
   "1. Create ticket for that account\n2. Inspect applied policy", "-", "Workspace default policy applied.", "Medium", "Positive", "Equivalence partitioning", MANUAL, "")
tc("TC-SLA-005", "FR-07", "Change tickets have no SLA timer", "Manager", "Staff signed in.",
   "1. Create a Change\n2. Inspect the SLA area", "-", "No SLA timers on the Change.", "Medium", "Positive", "Equivalence partitioning", AUTO, S)
tc("TC-SLA-006", "FR-07", "Standard policy clock stops outside business hours", "Manager", "Standard account; ability to create at Fri 17:50.",
   "1. Create P2 incident Fri 17:50\n2. Check due dates", "Fri 17:50", "Only 10 min consumed Friday; clock resumes Mon 09:00.", "Medium", "Boundary", "Boundary value analysis", MANUAL, "")
tc("TC-SLA-007", "FR-07", "Holidays excluded from Standard policy", "Manager", "Holiday configured.",
   "1. Create ticket the business day before a holiday\n2. Check resolution due", "Holiday", "Holiday hours are skipped.", "Low", "Positive", "Equivalence partitioning", MANUAL, "")
tc("TC-SLA-008", "FR-07, FR-10", "First public staff reply meets first response; internal note does not", "Employee", "New ticket assigned to employee.",
   "1. Add internal note → check response SLA\n2. Send public reply → check response SLA", "-", "Response SLA pending after note; met after public reply.", "High", "Positive", "State transition", AUTO, S)

# --- WAIT -------------------------------------------------------------------
S = "tests/lifecycle.spec.ts"
tc("TC-WAIT-001", "FR-11", "Waiting on customer pauses SLA", "Employee", "In-progress incident with SLA.",
   "1. Ask customer / set Waiting on customer\n2. Inspect SLA indicator", "-", "Status Waiting on customer; SLA shown paused.", "High", "Positive", "State transition", AUTO, S)
tc("TC-WAIT-002", "FR-11", "Customer reply returns ticket to In progress", "Customer", "Ticket in Waiting on customer.",
   "1. As customer, reply on the ticket\n2. As staff, reload ticket", "Reply text", "Status automatically In progress; SLA resumes.", "High", "Positive", "State transition", AUTO, S)
tc("TC-WAIT-003", "FR-11", "Waiting on third party does not pause SLA", "Employee", "In-progress incident.",
   "1. Set Waiting on third party\n2. Inspect SLA indicator", "-", "SLA continues running.", "Medium", "Negative", "State transition", AUTO, S)
tc("TC-WAIT-004", "FR-11", "Awaiting approval pauses SLA", "Employee", "Approvals enabled.",
   "1. Send request for approval\n2. Inspect SLA", "-", "SLA paused while awaiting approval.", "Medium", "Positive", "State transition", BLOCKED, "",
   "Approvals screens switched off in current build.")
tc("TC-WAIT-005", "FR-11", "Paused time is excluded from due date", "Employee", "Premium P3 ticket (24×7).",
   "1. Note resolution due\n2. Pause 30 min (Waiting on customer)\n3. Customer replies\n4. Note new due", "30 min pause", "Resolution due shifted by ≈30 min.", "High", "Positive", "Boundary value analysis", MANUAL, "")

# --- ALR --------------------------------------------------------------------
tc("TC-ALR-001", "FR-12", "At-risk alert at 75% of SLA (74/75/76%)", "Employee", "Premium P1 assigned ticket (10-min response); mailbox access.",
   "1. Create ticket\n2. Observe at 7m24s, 7m30s, 7m36s (checked every minute)", "Premium P1", "No alert before 75%; alert to assignee+team email and in-app notification within ~1 min after 75%.", "High", "Boundary", "Boundary value analysis", MANUAL, "")
tc("TC-ALR-002", "FR-12", "Breach alert when SLA missed", "Employee", "As above.",
   "1. Let response SLA expire", "-", "Breach alert to assignee and team; ticket flagged breached.", "High", "Positive", "State transition", MANUAL, "")
tc("TC-ALR-003", "FR-12, FR-20", "Dashboard At-risk / Breached counters update", "Manager", "At-risk and breached tickets exist.",
   "1. Note counters\n2. Let a ticket reach 75% and 100%\n3. Refresh dashboard", "-", "Counters increment accordingly.", "Medium", "Positive", "State transition", MANUAL, "")
tc("TC-ALR-004", "FR-12", "Alerts are not duplicated each minute", "Employee", "Ticket at risk.",
   "1. Wait 5 minutes after the at-risk alert\n2. Count alerts", "-", "Exactly one at-risk alert per SLA target.", "Medium", "Negative", "Error guessing", MANUAL, "")

# --- ASG --------------------------------------------------------------------
S = "tests/assignment.spec.ts"
tc("TC-ASG-001", "FR-08", "Auto-routing by category selects mapped team", "Manager", "Category→team mapping known.",
   "1. Create ticket with mapped category\n2. Inspect Team field", "Mapped category", "Team set to the mapped team.", "High", "Positive", "Decision table", AUTO, S)
tc("TC-ASG-002", "FR-08, FR-09", "Ticket without matching team lands unassigned", "Customer", "Category with no mapping.",
   "1. Create ticket without category / unmapped\n2. As Manager, view unassigned", "-", "Ticket appears in the unassigned queue.", "High", "Positive", "Decision table", AUTO, S)
tc("TC-ASG-003", "FR-08", "Round-robin assignment", "Manager", "Team set to round-robin with ≥2 available members.",
   "1. Create 4 tickets routed to the team", "-", "Assignees rotate in order.", "Medium", "Positive", "State transition", MANUAL, "")
tc("TC-ASG-004", "FR-08", "Least-loaded assignment", "Manager", "Team set to least-loaded; known open counts.",
   "1. Create a ticket routed to the team", "-", "Member with fewest open tickets is assigned.", "Medium", "Positive", "Decision table", MANUAL, "")
tc("TC-ASG-005", "FR-08", "Unavailable members are skipped", "Manager", "One member marked unavailable.",
   "1. Create tickets routed to the team", "-", "Unavailable member never assigned.", "Medium", "Negative", "Equivalence partitioning", MANUAL, "")
tc("TC-ASG-006", "FR-08", "Assignee list filtered by selected team", "Manager", "Multiple teams exist.",
   "1. Open a ticket\n2. Choose Team A then open Assignee list\n3. Switch to Team B", "-", "Assignee list shows only members of the selected team.", "Medium", "Positive", "Equivalence partitioning", AUTO, S)
tc("TC-ASG-007", "FR-09", "Manager assigns an unassigned ticket to the employee", "Super admin → Employee", "Unassigned ticket exists.",
   "1. As Manager, open unassigned ticket\n2. Set team and assignee = employee\n3. As Employee, open ticket list", "Employee user",
   "Assignment saved; ticket now visible to the employee.", "High", "Positive", "Use case", AUTO, S)
tc("TC-ASG-008", "FR-09, FR-19", "Reassignment is recorded in history", "Manager", "Assigned ticket.",
   "1. Reassign ticket\n2. Open History", "-", "History entry shows old/new assignee, user and time.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-ASG-009", "FR-27", "Assignee receives assignment notification", "Employee", "Mailbox access.",
   "1. Assign a ticket to the employee\n2. Check email and in-app notifications", "-", "Email and in-app notification with ticket details.", "Medium", "Positive", "Use case", MANUAL, "")

# --- WRK --------------------------------------------------------------------
S = "tests/lifecycle.spec.ts"
tc("TC-WRK-001", "FR-10, FR-23", "Public reply is visible to customer", "Employee → Customer", "Ticket assigned to employee.",
   "1. Employee sends public reply\n2. Customer opens the ticket", "Reply text", "Customer sees the reply.", "High", "Positive", "Use case", AUTO, S)
tc("TC-WRK-002", "FR-10, FR-23", "Internal note is hidden from customer", "Employee → Customer", "Ticket assigned to employee.",
   "1. Employee adds internal note\n2. Customer opens the ticket", "Note text", "Note not visible to the customer anywhere (thread, history, email).", "High", "Security", "Use case", AUTO, S)
tc("TC-WRK-003", "FR-10", "Staff attaches a file to a ticket", "Employee", "Ticket assigned to employee.",
   "1. Attach sample.txt\n2. Reload ticket", "sample.txt", "Attachment listed and downloadable.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-WRK-004", "FR-10, FR-19", "Staff edits ticket fields; history updated", "Employee", "Ticket assigned to employee.",
   "1. Change category/impact\n2. Save\n3. Open History", "-", "Values persisted; history shows each change.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-WRK-005", "FR-23", "Customer edits subject and description of own ticket", "Customer", CUST_TKT,
   "1. Edit subject and description\n2. Save and reload", "New text", "Changes saved.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-WRK-006", "FR-23, FR-02", "Customer cannot edit staff-only fields", "Customer", CUST_TKT,
   "1. Open own ticket\n2. Look for editable assignee, team, priority, status", "-", "Those fields are read-only or hidden.", "High", "Negative", "Decision table (role × field)", AUTO, S)
tc("TC-WRK-007", "FR-10, FR-28", "AI suggestion can be accepted from the ticket", "Employee", "Ticket with AI suggestions.",
   "1. Open AI panel\n2. Accept a category suggestion", "-", "Suggestion applied; acceptance counted in dashboard metric.", "Medium", "Positive", "Use case", MANUAL, "")

# --- INC --------------------------------------------------------------------
tc("TC-INC-001", "FR-15", "Start work moves New → In progress", "Employee", "New incident assigned to employee.",
   "1. Click Start work", "-", "Status In progress; history entry created.", "High", "Positive", "State transition", AUTO, S)
tc("TC-INC-002", "FR-13", "Resolve blocked without resolution code and notes", "Employee", "In-progress incident.",
   "1. Click Resolve\n2. Submit without code and notes", "Empty", "Resolution rejected with validation message; status unchanged.", "High", "Negative", "Decision table", AUTO, S)
tc("TC-INC-003", "FR-13", "Resolve with code and notes", "Employee", "In-progress incident.",
   "1. Resolve with code and notes", "Code + notes", "Status Resolved; resolution shown to customer.", "High", "Positive", "State transition", AUTO, S)
tc("TC-INC-004", "FR-15", "Resolve directly from New", "Manager", "New incident.",
   "1. Resolve a New incident with code+notes", "-", "Allowed — status Resolved.", "Medium", "Positive", "State transition", AUTO, S)
tc("TC-INC-005", "FR-14", "Customer confirms closure", "Customer", "Resolved incident.",
   "1. Customer clicks Confirm close", "-", "Status Closed; no further transitions offered.", "High", "Positive", "State transition", AUTO, S)
tc("TC-INC-006", "FR-14", "Customer reopens a resolved incident", "Customer", "Resolved incident.",
   "1. Customer clicks Reopen (with comment if required)", "Reopen reason", "Ticket returns to an open working state; SLA resumes; history recorded.", "High", "Positive", "State transition", AUTO, S)
tc("TC-INC-007", "FR-15", "Cancel requires a comment", "Employee", "Open incident.",
   "1. Click Cancel without comment\n2. Cancel with comment", "Comment", "Without comment blocked; with comment status Cancelled.", "Medium", "Negative", "Decision table", AUTO, S)
tc("TC-INC-008", "FR-15, FR-02", "Customer cannot cancel a ticket", "Customer", CUST_TKT,
   "1. Open own open ticket\n2. Look for Cancel", "-", "No Cancel action for customer.", "Medium", "Negative", "Decision table (role × action)", AUTO, S)
tc("TC-INC-009", "FR-15", "Invalid transitions not offered on Closed ticket", "Manager", "Closed incident.",
   "1. Open closed ticket\n2. Inspect actions", "-", "No Start work / Resolve actions.", "Medium", "Negative", "State transition", AUTO, S)
tc("TC-INC-010", "FR-14", "Auto-close after 5 days (boundary)", "System", "Resolved tickets aged 4d23h and 5d1h (DB/clock control).",
   "1. Prepare tickets\n2. Wait for hourly job", "4d23h / 5d1h", "4d23h stays Resolved; 5d1h becomes Closed.", "High", "Boundary", "Boundary value analysis", MANUAL, "",
   "Needs clock/DB manipulation or a 5-day soak.")
tc("TC-INC-011", "FR-13", "CSAT survey link sent and answered without sign-in", "Customer", "CSAT enabled; mailbox access.",
   "1. Resolve ticket\n2. Open survey link in private window\n3. Submit rating", "Rating 4", "Survey answered without login; CSAT on dashboard updated.", "Medium", "Positive", "Use case", MANUAL, "")
tc("TC-INC-012", "FR-13", "CSAT rating boundaries", "Customer", "Survey link.",
   "1. Submit 1 and 5\n2. Tamper to 0 and 6", "0,1,5,6", "1 and 5 accepted; 0 and 6 rejected.", "Low", "Boundary", "Boundary value analysis", MANUAL, "")

# --- REQ --------------------------------------------------------------------
tc("TC-REQ-001", "FR-16", "Request goes straight to fulfilment without approval", "Employee", "New service request assigned.",
   "1. Start fulfilment", "-", "Status In fulfilment.", "High", "Positive", "State transition", AUTO, S)
tc("TC-REQ-002", "FR-16", "Fulfil blocked without resolution notes", "Employee", "Request in fulfilment.",
   "1. Click Fulfil without notes", "-", "Blocked with validation message.", "High", "Negative", "Decision table", AUTO, S)
tc("TC-REQ-003", "FR-16, FR-14", "Fulfil with notes; customer closes", "Employee → Customer", "Request in fulfilment.",
   "1. Fulfil with notes\n2. Customer confirms close", "Notes", "Fulfilled then Closed.", "High", "Positive", "State transition", AUTO, S)
tc("TC-REQ-004", "FR-16", "Customer reopens fulfilled request", "Customer", "Fulfilled request.",
   "1. Customer clicks Reopen", "-", "Request returns to work.", "Medium", "Positive", "State transition", AUTO, S)
tc("TC-REQ-005", "FR-16", "Lead/manager rejects request at approval stage with comment", "Manager", "Approvals enabled.",
   "1. Send for approval\n2. Reject without then with comment", "-", "Comment mandatory; request rejected.", "Medium", "Positive", "Decision table", BLOCKED, "",
   "Approvals screens switched off in current build.")
tc("TC-REQ-006", "FR-16, FR-02", "Employee cannot reject a request", "Employee", "Approvals enabled.",
   "1. Open request awaiting approval as employee", "-", "Reject not offered.", "Medium", "Negative", "Decision table (role × action)", BLOCKED, "",
   "Approvals screens switched off in current build.")
tc("TC-REQ-007", "FR-16", "Workflow blocked until all approvals approved", "Employee", "Approvals enabled; two approvers.",
   "1. Request two approvals\n2. Approve one\n3. Try to proceed", "-", "Blocked until both approve.", "Medium", "Negative", "State transition", BLOCKED, "",
   "Approvals screens switched off in current build.")

# --- CHG --------------------------------------------------------------------
S = "tests/change.spec.ts"
tc("TC-CHG-001", "FR-04, NFR-01", "Customer cannot create a Change via direct URL", "Customer", "Customer signed in.",
   "1. Open the staff new-change URL directly", "-", "Denied / type not available.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-CHG-002", "FR-17", "Submit for assessment requires type, risk and back-out plan", "Manager", "Draft change.",
   "1. Submit for assessment with fields empty\n2. Fill fields and submit", "-", "Blocked when missing; moves to Assessment when complete.", "High", "Negative", "Decision table", AUTO, S)
tc("TC-CHG-003", "FR-17", "CAB review requires implementation window", "Manager", "Change in Assessment.",
   "1. Move to CAB without window\n2. Add window and retry", "-", "Blocked when missing; moves to CAB when present.", "High", "Negative", "Decision table", AUTO, S)
tc("TC-CHG-004", "FR-17", "Completing a change requires outcome", "Manager", "Change in Post-implementation review.",
   "1. Close without outcome\n2. Add outcome and close", "-", "Blocked when missing; Closed when present.", "Medium", "Negative", "Decision table", MANUAL, "",
   "Depends on approval step which is switched off; run manually once approvals path is clarified.")
tc("TC-CHG-005", "FR-17", "Full change happy path Draft → Closed", "Manager", "Approvals enabled.",
   "1. Progress through every stage", "-", "All transitions succeed in order.", "Medium", "Positive", "State transition", BLOCKED, "",
   "Approve/Schedule needs approval; approvals switched off.")
tc("TC-CHG-006", "FR-17, FR-02", "Employee cannot reject or close a change", "Employee", "Change assigned to employee.",
   "1. Open change as employee\n2. Inspect actions", "-", "No Reject/Close actions.", "Medium", "Negative", "Decision table (role × action)", AUTO, S)

# --- PRB --------------------------------------------------------------------
tc("TC-PRB-001", "FR-18", "Problems are staff-only", "Customer / Staff", "-",
   "1. Check customer type list\n2. Create Problem as staff", "-", "Customer cannot; staff can create Problem.", "Medium", "Negative", "Decision table", MANUAL, "",
   "Problem type/prefix not documented in §3 (DOC-02).")
tc("TC-PRB-002", "FR-18", "Known error / resolve require root cause and notes", "Employee", "Problem in RCA.",
   "1. Record known error without root cause\n2. With root cause", "-", "Blocked then allowed.", "Medium", "Negative", "Decision table", MANUAL, "")
tc("TC-PRB-003", "FR-18", "Only lead/manager can close a resolved problem", "Employee / Manager", "Resolved problem.",
   "1. Employee tries Close\n2. Manager closes", "-", "Employee blocked; Manager succeeds.", "Medium", "Negative", "Decision table (role × action)", MANUAL, "")

# --- MI ---------------------------------------------------------------------
S = "tests/major-incident.spec.ts"
tc("TC-MI-001", "FR-29", "Manager declares a major incident", "Manager", "P1 incident.",
   "1. Open incident\n2. Declare major incident", "-", "Ticket flagged as major incident; appears in Major Incidents report.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-MI-002", "FR-29, FR-02", "Employee cannot declare a major incident", "Employee", "Incident assigned to employee.",
   "1. Open incident\n2. Look for Declare major incident", "-", "Action not available.", "Medium", "Negative", "Decision table (role × action)", AUTO, S)

# --- AUD --------------------------------------------------------------------
S = "tests/audit.spec.ts"
tc("TC-AUD-001", "FR-19", "Ticket history shows changes with user and time", "Manager", "Ticket with edits.",
   "1. Open ticket History tab", "-", "Each change listed with field, old/new value, user, timestamp.", "High", "Positive", "Use case", AUTO, S)
tc("TC-AUD-002", "FR-19", "Super admin searches the audit log", "Manager", "Recent edits exist.",
   "1. Open Administration → Audit log\n2. Search by ticket number", "Ticket number", "Matching entries returned.", "High", "Positive", "Use case", AUTO, S)
tc("TC-AUD-003", "FR-19", "Audit log entries offer no edit/delete", "Manager", "Audit log open.",
   "1. Inspect entry actions", "-", "No edit/delete controls.", "Medium", "Negative", "Error guessing", AUTO, S)
tc("TC-AUD-004", "FR-19", "Database blocks UPDATE/DELETE on audit table", "DBA", "Read/write DB access in test env.",
   "1. Attempt UPDATE and DELETE on an audit row", "SQL", "Both statements rejected.", "High", "Security", "Error guessing", MANUAL, "")
tc("TC-AUD-005", "FR-19, FR-02", "Non-admin cannot open the audit log", "Employee", "Employee signed in.",
   "1. Open the audit log URL directly", "-", "Access denied.", "High", "Security", "Decision table (role × screen)", AUTO, S)

# --- DSH --------------------------------------------------------------------
S = "tests/dashboard.spec.ts"
tc("TC-DSH-001", "FR-20", "All KPI cards are displayed", "Manager", "Staff signed in.",
   "1. Open Dashboard", "-", "Open now, Open and breached, At risk, SLA met, Avg first response, Mean time to resolve, CSAT, AI suggestions accepted visible.", "High", "Positive", "Use case", AUTO, S)
tc("TC-DSH-002", "FR-20", "Period selector 7/30/90 days", "Manager", "Dashboard open.",
   "1. Select 7, 30, 90 days", "7/30/90", "Each option selectable; figures/charts refresh without error.", "High", "Positive", "Equivalence partitioning", AUTO, S)
tc("TC-DSH-003", "FR-20", "Account filter", "Manager", "Multiple accounts.",
   "1. Select an account", "-", "Figures restricted to that account.", "Medium", "Positive", "Equivalence partitioning", AUTO, S)
tc("TC-DSH-004", "FR-21", "Common charts displayed for staff", "Employee", "Staff signed in.",
   "1. Open Dashboard", "-", "Created vs resolved, Backlog age, Intake by channel, Open by priority visible.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-DSH-005", "FR-21", "Lead-level charts visible for Manager/Super admin", "Manager", "-",
   "1. Open Dashboard", "-", "Accounts this period and Open by team visible.", "Medium", "Positive", "Decision table (role × widget)", AUTO, S)
tc("TC-DSH-006", "FR-21, FR-02", "Lead-level charts hidden for Employee", "Employee", "-",
   "1. Open Dashboard", "-", "Accounts this period and Open by team not shown.", "High", "Security", "Decision table (role × widget)", AUTO, S)
tc("TC-DSH-007", "FR-20", "Employee KPIs reflect only own tickets", "Employee", "Known own-ticket counts.",
   "1. Count own open tickets in list\n2. Compare with Open now", "-", "Values equal.", "High", "Positive", "Data reconciliation", MANUAL, "")
tc("TC-DSH-008", "FR-20, FR-21", "Open by priority totals equal Open now", "Manager", "-",
   "1. Sum chart segments\n2. Compare with Open now", "-", "Totals equal.", "Medium", "Positive", "Data reconciliation", MANUAL, "")
tc("TC-DSH-009", "FR-20", "SLA met % calculation", "Manager", "Seeded resolved tickets with known breaches.",
   "1. Compute expected %\n2. Compare", "Seed data", "Matches expected per Doc §8 definition.", "High", "Positive", "Data reconciliation", MANUAL, "")
tc("TC-DSH-010", "FR-20", "Avg first response shown in minutes when under 1 h", "Manager", "Avg < 60 min.",
   "1. Read Avg first response", "-", "Displayed in minutes.", "Low", "Boundary", "Boundary value analysis", MANUAL, "")

# --- RPT --------------------------------------------------------------------
S = "tests/reports.spec.ts"
for i, (rep, pri) in enumerate([("Overview", "High"), ("Tickets", "High"), ("Major Incidents", "Medium"), ("Team Workload", "Medium")], start=1):
    tc(f"TC-RPT-00{i}", "FR-22", f"Export {rep} report as CSV and PDF", "Manager", "Reports page open.",
       f"1. Export {rep} as CSV\n2. Export {rep} as PDF", "-", "Both files download, are non-empty and of the correct type.", pri, "Positive", "Equivalence partitioning", AUTO, S)
tc("TC-RPT-005", "FR-22, FR-02", "Employee export contains only own tickets", "Employee", "Employee signed in.",
   "1. Export Tickets CSV\n2. Compare rows with ticket list", "-", "Row count equals employee's visible tickets.", "High", "Security", "Data reconciliation", AUTO, S)
tc("TC-RPT-006", "NFR-01", "CSV formula injection neutralised", "Customer / Super admin", "Ticket subject '=HYPERLINK(\"http://x\")'.",
   "1. Create ticket with formula subject\n2. Export Tickets CSV\n3. Open in Excel", "=cmd|...", "Cell is escaped (prefixed) and not executed.", "Medium", "Security", "Error guessing", MANUAL, "")

# --- CUS --------------------------------------------------------------------
S = "tests/customer-portal.spec.ts"
tc("TC-CUS-001", "FR-23", "Customer sees own and company-account tickets", "Customer", "Company colleague's ticket exists; default setting.",
   "1. Open My tickets / Company tickets", "-", "Own, watched and company tickets listed; no other companies.", "High", "Positive", "Equivalence partitioning", MANUAL, "",
   "Needs a second customer of the same account.")
tc("TC-CUS-002", "FR-23", "Customer replies from the portal", "Customer", CUST_TKT,
   "1. Open ticket\n2. Post reply", "Reply text", "Reply shown in thread; staff can see it.", "High", "Positive", "Use case", AUTO, S)
tc("TC-CUS-003", "FR-23", "Portal is installable (web app manifest)", "Customer", "-",
   "1. Inspect page for manifest link\n2. Fetch manifest", "-", "Valid manifest with name and icons.", "Low", "Positive", "Use case", AUTO, S)
tc("TC-CUS-004", "NFR-02", "Portal usable on mobile viewport", "Customer", "Viewport 375×812.",
   "1. Sign in on mobile viewport\n2. Open New request", "-", "No horizontal scroll; form usable.", "Medium", "Usability", "Use case", AUTO, S)
tc("TC-CUS-005", "FR-23", "Customer has no access to internal notes tab/filters", "Customer", CUST_TKT,
   "1. Open own ticket\n2. Look for Internal note option", "-", "No internal note composer or filter.", "High", "Security", "Decision table (role × action)", AUTO, S)

# --- KB ---------------------------------------------------------------------
S = "tests/knowledge-base.spec.ts"
tc("TC-KB-001", "FR-24", "Customer reads and votes on a public article", "Customer", "Published public article.",
   "1. Open Knowledge base\n2. Open article\n3. Vote helpful", "-", "Article readable; vote recorded once.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-KB-002", "FR-24", "Customer cannot see draft/internal articles", "Customer", "Draft article exists.",
   "1. Search for the draft title", "-", "Not found.", "Medium", "Security", "Equivalence partitioning", MANUAL, "")
tc("TC-KB-003", "FR-24", "Staff create, edit and delete an article", "Employee", "Staff signed in.",
   "1. Create article\n2. Edit\n3. Delete", "QA-AUTO KB <ts>", "Each operation succeeds.", "Medium", "Positive", "Use case", AUTO, S)
tc("TC-KB-004", "FR-24", "Resolved ticket converted to draft article", "Employee", "Resolved ticket.",
   "1. Choose 'Create article' from ticket", "-", "Draft article created from ticket content.", "Low", "Positive", "Use case", MANUAL, "")

# --- ADM --------------------------------------------------------------------
S = "tests/admin.spec.ts"
tc("TC-ADM-001", "FR-25", "Users screen has no create/invite option", "Manager", "-",
   "1. Open Users", "-", "No Create user / Invite button.", "Medium", "Negative", "Use case", AUTO, S)
tc("TC-ADM-002", "FR-25", "Edit, deactivate and reset a user", "Manager", "Dedicated throw-away user.",
   "1. Change role\n2. Deactivate → user cannot sign in\n3. Reactivate and reset password", "-", "Each action effective and audited.", "Medium", "Positive", "State transition", MANUAL, "",
   "Must not touch shared project accounts.")
tc("TC-ADM-003", "FR-25, FR-08", "Team assignment method configuration", "Manager", "-",
   "1. Set team to round-robin / least-loaded / manual", "-", "Saved and applied to new tickets.", "Medium", "Positive", "Equivalence partitioning", MANUAL, "")
tc("TC-ADM-004", "FR-25, FR-07", "SLA policy target edit applies to new tickets", "Manager", "-",
   "1. Change a target\n2. Create a ticket", "-", "New ticket uses the new target; existing unaffected (confirm with BA).", "Medium", "Positive", "Use case", MANUAL, "")
tc("TC-ADM-005", "FR-25, FR-07", "Business hours and holiday configuration", "Manager", "-",
   "1. Add holiday\n2. Change time zone", "-", "Saved; SLA calculation follows.", "Low", "Positive", "Use case", MANUAL, "")
tc("TC-ADM-006", "FR-25, FR-06", "Priority matrix edit applies to new tickets", "Manager", "-",
   "1. Change one cell\n2. Create ticket with that combination", "-", "New priority used.", "Medium", "Positive", "Decision table", MANUAL, "")
tc("TC-ADM-007", "FR-25", "Categories, ticket types and custom fields configuration", "Manager", "-",
   "1. Add a custom field to Incident\n2. Open new incident form", "-", "Field appears on form.", "Low", "Positive", "Use case", MANUAL, "")
tc("TC-ADM-008", "FR-25", "Automation rule fires on ticket creation", "Manager", "-",
   "1. Rule: on create with category X add tag Y\n2. Create ticket", "-", "Tag Y added; rule execution logged.", "Medium", "Positive", "Decision table", MANUAL, "")
tc("TC-ADM-009", "FR-25, FR-10", "Canned responses available in reply editor", "Employee", "Canned response configured.",
   "1. Insert canned response in reply", "-", "Text inserted.", "Low", "Positive", "Use case", MANUAL, "")
tc("TC-ADM-010", "FR-25, FR-03", "Failed inbound message can be re-queued", "Manager", "Failed message in outbox.",
   "1. Re-queue failed message", "-", "Message reprocessed; ticket created/updated.", "Medium", "Positive", "State transition", MANUAL, "")
tc("TC-ADM-011", "FR-25", "Administration navigation smoke", "Manager", "-",
   "1. Visit each admin menu item", "-", "Every page loads without error and with data.", "High", "Positive", "Use case", AUTO, S)

# --- MT ---------------------------------------------------------------------
tc("TC-MT-001", "FR-26", "Workspace isolation in UI", "Staff of workspace B", "Second workspace with a user.",
   "1. Open workspace A ticket URL as workspace B user", "-", "Not found / denied.", "High", "Security", "Error guessing", MANUAL, "",
   "Requires a second workspace (CLI).")
tc("TC-MT-002", "FR-26", "Workspace isolation in API", "API client", "Tokens for two workspaces.",
   "1. Query workspace A resources with B token", "-", "403/404; no data.", "High", "Security", "Error guessing", MANUAL, "")

# --- CHN --------------------------------------------------------------------
for i, (ch, exp) in enumerate([
    ("Email (webhook/IMAP)", "Ticket created with channel Email and sender as requester."),
    ("Email reply to existing ticket", "Reply threaded into the existing ticket."),
    ("WhatsApp", "Ticket created with channel WhatsApp."),
    ("Monitoring alert webhook", "Incident created with channel Monitoring."),
    ("API", "Ticket created via API with channel API."),
], start=1):
    tc(f"TC-CHN-00{i}", "FR-03", f"Intake via {ch}", "Customer / System", "Channel configured for the workspace.",
       f"1. Send a message via {ch}\n2. Inspect tickets", "-", exp, "High" if i <= 2 else "Medium", "Positive", "Use case", MANUAL, "",
       "Channel endpoints not provided to QA.")
tc("TC-CHN-006", "FR-20, FR-21", "Intake by channel chart reflects sources", "Manager", "Tickets via ≥2 channels.",
   "1. Compare chart with ticket list", "-", "Counts match per channel.", "Low", "Positive", "Data reconciliation", MANUAL, "")

# --- NTF --------------------------------------------------------------------
tc("TC-NTF-001", "FR-27", "Requester acknowledgement on creation", "Customer", "Mailbox access.",
   "1. Create ticket\n2. Check inbox", "-", "Acknowledgement with ticket number.", "Medium", "Positive", "Use case", MANUAL, "")
tc("TC-NTF-002", "FR-27, FR-13", "Resolution email with rating link", "Customer", "Mailbox access.",
   "1. Resolve ticket\n2. Check inbox", "-", "Resolution email with 1–5 rating link.", "Medium", "Positive", "Use case", MANUAL, "")
tc("TC-NTF-003", "FR-27", "Live event stream updates open ticket", "Employee", "Two sessions on same ticket.",
   "1. Post reply in session A\n2. Watch session B", "-", "Session B updates without reload.", "Low", "Positive", "Use case", MANUAL, "")

# --- AI ---------------------------------------------------------------------
for i, (t, e, p) in enumerate([
    ("Similar tickets and articles suggested", "Relevant similar tickets/articles listed.", "Medium"),
    ("Duplicate flagged and merged in one click", "Duplicate flagged; merge keeps history of both.", "Medium"),
    ("Triage suggests category, team, impact, urgency", "Suggestions shown; advisory unless auto-apply on.", "Medium"),
    ("Summary and draft reply generated", "Summary and draft produced; draft editable before sending.", "Low"),
    ("Personal data masked before leaving the system", "Emails/phones masked in outbound LLM payload.", "High"),
    ("Acceptance tracked in 'AI suggestions accepted'", "Metric changes after acceptance.", "Low"),
], start=1):
    tc(f"TC-AI-00{i}", "FR-28", t, "Employee", "Ticket with suitable content.",
       "1. Open ticket AI panel\n2. Exercise the feature", "-", e, p, "Security" if i == 5 else "Positive", "Use case", MANUAL, "",
       "AI output is non-deterministic; manual verification.")

# --- NFR --------------------------------------------------------------------
S = "tests/nfr.spec.ts"
tc("TC-NFR-001", "NFR-01", "Application served over HTTPS only", "Anonymous", "-",
   "1. Request http:// URL", "-", "Redirected to HTTPS or refused.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-NFR-002", "NFR-01", "Session cookie flags", "Any", "Signed in.",
   "1. Inspect session cookie", "-", "Secure and HttpOnly set; SameSite Lax/Strict.", "High", "Security", "Error guessing", AUTO, S)
tc("TC-NFR-003", "NFR-01", "Security response headers", "Anonymous", "-",
   "1. Inspect response headers", "-", "CSP or X-Frame-Options, X-Content-Type-Options present.", "Medium", "Security", "Error guessing", AUTO, S)
tc("TC-NFR-004", "NFR-02", "Dashboard and ticket list load within 3 s", "Manager", "-",
   "1. Measure load time", "-", "≤ 3 s on the test network (ngrok overhead noted).", "Medium", "Performance", "Use case", AUTO, S)
tc("TC-NFR-005", "NFR-02", "Cross-browser smoke (Chromium, Firefox, WebKit/Edge)", "Customer", "-",
   "1. Run AUTH and TKT smoke on each browser project", "-", "Same results on every browser.", "Medium", "Compatibility", "Use case", AUTO, "playwright.config.ts")
tc("TC-NFR-006", "NFR-02", "Accessibility basics on sign-in and new request", "Any", "Screen reader / axe.",
   "1. Run axe scan\n2. Keyboard-only navigation", "-", "No critical issues; all inputs labelled.", "Low", "Usability", "Checklist", MANUAL, "")

# ---------------------------------------------------------------------------
# Credential coverage, verified against the live build on 30-Oct-2026 (JWT role claim):
#   sakthibalaji.m (supplied as "Customer") = employee
#   saraswathi.karunanidhi (supplied as "Agent") = team_lead
#   sivasrigananapathi.sundaram (supplied as "Admin"/"Manager") = manager
# No customer and no Super admin login exist, so those cases are blocked.
# ---------------------------------------------------------------------------
CUSTOMER_ONLY = {
    "TC-AUTH-001", "TC-CHG-001", "TC-CUS-002", "TC-CUS-003", "TC-CUS-004", "TC-CUS-005", "TC-KB-001",
    "TC-WRK-001", "TC-WRK-002", "TC-WRK-005", "TC-WRK-006", "TC-INC-005", "TC-INC-006", "TC-INC-008",
    "TC-INC-009", "TC-WAIT-002", "TC-PRI-004", "TC-RBAC-001", "TC-RBAC-002", "TC-RBAC-008",
    "TC-REQ-003", "TC-REQ-004", "TC-TKT-001", "TC-TKT-002", "TC-TKT-003",
}
NO_CUSTOMER_NOTE = "No customer login available: the 'Customer' credential supplied is an Employee account. Scenario tagged @customer and skipped until one is provided."
for c in TEST_CASES:
    if c["id"] in CUSTOMER_ONLY and c["automation"] == AUTO:
        c["automation"], c["note"] = BLOCKED, NO_CUSTOMER_NOTE
    if c["id"] in {"TC-TKT-004", "TC-TKT-005", "TC-TKT-007", "TC-TKT-010", "TC-TKT-011"}:
        c["note"] = "Automated as the Employee: the new-ticket form is shared by all roles; repeat as a customer when a login exists."
    if c["id"] == "TC-RBAC-005":  # the "Agent" login is a Team lead
        c["automation"], c["note"] = AUTO, "Runs with saraswathi.karunanidhi (team_lead)."

SUPER_ADMIN_ONLY = {"TC-RBAC-007", "TC-RBAC-010", "TC-AUD-002", "TC-AUD-003"} | {
    c["id"] for c in TEST_CASES if c["module"] == "ADM"}
NO_SUPERADMIN_NOTE = "No Super admin credential supplied (shared admin login is a Manager) — set OPSDESK_SUPERADMIN_* in .env."
for c in TEST_CASES:
    if c["id"] in SUPER_ADMIN_ONLY:
        c["role"] = "Super admin"
        c["pre"] = c["pre"].replace("Manager signed in", "Super admin signed in")
        if c["automation"] == AUTO:
            c["automation"], c["note"] = BLOCKED, NO_SUPERADMIN_NOTE
    c["role"] = c["role"].replace("Super admin → Employee", "Manager → Employee")
    # Automation is Playwright + Cucumber BDD: point each case at its feature file.
    if c["spec"].startswith("tests/"):
        c["spec"] = "features/" + c["spec"][len("tests/"):].replace(".spec.ts", ".feature")
        if c["module"] == "REQ":
            c["spec"] = "features/service-request.feature"
    elif c["spec"] == "playwright.config.ts":
        c["spec"] = "@smoke scenarios with BROWSER=firefox / msedge"

# ---------------------------------------------------------------------------
# Functional tags: each automated scenario is tagged with the functionality it tests
# (first tag on the scenario), alongside its @TC id. Run one with e.g.
#   npx cucumber-js --tags "@logout"
# ---------------------------------------------------------------------------
FEATURE_TAGS = {
    "admin.feature": "@administration",
    "assignment.feature": "@routing_and_assignment",
    "audit.feature": "@history_and_audit",
    "auth.feature": "@authentication",
    "change.feature": "@change_lifecycle",
    "customer-portal.feature": "@customer_portal",
    "dashboard.feature": "@dashboard",
    "knowledge-base.feature": "@knowledge_base",
    "lifecycle.feature": "@ticket_lifecycle",
    "major-incident.feature": "@major_incident",
    "nfr.feature": "@non_functional",
    "priority.feature": "@priority_calculation",
    "rbac.feature": "@role_based_access",
    "reports.feature": "@report_export",
    "service-request.feature": "@service_request_lifecycle",
    "sla.feature": "@sla_timers",
    "tickets.feature": "@ticket_creation",
}

FUNCTION_TAGS = {
    # authentication
    "TC-AUTH-001": "@customer_login", "TC-AUTH-002": "@employee_login", "TC-AUTH-003": "@manager_login",
    "TC-AUTH-004": "@invalid_password_login", "TC-AUTH-005": "@user_enumeration_check",
    "TC-AUTH-006": "@login_form_validation", "TC-AUTH-008": "@logout",
    "TC-AUTH-009": "@protected_page_redirect", "TC-AUTH-011": "@email_case_insensitive_login",
    # role-based access
    "TC-RBAC-001": "@customer_dashboard_access", "TC-RBAC-002": "@customer_admin_access",
    "TC-RBAC-003": "@employee_admin_access", "TC-RBAC-012": "@manager_admin_access",
    "TC-RBAC-004": "@employee_ticket_visibility", "TC-RBAC-005": "@team_lead_ticket_visibility",
    "TC-RBAC-006": "@manager_unassigned_visibility", "TC-RBAC-007": "@super_admin_console_access",
    "TC-RBAC-008": "@customer_ticket_url_tampering", "TC-RBAC-009": "@employee_ticket_url_tampering",
    "TC-RBAC-010": "@super_admin_account_protection",
    # ticket creation
    "TC-TKT-001": "@raise_incident", "TC-TKT-002": "@raise_service_request",
    "TC-TKT-003": "@customer_ticket_types", "TC-TKT-004": "@incident_form_fields",
    "TC-TKT-005": "@service_request_form_fields", "TC-TKT-006": "@raise_change",
    "TC-TKT-007": "@mandatory_field_validation", "TC-TKT-010": "@kb_suggestions_while_typing",
    "TC-TKT-011": "@xss_protection", "TC-TKT-012": "@ticket_numbering",
    # priority / SLA
    "TC-PRI-001": "@priority_matrix", "TC-PRI-002": "@priority_boundaries",
    "TC-PRI-003": "@priority_override", "TC-PRI-004": "@customer_priority_restriction",
    "TC-SLA-005": "@change_has_no_sla", "TC-SLA-008": "@first_response_sla",
    # support work, waiting states, incident workflow
    "TC-WRK-001": "@public_reply", "TC-WRK-002": "@internal_note_privacy", "TC-WRK-003": "@file_attachment",
    "TC-WRK-004": "@ticket_field_edit", "TC-WRK-005": "@customer_edit_subject",
    "TC-WRK-006": "@customer_field_restriction",
    "TC-WAIT-001": "@waiting_on_customer_sla_pause", "TC-WAIT-002": "@customer_reply_resumes_work",
    "TC-WAIT-003": "@waiting_on_third_party",
    "TC-INC-001": "@start_work", "TC-INC-002": "@resolve_validation", "TC-INC-003": "@resolve_incident",
    "TC-INC-004": "@resolve_from_new", "TC-INC-005": "@confirm_closure", "TC-INC-006": "@reopen_incident",
    "TC-INC-007": "@cancel_with_comment", "TC-INC-008": "@customer_cannot_cancel",
    "TC-INC-009": "@closed_ticket_transitions",
    # service request / change / major incident
    "TC-REQ-001": "@fulfil_without_approval", "TC-REQ-002": "@fulfil_validation",
    "TC-REQ-003": "@fulfil_and_close_request", "TC-REQ-004": "@reopen_request", "TC-REQ-005": "@reject_request",
    "TC-CHG-001": "@change_form_access", "TC-CHG-002": "@change_assessment_gate",
    "TC-CHG-003": "@change_cab_gate", "TC-CHG-006": "@change_reject_close_permission",
    "TC-MI-001": "@declare_major_incident", "TC-MI-002": "@major_incident_permission",
    # assignment / audit
    "TC-ASG-001": "@auto_routing_by_category", "TC-ASG-002": "@unassigned_queue_routing",
    "TC-ASG-006": "@assignee_filtered_by_team", "TC-ASG-007": "@manual_assignment",
    "TC-ASG-008": "@assignment_history",
    "TC-AUD-001": "@ticket_history", "TC-AUD-002": "@audit_log_search",
    "TC-AUD-003": "@audit_log_tamper_proof", "TC-AUD-005": "@audit_log_access",
    # dashboard / reports
    "TC-DSH-001": "@dashboard_kpi_cards", "TC-DSH-002": "@dashboard_period_filter",
    "TC-DSH-003": "@dashboard_account_filter", "TC-DSH-004": "@dashboard_common_charts",
    "TC-DSH-005": "@dashboard_lead_charts", "TC-DSH-006": "@dashboard_lead_charts_hidden",
    "TC-RPT-001": "@export_overview_report", "TC-RPT-002": "@export_tickets_report",
    "TC-RPT-003": "@export_major_incidents_report", "TC-RPT-004": "@export_team_workload_report",
    "TC-RPT-005": "@export_visibility",
    # customer portal / KB / admin
    "TC-CUS-002": "@customer_portal_reply", "TC-CUS-003": "@pwa_install", "TC-CUS-004": "@mobile_layout",
    "TC-CUS-005": "@customer_no_internal_note",
    "TC-KB-001": "@kb_read_and_vote", "TC-KB-003": "@kb_article_management",
    "TC-ADM-001": "@user_admin_no_create", "TC-ADM-011": "@admin_pages_load",
    # non-functional
    "TC-NFR-001": "@https_enforced", "TC-NFR-002": "@session_token_security",
    "TC-NFR-003": "@security_headers", "TC-NFR-004": "@page_load_performance",
}

for c in TEST_CASES:
    if c["id"] in FUNCTION_TAGS and c["spec"].startswith("features/"):
        c["spec"] = f'{c["spec"]} {FUNCTION_TAGS[c["id"]]}'

# ---------------------------------------------------------------------------
# Design-technique artefacts
# ---------------------------------------------------------------------------
def priority_for(impact, urgency):
    s = impact + urgency
    return "P1" if s <= 3 else "P2" if s == 4 else "P3" if s <= 6 else "P4"


PRIORITY_DECISION_TABLE = [(i, u, i + u, priority_for(i, u)) for i in range(1, 5) for u in range(1, 5)]

SLA_TARGETS = [
    # priority, std response, std resolution, premium response, premium resolution
    ("P1", "15 min", "4 h", "10 min", "2 h"),
    ("P2", "30 min", "9 h", "30 min", "6 h"),
    ("P3", "4 h", "27 h", "2 h", "24 h"),
    ("P4", "8 h", "45 h", "4 h", "48 h"),
]

INCIDENT_TRANSITIONS = [
    # from, action, to, allowed roles, guard, covered by
    ("New", "Start work", "In progress", "Employee, Team lead, Manager", "-", "TC-INC-001"),
    ("In progress", "Ask customer", "Waiting on customer", "Staff", "SLA pauses", "TC-WAIT-001"),
    ("Waiting on customer", "Customer reply", "In progress", "Customer (automatic)", "SLA resumes", "TC-WAIT-002"),
    ("In progress", "Wait on third party", "Waiting on third party", "Staff", "SLA keeps running", "TC-WAIT-003"),
    ("Any open state", "Resolve", "Resolved", "Staff", "Resolution code + notes required", "TC-INC-002/003/004"),
    ("Any open state", "Cancel", "Cancelled", "Employee, Team lead, Manager", "Comment required", "TC-INC-007"),
    ("Resolved", "Confirm close", "Closed", "Customer", "-", "TC-INC-005"),
    ("Resolved", "Reopen", "In progress", "Customer", "-", "TC-INC-006"),
    ("Resolved", "5 days elapse", "Closed", "System (hourly)", "Workspace setting", "TC-INC-010"),
    ("Closed", "Start work / Resolve", "(not allowed)", "-", "Invalid transition", "TC-INC-009"),
]

ROLE_MATRIX = [
    # capability, Customer, Employee, Team lead, Manager, Super admin, covered by
    ("Raise Incident / Service Request", "Y", "Y", "Y", "Y", "Y", "TC-TKT-001/002"),
    ("Raise Change", "N", "Y", "Y", "Y", "Y", "TC-TKT-003/006, TC-CHG-001"),
    ("See unassigned tickets", "N", "N", "Y", "Y", "Y", "TC-RBAC-004/005/006"),
    ("See internal notes", "N", "Y", "Y", "Y", "Y", "TC-WRK-002, TC-CUS-005"),
    ("Dashboard", "N", "Own data", "Full", "Full", "Full", "TC-RBAC-001, TC-DSH-*"),
    ("Accounts this period / Open by team", "N", "N", "Y", "Y", "Y", "TC-DSH-005/006"),
    ("Exports", "N", "Own data", "Y", "Y", "Y", "TC-RPT-*"),
    ("Assign / reassign", "N", "-", "Y", "Y", "Y", "TC-ASG-007/008"),
    ("Declare major incident", "N", "N", "Y", "Y", "Y", "TC-MI-001/002"),
    ("Reject request / change, close problem / change", "N", "N", "Y", "Y", "Y", "TC-REQ-005/006, TC-CHG-006, TC-PRB-003"),
    ("Cancel ticket", "N", "Y", "Y", "Y", "Y", "TC-INC-007/008"),
    ("Administration / audit log", "N", "N", "N", "N", "Y", "TC-RBAC-002/003/007, TC-AUD-005"),
]
