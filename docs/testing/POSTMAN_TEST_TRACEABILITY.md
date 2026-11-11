# Postman test traceability

**Collection:** `Awardemics - Render HTML/Form QA (v2.1)`  
**Target:** `https://faststarter-9c75.onrender.com`  
**Checked-out source review:** 2026-11-10  
**Live execution:** **NOT RUN** — Render access was unavailable from the authoring environment and the deployed commit was not confirmed to match this checkout.

Every request has Postman post-response JavaScript using `pm.test` and
`pm.expect`. HTML responses are inspected as text, never parsed as JSON. The
custom unauthorised handler may render HTTP 200, so anonymous protected-route
checks assert the session-expired page and absence of protected form content.

| Test ID | Request | Workflow / requirement | Expected checks | Actual run result |
|---|---|---|---|---|
| API-SM-01 | Health is healthy | Public health contract | 200, JSON, `ok: true` | NOT RUN |
| API-LB-01 | Public leaderboard | UAT-LB-01 | 200 HTML, table, name/faculty/hours/awards markers | NOT RUN |
| API-LB-02 | Student name search | UAT-LB-02 | 200 HTML; every returned row contains `searchTerm` in name | NOT RUN |
| API-LB-03 | Faculty filter | UAT-LB-02 | 200 HTML; every returned row has selected faculty | NOT RUN |
| API-LB-04 | Sort by hours descending | UAT-LB-03 | 200 HTML; numeric hours are descending | NOT RUN |
| API-LB-05 | No-match search | UAT-LB-02 | 200 HTML; `No students match those filters.` | NOT RUN |
| API-EV-01 | Anonymous registration access blocked | IT-RG-04 | HTML session-expired page; no hours form; no redirect assumption | NOT RUN |
| AUTH-01 | Login (cookie + redirect) | Authentication prerequisite | 303; authenticated-home `Location`; `Set-Cookie: access_token` and HttpOnly | NOT RUN |
| API-EV-02 | Browse event cards | UAT-EV-01 / IT-EV-01 | 200 HTML; event-browser/search/view-details markers; optional expected event | NOT RUN |
| API-EV-03 | Search event cards | UAT-EV-02 | 200 HTML; search interface and configured matching event | NOT RUN |
| API-EV-04 | Selected event form prefilled | UAT-RG-01 | 200 HTML; selected hidden `event_id`; hours field | NOT RUN |
| API-EV-05 | Unknown event returns 404 | IT-RG-01 | 404 JSON; `detail` equals `Volunteer event not found.` | NOT RUN |
| API-RG-01 | Reject zero volunteer hours | UAT-RG-05 / IT-RG-03 | 400 HTML; hours-range error | NOT RUN |
| API-RG-02 | Reject non-existent event registration | IT-RG-03 | 400 HTML; selected-event-does-not-exist error | NOT RUN |
| API-RG-03 | Full event registration blocked | UAT-RG-04 / IT-RG-03 | 400 HTML; full-capacity error; requires `fullEventID` fixture | BLOCKED |
| API-RG-04 | Successful registration | UAT-RG-02 / IT-RG-01 | 200 HTML confirmation; event ID; registered-events link | NOT RUN |
| API-RG-05 | Registration appears in account | UAT-RG-02 | 200 HTML; selected event ID appears in registered list | NOT RUN |
| API-RG-06 | Duplicate registration rejected | UAT-RG-03 / IT-RG-02 | 400 HTML; duplicate error; no second registration | NOT RUN |
| API-RG-07 | Unregister restores availability | UAT-RG-06 / IT-RG-05 | 303; `Location` targets `/registered-events` | NOT RUN |
| API-RG-08 | Registration absent after unregister | IT-RG-05 | 200 HTML; selected event ID absent from registrations | NOT RUN |

`API-RG-03` is listed as **BLOCKED** for fixture readiness in addition to the
overall live run being NOT RUN. Before execution, change it to NOT RUN if a
verified full event fixture is available but the deployment remains unreachable.
Do not mark it PASS merely because a placeholder ID is present.

## Known implementation boundaries

- The route contracts are HTML/form contracts, not fictional JSON APIs.
- `/volunteer` accepts only `event_id` and `hours`; this collection sends no
  `studentID` or `details`.
- Registration identity is derived from the authenticated user's linked
  `Student` row.
- `fullEventID` and `eventID` both map to `VolunteerEvent.eventID`.
- Browser-only modal interactions are not asserted by Postman.
- The Render-deployed commit must be compared with the checked-out commit before
  interpreting live results.
