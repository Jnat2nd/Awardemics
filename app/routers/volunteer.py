from fastapi import Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.registered_event import RegisteredEventRepository
from app.repositories.volunteer_event import VolunteerEventRepository
from app.services.registered_event_service import RegisteredEventService
from app.services.volunteer_event_service import VolunteerEventService

from . import router, templates


@router.get("/volunteer", response_class=HTMLResponse, name="volunteer_view")
async def volunteer_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    event_id: str | None = None,
    search: str = "",
):
    event_service = VolunteerEventService(VolunteerEventRepository(db))
    event = event_service.find_event(event_id) if event_id else None
    if event_id and event is None:
        raise HTTPException(status_code=404, detail="Volunteer event not found.")
    events = event_service.browse_events(search) if search else []
    return templates.TemplateResponse(
        request=request,
        name="volunteer.html",
        context={
            "user": user,
            "event_id": event.eventID if event else "",
            "event": event,
            "event_hours": event.hours if event is not None else None,
            "events": events,
            "search": search,
        },
    )


@router.post("/volunteer", response_class=HTMLResponse, name="volunteer_action")
async def volunteer_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    event_id: int = Form(...),
    hours: int = Form(...),
):
    # TODO(student): complete this thin handler using the service abstraction.
    service = RegisteredEventService(
        RegisteredEventRepository(db),
        VolunteerEventRepository(db),
    )
    try:
        registration = service.register(event_id, user.id, hours, "")
    except ValueError as exc:
        event = VolunteerEventService(VolunteerEventRepository(db)).get_event(event_id)
        return templates.TemplateResponse(
            request=request,
            name="volunteer.html",
            context={
                "user": user,
                "event_id": event_id,
                "event": event,
                "event_hours": event.hours if event is not None else None,
                "error_message": str(exc),
                "hours": hours,
            },
            status_code=400,
        )
    return templates.TemplateResponse(
        request=request,
        name="volunteer-confirmation.html",
        context={"user": user, "registration": registration},
    )
