import pytest
from flask import Flask
from flask_smorest import Api
from app.routes.health_routes import blp as health_blp

import types

@pytest.fixture
def app():
    # Arrange: create and configure a Flask app instance with smorest
    app = Flask(__name__)
    app.config['API_TITLE'] = 'Test API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.2'
    api = Api(app)
    api.register_blueprint(health_blp)
    return app

@pytest.fixture
def client(app):
    # Flask test client
    return app.test_client()

def test_get_health_status_ok(client):
    # Act: call the health endpoint
    response = client.get('/health/')
    # Assert: Health endpoint should return HTTP 200, body {"status": "ok"}
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.is_json, "Expected JSON response body"
    data = response.get_json()
    assert data == {"status": "ok"}, f"Expected body {{'status': 'ok'}}, got {data}"

def test_get_health_status_extra_methods_not_allowed(client):
    # Act & Assert: Only GET method allowed, others should 405
    for method in ['post', 'put', 'patch', 'delete']:
        http_method = getattr(client, method)
        response = http_method('/health/')
        assert response.status_code == 405, f"Method {method.upper()} should NOT be allowed, got {response.status_code}"

@pytest.mark.parametrize("invalid_url", [
    '/health',  # missing trailing slash (could be redirected by Flask)
    '/health/foo',
    '/health//'
])
def test_get_health_invalid_url_returns_404(client, invalid_url):
    # Edge Case: wrong path gives 404
    response = client.get(invalid_url)
    assert response.status_code in (404, 308), f"Expected 404 or redirect, got {response.status_code} for {invalid_url}"

# Security test: ensure response does not leak internal server data
def test_health_status_response_does_not_leak_internal_data(client):
    response = client.get('/health/')
    assert 'server' not in response.headers.get('Content-Type', '').lower(), "Unexpected header in response"
    data = response.get_json()
    assert set(data.keys()) == {'status'}, f"Unexpected keys in health response: {list(data.keys())}"