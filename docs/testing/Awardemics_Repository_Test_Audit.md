# Awardemics — Repository-aligned test audit

**Reviewed:** 2026-11-10  
**Source:** https://github.com/Jnat2nd/Awardemics, default branch `main`  
**Target deployment (provided by project owner):** https://faststarter-9c75.onrender.com/  
**Verification status:** Repository source inspected. Live Render HTTP requests could not be performed from this environment; all deployment outcomes remain **NOT RUN**. Confirm the Render deploy commit matches the reviewed `main` before execution.

## Architecture

- FastAPI with Jinja2 server-side HTML views; SQLModel models / SQLAlchemy sessions; Render PostgreSQL in the blueprint; SQLite is the local default from the starter README.
- Code layers are `app/routers/`, `app/services/`, `app/repositories/`, `app/models/`, `app/templates/`.
- `requirements.txt` already includes `pytest==9.1.1`, `pytest-asyncio==1.4.0`, and `httpx==0.28.1`.
- There is no `tests/` directory on the reviewed branch.
- Application-level authentication is a JWT in the HTTP-only cookie named `access_token`; `POST /login` accepts `application/x-www-form-urlencoded` (`username`, `password`) and responds with a `303` redirect on success.
- `GET /api/users` is the sole JSON endpoint discovered under `/api`; it lists `id`, `username`, `email` without an authentication dependency. This is outside the three core workflows but deserves a privacy/security review. Do not assume `/api/events`, `/api/registrations`, or `/api/leaderboard` exist.

## Real route-to-workflow mapping

| Workflow | Method + URL | Input | Output / auth | Source |
|---|---|---|---|---|
| Public home | GET `/` | — | HTML, public | `app/routers/index.py` |
| Browse events | GET `/app` | Optional `search` | HTML, signed-in | `app/routers/user_home.py` |
| Lookup event / form | GET `/volunteer` | Optional `event_id`, `search` | HTML, signed-in; unknown `event_id` -> 404 | `app/routers/volunteer.py` |
| Register | POST `/volunteer` | Form: `event_id` int, `hours` int | HTML confirmation 200 or error form 400; signed-in | `app/routers/volunteer.py` |
| List registrations | GET `/registered-events` | — | HTML, signed-in | `app/routers/registered_events.py` |
| Unregister | POST `/registered-events/{event_id}/unregister` | Path `event_id` | 303 redirect; signed-in | `app/routers/registered_events.py` |
| Leaderboard | GET `/leaderboard` | `search`, `faculty`, `sort_by`, `sort_order` | HTML, public | `app/routers/leaderboard.py` |
| Log in | POST `/login` | Form `username`, `password` | 303 and access-token cookie on success | `app/routers/login.py` |
| Health | GET `/health` | — | JSON `{"ok": true}` | `app/main.py` |
| Users API (out of scope) | GET `/api/users` | — | JSON users array | `app/routers/users.py` |

## ERD and wireframe checks

| Area | Confirmed behaviour | UAT implication |
|---|---|---|
| Event browse | `/app` shows event cards, search, event-details Bootstrap modals; `Volunteer` links to `/volunteer?event_id=...` | Test modal and prefilled selection instead of assuming a separate details page. Mark the wireframe variation. |
| Registration | `/volunteer` form takes `event_id` (hidden) and `hours`; `RegisteredEventService.register` accepts `details` but router always passes empty string | Wireframe's event-specific-details input is **absent**; record missing feature separately rather than claiming a test passed. |
| Confirmation | `volunteer-confirmation.html` is a full page showing Event ID but not Student ID | Wireframe's success modal and Student ID are **not implemented** as drawn. |
| Leaderboard | `/leaderboard` filters by `faculty` (exact match) and `search` (case-insensitive partial name), sorts by rank/name/faculty/hours/awards using `sort_by`, `sort_order` | Test the actual query names, table and student modal; do not invent JSON API. |
| Leaderboard storage | Repository selects from `Student`; there is no SQLModel `Leaderboard` model | Derived leaderboard; evaluate behavior rather than demanding separate `LEADERBOARD` table. |
| Duplicate registration | `RegisteredEvent` has composite `(eventID, studentID)` primary key; service also checks prior registration | Test duplicate rejection and no extra slot consumption. |
| Student identity | Registration derives `studentID` by `Student.userID == authenticated User.id`; account signup does not make a Student row | Use a linked test student, not merely a newly created user. |
| Capacity | Service rejects `numberRegistered >= numberOfSlots`; increments count before repository commit | Unit + DB integration tests should verify counts. A true concurrent last-slot test is not yet proven safe/atomic. |
| Hours | Valid integers are `1..event.hours` inclusive | Test 0, 1, maximum, maximum+1; do not assume decimals are accepted. |
| Event eligibility | `list_upcoming()` currently neither filters by date/status nor does `register()` check `eventStatus` or date | If requirements exclude past/cancelled events, record as potential defect and obtain requirement decision; do not silently change source. |
| Earned hours | `register()` does not update `Student.totalHours` | Correct distinction unless new requirements explicitly demand immediate credit. |
| Authentication | Student actions depend on `access_token` cookie; current 401 exception handler returns an HTML template without explicitly setting response status | Assert blocked access/content, and observe/document actual status rather than assuming it is 401. |

