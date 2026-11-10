from datetime import date
from unittest.mock import Mock

import pytest

from app.models.registered_event import RegisteredEvent
from app.models.volunteer_event import VolunteerEvent
from app.services.registered_event_service import RegisteredEventService


def make_event(
    event_id: int = 101,
    *,
    slots: int = 5,
    registered: int = 1,
    hours: int = 4,
) -> VolunteerEvent:
    return VolunteerEvent(
        eventID=event_id,
        name="Community Build",
        organisation="Community Partners",
        location="North Hall",
        description="A useful volunteer event.",
        image="",
        date=date(2026, 12, 1),
        numberOfSlots=slots,
        numberRegistered=registered,
        hours=hours,
        eventStatus="Available",
    )


@pytest.fixture
def repository() -> Mock:
    repository = Mock()
    repository.student_id_for_user.return_value = 202
    repository.exists_for_student_event.return_value = False
    return repository


@pytest.fixture
def event_repository() -> Mock:
    return Mock()


@pytest.fixture
def service(repository: Mock, event_repository: Mock) -> RegisteredEventService:
    return RegisteredEventService(repository, event_repository)


def test_register_rejects_unknown_event(service: RegisteredEventService, repository: Mock, event_repository: Mock) -> None:
    # UT-RG-01: unknown events are rejected before an insert.
    event_repository.get_by_id.return_value = None

    with pytest.raises(ValueError, match="^The selected volunteer event does not exist\\.$"):
        service.register(404, 7, 2, "Details")

    repository.create.assert_not_called()
    event_repository.save.assert_not_called()


def test_register_rejects_user_without_student_mapping(
    service: RegisteredEventService, repository: Mock, event_repository: Mock
) -> None:
    # UT-RG-02: accounts without a Student.userID mapping are rejected.
    event_repository.get_by_id.return_value = make_event()
    repository.student_id_for_user.return_value = None

    with pytest.raises(ValueError, match="^Your account is not linked to a student profile\\.$"):
        service.register(101, 7, 2, "Details")

    repository.create.assert_not_called()
    event_repository.save.assert_not_called()


def test_register_rejects_duplicate_without_consuming_slot(
    service: RegisteredEventService, repository: Mock, event_repository: Mock
) -> None:
    # UT-RG-03: duplicate registrations are rejected before increment/create.
    event = make_event(registered=1)
    event_repository.get_by_id.return_value = event
    repository.exists_for_student_event.return_value = True

    with pytest.raises(ValueError, match="^You are already registered for this event\\.$"):
        service.register(101, 7, 2, "Details")

    assert event.numberRegistered == 1
    repository.create.assert_not_called()
    event_repository.save.assert_not_called()


def test_register_rejects_full_event_without_consuming_slot(
    service: RegisteredEventService, repository: Mock, event_repository: Mock
) -> None:
    # UT-RG-04: full capacity is rejected before increment/create.
    event = make_event(slots=2, registered=2)
    event_repository.get_by_id.return_value = event

    with pytest.raises(ValueError, match="^This volunteer event is full\\.$"):
        service.register(101, 7, 2, "Details")

    assert event.numberRegistered == 2
    repository.create.assert_not_called()
    event_repository.save.assert_not_called()


@pytest.mark.parametrize(
    ("hours", "message"),
    [
        (0, "Hours must be between 1 and 4."),
        (5, "Hours must be between 1 and 4."),
    ],
)
def test_register_rejects_hours_outside_event_range(
    service: RegisteredEventService,
    repository: Mock,
    event_repository: Mock,
    hours: int,
    message: str,
) -> None:
    # UT-RG-05: hours must be within the inclusive event range.
    event = make_event(hours=4, registered=1)
    event_repository.get_by_id.return_value = event

    with pytest.raises(ValueError, match=f"^{message}$"):
        service.register(101, 7, hours, "Details")

    assert event.numberRegistered == 1
    repository.create.assert_not_called()
    event_repository.save.assert_not_called()


@pytest.mark.parametrize("hours", [1, 4])
def test_register_creates_correct_registration_and_increments_event(
    service: RegisteredEventService,
    repository: Mock,
    event_repository: Mock,
    hours: int,
) -> None:
    # UT-RG-06: successful registration maps fields, saves once, and increments once.
    event = make_event(registered=1, hours=4)
    event_repository.get_by_id.return_value = event
    created_registration = object()
    repository.create.return_value = created_registration

    result = service.register(101, 7, hours, "Bring gloves")

    assert result is created_registration
    assert event.numberRegistered == 2
    event_repository.save.assert_called_once_with(event)
    repository.create.assert_called_once()
    registration = repository.create.call_args.args[0]
    assert registration.eventID == 101
    assert registration.studentID == 202
    assert registration.dateRegistered == date.today()
    assert registration.hoursVolunteering == hours
    assert registration.eventSpecificDetails == "Bring gloves"
    assert isinstance(registration, RegisteredEvent)


def test_list_for_user_returns_empty_when_user_has_no_student_mapping(
    service: RegisteredEventService, repository: Mock
) -> None:
    # UT-RG-07: listing an unlinked account does not query registrations.
    repository.student_id_for_user.return_value = None

    assert service.list_for_user(7) == []

    repository.list_for_student.assert_not_called()


def test_list_for_user_delegates_with_student_id(
    service: RegisteredEventService, repository: Mock
) -> None:
    # UT-RG-07: linked users list registrations by their mapped student ID.
    registrations = [(Mock(spec=RegisteredEvent), make_event())]
    repository.list_for_student.return_value = registrations

    assert service.list_for_user(7) is registrations

    repository.list_for_student.assert_called_once_with(202)


@pytest.mark.parametrize(
    ("starting_count", "expected_count", "save_count"),
    [(2, 1, 1), (0, 0, 0)],
)
def test_unregister_deletes_existing_registration_and_safely_decrements(
    service: RegisteredEventService,
    repository: Mock,
    event_repository: Mock,
    starting_count: int,
    expected_count: int,
    save_count: int,
) -> None:
    # UT-RG-07: existing registrations delete and decrement without going below zero.
    registration = Mock(spec=RegisteredEvent)
    event = make_event(registered=starting_count)
    event_repository.get_by_id.return_value = event
    repository.get_for_student.return_value = registration
    event_repository.db = Mock()

    assert service.unregister(7, 101) is True

    assert event.numberRegistered == expected_count
    repository.get_for_student.assert_called_once_with(202, 101)
    repository.delete.assert_called_once_with(registration)
    assert event_repository.save.call_count == save_count
    if save_count:
        event_repository.save.assert_called_once_with(event)
    event_repository.db.commit.assert_called_once_with()


def test_unregister_missing_registration_does_not_delete_or_decrement(
    service: RegisteredEventService, repository: Mock, event_repository: Mock
) -> None:
    # UT-RG-07: missing registrations return false with no side effects.
    event_repository.get_by_id.return_value = make_event(registered=2)
    repository.get_for_student.return_value = None

    assert service.unregister(7, 101) is False

    repository.get_for_student.assert_called_once_with(202, 101)
    repository.delete.assert_not_called()
    event_repository.get_by_id.assert_not_called()
    event_repository.save.assert_not_called()
    event_repository.db.commit.assert_not_called()
