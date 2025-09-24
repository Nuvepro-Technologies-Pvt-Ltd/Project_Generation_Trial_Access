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
    # INSTRUCTIONS:
    # 1. Retrieve the 'Authorization' header from the incoming request.
    # 2. If the header is missing, abort with 401 and a message indicating a missing Authorization header.
    # 3. Split the Authorization header by whitespace and validate the format is 'Bearer <token>'.
    #    - If not, abort with 401 and an appropriate error message.
    # 4. Return the token (the part after 'Bearer') for further processing.
    pass


def decode_token(token: str) -> dict:
    """
    Decodes the JWT token and returns claims.
    """
    # INSTRUCTIONS:
    # 1. Attempt to decode the provided JWT token using the JWT_SECRET and JWT_ALG variables.
    #    - Make sure to ignore audience verification for this demo (options={"verify_aud": False}).
    # 2. If the token is expired, abort with 401 and indicate the token has expired.
    # 3. If the token is otherwise invalid, abort with 401 and indicate an invalid token.
    # 4. If successful, return the decoded payload (claims dictionary).
    pass


def requires_scope(required_scopes: List[str], payload: dict) -> bool:
    """
    Checks if JWT payload contains at least one of the required scopes.
    The 'scope' field can be space-separated string or list.
    """
    # INSTRUCTIONS:
    # 1. Extract the 'scope' field from the payload.
    # 2. If the scope is a string, split it by whitespace to get a list.
    # 3. If the scope is a list, use it directly.
    # 4. Check if ANY of the required_scopes are present in the user's scope list.
    #    - Return True if at least one match; otherwise, return False.
    pass

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
        # INSTRUCTIONS:
        # 1. Call get_token_auth_header() to extract and validate the Bearer token from the request.
        # 2. Pass the extracted token to decode_token() to verify and decode it.
        # 3. Check if the user has at least one required scope by calling requires_scope(REQUIRED_SCOPES, payload).
        #    - If not, abort with 403 and a message indicating insufficient scope.
        # 4. If the user is authorized, call run_inference(data) with the input and return its result.
        pass
