# Awardemics Postman VS Code execution guide

## Scope and current contract

Import these two files from the repository:

- [`postman/Awardemics_Render_Forms.postman_collection.json`](../../postman/Awardemics_Render_Forms.postman_collection.json)
- [`postman/Awardemics_Render.postman_environment.json`](../../postman/Awardemics_Render.postman_environment.json)

The checked-out application exposes server-rendered HTML/form workflows. It does
not expose JSON REST resources for events, registrations, or the leaderboard.
`GET /api/users` is outside this collection and must not be used as a substitute
for private student or registration assertions.

The Render commit has not been independently confirmed to match this checkout.
The deployment was not reachable from the authoring environment, so this pack is
ready to run but its live result is **NOT RUN**.

## Import and workspace setup

1. Open VS Code with the Postman extension installed.
2. Sign in to Postman when prompted and select the intended Postman workspace.
3. Use **Import > File**, import the collection JSON, then import the environment JSON.
4. Select **Awardemics - Render development (safe fixture template)** in the environment selector.
5. In the local environment only, set:
   - `testUsername` and `testPassword` to a disposable account whose `Student.userID` points to that user.
   - `eventID` to an available event with `numberRegistered < numberOfSlots`.
   - `fullEventID` to a different event with `numberRegistered >= numberOfSlots`, where the test student is not registered.
   - `validHours` to an integer from `1` through the selected event's `hours`.
   - `expectedEventName`, `eventSearch`, `searchTerm`, and `faculty` to values present in the deployment.
   - Leave `invalidEventID` as an ID absent from the database, or replace it with another confirmed-absent integer.
6. Do not commit the populated local environment. The committed template contains no credentials, cookies, or production data.

## Fixture preparation and verification

`eventID` and `fullEventID` are identifiers for the existing
`VolunteerEvent.eventID` field; they are not new database attributes.

Prepare fixtures non-destructively using the existing SQLModel models and the
approved local/development database process. Do not call `python manage.py init`
against Render because it drops and recreates tables. Verify the values by
inspecting `VolunteerEvent.eventID`, `numberRegistered`, `numberOfSlots`,
`hours`, and the student's `Student.userID` link. No fixture-creation endpoint
exists and this collection does not invent one. If an actually full event or a
linked test student cannot be prepared safely, mark the affected cases
**BLOCKED** rather than substituting another event.

## Cookie and redirect configuration

Before folder 01, clear cookies for `faststarter-9c75.onrender.com` in the
Postman cookie manager. Confirm there is no `access_token` cookie. This is
required because folder 01's anonymous assertions must not inherit a prior login.

The collection has `followRedirects: false` on every request. Login and
unregister also explicitly carry this request-level setting. This makes the
login `303` plus `Set-Cookie` and the unregister `303` plus `Location` visible
to the runner. Do not add a Bearer header, paste a session cookie, or read the
HttpOnly cookie in test JavaScript. The cookie jar supplies it to subsequent
requests.

## Running and evidence

1. Open the collection's **Run** action in the Postman VS Code extension.
2. Run folder **01 - Public / read-only smoke tests** first with the cleared jar.
3. Run folder **02 - Authenticated browsing and form validation** second.
4. Run folder **03 - Stateful registration lifecycle** third, in its displayed
   order: create registration, read it, reject duplicate, unregister, verify
   absence. A single complete ordered run is also acceptable.
5. Inspect the **Passed** and **Failed** tabs, response status/content type, test
   output, and **Run history**.
6. Take a screenshot showing the collection name and the runner test counts.
7. If the collection or environment was changed in the extension, use the
   extension's export/save action and replace the repository JSON before
   submission. The on-disk files, not a workspace-only copy, are the submitted
   artifacts.

If the runner stops after `API-RG-04`, remove the registration non-destructively
by opening the registered-events form for the same account and confirming
unregister, then confirm the event count is restored before rerunning folder 03.

Postman can verify HTTP responses and HTML markers. It cannot verify Bootstrap
modal clicks or other browser-specific UI behavior; those remain manual UAT.

## Rubric/API gap

The three core workflows currently use HTML pages and form posts. If the rubric
requires dedicated JSON REST views for events, registrations, or leaderboard
data, that is a separate implementation gap for student/instructor decision.
This QA collection does not silently add those endpoints or change application
business logic.
