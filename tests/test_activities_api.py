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
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_success():
    new_email = "new_student@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": new_email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"

    # Verify participant was added
    response = client.get("/activities")
    assert new_email in response.json()["Chess Club"]["participants"]


def test_signup_for_activity_already_registered():
    email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_activity_activity_not_found():
    response = client.post("/activities/NoSuchActivity/signup", params={"email": "foo@bar.com"})
    assert response.status_code == 404


def test_remove_participant_success():
    target = "james@mergington.edu"
    response = client.delete(f"/activities/Basketball Team/participants/{target}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {target} from Basketball Team"

    response = client.get("/activities")
    assert target not in response.json()["Basketball Team"]["participants"]


def test_remove_participant_not_found():
    response = client.delete("/activities/Chess Club/participants/nonexistent@mergington.edu")
    assert response.status_code == 404
