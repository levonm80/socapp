# Insomnia Workspace Setup Guide

This guide explains how to import and use the Insomnia workspace for testing all backend API endpoints.

## Import the Workspace

1. **Open Insomnia** application
2. **Go to**: Application Menu → Preferences → Data → Import Data
3. **Select**: `insomnia_workspace.json` from the project root
4. **Click**: Import

Alternatively, you can drag and drop the `insomnia_workspace.json` file into the Insomnia window.

## Environment Configuration

The workspace includes a base environment with the following variables:

- `base_url`: Base URL for the API (default: `http://localhost:5000`)
- `auth_token`: JWT authentication token (automatically set after login)
- `log_file_id`: Log file ID for testing (set after uploading a file)
- `log_entry_id`: Log entry ID for testing (set after listing entries)

### Setting Up Environment Variables

1. **Select Environment**: Click on the environment dropdown (top left)
2. **Edit Variables**: Click "Manage Environments" or edit the "Base Environment"
3. **Update Variables**:
   - Set `base_url` to your backend URL (e.g., `http://localhost:5000`)
   - Leave `auth_token` empty initially (will be set after login)

## Quick Start Workflow

### 1. Login First

1. Go to **Authentication** folder
2. Open **Login** request
3. Update the request body with your credentials:
   ```json
   {
     "email": "test@example.com",
     "password": "your-secure-password"
   }
   ```
   
   **Note**: Create a test user first using the backend API or database. Replace `your-secure-password` with the actual password.
4. Click **Send**
5. Copy the `token` from the response
6. Go to **Environment** → **Base Environment**
7. Paste the token into `auth_token` variable

**Tip**: You can create a response hook to automatically set the token:
- Right-click on Login request → **Settings** → **Response** → Add a hook:
  ```javascript
  const jsonData = await response.json();
  if (jsonData.token) {
    insomnia.environment.set('auth_token', jsonData.token);
  }
  ```

### 2. Test Authentication Endpoints

- **Get Current User**: Test your authentication token
- **Logout**: Logout endpoint (token is removed client-side)

### 3. Upload a Log File

1. Go to **Logs** folder
2. Open **Upload Log File** request
3. In the **Body** tab, select **Multipart Form**
4. Click on the file field and select a log file from `test-data/` directory
5. Click **Send**
6. Copy the `log_file_id` from the response
7. Set it in the environment variable `log_file_id` (optional, for convenience)

### 4. Test Log Endpoints

- **List Log Files**: See all uploaded files
- **Get Log File**: Get details of a specific file
- **Preview Log File**: Get preview of log entries
- **List Log Entries**: List entries with filters
- **Get Log Entry**: Get details of a specific entry

### 5. Test Dashboard Endpoints

- **Dashboard Stats**: Get statistics
- **Dashboard Timeline**: Get timeline data for charts
- **Top Categories**: Get top URL categories
- **Top Domains**: Get top domains
- **Top Users**: Get top users by request count
- **Recent Logs**: Get recent log entries

### 6. Test Anomalies Endpoints

- **List Anomalies**: List detected anomalies with filters
- **Anomaly Timeline**: Get anomaly timeline data

### 7. Test AI Endpoints

- **Log Summary**: Get AI-generated summary of a log file
- **Explain Log Entry**: Get AI explanation for a log entry
- **Investigate**: Ask questions about log data

## Request Organization

The workspace is organized into folders:

### Authentication
- Login (POST)
- Logout (POST)
- Get Current User (GET)

### Logs
- Upload Log File (POST)
- List Log Files (GET)
- Get Log File (GET)
- Preview Log File (GET)
- List Log Entries (GET)
- Get Log Entry (GET)

### Dashboard
- Dashboard Stats (GET)
- Dashboard Timeline (GET)
- Top Categories (GET)
- Top Domains (GET)
- Top Users (GET)
- Recent Logs (GET)

### Anomalies
- List Anomalies (GET)
- Anomaly Timeline (GET)

### AI
- Log Summary (GET)
- Explain Log Entry (GET)
- Investigate (POST)

## Environment Variables Reference

### Global Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | Backend API base URL | `http://localhost:5000` |
| `auth_token` | JWT token for authentication | (set automatically) |

### Dynamic Variables (set during testing)

| Variable | Description | How to Set |
|----------|-------------|------------|
| `log_file_id` | UUID of a log file | Copy from Upload Log File response |
| `log_entry_id` | UUID of a log entry | Copy from List Log Entries response |

## Tips

### 1. Automatic Token Management

Create a response hook for the Login request to automatically set the token:

1. Right-click **Login** request
2. Select **Settings**
3. Go to **Response** tab
4. Add this hook:
   ```javascript
   const jsonData = await response.json();
   if (jsonData.token) {
     insomnia.environment.set('auth_token', jsonData.token);
   }
   ```