## Core updated test cases (execution pending)

The original `Student_Awards_Test_Plans.md` remains a **requirements-based baseline**. Use these repo-aligned cases for execution and use the baseline to track wireframe deviations.

| ID | Level | Preconditions / setup | Action | Observable pass criterion |
|---|---|---|---|---|
| UAT-EV-01 | UAT | Authenticated student, seeded events | Browse `/app`, click View details | Event modal shows selected ID, description, organisation, location, hours, status and spots left; Volunteer link preserves ID |
| UAT-EV-02 | UAT | Events with distinct names | Search by name/location/organisation, clear | Matching cards and empty state work; clearing restores list |
| UAT-RG-01 | UAT | Linked student, event with free slots | Open Volunteer from event modal | Correct selected Event ID is retained and hours field shown |
| UAT-RG-02 | UAT | Linked student, event with free slots | Submit valid hours | Registration Complete page appears; Event ID correct; registration appears under Registered Events |
| UAT-RG-03 | UAT | Already registered student | Resubmit same event | Error shown; second registration/slot is not created |
| UAT-RG-04 | UAT | Full event | Attempt registration | Rejection and no overbooking |
| UAT-RG-05 | UAT | Selected event | Enter hours 0 and > event.hours | Error shown; no record added |
| UAT-RG-06 | UAT | Student on volunteer page | Clear, Cancel, then confirm View registered events | Clear resets; Cancel returns to browsing; confirmation links navigate correctly |
| UAT-RG-07 | UAT | Wireframe as acceptance baseline | Inspect event-specific details / Student ID / modal | Record missing details field and confirmation variations as deviations (not automatic pass) |
| UAT-LB-01 | UAT | Signed out, seeded students | Visit `/leaderboard` | Public table accessible; rank/name/faculty/hours/awards visible |
| UAT-LB-02 | UAT | Students across faculties | Search, faculty filter, combined filter, clear | Expected matching rows and empty state; no unrelated students |
| UAT-LB-03 | UAT | Students with varied hours/ranks | Sort by hours ascending/descending | Numeric order matches selected sort direction |
| UAT-LB-04 | UAT | Known student | Click table row | Correct student modal with faculty/rank/total hours/latest event/latest award |
| UT-RG-01 | Unit | Mock repositories | Register unknown event | ValueError; no insert |
| UT-RG-02 | Unit | Mock repositories, no student link | Register | ValueError; no insert |
| UT-RG-03 | Unit | Mock repos, duplicate | Register | ValueError; no insert / slot increment |
| UT-RG-04 | Unit | Mock repos, full event | Register | ValueError; no insert / slot increment |
| UT-RG-05 | Unit | Mock repos, available event | Parametrize hours 0, 1, max, max+1 | Appropriate rejection / persistence and event count |
| UT-RG-06 | Unit | Mock repos, valid event | Register | Correct event/student/date/hours/details mapping; does not change Student.totalHours |
| UT-RG-07 | Unit | Mock repos | Unregister existing / absent | Removes registration and decrements count only once; absent returns False |
| UT-EV-01 | Unit | Mock volunteer repository | Search numeric ID vs text | Numeric uses get_by_id; text uses list_upcoming; no result returns [] |
| UT-EV-02 | Unit | Mock volunteer repository | find_event numeric/name | Correct lookup and trimming |
| UT-LB-01 | Unit | Mock leaderboard repository | search/faculty/order inputs | Service trims search and faculty and delegates valid values |
| IT-EV-01 | Integration | TestClient, disposable DB, seeded events | GET `/app` authenticated, query search | Real HTML shows seeded matching events; query selects right rows |
| IT-RG-01 | Integration | Linked authenticated user, empty registration, event slots | POST `/volunteer`, then GET `/registered-events` | One persisted `(eventID, studentID)` with count increased exactly once |
| IT-RG-02 | Integration | Prior registration | Re-POST `/volunteer` | 400 HTML and single DB row/count unchanged |
| IT-RG-03 | Integration | Full or invalid event | POST `/volunteer` | Rejected; no registration; no slot increment |
| IT-RG-04 | Integration | Two students, separate auth | Try direct unauthorized access | Cannot register as another student's identity; public leaderboard remains public |
| IT-RG-05 | Integration | Valid prior registration | POST `/registered-events/{id}/unregister` | 303, registration deleted, event capacity restored |
| IT-LB-01 | Integration | Three students across faculties | GET `/leaderboard` query params | Real HTML rows correspond to filtering/sorting from DB |
| IT-LB-02 | Integration | Signed-out client | GET `/leaderboard` | Accessible with no token; student modal renders; private registration details not exposed |

