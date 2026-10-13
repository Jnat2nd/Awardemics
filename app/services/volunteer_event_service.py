from app.models.volunteer_event import VolunteerEvent
from app.repositories.volunteer_event import VolunteerEventRepository


class VolunteerEventService:
    def __init__(self, repository: VolunteerEventRepository):
        self.repository = repository

    def browse_events(self, search: str = "") -> list[VolunteerEvent]:
        if search.strip().isdigit():
            event = self.repository.get_by_id(int(search.strip()))
            return [event] if event is not None else []
        return self.repository.list_upcoming(search)

    def get_event(self, event_id: int) -> VolunteerEvent | None:
        return self.repository.get_by_id(event_id)

    def find_event(self, reference: str) -> VolunteerEvent | None:
        return self.repository.find_by_reference(reference.strip())
