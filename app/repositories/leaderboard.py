from sqlmodel import Session, select

from app.models.student import Student


class LeaderboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_students(
        self,
        search: str = "",
        faculty: str = "",
        sort_by: str = "rank",
        sort_order: str = "asc",
    ) -> list[Student]:
        sort_columns = {
            "rank": Student.rank,
            "name": Student.name,
            "faculty": Student.faculty,
            "hours": Student.totalHours,
            "awards": Student.awardCount,
        }
        sort_column = sort_columns.get(sort_by, Student.rank)
        order_expression = sort_column.desc() if sort_order == "desc" else sort_column.asc()
        statement = select(Student).order_by(order_expression)
        if faculty:
            statement = statement.where(Student.faculty == faculty)
        if search:
            statement = statement.where(Student.name.ilike(f"%{search}%"))
        return list(self.db.exec(statement).all())

    def list_faculties(self) -> list[str]:
        statement = select(Student.faculty).distinct().order_by(Student.faculty)
        return list(self.db.exec(statement).all())