**Execution record fields:** Test ID, Tester, Date, Environment, Preconditions, Input/Test Data, Expected Result, Actual Result, Pass/Fail/Blocked, Screenshot/Log URL, Defect ID.

## Test setup and isolation rules

1. Create `tests/unit/` and `tests/integration/`. Configure a dedicated SQLModel SQLite DB for local integration tests. Override the `get_session` FastAPI dependency with the test session and restore the override in teardown. Populate `User` + linked `Student` + `VolunteerEvent` fixtures; only users with a linked student can register.
2. `app/database.py` binds an engine at import time. Use temporary DB fixture configuration carefully; never run `python manage.py init` without safe DB selection (the default drops tables).
3. For unit tests, instantiate real services with fake repositories / Mock objects, no database/network. Assert calls and side effects; test service rules, not template pixel positions.
4. For integration tests, use FastAPI `TestClient` or `httpx` with cookie authentication and a real SQLite/Postgres disposable test DB. Test DB count, composite keys and HTML content in the same test. Use fixtures to avoid cross-test state.
5. For Postman, remember these are mostly **HTML form endpoint tests**, not JSON resource API tests. Postman can test HTTP state and HTML strings, but UAT browser modal interactions remain manual. Do not label `/volunteer` a JSON API endpoint.
6. Separate the Render smoke/regression collection from tests that write registrations. Log in to the disposable Render environment using a user linked to `Student`. Stop redirects on login to inspect the `303`/cookie. Keep credentials uncommitted.
7. Compare commit SHA of Render deployment to reviewed GitHub `main` before interpreting remote results.

## Acceptance decisions / likely gaps

- G-01: Wireframe Event Details standalone page vs implemented modal.
- G-02: Registration-specific-details textarea absent in HTML despite model field.
- G-03: Wireframe success modal with Student ID vs actual confirmation page with Event ID only.
- G-04: Approval required for filtering out inactive/past events, because code does not implement that policy.
- G-05: Atomic capacity enforcement is not demonstrated for simultaneous final-slot registrations; use a true concurrency test before making a guarantee.
- G-06: Signup does not create a linked Student row. Use seeded/test student for registration; decide if general signups should become students.
- G-07: Verify unauthenticated HTTP status and render behaviour; 401 handler may serve HTML with status 200.
- G-08: Out-of-scope `GET /api/users` exposes user email fields without an auth dependency; review if appropriate before deploying to non-test users.
