# OpenAPI Documentation

This document explains how to use the OpenAPI specification for the SOC Application API.

## Overview

The `openapi.yaml` file contains a complete OpenAPI 3.0 specification for all backend endpoints. This specification can be used to:

- Generate API documentation
- Generate client SDKs
- Test endpoints interactively
- Validate API requests and responses
- Import into API tools (Postman, Insomnia, etc.)

## Viewing the Documentation

### Option 1: Swagger UI (Recommended)

**Online viewer:**
1. Go to [Swagger Editor](https://editor.swagger.io/)
2. File → Import File → Select `openapi.yaml`
3. View interactive documentation with "Try it out" functionality

**Local Swagger UI:**
```bash
# Using Docker
docker run -p 8080:8080 -e SWAGGER_JSON=/openapi.yaml -v $(pwd)/openapi.yaml:/openapi.yaml swaggerapi/swagger-ui

# Then open http://localhost:8080
```

### Option 2: Redoc

**Online viewer:**
1. Go to [Redoc](https://redocly.github.io/redoc/)
2. Paste the URL to your `openapi.yaml` file

**Local Redoc:**
```bash
# Using npx
npx @redocly/cli preview-docs openapi.yaml

# Then open http://localhost:8080
```

### Option 3: VS Code Extension

Install the "OpenAPI (Swagger) Editor" extension in VS Code:
1. Open `openapi.yaml` in VS Code
2. Right-click → "Preview Swagger"
3. View interactive documentation in the editor

## API Structure

### Endpoints (20 total)

#### Authentication (3 endpoints)
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

#### Logs (6 endpoints)
- `POST /api/logs/upload` - Upload log file
- `GET /api/logs/files` - List log files
- `GET /api/logs/files/{file_id}` - Get log file details
- `GET /api/logs/files/{file_id}/preview` - Preview log file
- `GET /api/logs/entries` - List log entries (with filters)
- `GET /api/logs/entries/{entry_id}` - Get log entry details

#### Dashboard (6 endpoints)
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/timeline` - Timeline data
- `GET /api/dashboard/top-categories` - Top URL categories
- `GET /api/dashboard/top-domains` - Top domains
- `GET /api/dashboard/top-users` - Top users
- `GET /api/dashboard/recent-logs` - Recent log entries

#### Anomalies (2 endpoints)
- `GET /api/anomalies` - List anomalies (with filters)
- `GET /api/anomalies/timeline` - Anomaly timeline

#### AI (3 endpoints)
- `GET /api/ai/log-summary/{log_file_id}` - AI log summary
- `GET /api/ai/explain-log-entry/{entry_id}` - Explain log entry
- `POST /api/ai/investigate` - AI investigation

### Data Models (11 schemas)

- `User` - User account information
- `LogFile` - Uploaded log file metadata
- `LogEntry` - Individual log entry with 30+ fields
- `DashboardStats` - Dashboard statistics
- `TimelineBucket` - Timeline data point
- `CategoryStats` - URL category statistics
- `DomainStats` - Domain statistics
- `UserStats` - User activity statistics
- `Anomaly` - Detected anomaly
- `AnomalyTimelineBucket` - Anomaly timeline data point
- `Error` - Error response

## Authentication

Most endpoints require JWT authentication:

1. Call `POST /api/auth/login` with email and password
2. Receive JWT token in response
3. Include token in subsequent requests:
   ```
   Authorization: Bearer <token>
   ```

The OpenAPI spec includes a security scheme for Bearer authentication.

## Generating Client SDKs

### Using OpenAPI Generator

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate -i openapi.yaml -g python -o ./client-python

# Generate TypeScript/JavaScript client
openapi-generator-cli generate -i openapi.yaml -g typescript-axios -o ./client-typescript

# Generate Java client
openapi-generator-cli generate -i openapi.yaml -g java -o ./client-java

# See all available generators
openapi-generator-cli list
```

### Using Swagger Codegen

```bash
# Using Docker
docker run --rm -v ${PWD}:/local swaggerapi/swagger-codegen-cli generate \
  -i /local/openapi.yaml \
  -l python \
  -o /local/client-python
```

## Importing into API Tools

### Postman

1. Open Postman
2. Import → Upload Files → Select `openapi.yaml`
3. Postman will create a collection with all endpoints
4. Set up environment variables for `baseUrl` and `bearerToken`

### Insomnia

1. Open Insomnia
2. Application Menu → Preferences → Data → Import Data
3. Select `openapi.yaml`
4. Insomnia will create requests for all endpoints

Note: You already have a native Insomnia workspace (`insomnia_workspace.json`), but you can also import the OpenAPI spec.

### Thunder Client (VS Code)

1. Install Thunder Client extension
2. Collections → Import → Select `openapi.yaml`
3. Thunder Client will create a collection

## Testing Endpoints

### Using curl with OpenAPI

Example from the spec:

```bash
# Login (replace with your actual credentials)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "your-secure-password"}'

# Get log files (with token)
curl -X GET http://localhost:5000/api/logs/files \
  -H "Authorization: Bearer <token>"

# Upload log file
curl -X POST http://localhost:5000/api/logs/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@test-data/zscaler_nss_like.log"
```

### Using httpie

```bash
# Login (replace with your actual credentials)
http POST localhost:5000/api/auth/login email=test@example.com password=your-secure-password

# Get log files
http GET localhost:5000/api/logs/files "Authorization: Bearer <token>"
```

## Validation

### Validate OpenAPI Spec

```bash
# Using Swagger CLI
npm install -g @apidevtools/swagger-cli
swagger-cli validate openapi.yaml

# Using Redocly CLI
npm install -g @redocly/cli
redocly lint openapi.yaml
```

### Validate Requests/Responses

The OpenAPI spec can be used to validate that your API requests and responses match the specification.

**Python example:**
```python
from openapi_core import create_spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator

# Load spec
with open('openapi.yaml') as f:
    spec_dict = yaml.safe_load(f)
    spec = create_spec(spec_dict)

# Validate request
request_validator = openapi_request_validator.RequestValidator(spec)
result = request_validator.validate(request)

# Validate response
response_validator = openapi_response_validator.ResponseValidator(spec)
result = response_validator.validate(request, response)
```

## Mock Server

Generate a mock server from the OpenAPI spec for testing:

```bash
# Using Prism
npm install -g @stoplight/prism-cli
prism mock openapi.yaml

# Mock server will run on http://localhost:4010
```

## Continuous Integration

Add OpenAPI validation to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Validate OpenAPI Spec
  run: |
    npm install -g @redocly/cli
    redocly lint openapi.yaml
```

## Updating the Spec

When adding new endpoints or modifying existing ones:

1. Update the route files in `backend/routes/`
2. Update `openapi.yaml` to match
3. Validate the spec: `swagger-cli validate openapi.yaml`
4. Regenerate documentation
5. Update client SDKs if needed

## Additional Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger Editor](https://editor.swagger.io/)
- [Redoc Documentation](https://redocly.com/docs/redoc/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)

## Differences from Insomnia Workspace

The `insomnia_workspace.json` and `openapi.yaml` serve different purposes:

| Feature | Insomnia Workspace | OpenAPI Spec |
|---------|-------------------|--------------|
| Purpose | Manual API testing | Documentation & code generation |
| Format | Insomnia-specific JSON | Standard OpenAPI 3.0 YAML |
| Environment variables | ✅ Yes | ❌ No (use servers) |
| Request examples | ✅ Yes | ✅ Yes (in schemas) |
| Response schemas | ❌ No | ✅ Yes (full schemas) |
| Code generation | ❌ No | ✅ Yes |
| Interactive docs | ❌ No | ✅ Yes (via Swagger UI) |
| Tool compatibility | Insomnia only | Many tools (Postman, etc.) |

**Recommendation:** Use both:
- Insomnia workspace for manual testing and development
- OpenAPI spec for documentation, client generation, and validation

