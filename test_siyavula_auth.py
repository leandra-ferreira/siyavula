import pytest
import requests
from unittest.mock import patch
from siyavula_auth import siyavula_get_token, app

@pytest.fixture
def client():
    """Creates a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("requests.post")
def test_siyavula_get_token_success(mock_post):
    """Test successful token retrieval from Siyavula API."""
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"client_token": "mock_client_token", "user_token": "mock_user_token"}'

    mock_post.return_value = mock_response

    result = siyavula_get_token("leandra_ferreira", "mock_password")

    assert result["status"] == "success"
    assert "client_token" in result["tokens"]
    assert "user_token" in result["tokens"]

@patch("requests.post")
def test_siyavula_get_token_invalid_credentials(mock_post):
    """Test failed authentication due to invalid credentials."""
    mock_response = requests.Response()
    mock_response.status_code = 401
    mock_response._content = b'{"message": "Invalid credentials"}'

    mock_post.return_value = mock_response

    result, status_code = siyavula_get_token("wrong_user", "wrong_password")

    assert status_code == 401
    assert result["status"] == "error"
    assert "Invalid credentials" in result["message"]

@patch("requests.post")
def test_siyavula_get_token_server_error(mock_post):
    """Test Siyavula server error handling (500)."""
    mock_response = requests.Response()
    mock_response.status_code = 500
    mock_response._content = b'{"message": "Internal Server Error"}'

    mock_post.return_value = mock_response

    result, status_code = siyavula_get_token("leandra_ferreira", "mock_password")

    assert status_code == 500
    assert result["status"] == "error"
    assert "Internal Server Error" in result["message"]

def test_siyavula_auth_missing_fields(client):
    """Test authentication request with missing username or password."""
    response = client.post("/siyavula-auth", json={"username": "leandra_ferreira"})

    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert data["message"] == "Username and password are required"