### 2. Chaining Requests

After uploading a log file, you can:
1. Copy the `log_file_id` from the response
2. Set it in environment variables
3. Use it in subsequent requests (they reference `{{ _.log_file_id }}`)

### 3. Filter Examples

For **List Log Entries**, you can use these filters:

- `action`: `Allowed` or `Blocked`
- `is_anomalous`: `true` or `false`
- `domain`: `example.com`
- `start_time`: `2022-06-20T00:00:00Z`
- `end_time`: `2022-06-20T23:59:59Z`

### 4. Testing Different Environments

Create multiple environments for different backends:

- **Development**: `http://localhost:5000`
- **Staging**: `http://staging.example.com`
- **Production**: `https://api.example.com`

Switch between them using the environment dropdown.

## Troubleshooting

### 401 Unauthorized

- Ensure you've logged in and set the `auth_token` variable
- Token may have expired (Flask-JWT tokens expire after 15 minutes by default)
- Re-login to get a new token

### Connection Refused

- Ensure the backend is running
- Check the `base_url` is correct
- Verify the port matches your backend configuration

### File Upload Fails

- Ensure the file exists at the specified path
- Check file size limits (Flask default is 16MB)
- Verify the file format matches Zscaler NSS log format

### Empty Responses

- Some endpoints return empty arrays if no data exists
- Upload a log file first to populate data
- Check that filters aren't too restrictive

## Example Request Sequences

### Sequence 1: Full Workflow

1. **Login** → Get token
2. **Upload Log File** → Get `log_file_id`
3. **List Log Files** → Verify upload
4. **List Log Entries** → See parsed entries
5. **Dashboard Stats** → View statistics
6. **List Anomalies** → Check for anomalies
7. **AI Log Summary** → Get AI summary

### Sequence 2: Analysis Workflow

1. **List Log Entries** with `is_anomalous=true`
2. **Get Log Entry** for a specific anomaly
3. **AI Explain Log Entry** → Get explanation
4. **Anomaly Timeline** → See timeline of anomalies
5. **Dashboard Top Domains** → See which domains are problematic

## Export/Import

You can export your workspace at any time:
- **Application Menu** → **Preferences** → **Data** → **Export Data**
- This creates a backup with all your environment variables and request configurations

### Troubleshooting Export Issues (Insomnia 12.0.0)

If you're experiencing export issues where Insomnia shows "scanning" but the collection appears empty:

#### Solution 1: Import First, Then Export
1. **First, import the workspace** from `insomnia_workspace.json`:
   - **Application Menu** → **Preferences** → **Data** → **Import Data**
   - Select `insomnia_workspace.json`
   - Verify that all requests appear in Insomnia
2. **Then export** (the workspace must be imported first for export to work)

#### Solution 2: Check for Plugin Conflicts
Some plugins can interfere with export. Try:
1. **Disable plugins temporarily**:
   - **Application Menu** → **Preferences** → **Plugins**
   - Disable all plugins
   - Try exporting again
   - Re-enable plugins if needed

#### Solution 3: Use Inso CLI (Recommended)
The Inso CLI is more reliable for exporting. Install and use it:

1. **Install Inso CLI**:
   ```bash
   npm install -g @kong/insomnia-cli
   # or
   brew install insomnia-cli
   ```

2. **Export using Inso**:
   ```bash
   # Navigate to your project directory
   cd /Users/levon/Working/socapp
   
   # Export the workspace
   inso export spec insomnia_workspace.json -o insomnia_export.yaml
   
   # Or export to OpenAPI format
   inso export spec insomnia_workspace.json --type openapi3 -o openapi_export.yaml
   ```

3. **Import using Inso** (if needed):
   ```bash
   inso import spec insomnia_workspace.json
   ```

#### Solution 4: Verify Workspace Structure
Ensure your workspace file is valid JSON:
```bash
# Validate JSON
cat insomnia_workspace.json | python3 -m json.tool > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

#### Solution 5: Clear Cache and Retry
1. **Quit Insomnia completely**
2. **Clear Insomnia cache** (macOS):
   ```bash
   rm -rf ~/Library/Application\ Support/Insomnia/cache
   rm -rf ~/Library/Application\ Support/Insomnia/cookies
   ```
3. **Restart Insomnia and try again**

#### Solution 6: Alternative Export Method
Try exporting via the workspace menu:
1. Right-click on the workspace name in the left sidebar
2. Select **Export** (if available)
3. Choose **Insomnia v4** or **Insomnia v5** format

### Known Issues with Insomnia 12.0.0
- Export may hang on "scanning" if workspace wasn't properly imported first
- Some UI elements may not reflect imported data immediately (try refreshing)
- Export format 5 (used in this workspace) should be compatible with Insomnia 12.0.0

---

**Note**: Remember to update the `base_url` environment variable if your backend runs on a different port or host.

