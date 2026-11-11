"""Build and optionally export the repository-aligned test report.

The rolling Markdown report is intentionally separate from the coursework
submission report.  Updating it never creates a PDF unless ``export_report``
is called explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from app.report_pdf import REPO_ROOT, _markdown_to_html, _new_pdf, _write_report_html

DEFAULT_REPORT = REPO_ROOT / "docs" / "Test_Report.md"
DEFAULT_PDF = REPO_ROOT / "docs" / "Test_Report.pdf"
DEFAULT_SOURCE_REPORT = REPO_ROOT / "docs" / "report.md"
DEFAULT_AUDIT = REPO_ROOT / "docs" / "testing" / "Awardemics_Repository_Test_Audit.md"
DEFAULT_TRACEABILITY = REPO_ROOT / "docs" / "testing" / "INTEGRATION_TEST_TRACEABILITY.md"
DEFAULT_MAPPING = REPO_ROOT / "docs" / "testing" / "IMPLEMENTATION_MAPPING.md"
DEFAULT_POSTMAN_COLLECTION = (
    REPO_ROOT / "postman" / "Awardemics_Render_Forms.postman_collection.json"
)
POSTMAN_SCREENSHOTS = {
    "01": (
        "Smoke tests",
        ("postman/Postman smoke tests 1.png", "postman/Postman smoke tests 2.png"),
    ),
    "02": (
        "Authenticated browsing and form validation",
        (
            "postman/Authenticated browsing and form val 1.png",
            "postman/Authenticated browsing and form val 2.png",
        ),
    ),
    "03": (
        "Stateful registration lifecycle",
        ("postman/Stateful 1.png", "postman/Stateful 2.png"),
    ),
}


@dataclass(frozen=True)
class TestReportExportResult:
    """Paths produced by a rolling test-report update or PDF export."""

    markdown_path: Path
    pdf_path: Path | None
    updated: bool


def _read_source_section(title: str) -> str:
    """Read a level-two section from the student report."""
    if not DEFAULT_SOURCE_REPORT.is_file():
        return "Not provided in docs/report.md."
    lines = DEFAULT_SOURCE_REPORT.read_text(encoding="utf-8").splitlines()
    wanted = title.casefold()
    captured: list[str] = []
    active = False
    for line in lines:
        if line.startswith("## "):
            if active:
                break
            active = line[3:].strip().casefold() == wanted
            continue
        if active:
            captured.append(line)
    return "\n".join(captured).strip() or "Not provided in docs/report.md."


def _read_test_plan_section(title: str) -> str:
    """Read one numbered test-plan section from the repository test plan."""
    plan = REPO_ROOT / "docs" / "testing" / "Student_Awards_Test_Plans.md"
    if not plan.is_file():
        return "Not provided in Student_Awards_Test_Plans.md."
    wanted = title.casefold()
    lines = plan.read_text(encoding="utf-8").splitlines()
    captured: list[str] = []
    active = False
    for line in lines:
        if line.startswith("## "):
            if active:
                break
            active = line[3:].strip().casefold() == wanted
            continue
        if active:
            captured.append(line)
    return "\n".join(captured).strip() or "Not provided in Student_Awards_Test_Plans.md."


def _artifact(path: str | Path | None) -> tuple[str, bool]:
    """Return a report-relative link and whether the file exists."""
    if not path:
        return "", False
    raw = str(path).replace("\\", "/")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    try:
        resolved = candidate.resolve()
        resolved.relative_to(REPO_ROOT.resolve())
    except (OSError, ValueError):
        return raw, False
    return resolved.relative_to(REPO_ROOT).as_posix(), resolved.is_file()


def _link_or_missing(label: str, path: str | Path | None, *, image: bool = False) -> str:
    relative, exists = _artifact(path)
    if not relative:
        return f"> {label}: Not provided. Use `update_report(...)` when available."
    if not exists:
        return f"> {label}: `{relative}` was requested but was not found."
    report_relative = (
        relative.removeprefix("docs/")
        if relative.startswith("docs/")
        else f"../{relative}"
    )
    if image:
        return f"![{label}]({report_relative})"
    return f"[{label}]({report_relative})"


def _test_file_links() -> str:
    files = [
        path.relative_to(REPO_ROOT).as_posix()
        for root in (REPO_ROOT / "tests" / "unit", REPO_ROOT / "tests" / "integration")
        if root.is_dir()
        for path in sorted(root.glob("test_*.py"))
    ]
    if not files:
        return "> No pytest files were found."
    return "\n".join(f"- [`{path}`](../{path})" for path in files)


def _unit_test_table() -> str:
    """Return the unit-test evidence table for the implementation section."""
    rows = [
        (
            "test_view_leaderboard_strips_filters_and_delegates_sorting()",
            "LeaderboardService.view_leaderboard()",
            "Trimmed filters and sorting arguments are delegated to the repository.",
        ),
        (
            "test_list_faculties_delegates_to_repository()",
            "LeaderboardService.list_faculties()",
            "Faculty options returned by the repository are passed through unchanged.",
        ),
        (
            "test_register_rejects_unknown_event()",
            "RegisteredEventService.register()",
            "Unknown events raise a validation error without creating a registration.",
        ),
        (
            "test_register_rejects_user_without_student_mapping()",
            "RegisteredEventService.register()",
            "Accounts without a linked student profile are rejected without writes.",
        ),
        (
            "test_register_rejects_duplicate_without_consuming_slot()",
            "RegisteredEventService.register()",
            "Duplicate student/event pairs are rejected and capacity is unchanged.",
        ),
        (
            "test_register_rejects_full_event_without_consuming_slot()",
            "RegisteredEventService.register()",
            "Full events are rejected and capacity is unchanged.",
        ),
        (
            "test_register_rejects_hours_outside_event_range()",
            "RegisteredEventService.register()",
            "Hours below one or above the event limit are rejected without writes.",
        ),
        (
            "test_register_creates_correct_registration_and_increments_event()",
            "RegisteredEventService.register()",
            "Valid registration fields are stored and the event count increments once.",
        ),
        (
            "test_list_for_user_returns_empty_when_user_has_no_student_mapping()",
            "RegisteredEventService.list_for_user()",
            "An unlinked account returns no registrations and does not query the repository.",
        ),
        (
            "test_list_for_user_delegates_with_student_id()",
            "RegisteredEventService.list_for_user()",
            "A linked account lists registrations using its mapped student ID.",
        ),
        (
            "test_unregister_deletes_existing_registration_and_safely_decrements()",
            "RegisteredEventService.unregister()",
            "Existing registrations are deleted and the event count never goes below zero.",
        ),
        (
            "test_unregister_missing_registration_does_not_delete_or_decrement()",
            "RegisteredEventService.unregister()",
            "Missing registrations return false without deletion or counter changes.",
        ),
        (
            "test_browse_events_numeric_search_uses_id_lookup()",
            "VolunteerEventService.browse_events()",
            "Numeric searches use ID lookup and return the matching event or an empty list.",
        ),
        (
            "test_browse_events_text_search_uses_upcoming_list()",
            "VolunteerEventService.browse_events()",
            "Text and empty searches delegate to the upcoming-event list.",
        ),
        (
            "test_find_event_delegates_trimmed_id_name_or_unknown_reference()",
            "VolunteerEventService.find_event()",
            "Trimmed IDs and names are delegated to reference lookup.",
        ),
    ]
    lines = [
        "| unit test | Module Tested | Expected Output |",
        "|---|---|---|",
    ]
    lines.extend(f"| {test} | {module} | {expected} |" for test, module, expected in rows)
    return "\n".join(lines)


def _integration_test_table() -> str:
    """Return the integration-test evidence table for the implementation section."""
    rows = [
        (
            "test_it_ev_01_authenticated_event_search_and_modal()",
            "GET /app with authenticated_client",
            "Event search returns the matching event details and Volunteer link.",
        ),
        (
            "test_it_rg_01_volunteer_lookup_and_invalid_event()",
            "GET /volunteer with authenticated_client",
            "A valid event pre-fills the form; an unknown event returns 404.",
        ),
        (
            "test_it_rg_01_registration_persists_once_and_is_listed()",
            "POST /volunteer; GET /registered-events",
            "A valid registration persists once, increments capacity, and is listed.",
        ),
        (
            "test_it_rg_02_duplicate_registration_does_not_consume_slot()",
            "Two POST /volunteer requests for the same event",
            "The duplicate is rejected with HTTP 400 and does not consume a slot.",
        ),
        (
            "test_it_rg_03_rejected_registration_does_not_write_or_increment()",
            "POST /volunteer with full, invalid-hours, or unknown-event fixtures",
            "Invalid registrations return HTTP 400 with no database write or increment.",
        ),
        (
            "test_it_rg_04_unauthenticated_student_routes_show_no_personal_data_or_mutation()",
            "Anonymous student routes and registration actions",
            "Unauthenticated requests expose no personal data and mutate nothing.",
        ),
        (
            "test_it_rg_05_unregister_redirects_deletes_registration_and_releases_slot()",
            "POST /registered-events/{event_id}/unregister",
            "The registration is deleted, the slot is released, and the request redirects.",
        ),
        (
            "test_it_lb_01_public_leaderboard_filters_and_sorts()",
            "GET /leaderboard with search, faculty, and sort parameters",
            "The public leaderboard filters and sorts seeded students correctly.",
        ),
        (
            "test_it_lb_02_student_modal_has_public_fields_not_registration_details()",
            "GET /leaderboard with authenticated-independent fixtures",
            "The student modal shows public fields but excludes private registration details.",
        ),
        (
            "test_it_lb_02_public_leaderboard_does_not_require_authentication()",
            "Anonymous GET /leaderboard",
            "The leaderboard is accessible without authentication.",
        ),
    ]
    lines = [
        "| Test | Dependencies | Description |",
        "|---|---|---|",
    ]
    lines.extend(f"| {test} | {dependencies} | {description} |" for test, dependencies, description in rows)
    return "\n".join(lines)


def _source_links() -> str:
    links = []
    for path in (DEFAULT_AUDIT, DEFAULT_TRACEABILITY, DEFAULT_MAPPING):
        if path.is_file():
            relative = path.relative_to(REPO_ROOT).as_posix()
            links.append(f"- [{path.name}]({relative.removeprefix('docs/')})")
    return "\n".join(links) or "> No testing artefacts were found."


def _missing_note(label: str, path: str | Path | None) -> str:
    relative, exists = _artifact(path)
    if relative and exists:
        return ""
    if relative:
        return f"Not provided or not found: `{relative}`."
    return f"Not provided. Add the {label} path with `update_report(...)`."


def _first_existing(*paths: Path) -> Path | None:
    return next((path for path in paths if path.is_file()), None)


def _model_diagram() -> str:
    """Return the ERD Mermaid block from the student report."""
    source = DEFAULT_SOURCE_REPORT.read_text(encoding="utf-8")
    marker = "## Model diagram"
    start = source.find(marker)
    if start < 0:
        return "```text\nModel diagram not provided.\n```"
    block_start = source.find("```mermaid", start)
    if block_start < 0:
        return "```text\nModel diagram not provided.\n```"
    block_end = source.find("```", block_start + len("```mermaid"))
    if block_end < 0:
        return "```text\nModel diagram is incomplete.\n```"
    return source[block_start : block_end + 3]


def _postman_items() -> list[tuple[str, str, str, str, str]]:
    """Flatten collection folders into table rows matching the supplied format."""
    if not DEFAULT_POSTMAN_COLLECTION.is_file():
        return []
    payload = json.loads(DEFAULT_POSTMAN_COLLECTION.read_text(encoding="utf-8"))
    rows: list[tuple[str, str, str, str, str]] = []
    for folder in payload.get("item", []):
        folder_name = str(folder.get("name", ""))
        access = "public" if "Public" in folder_name else "authenticated"
        if "Stateful" in folder_name:
            access = "authenticated / stateful"
        for item in folder.get("item", []):
            request = item.get("request", {})
            url = request.get("url", "")
            if isinstance(url, dict):
                path = url.get("raw", "")
            else:
                path = str(url)
            path = path.replace("{{baseUrl}}", "")
            body = request.get("body", {})
            request_body = ""
            if isinstance(body, dict):
                formdata = body.get("formdata", []) or body.get("urlencoded", [])
                if formdata:
                    request_body = ", ".join(
                        str(field.get("key", ""))
                        for field in formdata
                        if field.get("key")
                    )
                elif body.get("raw"):
                    request_body = "raw request body"
            checks: list[str] = []
            for event in item.get("event", []):
                script = event.get("script", {})
                for line in script.get("exec", []):
                    if 'pm.test("' in line:
                        checks.append(line.split('pm.test("', 1)[1].split('"', 1)[0])
            outcome = "; ".join(checks) or "No post-response assertions recorded"
            if path == "/login":
                access = "public"
            rows.append(
                (
                    access,
                    str(request.get("method", "")),
                    path,
                    request_body or "—",
                    outcome,
                )
            )
    return rows


def _postman_table() -> str:
    rows = _postman_items()
    if not rows:
        return "> Postman collection not provided."
    lines = [
        "| Access | Method | Path | Request Body | Success / Errors |",
        "|---|---|---|---|---|",
    ]
    for access, method, path, body, outcome in rows:
        cells = [access, method, path, body, outcome]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    return "\n".join(lines)


def _postman_screenshot_sections() -> str:
    sections: list[str] = []
    for key, (title, paths) in POSTMAN_SCREENSHOTS.items():
        images = [
            _link_or_missing(f"{title} screenshot", path, image=True)
            for path in paths
            if _artifact(path)[1]
        ]
        sections.append(f"#### {key} — {title}\n\n" + "\n\n".join(images))
    return "\n\n".join(sections)


def build_markdown(
    *,
    name: str,
    student_id: str,
    postman_collection: str | Path | None = None,
    unit_report_screenshot: str | Path | None = None,
    integration_report_screenshot: str | Path | None = None,
    postman_report_screenshot: str | Path | None = None,
) -> str:
    """Build the complete rolling Markdown report from current repository artefacts."""
    name = name.strip() or "Not provided"
    student_id = student_id.strip() or "Not provided"
    unit_report_screenshot = unit_report_screenshot or _first_existing(
        REPO_ROOT / "tests" / "unit" / "Unit Test Report.png",
    )
    integration_report_screenshot = integration_report_screenshot or _first_existing(
        REPO_ROOT / "tests" / "integration" / "Integration Test Report.png",
    )
    postman_collection = postman_collection or DEFAULT_POSTMAN_COLLECTION
    repo_url = "https://github.com/Jnat2nd/Awardemics"
    source_description = _read_source_section("Assigned project")

    return f"""# Test Report

