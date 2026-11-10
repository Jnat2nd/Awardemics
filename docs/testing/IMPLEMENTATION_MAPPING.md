# Awardemics implementation mapping

Reviewed against the checked-out branch on 2026-11-10. This document maps every
UAT, UT, and IT case in
[`Awardemics_Repository_Test_Audit.md`](./Awardemics_Repository_Test_Audit.md)
to the current implementation. It is a test-design artifact only: no tests or
application code are added by this change.

## Route inventory

| Route | Current implementation | Auth / response |
|---|---|---|
| `GET /app?search=` | `user_home_view` in [`app/routers/user_home.py`](../../app/routers/user_home.py#L10) calls `VolunteerEventService.browse_events` | `AuthDep`; Jinja HTML |
| `GET /volunteer?event_id=` | `volunteer_view` in [`app/routers/volunteer.py`](../../app/routers/volunteer.py#L14) calls `find_event` | `AuthDep`; Jinja HTML; unknown ID is 404 |
| `POST /volunteer` | `volunteer_action` in [`app/routers/volunteer.py`](../../app/routers/volunteer.py#L41) calls `RegisteredEventService.register` | `AuthDep`; form HTML confirmation or 400 HTML |
| `GET /registered-events` | `registered_events_view` in [`app/routers/registered_events.py`](../../app/routers/registered_events.py#L13) calls `list_for_user` | `AuthDep`; Jinja HTML |
| `POST /registered-events/{event_id}/unregister` | `unregister_event_action` in [`app/routers/registered_events.py`](../../app/routers/registered_events.py#L31) calls `unregister` | `AuthDep`; 303 redirect |
| `GET /leaderboard?search=&faculty=&sort_by=&sort_order=` | `leaderboard_view` in [`app/routers/leaderboard.py`](../../app/routers/leaderboard.py#L12) calls `view_leaderboard` and `list_faculties` | Public; Jinja HTML |
| `POST /login` | `login_action_ajax` in [`app/routers/login.py`](../../app/routers/login.py#L19) calls `AuthService.authenticate_user` | Form; success is 303 and sets `access_token` |
| `GET /health` | `health` in [`app/main.py`](../../app/main.py#L57) | Public JSON `{"ok": true}` |

`SessionDep` is an `Annotated` dependency bound to
[`app.database.get_session`](../../app/dependencies/session.py#L6), not directly
to the module-level engine. The only JSON API found under `/api` is
`GET /api/users` in [`app/routers/users.py`](../../app/routers/users.py#L12).
No `/api/events`, `/api/registrations`, or `/api/leaderboard` was found.

## Case mapping

Status meanings:

- **Verified implementation**: the route/method exists and its observable
  behavior is supported by the source.
- **Requirement deviation**: the requested or wireframe behavior differs from
  the implementation; execute the test to document the actual result.
- **Unimplemented behavior**: no source path implements the required behavior.

### UAT cases

| ID | Source mapping | Status and test boundary |
|---|---|---|
| UAT-EV-01 | `GET /app` → `user_home_view` → `VolunteerEventService.browse_events`; [`app/templates/app.html`](../../app/templates/app.html) renders cards, modal fields, and Volunteer link | **Verified implementation** for the modal/card behavior. |
| UAT-EV-02 | `browse_events` → `VolunteerEventRepository.list_upcoming` in [`app/repositories/volunteer_event.py`](../../app/repositories/volunteer_event.py#L10) filters name, location, and organisation; template has clear/empty states | **Verified implementation**. |
| UAT-RG-01 | `GET /volunteer` → `volunteer_view` → `find_event`; [`app/templates/volunteer.html`](../../app/templates/volunteer.html) retains hidden `event_id` and displays hours | **Verified implementation**. |
| UAT-RG-02 | `POST /volunteer` → `volunteer_action` → `RegisteredEventService.register` → repositories; confirmation is [`app/templates/volunteer-confirmation.html`](../../app/templates/volunteer-confirmation.html) and list is `GET /registered-events` | **Verified implementation** for registration, persistence, and navigation. |
| UAT-RG-03 | `register` checks `exists_for_student_event` before increment/create | **Verified implementation**; test row and event count remain unchanged. |
| UAT-RG-04 | `register` rejects `numberRegistered >= numberOfSlots` | **Verified implementation** for sequential requests; atomic concurrent safety is not implemented/proven. |
| UAT-RG-05 | `register` enforces `1 <= hours <= event.hours`; router receives integer form data | **Verified implementation** for integer bounds. |
| UAT-RG-06 | `volunteer.html` implements Clear/Cancel; confirmation template links to registered events and events | **Verified implementation** for the rendered links. |
| UAT-RG-07 | Model has `eventSpecificDetails`, but router passes `""`; confirmation renders Event ID only | **Requirement deviation / unimplemented behavior**: no details field, no Student ID, and confirmation is a page rather than the wireframe modal. |
| UAT-LB-01 | Public `GET /leaderboard` → `LeaderboardService.view_leaderboard`; template renders rank/name/faculty/hours/awards | **Verified implementation**. |
| UAT-LB-02 | `LeaderboardRepository.list_students` applies exact faculty and case-insensitive partial name filters | **Verified implementation**; empty-state template is present. |
| UAT-LB-03 | `list_students` supports rank/name/faculty/hours/awards and asc/desc expressions | **Verified implementation** for supported values; invalid `sort_by` falls back to rank. |
| UAT-LB-04 | Leaderboard table rows open modal containing faculty/rank/hours/latest event/latest award | **Verified implementation**. |

### Unit cases

| ID | Exact method(s) | Status |
|---|---|---|
| UT-RG-01 | `RegisteredEventService.register` unknown-event branch; `VolunteerEventRepository.get_by_id` | **Verified implementation**: raises `ValueError`, before create. |
| UT-RG-02 | `RegisteredEventService.register` `student_id_for_user` branch | **Verified implementation**: raises `ValueError`, before create. |
| UT-RG-03 | `register` duplicate branch; `RegisteredEventRepository.exists_for_student_event` | **Verified implementation**: raises before increment/create. |
| UT-RG-04 | `register` full-capacity branch | **Verified implementation**: raises before increment/create. |
| UT-RG-05 | `register` hours range branch | **Verified implementation**: raises before increment/create. |
| UT-RG-06 | `register` event mutation, `RegisteredEvent` construction, repository `create` | **Verified implementation** for event/student/date/hours/details mapping; it intentionally does not update `Student.totalHours`. |
| UT-RG-07 | `RegisteredEventService.unregister`; repository `get_for_student`, `delete`, event `save` | **Verified implementation** for existing and absent registrations; decrement is bounded at zero. |
| UT-EV-01 | `VolunteerEventService.browse_events` numeric branch vs text branch | **Verified implementation**: numeric input uses `get_by_id`; text uses `list_upcoming`; missing numeric event returns `[]`. |
| UT-EV-02 | `VolunteerEventService.find_event` → `VolunteerEventRepository.find_by_reference` | **Verified implementation** for trimming, numeric ID, and exact name lookup. |
| UT-LB-01 | `LeaderboardService.view_leaderboard` → `LeaderboardRepository.list_students` and `list_faculties` | **Verified implementation**: search/faculty are trimmed and all sort arguments are delegated. |

### Integration cases

| ID | Route and persistence path | Status / required assertion |
|---|---|---|
| IT-EV-01 | `GET /app` → event repository query → rendered `app.html` | **Verified implementation**; assert matching HTML and absence of non-matching event. |
| IT-RG-01 | `POST /volunteer` → `register` → `RegisteredEventRepository.create` and event save, then `GET /registered-events` | **Verified implementation**; assert one composite-key row and one count increment. |
| IT-RG-02 | Repeat `POST /volunteer` → duplicate branch | **Verified implementation**; assert 400 HTML, one row, unchanged count. |
| IT-RG-03 | `POST /volunteer` with full/invalid event → `register` rejection | **Verified implementation**; assert no row and unchanged count. |
| IT-RG-04 | Auth identity comes from `access_token` → `get_current_user` → `UserRepository.get_by_id`; leaderboard has `IsUserLoggedIn` only | **Verified implementation** for identity scoping and public leaderboard. Cross-user attempts must be made with separate cookie-bearing clients. |
| IT-RG-05 | `POST /registered-events/{id}/unregister` → `unregister` → delete and event decrement → 303 | **Verified implementation**; assert response location, deletion, and restored capacity. |
| IT-LB-01 | `GET /leaderboard` → `LeaderboardRepository.list_students` with all query parameters | **Verified implementation**; assert DB-backed filter/sort order in HTML. |
| IT-LB-02 | Signed-out `GET /leaderboard`; `is_logged_in` returns false without a cookie | **Verified implementation** for public access and student modal; no registration data is queried. |

## Isolated fixture design

### Database and dependency override

Use a pytest fixture that creates a unique temporary SQLite file or
`sqlite://` database and an engine with `connect_args={"check_same_thread": False}`.
Import the model package before `SQLModel.metadata.create_all(test_engine)`.
The fixture must assert that the normalized test URI is not equal to
`get_settings().database_uri` and is not the committed
`sqlite:///database.db` path. Never call `python manage.py init` in a test
fixture: the application database engine is created at import time and the
command can drop live tables.

Override the dependency actually used by `SessionDep`:

```python
app.dependency_overrides[get_session] = override_get_session
```

`override_get_session` should yield a session connected to the temporary engine.
Remove the exact override in teardown and dispose the temporary engine. Do not
replace only `app.database.engine`; route dependencies resolve through
`get_session`.

The application lifespan calls `ensure_db_and_tables()` against the imported
global engine. Tests should either construct `TestClient` with lifespan
disabled where supported, or make the global-engine/lifespan interaction an
explicit fixture concern. The safest integration setup is to keep the test
engine and dependency override isolated, avoid startup schema creation against
the default engine, and restore global state after each test.

### Deterministic seed data

Use a fixture namespace such as `qa_20261110_01` and deterministic IDs that
cannot collide with local demo data:

- one `User` with a unique username/email and a password produced by
  `encrypt_password`, plus a `Student(userID=<user.id>, ...)`;
- at least two additional students with different faculties and distinct
  `rank`, `totalHours`, and `awardCount` values;
- an available event with free capacity;
- a full event where `numberRegistered == numberOfSlots`;
- optionally a second available event with different searchable name,
  organisation, and location;
- no registration rows initially, except in tests whose precondition explicitly
  creates one.

Use explicit primary keys or capture inserted IDs and reuse them; do not rely on
database auto-increment state. Each test should get a fresh schema or rollback
scope so registration counts and composite keys cannot leak.

### Authentication in `TestClient`

Obtain the cookie through the real form flow, not by manufacturing a JWT in
integration tests:

```python
response = client.post(
    "/login",
    data={"username": fixture_user.username, "password": fixture_password},
    follow_redirects=False,
)
assert response.status_code == 303
assert "access_token" in client.cookies
```

`login_action_ajax` sets the HTTP-only `access_token` cookie on the 303
response. A separate `TestClient` should log in as each separate user when
testing identity boundaries. For unit tests, bypass HTTP and use fake
repositories; cookie handling is an integration concern.

There is currently no `tests/` directory. Future tests should be separated into
`tests/unit/` for service rules and `tests/integration/` for TestClient plus
temporary database behavior. No tests are generated by this mapping.

## Known deviations and non-guarantees

- Event browsing does not filter by date or `eventStatus`; registration does
  not reject past/cancelled events. This needs a product decision before being
  labelled a defect.
- Capacity checking is a read/check/increment sequence, not an atomic
  database operation; sequential full-event behavior is implemented, concurrent
  last-slot safety is not established.
- Signup creates a `User` but not a linked `Student`; registration fixtures must
  explicitly create the link.
- `Student.totalHours` is not incremented by registration.
- The 401 exception handler in [`app/main.py`](../../app/main.py#L65) returns
  the `401.html` template without explicitly passing a 401 response status;
  integration tests should record the actual status rather than assume it.
- `GET /api/users` is an unauthenticated JSON endpoint returning user identity
  fields, including email. It is outside the listed core workflows but should
  receive a separate privacy/security decision before production use.
