from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates
from app.repositories.volunteer_event import VolunteerEventRepository
from app.services.volunteer_event_service import VolunteerEventService

@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db:SessionDep,
    search: str = "",
):
    # TODO(student): complete this thin handler so it gets events through the
    # service abstraction and passes them to the app template.
    repository = VolunteerEventRepository(db)
    volunteerService = VolunteerEventService(repository)
    events = volunteerService.browse_events(search.strip())
    return templates.TemplateResponse(
        request=request, 
        name="app.html",
        context={
            "user": user,
            "events": events,
            "search": search,
        }
    )