from flask import request, abort
from flask_smorest import Blueprint
from flask.views import MethodView
from src.app.schemas.inference_schema import InferenceRequestSchema, InferenceResponseSchema
from src.app.services.inference_service import run_inference
import jwt
import os
from typing import List

blp = Blueprint(
    "Inference",
    "inference",
    url_prefix="/api/inference"
)

# Configuration for demo - in real world, use environment/env config and obtain the public key or secret securely
JWT_SECRET = os.environ.get('OAUTH2_JWT_SECRET', 'supersecretkey')  # change to your public/private key in production
JWT_ALG = os.environ.get('OAUTH2_JWT_ALG', 'HS256') # Typically RS256 in real deployments
REQUIRED_SCOPES = ["inference:run", "admin"]


def get_token_auth_header():
    """
    Extracts Authorization header and ensures it is a Bearer JWT token.
    """
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        abort(401, "Missing Authorization header.")
    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        abort(401, "Invalid Authorization header format. Use 'Bearer <token>'.")
    return parts[1]


def decode_token(token: str) -> dict:
    """
    Decodes the JWT token and returns claims.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG], options={"verify_aud": False})
        return payload
    except jwt.ExpiredSignatureError:
        abort(401, "Token has expired.")
    except jwt.InvalidTokenError:
        abort(401, "Invalid token.")


def requires_scope(required_scopes: List[str], payload: dict) -> bool:
    """
    Checks if JWT payload contains at least one of the required scopes.
    The 'scope' field can be space-separated string or list.
    """
    scopes = payload.get('scope')
    if isinstance(scopes, str):
        scopes = scopes.split()
    if scopes:
        for scope in required_scopes:
            if scope in scopes:
                return True
    return False

@blp.route("/")
class InferenceResource(MethodView):
    @blp.arguments(InferenceRequestSchema, location="json")
    @blp.response(200, InferenceResponseSchema)
    @blp.doc(
        tags=["AI Model Inference"],
        summary="Run AI model inference on healthcare data.",
        security=[{"BearerAuth": ["inference:run"]}]
    )
    def post(self, data):
        # 1. Extract and validate bearer token
        token = get_token_auth_header()
        payload = decode_token(token)

        # 2. Check required scopes
        if not requires_scope(REQUIRED_SCOPES, payload):
            abort(403, "Insufficient OAuth2 scope for this endpoint.")

        # 3. If valid, run underlying business logic
        result = run_inference(data)
        return result
