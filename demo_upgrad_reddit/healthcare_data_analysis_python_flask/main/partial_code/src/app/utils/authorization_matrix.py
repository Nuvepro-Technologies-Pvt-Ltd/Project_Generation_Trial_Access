ROLE_DEFINITIONS = {
    "admin": {
        "description": "Full platform administrator. Can access and manage all endpoints, user accounts, datasets, and configurations."
    },
    "clinician": {
        "description": "Licensed healthcare provider (physician, nurse, or allied health). Can run inferences, request/generate synthetic data for patients, and view results."
    },
    "researcher": {
        "description": "Academic or industry researcher. May request synthetic data and view aggregate results but cannot access real patient clinical inference endpoints."
    },
    "auditor": {
        "description": "Regulatory or compliance auditor. Can access API logs and reports but cannot invoke model inferences or synthetic data generation."
    }
}

AUTHORIZATION_MATRIX = [
    {
        "Endpoint": "/api/inference/",
        "HTTP Method": "POST",
        "Allowed Roles": ["admin", "clinician"],
        "Denied Roles": ["researcher", "auditor"],
        "Rationale": "Inference on clinical data is restricted to licensed clinicians for direct patient care, plus admins for system/safety checks. Researchers and auditors are denied to comply with HIPAA and maintain PHI privacy."
    },
    {
        "Endpoint": "/api/v1/synthetic-data/",
        "HTTP Method": "POST",
        "Allowed Roles": ["admin", "clinician", "researcher"],
        "Denied Roles": ["auditor"],
        "Rationale": "Admins, clinicians, and researchers may generate synthetic (non-PHI) data for analytics and R&D. Auditors do not require data generation for oversight and are restricted."
    }
]

ERROR_HANDLING = {
    "Missing or Invalid Auth Token": {
        "http_status": 401,
        "response": {
            "error": "Missing or invalid Authorization header.",
            "message": "A valid Bearer token must be provided in the Authorization header."
        }
    },
    "Insufficient Role/Permissions": {
        "http_status": 403,
        "response": {
            "error": "Forbidden",
            "message": "Your account does not have permission to access this resource. Contact the administrator if you believe you are authorized."
        }
    }
}

EXAMPLES = {
    "Unauthorized Access - No Token": {
        "request": {
            "headers": {
                "Content-Type": "application/json"
            },
            "body": {
                "patient_id": "12345",
                "symptoms": ["fever"]
            }
        },
        "response": {
            "status": 401,
            "body": {
                "error": "Missing or invalid Authorization header.",
                "message": "A valid Bearer token must be provided in the Authorization header."
            }
        }
    },
    "Unauthorized Access - Insufficient Role": {
        "request": {
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer (researcher-token)"
            },
            "body": {
                "patient_id": "12345"
            }
        },
        "response": {
            "status": 403,
            "body": {
                "error": "Forbidden",
                "message": "Your account does not have permission to access this resource. Contact the administrator if you believe you are authorized."
            }
        }
    }
}

def get_authorization_matrix():
    # Instructions to implement this function:
    # 1. Collect the following data structures already initialized above in the module:
    #    - ROLE_DEFINITIONS: definitions and descriptions of available roles.
    #    - AUTHORIZATION_MATRIX: the matrix specifying which roles can/cannot access which endpoints/methods, and the rationale for each rule.
    #    - ERROR_HANDLING: guidance for consistent error responses for authentication/authorization issues.
    #    - EXAMPLES: practical request/response example scenarios for unauthorized cases.
    # 2. Return a dictionary that includes these four keys with their corresponding values grouped together:
    #    {
    #        "roles": ROLE_DEFINITIONS,
    #        "matrix": AUTHORIZATION_MATRIX,
    #        "error_handling": ERROR_HANDLING,
    #        "examples": EXAMPLES
    #    }
    pass
