## Step-by-Step Dockerization Plan for Healthcare AI Flask API (Azure/Healthcare Compliance)

### 1. Component and Dependency Inventory
- Application Source Code (all modules under `src/app/`)
- Python Runtime Environment (e.g., python:3.10-slim)
- Python Dependencies (Flask, Flask-Smorest, Marshmallow, PyJWT, etc. as declared in requirements.txt)
- Model Files/Assets (if required by inference)
- Configuration Directory (for settings/config/profiles)
- Gunicorn (or uWSGI) as a production WSGI server
- (Optional) Nginx/Reverse Proxy for TLS/Static assets/compression (usually managed by Azure App Gateway)

### 2. Secure Handling of Sensitive Configuration (Secrets Management)
- **NEVER bake secrets (e.g., JWT_SECRET, DB credentials, API keys) into code or Docker image history.**
- Use ENV variables for runtime configuration: inject via `docker run -e` or Azure App Service environment blade.
  Example: `OAUTH2_JWT_SECRET`, `OAUTH2_JWT_ALG`, `FLASK_ENV`, database URLs, logging configs, etc.
- Mark all secrets as required in deployment documentation.
- For Azure, use [Azure Key Vault](https://docs.microsoft.com/en-us/azure/key-vault/) and [Azure Managed Identities](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview) to pass secrets securely to the container at runtime.
- For local dev, store secrets in a `.env` file included in `.gitignore`, loaded by your entrypoint script or Docker Compose.

### 3. Storage Management/Healthcare Data Compliance
- **Persistent Volumes:**
  - For temporary or intermediary files (such as generated synthetic data or batch inference results), mount a Docker named volume or Azure Files share at `/data`.
  - For long-term/PHI storage, integrate with Azure Blob Storage or an encrypted managed database. Do not persist any PHI inside the container image or filesystem when running in production.
- **Stateless Container Principle:**
  - App containers must not store any persistent PHI or PII on their local filesystems.
  - Ensure logs, uploads, and generated files are routed to external, secure, and compliance-audited storage.
  - Configure log output to stdout/stderr for Azure log streaming and central monitoring.
- **Compliance Controls:**
  - Use Azure Disk encryption and ensure any mounted volumes are encrypted-at-rest and have stringent access controls.
  - Do not permit world-writable directories in the container FS.

### 4. Docker Build, Tag, and Push Process (for Azure)
- **Dockerfile example outline:**
  ```dockerfile
  FROM python:3.10-slim
  WORKDIR /app
  COPY requirements.txt ./
  RUN pip install --no-cache-dir -r requirements.txt
  COPY src/ ./src/
  ENV PYTHONUNBUFFERED=1
  EXPOSE 5000
  CMD ["gunicorn", "src.app.main:app", "-b", "0.0.0.0:5000", "--timeout=180", "--workers=2"]
  ```
- **Build and Tag:**
  ```sh
  docker build -t healthcare-ai-api:latest .
  docker tag healthcare-ai-api:latest <azurecr>.azurecr.io/healthcare-ai-api:v1.0.0
  ```
- **Login to Azure Container Registry:**
  ```sh
  az acr login --name <azurecr>
  ```
- **Push Image:**
  ```sh
  docker push <azurecr>.azurecr.io/healthcare-ai-api:v1.0.0
  ```
- **Azure Deployment:**
  - Deploy container to Azure App Service (Web App for Containers) or Azure Kubernetes Service (AKS), referencing this image tag.
  - Configure environment variables and storage bindings via Azure portal or Bicep/ARM templates.

### 5. Production Readiness: Health Checks and Orchestration
- **Health Check Endpoint:**
  - Implement a `/health` or `/api/health` route returning HTTP 200 for basic liveness (can be as simple as importing Flask and returning status OK).
  - Optionally, extend readiness checks to test DB/model availability.
  - In `Dockerfile` or Azure deployment config, specify:
    ```
    HEALTHCHECK CMD curl --fail http://localhost:5000/health || exit 1
    ```
  - On AKS or Web App for Containers, configure liveness and readiness probes to this endpoint.

- **Resource Limits:**
  - Define memory/CPU requests/limits in K8s YAML or Azure Web App plan.
  - Example for AKS:
    ```yaml
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1"
    ```
  - For App Service, use Standard+ SKUs and scale plans as needed.

- **Reliability and Scaling:**
  - Replicas: Recommended minimum of 2 containers for production to ensure redundancy.
  - Configure auto-scaling in Azure based on CPU or request queue.
  - Use Azure App Gateway/App Service Managed Certificates for TLS termination and secure client connections.
  - Regularly rotate all credentials/secrets as per hospital security policy.
  - Integrate logging with Azure Monitor and set up Application Insights for tracing and error reporting.

### 6. Audit/Compliance Traceability
- Enable detailed request/response logging with PHI masking on all outbound logs.
- Configure centralized logging and monitoring for audit trails.
- Ensure all access control and authorization checks from backend are enforced (as per provided authorization matrix), and audit all failed accesses.

### Summary Table
| Step | Description |
|------|-------------|
| 1 | Inventory components and dependencies |
| 2 | Secrets/Config injection via env and Azure Key Vault |
| 3 | External persistent storage, compliance controls |
| 4 | Build/tag/push Docker image, Azure deploy steps |
| 5 | Health check route, resource requests/limits, readiness probes |
| 6 | Monitoring, alerts, PHI masking, secure log routing |

This plan ensures HIPAA compatibility, Azure deployment best practices, secure containerization, and operational readiness for healthcare-grade AI APIs running with Flask/Gunicorn.