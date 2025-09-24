import pytest
from flask import Flask
from flask_smorest import Api
from unittest.mock import patch, MagicMock
import jwt
import datetime
import os
from src.app.routes.inference_routes import blp, JWT_SECRET, JWT_ALG
from src.app.services import inference_service

# Test suite for Secure Model Inference Endpoint with OAuth2 Bearer Token and Scope Enforcement
# Uses pytest as primary framework and unittest.mock for mocking dependencies

@pytest.fixture
def app():
    # Configure Flask app and register blueprint
    app = Flask(__name__)
    app.config['TESTING'] = True
    api = Api(app)
    api.register_blueprint(blp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def _make_jwt_token(payload_override=None, secret=JWT_SECRET, alg=JWT_ALG, expired=False):
    """Helper to create a signed JWT token for tests."""
    payload = {
        'sub': 'test-user',
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=(-1 if expired else 60)),
        'scope': "inference:run admin"
    }
    if payload_override:
        payload.update(payload_override)
    return jwt.encode(payload, secret, algorithm=alg)

def test_post_inference_success(client, monkeypatch):
    """
    Test successful inference when provided with valid bearer token and required scope.
    """
    token = _make_jwt_token()
    test_payload = {
        "patient_id": "12345",
        "symptoms": ["fever", "headache"],
        "clinical_text": "Patient has a high fever and severe headache."
    }
    expected_result = {
        "diagnosis": "flu",
        "confidence": 0.94,
        "entities": [{
            "entity": "fever", "label": "symptom", "value": "high fever"
        }]
    }
    # Patch run_inference to avoid business logic dependency
    with patch('src.app.services.inference_service.run_inference', return_value=expected_result) as mock_run_inf:
        response = client.post(
            '/api/inference/',
            json=test_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"
        assert response.json == expected_result, "Response JSON does not match expected inference output."
        mock_run_inf.assert_called_once_with(test_payload)

def test_post_inference_missing_authorization(client):
    """
    Test endpoint returns 401 if Authorization header is missing.
    """
    response = client.post(
        '/api/inference/',
        json={"patient_id": "1"}
    )
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    assert b"Missing Authorization header" in response.data

def test_post_inference_malformed_authorization(client):
    """
    Test endpoint returns 401 if Authorization header is malformed.
    """
    token = _make_jwt_token()
    malformed_headers = [
        {"Authorization": "Bearer"},
        {"Authorization": f"Token {token}"},
        {"Authorization": f"Bearer {token} extra"}
    ]
    for h in malformed_headers:
        response = client.post(
            '/api/inference/',
            json={"patient_id": "1"},
            headers=h
        )
        assert response.status_code == 401, f"Malformed header {h['Authorization']} should get 401"

def test_post_inference_expired_token(client):
    """
    Test endpoint returns 401 if JWT token is expired.
    """
    token = _make_jwt_token(expired=True)
    response = client.post(
        '/api/inference/',
        json={"patient_id": "1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert b"Token has expired." in response.data

def test_post_inference_invalid_token(client):
    """
    Test endpoint returns 401 if JWT token signature is invalid or corrupted.
    """
    # Use wrong secret for signature
    token = _make_jwt_token(secret="not_the_right_secret")
    response = client.post(
        '/api/inference/',
        json={"patient_id": "1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert b"Invalid token." in response.data

def test_post_inference_missing_scope(client):
    """
    Test endpoint returns 403 if JWT token missing required scope.
    """
    token = _make_jwt_token(payload_override={"scope": "other:read"})
    response = client.post(
        '/api/inference/',
        json={"patient_id": "1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert b"Insufficient OAuth2 scope" in response.data

def test_post_inference_scope_as_list(client, monkeypatch):
    """
    Test endpoint accepts 'scope' as list type and passes if required scope present.
    """
    token = _make_jwt_token(payload_override={"scope": ["read", "inference:run"]})
    expected_result = {"diagnosis": "abc", "confidence": 0.9, "entities": []}
    with patch('src.app.services.inference_service.run_inference', return_value=expected_result):
        response = client.post(
            '/api/inference/',
            json={"patient_id": "xyz"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json == expected_result

def test_post_inference_request_validation(client):
    """
    Test endpoint returns 400 on missing required request field(s).
    """
    token = _make_jwt_token()
    # 'patient_id' is required
    response = client.post(
        '/api/inference/',
        json={"symptoms": ["test"]},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400, f"Should fail schema validation with 400, got {response.status_code}"

# Additional: test for input security edge (very long texts, injection attempt)
def test_post_inference_security_input_injection(client, monkeypatch):
    """
    Test input with potential injection to ensure no unexpected behavior (inference_service should get original data).
    """
    token = _make_jwt_token()
    payload = {
        "patient_id": "inject'; DROP TABLE patients;--",
        "clinical_text": "<script>alert('XSS')</script>",
        "symptoms": ["fever"]
    }
    expected_result = {
        "diagnosis": "safe",
        "confidence": 1.0,
        "entities": []
    }
    with patch('src.app.services.inference_service.run_inference', return_value=expected_result) as m:
        response = client.post(
            '/api/inference/',
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, "Should process input safely"
        m.assert_called_once_with(payload)

# Advanced: parameterized test for error scenarios
import pytest
@pytest.mark.parametrize("payload,override_scope,expected_status,expect_msg", [
    ({"patient_id": "1"}, "inference:run", 200, None),
    ({}, "inference:run", 400, b"'patient_id' is a required property"),
    ({"patient_id": "1"}, "", 403, b"Insufficient OAuth2 scope"),
    ({"patient_id": "1"}, "wrong:scope", 403, b"Insufficient OAuth2 scope")
])
def test_post_inference_parameterized(client, monkeypatch, payload, override_scope, expected_status, expect_msg):
    token = _make_jwt_token(payload_override={"scope": override_scope})
    expected_result = {"diagnosis": "zzz", "confidence": 1.0, "entities": []}
    with patch('src.app.services.inference_service.run_inference', return_value=expected_result):
        response = client.post(
            '/api/inference/',
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == expected_status, f"{payload}, {override_scope} -> {response.status_code}"
        if expect_msg is not None:
            assert expect_msg in response.data, f"Should include message {expect_msg}"