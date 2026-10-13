from sqlmodel import Field, SQLModel


class Student(SQLModel, table=True):
    studentID: int | None = Field(default=None, primary_key=True)
    userID: int | None = Field(default=None, foreign_key="user.id", unique=True)
    name: str
    faculty: str
    degreeLevel: str
    year: int
    totalHours: int = 0
    rank: int = 0
    awardCount: int = 0
    latestEvent: str = ""
    latestAward: str = ""
