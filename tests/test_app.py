import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_root_redirect(client):
    """Test that GET / serves the static index page."""
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Mergington High School" in response.text


def test_get_activities(client):
    """Test GET /activities returns all activities with correct structure."""
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 4  # Four activities in the database

    # Check that all expected activities are present
    expected_activities = ["Chess Club", "Programming Class", "Gym Class", "Math Club"]
    for activity in expected_activities:
        assert activity in data

    # Check structure of one activity (Chess Club)
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)
    assert len(chess_club["participants"]) == 2  # Pre-loaded participants


def test_signup_success(client):
    """Test successful signup for an activity."""
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert result["message"] == f"Signed up {email} for {activity}"

    # Verify the participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate_registration(client):
    """Test that signing up a student already registered returns an error."""
    # Arrange
    email = "michael@mergington.edu"  # Already registered in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "already registered" in result["detail"]


def test_signup_invalid_activity(client):
    """Test signup for a non-existent activity returns 404."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]


def test_unregister_success(client):
    """Test successful unregistration from an activity."""
    # Arrange
    email = "daniel@mergington.edu"  # Already registered in Chess Club
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "message" in result
    assert result["message"] == f"Unregistered {email} from {activity}"

    # Verify the participant was removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity]["participants"]


def test_unregister_not_registered(client):
    """Test unregistering a student not registered returns an error."""
    # Arrange
    email = "notregistered@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "detail" in result
    assert "not registered" in result["detail"]


def test_unregister_invalid_activity(client):
    """Test unregistering from a non-existent activity returns 404."""
    # Arrange
    email = "test@mergington.edu"
    activity = "NonExistentActivity"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "detail" in result
    assert "Activity not found" in result["detail"]