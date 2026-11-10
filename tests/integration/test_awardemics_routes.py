from datetime import date

import pytest
from sqlmodel import select

from app.models.registered_event import RegisteredEvent
from app.models.student import Student
from app.models.volunteer_event import VolunteerEvent


def test_it_ev_01_authenticated_event_search_and_modal(
    authenticated_client, test_context
):
    response = authenticated_client.get("/app", params={"search": "Community"})

    assert response.status_code == 200
    assert "Community Build" in response.text
    assert "North Hall" in response.text
    assert "Build useful resources with local volunteers." in response.text
    assert f'id="event-{test_context["available_event_id"]}"' in response.text
    assert (
        f"/volunteer?event_id={test_context['available_event_id']}" in response.text
    )
    assert "River Cleanup" not in response.text


def test_it_rg_01_volunteer_lookup_and_invalid_event(authenticated_client, test_context):
    response = authenticated_client.get(
        "/volunteer",
        params={"event_id": test_context["available_event_id"]},
    )

    assert response.status_code == 200
    assert (
        f'name="event_id" value="{test_context["available_event_id"]}"'
        in response.text
    )
    assert 'max="4"' in response.text

    invalid = authenticated_client.get("/volunteer", params={"event_id": 99999})
    assert invalid.status_code == 404


def test_it_rg_01_registration_persists_once_and_is_listed(
    authenticated_client, db, test_context
):
    event_id = test_context["available_event_id"]
    response = authenticated_client.post(
        "/volunteer",
        data={"event_id": event_id, "hours": 3},
    )

    assert response.status_code == 200
    assert "Registration Complete" in response.text
    registrations = db.exec(select(RegisteredEvent)).all()
    assert len(registrations) == 1
    assert registrations[0].eventID == event_id
    assert registrations[0].studentID == test_context["student_id"]
    event = db.get(VolunteerEvent, event_id)
    assert event is not None
    assert event.numberRegistered == 1

    listed = authenticated_client.get("/registered-events")
    assert listed.status_code == 200
    assert "Community Build" in listed.text


def test_it_rg_02_duplicate_registration_does_not_consume_slot(
    authenticated_client, db, test_context
):
    event_id = test_context["available_event_id"]
    authenticated_client.post("/volunteer", data={"event_id": event_id, "hours": 2})
    response = authenticated_client.post(
        "/volunteer",
        data={"event_id": event_id, "hours": 2},
    )

    assert response.status_code == 400
    assert "already registered" in response.text
    assert len(db.exec(select(RegisteredEvent)).all()) == 1
    event = db.get(VolunteerEvent, event_id)
    assert event is not None
    assert event.numberRegistered == 1


@pytest.mark.parametrize(
    ("case", "event_key", "hours"),
    [
        ("full_event", "full_event_id", 1),
        ("hours_below_minimum", "available_event_id", 0),
        ("hours_above_event_limit", "available_event_id", 5),
        ("unknown_event", None, 1),
    ],
)
def test_it_rg_03_rejected_registration_does_not_write_or_increment(
    case, event_key, hours, authenticated_client, db, test_context
):
    event_id = test_context[event_key] if event_key else 99999
    response = authenticated_client.post(
        "/volunteer",
        data={"event_id": event_id, "hours": hours},
    )

    assert response.status_code == 400
    assert len(db.exec(select(RegisteredEvent)).all()) == 0
    if event_key:
        event = db.get(VolunteerEvent, event_id)
        assert event is not None
        expected = 2 if case == "full_event" else 0
        assert event.numberRegistered == expected


def test_it_rg_04_unauthenticated_student_routes_show_no_personal_data_or_mutation(
    client, db, test_context
):
    before_events = {
        event.eventID: event.numberRegistered
        for event in db.exec(select(VolunteerEvent)).all()
    }

    responses = [
        client.get("/app"),
        client.get("/volunteer", params={"event_id": test_context["available_event_id"]}),
        client.get("/registered-events"),
        client.post(
            "/volunteer",
            data={"event_id": test_context["available_event_id"], "hours": 1},
        ),
        client.post(
            f"/registered-events/{test_context['available_event_id']}/unregister"
        ),
    ]

    assert all(response.status_code == 200 for response in responses)
    assert all("Community Build" not in response.text for response in responses)
    assert all("Registration Complete" not in response.text for response in responses)
    assert len(db.exec(select(RegisteredEvent)).all()) == 0
    after_events = {
        event.eventID: event.numberRegistered
        for event in db.exec(select(VolunteerEvent)).all()
    }
    assert after_events == before_events


def test_it_rg_05_unregister_redirects_deletes_registration_and_releases_slot(
    authenticated_client, db, test_context
):
    event_id = test_context["available_event_id"]
    db.add(
        RegisteredEvent(
            eventID=event_id,
            studentID=test_context["student_id"],
            dateRegistered=date.today(),
            hoursVolunteering=2,
            eventSpecificDetails="private-registration-detail",
        )
    )
    event = db.get(VolunteerEvent, event_id)
    assert event is not None
    event.numberRegistered = 1
    db.add(event)
    db.commit()

    response = authenticated_client.post(
        f"/registered-events/{event_id}/unregister",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].endswith("/registered-events")
    assert len(db.exec(select(RegisteredEvent)).all()) == 0
    event = db.get(VolunteerEvent, event_id)
    assert event is not None
    assert event.numberRegistered == 0


def test_it_lb_01_public_leaderboard_filters_and_sorts(client):
    response = client.get("/leaderboard")

    assert response.status_code == 200
    assert "Avery Integration" in response.text
    assert "Morgan Arts" in response.text
    assert "Jordan Science" in response.text
    assert "42" in response.text

    filtered = client.get(
        "/leaderboard",
        params={"search": "Integration", "faculty": "Engineering"},
    )
    assert filtered.status_code == 200
    assert "Avery Integration" in filtered.text
    assert "Morgan Arts" not in filtered.text
    assert "Jordan Science" not in filtered.text

    sorted_by_hours = client.get(
        "/leaderboard",
        params={"sort_by": "hours", "sort_order": "desc"},
    )
    assert sorted_by_hours.status_code == 200
    assert sorted_by_hours.text.index("Jordan Science") < sorted_by_hours.text.index(
        "Avery Integration"
    )


def test_it_lb_02_student_modal_has_public_fields_not_registration_details(
    client, db, test_context
):
    response = client.get(
        "/leaderboard",
        params={"faculty": "Engineering", "sort_by": "rank", "sort_order": "asc"},
    )

    assert response.status_code == 200
    assert "Avery Integration" in response.text
    assert "Engineering" in response.text
    assert "Latest event:</strong> Community Build" in response.text
    assert "Latest award:</strong> Impact Award" in response.text
    assert "private-registration-detail" not in response.text
    assert len(db.exec(select(RegisteredEvent)).all()) == 0


def test_it_lb_02_public_leaderboard_does_not_require_authentication(client):
    response = client.get(
        "/leaderboard",
        params={"search": "Science", "faculty": "Science", "sort_by": "rank"},
    )

    assert response.status_code == 200
    assert "Jordan Science" in response.text
