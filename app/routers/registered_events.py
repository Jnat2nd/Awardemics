from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.registered_event import RegisteredEventRepository
from app.repositories.volunteer_event import VolunteerEventRepository
from app.services.registered_event_service import RegisteredEventService

from . import router, templates


@router.get("/registered-events", response_class=HTMLResponse, name="registered_events_view")
async def registered_events_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    service = RegisteredEventService(
        RegisteredEventRepository(db),
        VolunteerEventRepository(db),
    )
    registrations = service.list_for_user(user.id)
    return templates.TemplateResponse(
        request=request,
        name="registered-events.html",
        context={"user": user, "registrations": registrations},
    )


@router.post(
    "/registered-events/{event_id}/unregister",
    name="unregister_event_action",
)
async def unregister_event_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    event_id: int,
):
    service = RegisteredEventService(
        RegisteredEventRepository(db),
        VolunteerEventRepository(db),
    )
    service.unregister(user.id, event_id)
    return RedirectResponse(
        url=request.url_for("registered_events_view"),
        status_code=303,
    )
