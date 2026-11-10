from unittest.mock import Mock

import pytest

from app.models.student import Student
from app.services.leaderboard_service import LeaderboardService


@pytest.fixture
def repository() -> Mock:
    return Mock()


@pytest.fixture
def service(repository: Mock) -> LeaderboardService:
    return LeaderboardService(repository)


@pytest.mark.parametrize(
    ("search", "faculty", "sort_by", "sort_order"),
    [
        ("  Avery  ", "  Engineering ", "hours", "desc"),
        ("", "", "rank", "asc"),
    ],
)
def test_view_leaderboard_strips_filters_and_delegates_sorting(
    service: LeaderboardService,
    repository: Mock,
    search: str,
    faculty: str,
    sort_by: str,
    sort_order: str,
) -> None:
    # UT-LB-01: filters are trimmed and all sort arguments are delegated.
    students = [Mock(spec=Student)]
    repository.list_students.return_value = students

    assert service.view_leaderboard(search, faculty, sort_by, sort_order) is students

    repository.list_students.assert_called_once_with(
        search.strip(),
        faculty.strip(),
        sort_by,
        sort_order,
    )


def test_list_faculties_delegates_to_repository(
    service: LeaderboardService, repository: Mock
) -> None:
    # UT-LB-01: faculty options come directly from the repository.
    faculties = ["Arts", "Engineering"]
    repository.list_faculties.return_value = faculties

    assert service.list_faculties() is faculties

    repository.list_faculties.assert_called_once_with()
