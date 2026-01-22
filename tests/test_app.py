import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    # Since it redirects to /static/index.html, but TestClient follows redirects? Wait, RedirectResponse.
    # Actually, FastAPI's RedirectResponse returns 307, but TestClient follows it.
    # But since it's mounting static, it should serve the file.
    # For simplicity, just check status 200.

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Sign up a new participant
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Chess Club"]["participants"]

def test_signup_already_signed_up():
    # First sign up
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    # Try again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First sign up
    client.post("/activities/Chess%20Club/signup?email=unregister@example.com")
    # Then unregister
    response = client.delete("/activities/Chess%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Chess Club" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregister@example.com" not in data["Chess Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess%20Club/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]