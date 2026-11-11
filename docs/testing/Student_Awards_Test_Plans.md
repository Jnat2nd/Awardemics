# Student Awards — Test Plan and Traceability

**Scope:** Student Awards incentive system: browsing volunteer events (student), registering for events (student), and viewing/filtering leaderboards (public).  
**Inputs:** supplied wireframe sequence and ERD, plus UAT example table.  
**Status:** compared with the checked-out pytest suite and recorded test reports on 2026-11-10. Covered automated cases were removed below. UAT statuses marked **Pass (automated evidence)** reflect repository integration-test outcomes, not manual browser execution; remaining manual and Postman cases are **Not run**.

## How to use this pack

1. Resolve the decisions labeled **Needs confirmation** below before enforcing them as acceptance criteria.
2. Execute UAT manually against the screens and fill in **Success** (Pass / Fail / Blocked / N/A) with screenshots or evidence.
3. Place this Markdown file in the repository, then give GitHub Copilot the prompts in `Copilot_Test_Generation_Prompts.md` in order. It must inspect real application code before creating pytest modules.
4. Import the companion Postman collection into Postman. Map every placeholder route, sample identity, and status code to the *actual* backend before running it against a disposable test DB.

## Source-of-truth summary

- **WF-01 Browse:** Events tab shows event cards with name, image, ID, organisation, hours, date, status and spots left. A card opens Event Details with description and other fields. Volunteer navigates to registration with the Event ID already selected. Back returns to the event grid.
- **WF-02 Register:** Volunteer form allows event selection, displays event details, takes hours volunteering and event-specific information. Clear, Cancel and Submit appear. Successful submission opens a modal showing Event ID and Student ID; OK returns to Browse and View opens a registration list.
- **WF-03 Leaderboard:** public leaderboard displays rank, name, faculty, hours and award count, has Search and column-level controls. Selecting a row opens a Student Information modal with name, faculty, rank, total hours, latest event and latest award.
- **ERD:** `VOLUNTEER_EVENT(eventID PK, name, organisation, location, description, image, date, numberOfSlots, numberRegistered, hours, eventStatus)`; `STUDENT(studentID PK, name, faculty, degreeLevel, year, totalHours, rank, awardCount, latestEvent, latestAward)`; `REGISTERED_EVENT(eventID PK/FK, studentID PK/FK, dateRegistered, hoursVolunteering, eventSpecificDetails)`; `LEADERBOARD(listingID PK, studentName, studentFaculty, totalHours, rank, awardCount)`.

**Important distinctions:** The ERD has a composite `REGISTERED_EVENT(eventID, studentID)` key, so duplicates must not produce additional rows. It does **not** say when registration hours become *earned* hours; test plans do not assume immediate updates to `STUDENT.totalHours`. `LEADERBOARD` has no `studentID` field, so student-modal lookup requires a stable identifier/mapping; matching by name alone is unsafe. No API URLs, auth approach, HTTP status codes, or ranking tie rules should be invented.

## Test levels and execution

| Level | Purpose | Execution approach | What it does *not* prove |
|---|---|---|---|
| UAT | Student/public user can complete the visible workflow | Human tester follows UI steps; captures evidence | Internal code correctness |
| Unit | Isolated domain, validation, query or mapping rule | `pytest`, dependency mocks, parametrized values | Database integration or UI navigation |
| Integration | Real interactions across app, DB and auth boundaries | `pytest` client + test database; reset after tests | Browser clicks unless a UI test tool is added |
| API | HTTP contract, state changes, error handling | Postman/Newman against disposable environment | Pixel/UI behaviour |

**Test data:** at least three students from two faculties; two with the same name; events with free slots, one remaining slot, full capacity, and (if supported) inactive status; one student who is already registered. Use synthetic event-specific details only. Ensure tests do not hit production or mutate a shared DB.


## Repository comparison

The checked-out automated tests were reviewed before this copy was updated. The following planned automated cases were removed because equivalent executable coverage exists:

- Unit: `UT-RG-03` duplicate registration, `UT-RG-04` full-event rejection, `UT-RG-05` hours validation, `UT-RG-06` registration record creation, and `UT-RG-07` registration listing/unregister behavior.
- Integration: `IT-EV-01` event browsing/search, `IT-RG-01` registration persistence, `IT-RG-02` duplicate registration, `IT-RG-03` rejected registration cases, `IT-RG-05` unregister flow, `IT-LB-01` public leaderboard filtering/sorting, and `IT-LB-02` public student modal/data minimization.

