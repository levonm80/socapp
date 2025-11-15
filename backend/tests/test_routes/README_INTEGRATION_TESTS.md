# Integration Tests for Backend Endpoints

This directory contains integration tests for all backend API endpoints using `pytest` and `requests`. These tests assume the backend is running and make real HTTP requests.

## Prerequisites

1. **Backend must be running** - These are integration tests that connect to a live backend
2. **Test user must exist** - The tests authenticate using a test user that must exist in the database
3. **Test data available** - Some tests require log files to be uploaded (uses test-data directory)

## Configuration

### Environment Variables

The tests support configuration via environment variables:

- `API_BASE_URL` - Base URL for the API (default: `http://localhost:5000`)
- `TEST_USER_EMAIL` - Email for test user authentication (default: `test@example.com`)
- `TEST_USER_PASSWORD` - Password for test user authentication (default: `testpassword123` - **change this in production**)

### Example Configuration

```bash
# Set API base URL
export API_BASE_URL=http://localhost:5000

# Set test credentials
export TEST_USER_EMAIL=test@example.com
export TEST_USER_PASSWORD=testpassword123

# Run tests
pytest tests/test_routes/test_integration_*.py
```

## Running Tests

### Run All Integration Tests

```bash
cd backend
pytest tests/test_routes/test_integration_*.py -v
```

### Run Specific Test File

```bash
# Auth endpoints
pytest tests/test_routes/test_integration_auth.py -v

# Logs endpoints
pytest tests/test_routes/test_integration_logs.py -v

# Dashboard endpoints
pytest tests/test_routes/test_integration_dashboard.py -v

# Anomalies endpoints
pytest tests/test_routes/test_integration_anomalies.py -v

# AI endpoints
pytest tests/test_routes/test_integration_ai.py -v
```

### Run Specific Test

```bash
pytest tests/test_routes/test_integration_auth.py::TestAuthEndpointsIntegration::test_should_login_when_valid_credentials_provided -v
```

### Run with Coverage

```bash
pytest tests/test_routes/test_integration_*.py --cov=backend --cov-report=term-missing
```

## Test Structure

All tests follow the **Arrange-Act-Assert** pattern and use descriptive names:

- Test class: `Test{EndpointGroup}EndpointsIntegration`
- Test method: `test_should_{expected_behavior}_when_{context}`

### Fixtures Used

- `api_base_url` - Base URL for API (configurable via env var)
- `api_session` - Requests session without authentication
- `authenticated_session` - Requests session with JWT token (auto-authenticates)

## Endpoints Tested

### Authentication (`/api/auth`)
- `POST /api/auth/login` - Login with credentials
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Logs (`/api/logs`)
- `POST /api/logs/upload` - Upload log file
- `GET /api/logs/files` - List log files
- `GET /api/logs/files/<id>` - Get log file details
- `GET /api/logs/files/<id>/preview` - Preview log file
- `GET /api/logs/entries` - List log entries (with filters)
- `GET /api/logs/entries/<id>` - Get log entry details

### Dashboard (`/api/dashboard`)
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/timeline` - Timeline data
- `GET /api/dashboard/top-categories` - Top URL categories
- `GET /api/dashboard/top-domains` - Top domains
- `GET /api/dashboard/top-users` - Top users
- `GET /api/dashboard/recent-logs` - Recent log entries

### Anomalies (`/api/anomalies`)
- `GET /api/anomalies` - List anomalies (with filters)
- `GET /api/anomalies/timeline` - Anomaly timeline

### AI (`/api/ai`)
- `GET /api/ai/log-summary/<file_id>` - AI log summary
- `GET /api/ai/explain-log-entry/<entry_id>` - AI explanation for entry
- `POST /api/ai/investigate` - AI investigation copilot

## Setup Test Data

Before running tests, ensure:

1. **Backend is running** on the configured port (default: 5000)
2. **Database is set up** with migrations applied
3. **Test user exists** in the database:
   ```python
   from models import User
   from extensions import db
   
   # Use the same password as TEST_USER_PASSWORD environment variable
   user = User(email='test@example.com', password='your-test-password')
   db.session.add(user)
   db.session.commit()
   ```
4. **Test log files available** in `test-data/` directory (optional, some tests will skip if not available)

## Test Behavior

- **Tests will skip** if backend is not accessible (connection errors)
- **Tests will skip** if authentication fails
- **Tests will skip** if required test data is not available
- **AI endpoint tests** may accept 500 errors if OpenAI API is not configured (service errors are expected)

## Troubleshooting

### Connection Errors

```
pytest.skip: Cannot connect to backend at http://localhost:5000. Is the backend running?
```

**Solution**: Start the backend server before running tests.

### Authentication Errors

```
pytest.skip: Cannot authenticate: 401 - Invalid credentials
```

**Solution**: Ensure test user exists in database with correct credentials.

### Missing Test Data

Some tests will skip if test data is not available. This is expected behavior - tests are designed to be resilient to missing data.

### Timeout Errors

Some tests (especially upload and AI endpoints) have longer timeouts. If you experience timeout errors:

1. Check backend performance
2. Increase timeout values in test code if needed
3. Verify network connectivity

## CI/CD Integration

These integration tests are designed for local and CI/CD environments:

```yaml
# Example GitHub Actions
- name: Run Integration Tests
  env:
    API_BASE_URL: http://localhost:5000
    TEST_USER_EMAIL: test@example.com
    TEST_USER_PASSWORD: your-test-password  # Set a secure test password
  run: |
    pytest tests/test_routes/test_integration_*.py -v
```

Ensure backend is running in CI environment before running tests.

