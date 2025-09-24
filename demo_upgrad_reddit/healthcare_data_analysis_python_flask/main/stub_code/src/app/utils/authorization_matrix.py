# Define the ROLE_DEFINITIONS dictionary to describe each role and its permissions
# ROLE_DEFINITIONS = {
#     "admin": {"description": "..."},
#     "clinician": {"description": "..."},
#     ...
# }

# Define the AUTHORIZATION_MATRIX as a list of dictionaries, each representing an endpoint's allowed/denied roles
# AUTHORIZATION_MATRIX = [
#     {
#         "Endpoint": "/api/inference/",
#         "HTTP Method": "POST",
#         "Allowed Roles": ["admin", "clinician"],
#         "Denied Roles": ["researcher", "auditor"],
#         "Rationale": "..."
#     },
#     ...
# ]

# Define the ERROR_HANDLING dictionary mapping error situations to http status codes and response content
# ERROR_HANDLING = {
#     "Missing or Invalid Auth Token": {...},
#     "Insufficient Role/Permissions": {...}
# }

# Define EXAMPLES dictionary providing example request/response payloads for common error cases
# EXAMPLES = {
#     "Unauthorized Access - No Token": {...},
#     "Unauthorized Access - Insufficient Role": {...}
# }

# Define the function get_authorization_matrix which returns a dictionary containing all the above data
# def get_authorization_matrix():
#     """
#     Return a dictionary with keys: roles, matrix, error_handling, and examples
#     Each key contains the corresponding definitions described above.
#     """
#     pass
