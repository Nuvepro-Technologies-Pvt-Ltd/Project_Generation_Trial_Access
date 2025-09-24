import pytest
from src.app.utils import authorization_matrix

class TestAuthorizationMatrix:
    """
    Unit and integration tests for get_authorization_matrix, role definitions,
    endpoint-role authorization matrix, and error handling.
    """

    def test_get_authorization_matrix_structure_and_keys(self):
        # Arrange & Act
        matrix = authorization_matrix.get_authorization_matrix()

        # Assert
        assert isinstance(matrix, dict), "get_authorization_matrix should return a dict."
        assert set(matrix.keys()) == {"roles", "matrix", "error_handling", "examples"}, "Returned dictionary should contain all required keys."

    def test_role_definitions_content_and_valid_keys(self):
        roles = authorization_matrix.get_authorization_matrix()["roles"]
        assert isinstance(roles, dict), "Roles should be a dictionary."
        assert set(roles.keys()) == {"admin", "clinician", "researcher", "auditor"}, "All system roles should be present."
        # Validate at least description field per role
        for r in ["admin", "clinician", "researcher", "auditor"]:
            assert "description" in roles[r] and isinstance(roles[r]["description"], str) and roles[r]["description"], f"Role '{r}' must have a non-empty description."

    @pytest.mark.parametrize("endpoint,method,expected_allowed,expected_denied", [
        ("/api/inference/", "POST", {"admin", "clinician"}, {"researcher", "auditor"}),
        ("/api/v1/synthetic-data/", "POST", {"admin", "clinician", "researcher"}, {"auditor"})
    ])
    def test_matrix_role_assignments(self, endpoint, method, expected_allowed, expected_denied):
        matrix = authorization_matrix.get_authorization_matrix()["matrix"]
        found = [rule for rule in matrix if rule["Endpoint"] == endpoint and rule["HTTP Method"] == method]
        assert len(found) == 1, f"There should be exactly one rule for {endpoint} {method}."
        rule = found[0]
        assert set(rule["Allowed Roles"]) == expected_allowed, f"Allowed roles mismatch for {endpoint}."
        assert set(rule["Denied Roles"]) == expected_denied, f"Denied roles mismatch for {endpoint}."
        assert isinstance(rule["Rationale"], str) and rule["Rationale"], "Rationale must be a non-empty string."

    def test_error_handling_structure_and_codes(self):
        error_handling = authorization_matrix.get_authorization_matrix()["error_handling"]
        # Check error keys and structure
        for key, details in error_handling.items():
            assert "http_status" in details
            assert "response" in details
            http_status = details["http_status"]
            resp = details["response"]
            assert isinstance(http_status, int) and 400 <= http_status < 600, f"Invalid HTTP status for {key}"
            assert all(k in resp for k in ("error", "message")), f"Response for {key} must include 'error' and 'message'"
            assert resp["error"] and resp["message"], f"Error and message must be non-empty for {key}"

    @pytest.mark.parametrize("example_key,expected_status,expected_error", [
        ("Unauthorized Access - No Token", 401, "Missing or invalid Authorization header."),
        ("Unauthorized Access - Insufficient Role", 403, "Forbidden")
    ])
    def test_examples_unauthorized_responses(self, example_key, expected_status, expected_error):
        examples = authorization_matrix.get_authorization_matrix()["examples"]
        assert example_key in examples
        ex = examples[example_key]
        resp = ex["response"]
        assert resp["status"] == expected_status, f"Response status code should match for {example_key}"
        assert resp["body"]["error"] == expected_error, f"Error message mismatch for {example_key}"

    def test_matrix_denied_roles_are_never_in_allowed(self):
        matrix = authorization_matrix.get_authorization_matrix()["matrix"]
        for rule in matrix:
            allowed = set(rule["Allowed Roles"])
            denied = set(rule["Denied Roles"])
            assert allowed.isdisjoint(denied), f"Roles in 'Allowed Roles' should never appear in 'Denied Roles' for endpoint {rule['Endpoint']}"

    def test_invalid_role_not_in_any_matrix_rule(self):
        matrix = authorization_matrix.get_authorization_matrix()["matrix"]
        valid_roles = set(authorization_matrix.get_authorization_matrix()["roles"].keys())
        for rule in matrix:
            for role in rule["Allowed Roles"] + rule["Denied Roles"]:
                assert role in valid_roles, f"Role '{role}' in matrix is not defined in roles."

    def test_error_handling_for_undefined_error(self):
        # Negative scenario: query for an undefined error
        error_handling = authorization_matrix.get_authorization_matrix()["error_handling"]
        undefined_error = error_handling.get("Nonexistent Error Key", None)
        assert undefined_error is None, "Fetching an undefined error key should return None."

    def test_no_side_effects_on_matrix(self):
        # Arrange
        original = authorization_matrix.get_authorization_matrix()
        # Act
        out = authorization_matrix.get_authorization_matrix()
        # Assert
        assert original == out, "get_authorization_matrix should return consistent (idempotent) results on each call."

    def test_error_handling_401_and_403_examples(self):
        # Integration-like check that ERROR_HANDLING matches EXAMPLES response
        matrix = authorization_matrix.get_authorization_matrix()
        examples = matrix["examples"]
        error_handling = matrix["error_handling"]

        # No Token
        ex = examples["Unauthorized Access - No Token"]
        eh = error_handling["Missing or Invalid Auth Token"]
        assert ex["response"]["status"] == eh["http_status"], "401 Unauthorized error status should match error handling."
        assert ex["response"]["body"] == eh["response"], "401 Unauthorized example response body should match error handling config."

        # Insufficient Role
        ex = examples["Unauthorized Access - Insufficient Role"]
        eh = error_handling["Insufficient Role/Permissions"]
        assert ex["response"]["status"] == eh["http_status"], "403 Forbidden status should match error handling."
        assert ex["response"]["body"] == eh["response"], "403 Forbidden example response body should match error handling config."