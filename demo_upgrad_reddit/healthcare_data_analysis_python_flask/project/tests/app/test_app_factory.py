import pytest
from flask import Flask
from flask_smorest import Api
from unittest.mock import patch, MagicMock
from src.app import create_app

class DummyBlueprint:
    # Mock Blueprint object, just needs to have a name
    name = "dummy_blp"

def test_create_app_returns_flask_instance():
    # Arrange & Act
    app = create_app()
    # Assert
    assert isinstance(app, Flask), "create_app should return a Flask app instance"

def test_app_configurations_set():
    app = create_app()
    assert app.config["API_TITLE"] == "Healthcare AI Inference API"
    assert app.config["API_VERSION"] == "v1"
    assert app.config["OPENAPI_VERSION"] == "3.0.2"
    assert app.config["OPENAPI_URL_PREFIX"] == "/"
    assert app.config["OPENAPI_SWAGGER_UI_PATH"] == "/swagger-ui"
    assert app.config["OPENAPI_SWAGGER_UI_URL"] == "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/"

def test_blueprints_registered(monkeypatch):
    # Patch blueprints imported in __init__, so we can track registration
    dummy_inference = DummyBlueprint()
    dummy_synth = DummyBlueprint()
    dummy_health = DummyBlueprint()
    # Patch the Api class to a MagicMock to track register_blueprint calls
    with patch("src.app.__init__.inference_blp", dummy_inference), \
         patch("src.app.__init__.synthetic_data_blp", dummy_synth), \
         patch("src.app.__init__.health_blp", dummy_health), \
         patch("src.app.__init__.Api") as MockApi:
        api_instance = MagicMock()
        MockApi.return_value = api_instance
        from src.app import create_app as patched_create_app
        app = patched_create_app()
        # Assert correct blueprint registration
        calls = [c[0][0] for c in api_instance.register_blueprint.call_args_list]
        assert dummy_inference in calls, "Inference blueprint not registered"
        assert dummy_synth in calls, "Synthetic data blueprint not registered"
        assert dummy_health in calls, "Health blueprint not registered"

def test_app_integration_routes(monkeypatch):
    # Test all three blueprints are actually accessible as Flask blueprints in the app context
    app = create_app()
    # The blueprints should be registered internally by flask-smorest
    # We can check the Flask app has the smorest Api extension
    assert hasattr(app, "extensions"), "App does not have extensions registry"
    assert "smorest" in app.extensions, "FlaskSmorest API extension not found in app.extensions"

# Edge case: What if a blueprint is missing? Patch one as None and test error handling
@pytest.mark.parametrize("missing_blp_name", ["inference_blp", "synthetic_data_blp", "health_blp"])
def test_missing_blueprint_fails_registration(missing_blp_name, monkeypatch):
    with patch(f"src.app.__init__.{missing_blp_name}", None):
        with pytest.raises(Exception):
            # Should raise when Api attempts to register a None blueprint
            create_app()

# Note: Since Flask apps are stateful and testing Swagger UI path/URL is static config,
# there is no need to test their HTTP serving here, as route serving is the responsibility of blueprints themselves.