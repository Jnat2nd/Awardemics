"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.volunteer_event import VolunteerEvent
from app.models.registered_event import RegisteredEvent
from app.models.student import Student

__all__ = ["User", "VolunteerEvent", "RegisteredEvent", "Student"]
