from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models
from app.database import engine as application_engine
from app.database import get_session
from app.main import app
from app.models.student import Student
from app.models.user import User
from app.models.volunteer_event import VolunteerEvent
from app.utilities.security import encrypt_password


FIXTURE_PASSWORD = "qa-integration-password"
USER_ID = 91001
STUDENT_ID = 92001
AVAILABLE_EVENT_ID = 93001
FULL_EVENT_ID = 93002
SECOND_EVENT_ID = 93003


@pytest.fixture
def test_context():
    """Create an isolated schema and deterministic Awardemics fixture set."""
    database_uri = "sqlite://"
    assert database_uri != "sqlite:///database.db"

    engine = create_engine(
        database_uri,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    assert str(engine.url) != str(application_engine.url)
    assert str(engine.url) == "sqlite://"
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            id=USER_ID,
            username="qa_student_91001",
            email="qa_student_91001@example.test",
            password=encrypt_password(FIXTURE_PASSWORD),
            role="",
        )
        session.add(user)
        session.add(
            Student(
                studentID=STUDENT_ID,
                userID=USER_ID,
                name="Avery Integration",
                faculty="Engineering",
                degreeLevel="Undergraduate",
                year=3,
                totalHours=42,
                rank=2,
                awardCount=3,
                latestEvent="Community Build",
                latestAward="Impact Award",
            )
        )
        session.add(
            Student(
                studentID=92002,
                name="Morgan Arts",
                faculty="Arts",
                degreeLevel="Undergraduate",
                year=2,
                totalHours=18,
                rank=4,
                awardCount=1,
                latestEvent="Campus Garden",
                latestAward="Service Award",
            )
        )
        session.add(
            Student(
                studentID=92003,
                name="Jordan Science",
                faculty="Science",
                degreeLevel="Postgraduate",
                year=1,
                totalHours=65,
                rank=1,
                awardCount=5,
                latestEvent="Science Outreach",
                latestAward="Leadership Award",
            )
        )
        future = date.today() + timedelta(days=30)
        session.add_all(
            [
                VolunteerEvent(
                    eventID=AVAILABLE_EVENT_ID,
                    name="Community Build",
                    organisation="QA Community",
                    location="North Hall",
                    description="Build useful resources with local volunteers.",
                    image="",
                    date=future,
                    numberOfSlots=5,
                    numberRegistered=0,
                    hours=4,
                    eventStatus="Available",
                ),
                VolunteerEvent(
                    eventID=FULL_EVENT_ID,
                    name="Full Pantry Shift",
                    organisation="QA Pantry",
                    location="South Hall",
                    description="This event has no remaining spaces.",
                    image="",
                    date=future + timedelta(days=1),
                    numberOfSlots=2,
                    numberRegistered=2,
                    hours=3,
                    eventStatus="Full",
                ),
                VolunteerEvent(
                    eventID=SECOND_EVENT_ID,
                    name="River Cleanup",
                    organisation="QA Environment",
                    location="River Park",
                    description="Help restore the river trail.",
                    image="",
                    date=future + timedelta(days=2),
                    numberOfSlots=8,
                    numberRegistered=0,
                    hours=2,
                    eventStatus="Available",
                ),
            ]
        )
        session.commit()

    previous_overrides = app.dependency_overrides.copy()

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    try:
        yield {
            "engine": engine,
            "user_id": USER_ID,
            "student_id": STUDENT_ID,
            "available_event_id": AVAILABLE_EVENT_ID,
            "full_event_id": FULL_EVENT_ID,
            "second_event_id": SECOND_EVENT_ID,
        }
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        engine.dispose()


@pytest.fixture
def client(test_context):
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def authenticated_client(client):
    response = client.post(
        "/login",
        data={"username": "qa_student_91001", "password": FIXTURE_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "access_token" in client.cookies
    return client


@pytest.fixture
def db(test_context):
    with Session(test_context["engine"]) as session:
        yield session
