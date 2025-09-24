from flask import request
from flask_smorest import Blueprint
from flask.views import MethodView
from src.app.schemas.synthetic_data_schema import SyntheticDataRequestSchema, SyntheticDataResponseSchema
from src.app.services.synthetic_data_service import generate_synthetic_data

blp = Blueprint(
    "SyntheticDataGeneration",
    "synthetic_data_generation",
    url_prefix="/api/v1/synthetic-data"
)

@blp.route("/")
class SyntheticDataResource(MethodView):
    @blp.arguments(SyntheticDataRequestSchema, location="json")
    @blp.response(200, SyntheticDataResponseSchema)
    @blp.doc(tags=["Synthetic Data Generation"], summary="Request AI-generated synthetic healthcare data.", security=[{"BearerAuth": []}])
    def post(self, data):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            from flask import abort
            abort(401, "Missing or invalid Authorization header.")
        result = generate_synthetic_data(data)
        return result