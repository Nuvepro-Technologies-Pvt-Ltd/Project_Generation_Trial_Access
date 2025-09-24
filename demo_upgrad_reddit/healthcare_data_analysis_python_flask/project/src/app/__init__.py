from flask import Flask
from flask_smorest import Api
from src.app.routes.inference_routes import blp as inference_blp
from src.app.routes.synthetic_data_routes import blp as synthetic_data_blp
from src.app.routes.health_routes import blp as health_blp

def create_app():
    app = Flask(__name__)
    app.config["API_TITLE"] = "Healthcare AI Inference API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.23.11/"
    api = Api(app)
    api.register_blueprint(inference_blp)
    api.register_blueprint(synthetic_data_blp)
    api.register_blueprint(health_blp)
    return app