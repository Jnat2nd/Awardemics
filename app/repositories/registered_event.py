from datetime import date

from sqlmodel import Session, select

from app.models.registered_event import RegisteredEvent
from app.models.student import Student
from app.models.volunteer_event import VolunteerEvent


class RegisteredEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, registration: RegisteredEvent) -> RegisteredEvent:
        self.db.add(registration)
        self.db.commit()
        self.db.refresh(registration)
        return registration

    def exists_for_student_event(self, student_id: int, event_id: int) -> bool:
        statement = select(RegisteredEvent).where(
            RegisteredEvent.studentID == student_id,
            RegisteredEvent.eventID == event_id,
        )
        return self.db.exec(statement).first() is not None

    def student_id_for_user(self, user_id: int) -> int | None:
        statement = select(Student.studentID).where(Student.userID == user_id)
        return self.db.exec(statement).first()

    def list_for_student(self, student_id: int) -> list[tuple[RegisteredEvent, VolunteerEvent]]:
        statement = (
            select(RegisteredEvent, VolunteerEvent)
            .join(VolunteerEvent, RegisteredEvent.eventID == VolunteerEvent.eventID)
            .where(RegisteredEvent.studentID == student_id)
            .order_by(RegisteredEvent.dateRegistered.desc())
        )
        return list(self.db.exec(statement).all())

    def get_for_student(self, student_id: int, event_id: int) -> RegisteredEvent | None:
        statement = select(RegisteredEvent).where(
            RegisteredEvent.studentID == student_id,
            RegisteredEvent.eventID == event_id,
        )
        return self.db.exec(statement).first()

    def delete(self, registration: RegisteredEvent) -> None:
        self.db.delete(registration)
        self.db.commit()
