from datetime import date

from app.models.registered_event import RegisteredEvent
from app.models.volunteer_event import VolunteerEvent
from app.repositories.registered_event import RegisteredEventRepository
from app.repositories.volunteer_event import VolunteerEventRepository


class RegisteredEventService:
    def __init__(
        self,
        repository: RegisteredEventRepository,
        event_repository: VolunteerEventRepository,
    ):
        self.repository = repository
        self.event_repository = event_repository

    def register(
        self,
        event_id: int,
        user_id: int,
        hours: int,
        details: str,
    ) -> RegisteredEvent:
        event = self.event_repository.get_by_id(event_id)
        if event is None:
            raise ValueError("The selected volunteer event does not exist.")
        student_id = self.repository.student_id_for_user(user_id)
        if student_id is None:
            raise ValueError("Your account is not linked to a student profile.")
        if self.repository.exists_for_student_event(student_id, event_id):
            raise ValueError("You are already registered for this event.")
        if event.numberRegistered >= event.numberOfSlots:
            raise ValueError("This volunteer event is full.")
        if hours < 1 or hours > event.hours:
            raise ValueError(f"Hours must be between 1 and {event.hours}.")
        event.numberRegistered += 1
        self.event_repository.save(event)
        registration = RegisteredEvent(
            eventID=event_id,
            studentID=student_id,
            dateRegistered=date.today(),
            hoursVolunteering=hours,
            eventSpecificDetails=details,
        )
        return self.repository.create(registration)

    def list_for_user(self, user_id: int) -> list[tuple[RegisteredEvent, VolunteerEvent]]:
        student_id = self.repository.student_id_for_user(user_id)
        if student_id is None:
            return []
        return self.repository.list_for_student(student_id)

    def unregister(self, user_id: int, event_id: int) -> bool:
        student_id = self.repository.student_id_for_user(user_id)
        if student_id is None:
            return False
        registration = self.repository.get_for_student(student_id, event_id)
        if registration is None:
            return False
        event = self.event_repository.get_by_id(event_id)
        if event is not None and event.numberRegistered > 0:
            event.numberRegistered -= 1
            self.event_repository.save(event)
        self.repository.delete(registration)
        self.event_repository.db.commit()
        return True
