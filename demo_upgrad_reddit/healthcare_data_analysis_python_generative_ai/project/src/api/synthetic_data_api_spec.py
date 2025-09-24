from typing import List, Dict, Any

def get_api_specification() -> Dict[str, Any]:
    """
    Returns the RESTful API design specification for synthetic healthcare data generation
    adhering to FHIR interoperability and privacy standards.
    """
    return {
        "description": "RESTful API for requesting, generating, and retrieving synthetic healthcare data (tabular and clinical text) with FHIR compliance, privacy mechanisms, logging, and auditability.",
        "authentication": {
            "methods": [
                {
                    "type": "OAuth2",
                    "requirement": "Required for all endpoints. Client must obtain an access token via the /auth/token endpoint and include it in the Authorization header using Bearer scheme.",
                    "scopes": ["data:generate", "data:read"],
                    "compliance": "Covers HIPAA technical safeguard for authentication and access control. Logs all authentication events."
                }
            ]
        },
        "endpoints": [
            {
                "name": "Request Synthetic Tabular Data Generation",
                "method": "POST",
                "endpoint": "/api/v1/data/tabular/generate",
                "request_body": {
                    "fhir_resource_type": "string (e.g., 'Patient', 'Observation')",
                    "num_rows": "integer; number of synthetic samples to generate",
                    "deidentification": {
                        "remove_cols": "list of strings; columns to drop for privacy (PII/PHI)",
                        "dp_epsilon": "float (optional); differential privacy epsilon value",
                        "compliance_level": "string (e.g., 'high', 'moderate', 'audit'); selects pre-defined privacy profiles"
                    },
                    "downstream_task": "string (optional); task type (classification, regression, etc.) to inform data generation utility"
                },
                "response": {
                    "synth_id": "string; unique job/resource ID",
                    "status": "string; 'pending', 'completed', or 'failed'",
                    "download_url": "string (optional; present if completed); presigned link to CSV or JSON file with synthetic data",
                    "run_report": "object; metrics including dataset/model version, privacy metrics (e.g., DP epsilon, MIA risk), utility evaluation, audit log ref"
                },
                "logging": {
                    "access_audit": "Logs user ID, timestamp, parameters, and outcome for HIPAA compliance.",
                    "event_monitoring": "Logs system/resource performance, failures, throughput." 
                },
                "usage": "For programmatic batch synthetic tabular data generation."
            },
            {
                "name": "Request Synthetic Clinical Text Data Generation",
                "method": "POST",
                "endpoint": "/api/v1/data/text/generate",
                "request_body": {
                    "fhir_resource_type": "string; target FHIR resource (e.g., 'Condition', 'Procedure')",
                    "num_records": "integer; how many synthetic clinical notes/texts to generate",
                    "entity_labels": "list of strings (optional); NER label set for text entities",
                    "deidentification": {
                        "remove_fields": "list of strings; FHIR fields to omit for privacy",
                        "custom_regex_patterns": "list of strings (optional); custom regex patterns for extra PHI removal",
                        "compliance_level": "string; privacy profile"
                    }
                },
                "response": {
                    "synth_id": "unique string ID",
                    "status": "'pending', 'completed', 'failed'",
                    "download_url": "string (if completed); download presigned link for generated text in FHIR/JSONL",
                    "run_report": "metrics and linkage to logs/audit trail"
                },
                "logging": {
                    "access_audit": "Logs request details for traceability and regulatory compliance.",
                    "event_monitoring": "Monitors success/failure, resource use per job."
                },
                "usage": "Generates synthetic clinical free-text records in FHIR-compatible format."
            },
            {
                "name": "Retrieve Synthetically Generated Data via Job ID",
                "method": "GET",
                "endpoint": "/api/v1/data/{synth_id}",
                "request_params": {
                    "synth_id": "string; unique synthetic job/resource ID. Path param."
                },
                "response": {
                    "status": "'pending', 'completed', or 'failed'",
                    "download_url": "(if completed) download link",
                    "run_report": "object; job details, privacy/utility/audit metrics"
                },
                "logging": {
                    "access_audit": "Each access to synthetic data is logged to immutable audit store."
                },
                "usage": "Enables polling/callback pattern for job status and result retrieval."
            },
            {
                "name": "List Available FHIR Resource Types",
                "method": "GET",
                "endpoint": "/api/v1/config/fhir_resources",
                "response": {
                    "resources": "list of supported FHIR resource type strings"
                },
                "logging": {
                    "access_audit": "Resource list queries are logged for monitoring but do not require special authorization."
                },
                "usage": "For UI and programmatic discovery of compatible FHIR objects to synthesize."
            },
            {
                "name": "Authentication Token Endpoint",
                "method": "POST",
                "endpoint": "/auth/token",
                "request_body": {
                    "client_id": "string",
                    "client_secret": "string",
                    "grant_type": "string; only 'client_credentials' allowed"
                },
                "response": {
                    "access_token": "JWT string",
                    "expires_in": "int (seconds)"
                },
                "logging": {
                    "access_audit": "Tracks token issuance, IP, and scopes for all clients."
                },
                "usage": "Required prerequisite for all data-related API calls."
            }
        ],
        "logging_and_monitoring": {
            "audit_trails": "Every API interaction is tied to a user/service ID with parameters, timestamps, and result codes stored in an immutable, queryable journal for regulatory inspection (logs written to WORM-compliant storage or cryptographically verifiable archive).",
            "performance_monitoring": "Each endpoint action is measured via system metrics (latency, resource load, failure rate) and triggers alerts if anomalous patterns are detected.",
            "privacy_monitoring": "Synthetic data requests are assessed post-creation for privacy metrics (e.g., differential privacy, MIA), and anomalous/unsafe requests trigger alerts and block download access until reviewed.",
            "traceability": "All requests and data are fully traceable via synth_id and user/service principal, supporting security and incident response."
        },
        "compliance": {
            "hipaa": "Authentication, access control, logging, and privacy features are aligned with HIPAA technical safeguard and audit (45 CFR 164.312).",
            "gdpr": "All endpoints requiring data transformation support data minimization and audit, and sensitive fields are scrubbed or never synthesized as per privacy profile."
        }
    }
