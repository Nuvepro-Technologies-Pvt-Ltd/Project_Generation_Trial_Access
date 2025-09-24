import re
import pytest

# Test suite for validating the Dockerization Plan document's compliance, completeness, and critical cloud/healthcare operational requirements.
# Focuses on: essentials coverage, configuration injection, PHI/PII/data controls, Azure specifics, health-checks, resilience, logging, compliance language.

import re
import pytest

# Constants for expected values/sections, to avoid magic strings and ease maintenance.
MANDATORY_SECTIONS = [
    'Component and Dependency Inventory',
    'Secure Handling of Sensitive Configuration',
    'Storage Management/Healthcare Data Compliance',
    'Docker Build, Tag, and Push Process',
    'Production Readiness: Health Checks and Orchestration',
    'Audit/Compliance Traceability',
    'Summary Table'
]

AZURE_KEYWORDS = [
    'Azure', 'azure', 'Web App for Containers', 'Azure Kubernetes Service', 'AKS',
    'Azure Key Vault', 'Managed Identities', 'Azure App Gateway',
    'Azure App Service', 'azurecr', 'Bicep', 'ARM templates', 'Azure Files',
    'Azure Blob Storage', 'Azure Monitor', 'Application Insights'
]

PHI_PII_TERMS = ['PHI', 'PII', 'compliance', 'HIPAA']

SECRETS_LANG = [
    'NEVER bake secrets', 'ENV variables', 'environment variable', 'secrets',
    'Key Vault', '.env file', 'credentials', 'permissions', 'access control',
    'encryption', 'encrypted', 'managed identities'
]

def get_plan_text():
    """Load Dockerization plan as fixture/constant for tests. In a real test suite, this would read the file from disk."""
    # This string simulates retrieving the actual documentation.
    return open('src/app/utils/docker_deployment_plan.md', encoding='utf-8').read()

@pytest.fixture(scope="module")
def docker_plan():
    return get_plan_text()

@pytest.mark.parametrize("section", MANDATORY_SECTIONS)
def test_section_presence(docker_plan, section):
    """Test that all mandatory sections are present in the Dockerization plan."""
    assert section in docker_plan, f"Section '{section}' not found in Dockerization plan."

def test_azure_references_present(docker_plan):
    """Test that Dockerization plan references Azure-specific processes, ensuring cloud compliance."""
    found = any(word in docker_plan for word in AZURE_KEYWORDS)
    assert found, "Azure-specific keywords not found; ensure cloud platform instructions are present."

def test_secrets_handling_best_practices(docker_plan):
    """Test presence of correct secrets/configuration management best practices (env vars, Key Vault, never in image, etc)."""
    matches = sum(1 for term in SECRETS_LANG if term.lower() in docker_plan.lower())
    assert matches >= len(SECRETS_LANG) // 2, "Not enough best practice secrets/config patterns found."

def test_health_check_example_present(docker_plan):
    """Test that a health check endpoint and Dockerfile/AKS liveness/readiness probe example are present."""
    # Look for /health endpoint
    assert '/health' in docker_plan,
           "Health check endpoint '/health' should be mentioned."
    # Look for HEALTHCHECK in Dockerfile or AKS readiness probes
    healthcheck_pattern = r'HEALTHCHECK.+(curl|http|exit)'
    probe_pattern = r'readiness probes?'
    assert re.search(healthcheck_pattern, docker_plan, re.IGNORECASE) or \
           re.search(probe_pattern, docker_plan, re.IGNORECASE), "No Docker or Azure healthcheck example found."

def test_persistence_and_stateless_guidance(docker_plan):
    """Ensure plan enforces stateless app container, persistent storage via Azure, no PHI/PII in fs, and correct mounting."""
    stateless = 'stateless container' in docker_plan.lower()
    external_vol = any(storage in docker_plan for storage in ["Azure Files", "Blob Storage", "/data", "volume", "mount"])
    no_phi_on_fs = re.search(r'no.*phi.*filesyst', docker_plan, re.IGNORECASE) is not None
    assert stateless and external_vol and no_phi_on_fs, (
        "Statelessness, external storage, and PHI/PII filesystem restrictions must be described.")

def test_compliance_and_logging_controls(docker_plan):
    """Ensure plan addresses PHI/PII, logging with masking, and audit trail controls."""
    phi_mentions = sum(1 for term in PHI_PII_TERMS if term in docker_plan)
    logging = 'logging' in docker_plan.lower() and 'masking' in docker_plan.lower()
    audit = 'audit' in docker_plan.lower()
    assert phi_mentions >= 2 and logging and audit, "Compliance, logging, or audit trail not sufficiently covered."

def test_example_dockerfile_formatting_and_runtime(docker_plan):
    """Verify example Dockerfile snippet covers base image, WORKDIR, requirements, pip install, source copy, ENV, EXPOSE, and Gunicorn run."""
    dockerfile_block = re.search(r'```dockerfile(.+?)```', docker_plan, re.DOTALL)
    assert dockerfile_block, "Dockerfile example code block not found."
    block = dockerfile_block.group(1)
    key_lines = ['FROM python:3.10-slim', 'WORKDIR /app', 'COPY requirements.txt', 'pip install', 'COPY src', 'ENV PYTHONUNBUFFERED', 'EXPOSE 5000', 'CMD ["gunicorn"']
    for key_line in key_lines:
        assert key_line in block, f"'{key_line}' missing from Dockerfile example."

def test_summary_table_correctness(docker_plan):
    """Ensure summary table covers steps from inventory through monitoring and compliance."""
    table_pattern = r'\| *Step *\| *Description *\|.*Inventory[^\n]+Secrets[^\n]+External[^\n]+Build/[^\n]+Health check[^\n]+Monitoring'
    match = re.search(table_pattern, docker_plan, re.DOTALL | re.IGNORECASE)
    assert match, "Summary table does not appear complete or is poorly formed."

# Edge case: Plan must not suggest storing PHI, secrets, or credentials in base image, source control, or local container filesystem.
def test_no_secret_storage_in_image_or_vcs(docker_plan):
    """Check for anti-patterns like secret storage in code, Dockerfile, or VCS."""
    red_flags = [r'secret.+(hardcoded|in code|in image|in repo|git)', r'credential.+(hardcoded|in code|in image|in repo|git)']
    for pattern in red_flags:
        assert not re.search(pattern, docker_plan, re.IGNORECASE), f"Insecure secret storage guidance detected: pattern {pattern}"