Generated: {date.today().isoformat()}

## Name & ID

- Name: {name}
- ID: {student_id}

## Project Description

{source_description}

## Use Case Diagram

![Use case diagram](diagrams/use-case.png)

## Entity Relationship Diagram

{_model_diagram()}

## Application Wireframe

![Application wireframe](wireframes/wireframe.excalidraw.png)

## Test Plans

### User Acceptance Test Plans

#### 1. User acceptance testing plan

{_read_test_plan_section("1. User acceptance testing plan")}

### Unit Tests

#### 2. Unit test plan (pytest)

{_read_test_plan_section("2. Unit test plan (`pytest`)")}

### Integration Tests

#### 3. Integration test plan (pytest)

{_read_test_plan_section("3. Integration test plan (`pytest`)")}

## Implementation

### Link to repository

{repo_url}

### Unit Tests

{_unit_test_table()}

### Integration Tests

{_integration_test_table()}

### API Tests (Postman collection exported to JSON in repo)

The collection is represented below as an endpoint test table; the JSON is kept
in the repository for Postman import and is not included in this report.

{_postman_table()}

## Reports

### Unit Tests Report

{_link_or_missing("Unit test results", unit_report_screenshot, image=True)}

{f"Missing-artifact note: {_missing_note('unit-test screenshot', unit_report_screenshot)}" if not _artifact(unit_report_screenshot)[1] else ""}

