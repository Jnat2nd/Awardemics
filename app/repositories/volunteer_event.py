from sqlmodel import Session, or_, select

from app.models.volunteer_event import VolunteerEvent


class VolunteerEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_upcoming(self, search: str = "") -> list[VolunteerEvent]:
        statement = select(VolunteerEvent)
        if search:
            term = f"%{search}%"
            statement = statement.where(
                or_(
                    VolunteerEvent.name.ilike(term),
                    VolunteerEvent.location.ilike(term),
                    VolunteerEvent.organisation.ilike(term),
                )
            )
        statement = statement.order_by(VolunteerEvent.date)
        return list(self.db.exec(statement).all())

    def get_by_id(self, event_id: int) -> VolunteerEvent | None:
        return self.db.get(VolunteerEvent, event_id)

    def save(self, event: VolunteerEvent) -> VolunteerEvent:
        self.db.add(event)
        return event

    def find_by_reference(self, reference: str) -> VolunteerEvent | None:
        if reference.isdigit():
            return self.get_by_id(int(reference))
        statement = select(VolunteerEvent).where(VolunteerEvent.name == reference)
        return self.db.exec(statement).first()