Implemented tests reviewed:

- `tests/unit/test_registered_event_service.py`
- `tests/integration/test_awardemics_routes.py`
- `tests/unit/test_volunteer_event_service.py`
- `tests/unit/test_leaderboard_service.py`

### Missing or still-unverified automated coverage

The remaining unit/integration rows are not covered by the current pytest suite and should remain planned: event capacity/slot calculation and mapping, concurrency/transaction rollback, closed-event eligibility, complete authentication/impersonation checks, earned-hours behavior, deterministic ranking/ties, stable leaderboard identity, event-detail API behavior, and public/private data-boundary cases not exercised by the existing tests. UAT cases without direct automated evidence remain manual UI checks, and the API rows remain Postman checks that have not been executed.

## 1. User acceptance testing plan

Matches the example format: **Test Case → Pre-conditions → Test Steps → Test Criteria → Success**. Extra IDs, evidence, and specification-status fields support traceability and honest execution reporting. A row marked **Needs confirmation** is a proposed criterion rather than a claim that the wireframe specified that behaviour.

| Test ID | Test Case | Pre-conditions | Test Steps | Test Criteria | Success | Spec status |
|---|---|---|---|---|---|---|
| UAT-BR-01 | Browse available volunteer event cards | Student is on the Events tab; events exist in the catalogue. | 1. Select Events.<br>2. Scroll the Browse grid. | Cards are displayed with event name, image, ID, organisation, hours, date, status and spots left. | Pass (automated evidence) | Shown / derived; IT-EV-01 passed |
| UAT-BR-02 | Open a listed event | At least one event is visible. | 1. Click a specific event card.<br>2. Compare the card with Event Details. | Event Details opens for the selected event and shows the matching ID, name, organisation, hours, location, status, spots left, image and description. | Pass (automated evidence) | Shown / derived; IT-EV-01 passed |
| UAT-BR-03 | Return from event details | Student is viewing Event Details. | 1. Click the back arrow. | The Browse view reappears; no registration is created. | Not run | Shown / derived |
| UAT-BR-04 | Start registration from event details | Student is viewing an event that is eligible for registration. | 1. Click Volunteer.<br>2. Inspect the form. | The Volunteer form opens with the selected event ID prefilled and the corresponding event details displayed. | Pass (automated evidence) | Shown / derived; IT-RG-01 passed |
| UAT-BR-05 | Find an event using the search icon | Multiple events exist, including one with a unique name. | 1. Open Events.<br>2. Use the search control to enter an event name. | Matching event(s) can be located without changing unrelated event data. | Pass (automated evidence) | Needs confirmation; IT-EV-01 passed |
| UAT-BR-06 | Handle no event matches | A search term exists that matches no event. | 1. Search for an unmatched event name. | The screen displays a clear empty-results state and no invalid cards. | Not run | Needs confirmation |
| UAT-BR-07 | Display accurate remaining slots | An event has known numberOfSlots and numberRegistered fixture values. | 1. Open Events.<br>2. Inspect Spots left on the card and details. | Both views show the same remaining capacity, consistent with the application’s approved calculation. | Not run | Needs confirmation |
| UAT-RG-01 | Choose an event from Volunteer tab | Authenticated student; at least one event exists. | 1. Click Volunteer in the navigation bar.<br>2. Open Event ID selector.<br>3. Select an event. | The selected Event ID is shown and event details populate the form. | Pass (automated evidence) | Needs confirmation; IT-RG-01 passed |
| UAT-RG-02 | Submit a valid event registration | Authenticated student; selected event is open and has room; student not registered for it. | 1. Select event (or arrive from Event Details).<br>2. Enter valid Hours Volunteering.<br>3. Enter optional event-specific details.<br>4. Click Submit. | A Registration Complete modal appears with the actual Event ID and the authenticated Student ID; only one registration is stored. | Fail (implementation deviation) | Needs confirmation; IT-RG-01 passed persistence/listing only; confirmation modal and Student ID are absent |
| UAT-RG-03 | Confirmation OK action | Registration Complete modal is open. | 1. Click OK. | The modal closes and student is returned to event browsing. | Not run | Shown / derived |
| UAT-RG-04 | Confirmation View action | Registration Complete modal is open. | 1. Click View. | The list of the student’s registrations opens and includes the newly registered event. | Not run | Shown / derived |
| UAT-RG-05 | Clear form without submitting | Volunteer form contains an event selection and entered values. | 1. Click Clear. | Editable form fields reset as designed; no registration is created. | Not run | Needs confirmation |
| UAT-RG-06 | Cancel registration | Volunteer form has unsaved input. | 1. Click Cancel. | The screen returns to Event Details or Browse; no registration is created. | Not run | Shown / derived |
| UAT-RG-07 | Reject missing mandatory inputs | Student is signed in; at least one required field is missing. | 1. Leave Event ID blank, then Submit.<br>2. Select an event, leave required hours blank, then Submit. | Submission is prevented with visible, field-specific guidance and no registration is stored. | Not run | Needs confirmation |
| UAT-RG-08 | Reject duplicate student-event registration | Student already registered for the selected event. | 1. Open same event again.<br>2. Submit a second registration. | Student receives understandable feedback and no duplicate registration is created. | Pass (automated evidence) | Shown / derived; IT-RG-02 passed |
| UAT-RG-09 | Prevent booking when no slots remain | Selected event has no remaining slots. | 1. Open Event Details.<br>2. Attempt to use Volunteer / Submit. | The application prevents a new registration and does not exceed event capacity. | Pass (automated evidence) | Needs confirmation; IT-RG-03 full-event case passed |
| UAT-RG-10 | Reject invalid hours value | Student is signed in and the selected event is open. | 1. Enter zero or negative hours.<br>2. Try to Submit. | An invalid hours value is rejected according to confirmed validation rules; no record is created. | Pass (automated evidence) | Needs confirmation; IT-RG-03 hours cases passed |
| UAT-RG-11 | Access protection for student registration | Student is signed out; a sign-in mechanism exists. | 1. Navigate directly to the Volunteer form.<br>2. Try to submit. | Anonymous user cannot create a registration under an arbitrary Student ID; user receives appropriate sign-in/authorization feedback. | Pass (automated evidence) | Needs confirmation; IT-RG-04 passed |
| UAT-RG-12 | Limit disclosure of sensitive event details | Student enters private details (e.g. dietary/medical needs) in eventSpecificDetails. | 1. Submit the form.<br>2. Open publicly accessible pages and another user’s account. | Private event-specific details do not appear on the public leaderboard or another student’s UI. | Pass (automated evidence) | Needs confirmation; IT-LB-02 passed public-data exclusion |
| UAT-LB-01 | Open public leaderboard | User is not signed in; leaderboard contains records. | 1. Navigate to Leaderboard. | Leaderboard is accessible without student login. | Pass (automated evidence) | Shown / derived; IT-LB-02 public-access case passed |
| UAT-LB-02 | Inspect leaderboard columns | Leaderboard has known seeded student records. | 1. View the table.<br>2. Check headers and sample rows. | Rank, name, faculty, hours and award count are displayed and match the chosen student records. | Pass (automated evidence) | Shown / derived; IT-LB-01 passed |
| UAT-LB-03 | Sort leaderboard by hours | Seeded students have different total hours. | 1. Click Hours heading/sort control.<br>2. Observe ordering; reverse sort if UI allows. | Rows reorder by numeric total hours, matching the selected direction. | Pass (automated evidence) | Needs confirmation; IT-LB-01 passed descending hours |
| UAT-LB-04 | Filter by faculty | At least two faculties exist in leaderboard. | 1. Open Faculty dropdown/filter.<br>2. Choose a faculty. | Only entries with the selected faculty remain; displayed rank/hours are not corrupted. | Pass (automated evidence) | Needs confirmation; IT-LB-01 passed |
| UAT-LB-05 | Search by student name | A seeded student has a distinctive name. | 1. Enter the name in Search. | Matching student records are shown and nonmatches are hidden. | Pass (automated evidence) | Needs confirmation; IT-LB-01 passed combined search |
| UAT-LB-06 | Combine and clear search and filters | Name matches across at least two faculties. | 1. Filter faculty.<br>2. Enter a name search.<br>3. Clear the search/filter. | Results satisfy both active criteria; clearing restores the correct unfiltered result. | Not run | Needs confirmation |
| UAT-LB-07 | Open student information modal | A leaderboard row is visible. | 1. Click the selected row. | Student Information modal opens for that exact student with full name, faculty, rank, total hours, latest event and latest award. | Pass (automated evidence) | Shown / derived; IT-LB-02 passed |
| UAT-LB-08 | Close student modal | Student Information modal is open. | 1. Click X. | Modal closes and returns to the same leaderboard context without navigating elsewhere. | Not run | Shown / derived |
| UAT-LB-09 | Select one of two students with the same name | Two seeded students share the same name but have different IDs. | 1. Select the first row.<br>2. Close modal.<br>3. Select the second row. | Each modal shows the correct distinct student, never relying on name alone for identity. | Not run | Needs confirmation |
| UAT-LB-10 | Handle unmatched leaderboard search | No seeded student matches the search term. | 1. Search for a nonexistent name. | An understandable empty-results message appears, without stale rows or errors. | Not run | Needs confirmation |


