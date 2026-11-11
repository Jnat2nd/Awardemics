"""Build and optionally export the repository-aligned test report.

The rolling Markdown report is intentionally separate from the coursework
submission report.  Updating it never creates a PDF unless ``export_report``
is called explicitly.
"""

from __future__ import annotations

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

The model diagram is maintained in the project report:
[`docs/report.md`](report.md#model-diagram).

## Application Wireframe

![Application wireframe](wireframes/wireframe.excalidraw.png)

## Test Plans

### User Acceptance Tests Plan

The repository-aligned UAT plan is documented in:
{_source_links()}

The current plan covers event browsing, event registration, duplicate/full/invalid
registration handling, registered-event navigation, and public leaderboard
filtering, sorting, and student details.

### Integration Tests

Integration traceability and the executed result are documented in:
[`INTEGRATION_TEST_TRACEABILITY.md`](testing/INTEGRATION_TEST_TRACEABILITY.md).

Current recorded result: **13 passed, 0 failed**.

## Implementation

### Link to repository

{repo_url}

### Unit Tests

{_test_file_links()}

### Integration Tests

- [`tests/integration/test_awardemics_routes.py`](../tests/integration/test_awardemics_routes.py)
- [`tests/integration/conftest.py`](../tests/integration/conftest.py)

### API Tests (Postman collection exported to JSON in repo)

{_link_or_missing("Postman collection", postman_collection)}

{f"Missing-artifact note: {_missing_note('Postman collection JSON', postman_collection)}" if not _artifact(postman_collection)[1] else ""}

## Reports

### Unit Tests Report

{_link_or_missing("Unit test results", unit_report_screenshot, image=True)}

{f"Missing-artifact note: {_missing_note('unit-test screenshot', unit_report_screenshot)}" if not _artifact(unit_report_screenshot)[1] else ""}

### Integration Tests Report

{_link_or_missing("Integration test results", integration_report_screenshot, image=True)}

{f"Missing-artifact note: {_missing_note('integration-test screenshot', integration_report_screenshot)}" if not _artifact(integration_report_screenshot)[1] else ""}

### Postman Collection Run Report

{_link_or_missing("Postman collection run results", postman_report_screenshot, image=True)}

{f"Missing-artifact note: {_missing_note('Postman run screenshot', postman_report_screenshot)}" if not _artifact(postman_report_screenshot)[1] else ""}
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
    pdf = _new_pdf(False)
    markdown = updated.markdown_path.read_text(encoding="utf-8")
    html = _markdown_to_html(markdown, updated.markdown_path.parent, pdf_path.parent)
    _write_report_html(pdf, html)
    pdf.output(pdf_path)
    return TestReportExportResult(updated.markdown_path, pdf_path, True)
