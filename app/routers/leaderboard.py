from fastapi import Request
from fastapi.responses import HTMLResponse

from app.dependencies.auth import IsUserLoggedIn, get_current_user
from app.dependencies.session import SessionDep
from app.repositories.leaderboard import LeaderboardRepository
from app.services.leaderboard_service import LeaderboardService

from . import router, templates


@router.get("/leaderboard", response_class=HTMLResponse, name="leaderboard_view")
async def leaderboard_view(
    request: Request,
    db: SessionDep,
    user_logged_in: IsUserLoggedIn,
    search: str = "",
    faculty: str = "",
    sort_by: str = "rank",
    sort_order: str = "asc",
):
    # TODO(student): complete this thin handler through the service abstraction.
    service = LeaderboardService(LeaderboardRepository(db))
    students = service.view_leaderboard(search, faculty, sort_by, sort_order)
    faculties = service.list_faculties()
    user = await get_current_user(request, db) if user_logged_in else None
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={
            "students": students,
            "search": search,
            "faculty": faculty,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "faculties": faculties,
            "user_logged_in": user_logged_in,
            "user": user,
        },
    )
