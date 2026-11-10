from datetime import date
from unittest.mock import Mock

import pytest

from app.models.volunteer_event import VolunteerEvent
from app.services.volunteer_event_service import VolunteerEventService


def make_event(event_id: int = 101, name: str = "Community Build") -> VolunteerEvent:
    return VolunteerEvent(
        eventID=event_id,
        name=name,
        organisation="Community Partners",
        location="North Hall",
        description="A useful volunteer event.",
        image="",
        date=date(2026, 12, 1),
        numberOfSlots=5,
        numberRegistered=1,
        hours=4,
        eventStatus="Available",
    )


@pytest.fixture
def repository() -> Mock:
    return Mock()


@pytest.fixture
def service(repository: Mock) -> VolunteerEventService:
    return VolunteerEventService(repository)


@pytest.mark.parametrize(
    ("search", "event"),
    [
        ("101", make_event()),
        (" 101 ", make_event()),
    ],
)
def test_browse_events_numeric_search_uses_id_lookup(
    service: VolunteerEventService,
    repository: Mock,
    search: str,
    event: VolunteerEvent,
) -> None:
    # UT-EV-01: numeric browse searches use get_by_id and wrap a match.
    repository.get_by_id.return_value = event

    assert service.browse_events(search) == [event]

    repository.get_by_id.assert_called_once_with(101)
    repository.list_upcoming.assert_not_called()


def test_browse_events_numeric_search_returns_empty_for_unknown_event(
    service: VolunteerEventService, repository: Mock
) -> None:
    # UT-EV-01: a missing numeric event produces an empty result.
    repository.get_by_id.return_value = None

    assert service.browse_events("999") == []

    repository.get_by_id.assert_called_once_with(999)
    repository.list_upcoming.assert_not_called()


@pytest.mark.parametrize("search", ["build", ""])
def test_browse_events_text_search_uses_upcoming_list(
    service: VolunteerEventService, repository: Mock, search: str
) -> None:
    # UT-EV-01: text and empty searches use list_upcoming.
    events = [make_event()]
    repository.list_upcoming.return_value = events

    assert service.browse_events(search) is events

    repository.list_upcoming.assert_called_once_with(search)
    repository.get_by_id.assert_not_called()


@pytest.mark.parametrize(
    ("reference", "repository_result"),
    [
        ("101", make_event()),
        (" Community Build ", make_event(name="Community Build")),
        ("unknown", None),
    ],
)
def test_find_event_delegates_trimmed_id_name_or_unknown_reference(
    service: VolunteerEventService,
    repository: Mock,
    reference: str,
    repository_result: VolunteerEvent | None,
) -> None:
    # UT-EV-02: find_event supports numeric IDs, names, and unknown references.
    repository.find_by_reference.return_value = repository_result

    assert service.find_event(reference) is repository_result

    expected_reference = reference.strip()
    repository.find_by_reference.assert_called_once_with(expected_reference)
