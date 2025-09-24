import os

class Config:
    SECRET_KEY = os.environ.get("API_SECRET_KEY", "unsafe-dev-key")
    # SECRET_KEY is required by Flask applications for session management.

    OPENAPI_ENABLE_OAUTH2 = True
    # Enables OAuth2 support for the OpenAPI docs UI, if supported by the documentation generator.
    
    OAUTH2_CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID", "dev-oauth2-client")
    # The OAuth2 client ID should be set in production via environment variable.
    
    OAUTH2_CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET", "dev-oauth2-secret")
    # The OAuth2 client secret for confidential client scenarios.
    
    PROPAGATE_EXCEPTIONS = True
    # Ensures Flask propagates exceptions for proper error reporting and testing.

class ProductionConfig(Config):
    ENV = "production"
    DEBUG = False
    # Explicit production environment settings to disable debug mode.
