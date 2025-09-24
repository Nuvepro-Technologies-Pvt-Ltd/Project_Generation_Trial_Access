
class Config:
    # TODO: Set SECRET_KEY using environment variable or default for session management
    SECRET_KEY = None
    
    # TODO: Enable OAuth2 for OpenAPI docs UI as needed
    OPENAPI_ENABLE_OAUTH2 = None
    
    # TODO: Retrieve OAUTH2_CLIENT_ID from environment or use default for OAuth2 client
    OAUTH2_CLIENT_ID = None
    
    # TODO: Retrieve OAUTH2_CLIENT_SECRET from environment or use default for confidential clients
    OAUTH2_CLIENT_SECRET = None
    
    # TODO: Set to propagate exceptions appropriately for error reporting
    PROPAGATE_EXCEPTIONS = None

class ProductionConfig(Config):
    # TODO: Set environment to 'production' and disable debug mode
    ENV = None
    DEBUG = None