## 2. Unit test plan (`pytest`)

Unit tests must call real service/validator/serializer functions discovered in the repository, with external dependencies mocked. Browser navigation and button-click behaviour remain in UAT unless the repository contains testable Python UI state logic.

| Test ID | Target logic | Isolation/setup | Inputs/action | Expected assertion | Fixture | Spec status |
|---|---|---|---|---|---|---|
| UT-EV-01 | Compute remaining event slots | Isolate capacity or serializer logic. | numberOfSlots=10; numberRegistered=7; also test 0/0 and 10/10. | Remaining spots are consistent and never misreported; behavior for inconsistent stored values is defined. | Pure function, mocked event | Needs confirmation |
| UT-EV-02 | Map event list / details fields | Isolate DTO/serializer (if present). | Input event with all ERD properties. | List and detail output contain required fields without accidental field swaps. | Fake VOLUNTEER_EVENT | Shown / derived |
| UT-EV-03 | Filter/search event list when implemented backend-side | Isolate event query/filter service if it exists. | Matching name, unmatched term, special characters. | Matches handled according to real search semantics; no unrelated events. | In-memory event collection | Needs confirmation |
| UT-RG-01 | Validate required registration fields | Isolate existing validation function/model. | Missing event ID; missing hours; malformed payload. | Invalid payload rejected with appropriate validation result. | Pure validation fixture | Needs confirmation |
| UT-RG-02 | Validate hoursVolunteering | Use approved hours constraints; do not invent max value. | Zero, negative, fractional/positive and boundary values applicable to schema. | Only permitted values accepted; unsupported values rejected. | Parametrized input cases | Needs confirmation |
| UT-RG-08 | Keep registration separate from earned total hours | Isolate update side effects. | Create a new future event registration. | STUDENT.totalHours is not changed merely by registration unless approved business rule explicitly requires it. | Mock student repository | Needs confirmation |
| UT-LB-01 | Sort/rank students | Isolate leaderboard service/query helper. | Students with different totalHours, awardCount and rank. | Ordering follows documented sort/rank rule; no lexicographic numeric sorting. | Seeded student value objects | Needs confirmation |
| UT-LB-02 | Handle tied rankings deterministically | Isolate ranking rule (if rank is calculated). | Two students have equal totalHours. | Ties follow an explicitly approved rank/secondary-order policy. | Parametrized student fixture | Needs confirmation |
| UT-LB-03 | Filter leaderboard by faculty | Isolate backend filter/query function if present. | Different faculties, mixed-case input, invalid faculty. | Only matching rows returned as defined by filter contract. | Student fixture | Needs confirmation |
| UT-LB-04 | Search leaderboard names | Isolate backend search function if present. | Exact, partial and no-match name searches. | Matches follow real API search semantics; no unexpected rows. | Student fixture | Needs confirmation |
| UT-LB-05 | Project public leaderboard fields | Isolate public serializer / response model. | Student with private and public fields. | Only intended public values exposed; no eventSpecificDetails or unrelated private data. | Mock student / registered event | Shown / derived |
| UT-LB-06 | Resolve selected row by stable student ID | Isolate student lookup/detail projection. | Two students share the same name. | Click target/detail lookup identifies one stable student, not a name-only match. | Two distinct student IDs | Needs confirmation |


