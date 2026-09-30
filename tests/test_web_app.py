import pytest
from fastapi.testclient import TestClient

def test_web_app_routes():
    from src.web.app import app
    client = TestClient(app)
    
    # Test dashboard page
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AutoJobForge" in resp.text
    assert "Applications" in resp.text

    # Test profile page
    resp = client.get("/profile")
    assert resp.status_code == 200
    assert "Profile" in resp.text

    # Test settings page
    resp = client.get("/settings")
    assert resp.status_code == 200
    assert "Settings" in resp.text
