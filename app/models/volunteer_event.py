from datetime import date

from sqlmodel import Field, SQLModel


class VolunteerEvent(SQLModel, table=True):
    """A volunteer opportunity listed in Awardemics."""

    eventID: int | None = Field(default=None, primary_key=True)

    # TODO(student): complete the remaining fields from the ERD.
    name: str
    organisation: str
    location: str
    description: str
    image: str
    date: date
    numberOfSlots: int
    numberRegistered: int
    hours: int
    eventStatus: str