## 3. Integration test plan (`pytest`)

Integration tests should use the application's **real** framework test client and a **dedicated** test database. Each test must leave the test environment in its original state. Confirm response status codes from the API contract instead of hard-coding assumptions from the wireframe.

| Test ID | Boundary under test | Pre-conditions | Actions | Expected assertion | Fixture/cleanup | Spec status |
|---|---|---|---|---|---|---|
| IT-EV-02 | Event detail API ↔ event storage | Seed one event with distinct ID, status, description. | 1. Request selected event by ID.<br>2. Request nonexistent ID. | Correct event is returned and nonexistent ID gets documented not-found response. | Temporary DB with one known event | Shown / derived |
| IT-RG-04 | Concurrent capacity enforcement / transaction atomicity | Event has exactly one slot remaining; two different students. | 1. Submit competing registrations concurrently.<br>2. Query committed records/counter. | At most one new registration succeeds and stored counts remain consistent. | Isolated DB supporting concurrency | Needs confirmation |
| IT-RG-06 | Authenticated identity ↔ registration ownership | Two students and valid event; auth system available. | 1. Register as student A.<br>2. Attempt to spoof student B.<br>3. Try anonymous submission. | Ownership follows authenticated identity; anonymous/spoofed registrations are denied per auth contract. | Tokens/session fixtures | Needs confirmation |
| IT-RG-07 | Registration write ↔ student registration read | Seed student and event; no existing registration. | 1. Create registration.<br>2. Request current student’s registrations. | Created event appears for correct student with matching ID/hours; other students cannot see private registration details. | Test users, DB rollback | Needs confirmation |
| IT-RG-08 | Rollback on failed DB operation | Simulate insert or counter update failure. | 1. Start registration.<br>2. Force a controlled persistence failure.<br>3. Inspect DB. | No partial registration or incorrect numberRegistered persists. | Injected repo/transaction failure | Needs confirmation |
| IT-LB-03 | Public API authorization/data minimization | Seed eventSpecificDetails including sensitive example text. | 1. Request leaderboard and public student details anonymously. | Only public fields returned; event-specific private details and sensitive registration data absent. | Student + registration fixture | Needs confirmation |
| IT-LB-04 | Sorting/filtering across DB query and API | Seed several faculties, distinct ranks/hours/award counts. | 1. Request each implemented sort key.<br>2. Combine supported name query and faculty filter. | Results are sorted numerically where appropriate, filtered accurately and stable across pages if pagination exists. | DB with deterministic data | Needs confirmation |


