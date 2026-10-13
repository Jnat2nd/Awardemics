from app.models.student import Student
from app.repositories.leaderboard import LeaderboardRepository


class LeaderboardService:
    def __init__(self, repository: LeaderboardRepository):
        self.repository = repository

    def view_leaderboard(
        self,
        search: str = "",
        faculty: str = "",
        sort_by: str = "rank",
        sort_order: str = "asc",
    ) -> list[Student]:
        return self.repository.list_students(
            search.strip(),
            faculty.strip(),
            sort_by,
            sort_order,
        )

    def list_faculties(self) -> list[str]:
        return self.repository.list_faculties()
