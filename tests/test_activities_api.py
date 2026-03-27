from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Save original state and restore between tests to avoid cross-test pollution
original_activities = None


def setup_function():
    global original_activities
    import copy
    original_activities = copy.deepcopy(activities)


def teardown_function():
    activities.clear()
    activities.update(original_activities)


def test_get_activities():
    # Arrange
    # No setup needed; activities are pre-loaded

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    # Arrange
    new_email = "new_student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"

    # Verify participant was added
    response = client.get("/activities")
    assert new_email in response.json()["Chess Club"]["participants"]


def test_signup_for_activity_already_registered():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_activity_not_found():
    # Arrange
    activity_name = "NoSuchActivity"
    email = "foo@bar.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_remove_participant_success():
    # Arrange
    activity_name = "Basketball Team"
    target_email = "james@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{target_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {target_email} from {activity_name}"

    # Verify participant was removed
    response = client.get("/activities")
    assert target_email not in response.json()[activity_name]["participants"]


def test_remove_participant_not_found():
    # Arrange
    activity_name = "Chess Club"
    nonexistent_email = "nonexistent@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{nonexistent_email}")

    # Assert
    assert response.status_code == 404