## 4. Traceability matrix

`API-*` IDs correspond to requests in the bundled Postman starter collection. A dash means the behaviour is intentionally left to UAT rather than incorrectly claimed as covered by backend tests.

| Requirement ID | Behaviour | UAT | Unit | Integration | API | Notes |
|---|---|---|---|---|---|---|
| REQ-BR-01 | Browse grid + event cards | UAT-BR-01, UAT-BR-07 | UT-EV-01, UT-EV-02 | - | API-EV-01 | Slots formula / status policy to confirm |
| REQ-BR-02 | Event detail navigation | UAT-BR-02, UAT-BR-03 | UT-EV-02 | IT-EV-02 | API-EV-02 | Back navigation is browser/UI UAT, not API |
| REQ-BR-03 | Event search | UAT-BR-05, UAT-BR-06 | UT-EV-03 | - | API-EV-01 | Test backend search only if implemented there |
| REQ-RG-01 | Prefill / select event | UAT-BR-04, UAT-RG-01 | UT-EV-02 | IT-EV-02 | API-EV-02 | UI navigation not testable via API alone |
| REQ-RG-02 | Register student for event | UAT-RG-02, UAT-RG-03, UAT-RG-04 | UT-RG-01 | IT-RG-07 | API-RG-01, API-RG-02 | Authentication, hours, success shape to map |
| REQ-RG-03 | Clear/cancel without write | UAT-RG-05, UAT-RG-06 | — | — | — | UI-only behaviour |
| REQ-RG-04 | Duplicate prevention | UAT-RG-08 | - | - | API-RG-03 | Composite primary key confirmed by ERD |
| REQ-RG-05 | Capacity / eligibility | UAT-RG-09, UAT-RG-10 | UT-RG-02 | IT-RG-04 | API-RG-04 | Business rules need signoff |
| REQ-RG-06 | Authenticated registration | UAT-RG-11 | - | IT-RG-06 | API-RG-05 | Confirm actual authentication design |
| REQ-RG-07 | Private event details | UAT-RG-12 | UT-LB-05 | IT-LB-03 | API-LB-04 | Confidential data must not leak |
| REQ-LB-01 | Public leaderboard rows | UAT-LB-01, UAT-LB-02 | UT-LB-01, UT-LB-05 | - | API-LB-01 | Define source of truth for rank/hours |
| REQ-LB-02 | Leaderboard sorting, search and filter | UAT-LB-03, UAT-LB-04, UAT-LB-05, UAT-LB-06, UAT-LB-10 | UT-LB-02, UT-LB-03, UT-LB-04 | IT-LB-04 | API-LB-02 | Confirm sort fields and search behaviour |
| REQ-LB-03 | Student info modal | UAT-LB-07, UAT-LB-08, UAT-LB-09 | UT-LB-06 | - | API-LB-03 | ERD LEADERBOARD has no studentID |


