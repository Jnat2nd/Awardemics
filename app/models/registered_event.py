from datetime import date

from sqlmodel import Field, SQLModel


class RegisteredEvent(SQLModel, table=True):
    """A student's registration for a volunteer event."""

    # TODO(student): complete the ERD fields and key constraints.
    eventID: int = Field(primary_key=True, foreign_key="volunteerevent.eventID")
    studentID: int = Field(primary_key=True, foreign_key="student.studentID")
    dateRegistered: date
    hoursVolunteering: int
    eventSpecificDetails: str
