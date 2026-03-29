import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)

# Initial activities data for resetting
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 25,
        "participants": []
    },
    "Debate Club": {
        "description": "Practice public speaking and argumentation",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Tuesdays, 4:00 - 5:30 PM",
        "max_participants": 16,
        "participants": []
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    global activities
    activities.clear()
    activities.update(initial_activities)


def test_root_redirect():
    """Test that GET / redirects to /static/index.html"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_get_activities():
    """Test GET /activities returns all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # All activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    response = client.post("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up test@mergington.edu for Basketball Team" in data["message"]
    # Verify added to participants
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" in activities_data["Basketball Team"]["participants"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_signup_already_signed_up():
    """Test signup when already signed up"""
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    # Try again
    response = client.post("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First signup
    client.post("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered test@mergington.edu from Basketball Team" in data["message"]
    # Verify removed from participants
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "test@mergington.edu" not in activities_data["Basketball Team"]["participants"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    """Test unregister when not signed up"""
    response = client.delete("/activities/Basketball%20Team/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student not signed up for this activity"