## 5. Open decisions and requirements clarification

| ID | Decision | Impact | Handling until clarified | Responsible role |
|---|---|---|---|---|
| D-01 | What backend language/framework, routes, JSON envelopes and status codes exist? | Determines pytest imports, route mapping and accurate Postman requests. | Discover from the repository; never invent routes. | Repository owner |
| D-02 | How is Student authenticated and is registration login-only? | Controls studentID ownership, permissions and UAT access expectations. | Assume student-only action, verify auth implementation. | Product owner |
| D-03 | How is “Spots left” calculated and what if stored counts disagree? | Affects capacity, displayed slots and concurrency tests. | Candidate: numberOfSlots - numberRegistered; needs approval. | Product owner |
| D-04 | What eventStatus values permit registration? | Closed/cancelled/full edge cases depend on policy. | Do not hardcode statuses before reviewing repo. | Product owner |
| D-05 | What are hoursVolunteering constraints, and when are totalHours awarded? | Registration hours versus earned hours are not identical concepts. | Do not increment earned hours on signup unless specified. | Product owner |
| D-06 | How are leaderboard rank ties resolved and what is the ranking source? | Needed for deterministic assertions and sorting. | Use documented rank field or verified ranking service. | Product owner |
| D-07 | How does LEADERBOARD identify STUDENT uniquely? | Student names are not unique; leaderboard schema lacks studentID. | Expose stable studentID in public API or create explicit mapping; avoid name matching. | Data designer |
| D-08 | What search/filter fields and matching semantics exist? | Determines UI and API tests. | Test only visible/implemented controls; get approval for new requirements. | Product owner |
| D-09 | What are permitted details and retention/access controls for eventSpecificDetails? | Dietary/medical information may be sensitive. | Keep it out of public responses and test fixtures; use synthetic data. | Product owner |
| D-10 | Does Register success “View” list exist and what is its API route? | Wireframe references list but its screen not provided. | Verify navigation target, avoid guessing endpoint. | Product owner |
| D-11 | What is the empty-state and invalid-input UX? | Not specified in wireframe. | Proposed UAT tests require signoff. | Product owner |
| D-12 | What test DB, auth tokens, fixtures and reset strategy are available? | Integration/postman tests must be isolated and non-destructive. | Require dedicated test environment and cleanup. | Developer/QA |


## 6. Definition of done / execution evidence

- All shown/derived UAT cases exercised and results recorded; proposed cases are either approved or explicitly excluded with rationale.
- Each implemented rule has a direct unit test, boundary/invalid case, and no live database dependence.
- Integration cases run in an isolated environment with fixtures, proper cleanup and unambiguous failure messages.
- API requests are mapped to actual routes and use approved HTTP statuses, schema, and authorization. Postman tests assert observable response/body, not merely HTTP 2xx.
- No test is silently skipped or adjusted simply to make the suite pass. Unimplemented interfaces or unclear rules are reported as **Blocked** with a documented reason.
- Evidence includes pytest output, coverage summary (if available), Newman/Postman run, and screenshots for UAT.

**Useful commands after Copilot generates the suite:** `python -m pytest tests/unit -q`; `python -m pytest tests/integration -q`; and `newman run Student_Awards_Postman_Starter.postman_collection.json -e Student_Awards_Local.postman_environment.json` (only after real route mapping and test fixture setup).
