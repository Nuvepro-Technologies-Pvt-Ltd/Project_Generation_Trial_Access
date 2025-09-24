from flask import Flask
from flask_smorest import Api
from src.app.routes.inference_routes import blp as inference_blp
from src.app.routes.synthetic_data_routes import blp as synthetic_data_blp
from src.app.routes.health_routes import blp as health_blp

def create_app():
    # Create a new Flask app instance
    app = Flask(__name__)
    
    # Set configuration options for the Flask app, including API metadata and OpenAPI settings
    # - Set 'API_TITLE' to the desired title for the API
    # - Set 'API_VERSION' for versioning
    # - Set 'OPENAPI_VERSION' to the desired OpenAPI spec version
    # - Set 'OPENAPI_URL_PREFIX' for the API docs prefix
    # - Set 'OPENAPI_SWAGGER_UI_PATH' for the documentation UI path
    # - Set 'OPENAPI_SWAGGER_UI_URL' to the URL for Swagger UI resources
    app.config["API_TITLE"] = "Healthcare AI Inference API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/"

    # Initialize an Api instance with the Flask app
    api = Api(app)
    
    # Register all the blueprints with the API instance for the respective modules:
    # - inference_blp: Blueprint for inference routes
    # - synthetic_data_blp: Blueprint for synthetic data routes
    # - health_blp: Blueprint for health check routes (Your task is to ensure this is registered)
    # 1. Make sure that api.register_blueprint(health_blp) is called to register health_blp
    # 2. You may want to check the order of registrations depending on route precedence requirements
    api.register_blueprint(inference_blp)
    api.register_blueprint(synthetic_data_blp)
    api.register_blueprint(health_blp)

    # Return the configured Flask app instance
    return app