### Integration Tests Report

{_link_or_missing("Integration test results", integration_report_screenshot, image=True)}

{f"Missing-artifact note: {_missing_note('integration-test screenshot', integration_report_screenshot)}" if not _artifact(integration_report_screenshot)[1] else ""}

### Postman Collection Run Report

Screenshots are organized in collection execution order:
smoke tests, authenticated browsing/form validation, then the stateful
registration lifecycle.

{_postman_screenshot_sections()}
"""


def update_report(
    *,
    name: str,
    student_id: str,
    report_path: Path | None = None,
    postman_collection: str | Path | None = None,
    unit_report_screenshot: str | Path | None = None,
    integration_report_screenshot: str | Path | None = None,
    postman_report_screenshot: str | Path | None = None,
) -> TestReportExportResult:
    """Refresh rolling Markdown without exporting a PDF."""
    destination = report_path or DEFAULT_REPORT
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build_markdown(
            name=name,
            student_id=student_id,
            postman_collection=postman_collection,
            unit_report_screenshot=unit_report_screenshot,
            integration_report_screenshot=integration_report_screenshot,
            postman_report_screenshot=postman_report_screenshot,
        ),
        encoding="utf-8",
    )
    return TestReportExportResult(destination, None, True)


def export_report(
    *,
    name: str,
    student_id: str,
    report_path: Path | None = None,
    output: Path | None = None,
    postman_collection: str | Path | None = None,
    unit_report_screenshot: str | Path | None = None,
    integration_report_screenshot: str | Path | None = None,
    postman_report_screenshot: str | Path | None = None,
) -> TestReportExportResult:
    """Refresh Markdown and explicitly export it to PDF."""
    updated = update_report(
        name=name,
        student_id=student_id,
        report_path=report_path,
        postman_collection=postman_collection,
        unit_report_screenshot=unit_report_screenshot,
        integration_report_screenshot=integration_report_screenshot,
        postman_report_screenshot=postman_report_screenshot,
    )
    pdf_path = output or DEFAULT_PDF
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf = _new_pdf(False, assignment_title="COMP 3613 Assignment 2")
    markdown = updated.markdown_path.read_text(encoding="utf-8")
    html = _markdown_to_html(
        markdown,
        updated.markdown_path.parent,
        pdf_path.parent,
    )
    _write_report_html(pdf, html)
    pdf.output(pdf_path)
    return TestReportExportResult(updated.markdown_path, pdf_path, True)
