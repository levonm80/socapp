# SOC Application - AI-Powered Security Operations Center

A full-stack application for analyzing Zscaler NSS web proxy logs with AI-powered threat detection and investigation capabilities.

## Features

- **Log Upload & Parsing**: Upload and parse Zscaler NSS web proxy logs (34 fields)
- **Anomaly Detection**: Deterministic rules for detecting:
  - Burst of blocked requests
  - Malicious domain access
  - Risky category access
  - Unusual user agents (curl, python-requests)
  - Large downloads (>50MB)
- **User Risk Scoring**: Calculate risk scores per user based on behavior
- **AI Integration**: 
  - SOC-style log summaries
  - Plain-English log entry explanations
  - Natural-language investigation copilot
- **Dashboard**: Real-time statistics, charts, and AI summaries
- **Log Explorer**: Filterable, paginated log entry browser
- **Anomalies View**: Timeline and detailed anomaly analysis

## Tech Stack

- **Frontend**: Next.js 14 (App Router), TypeScript, TailwindCSS
- **API Gateway**: Kong Gateway (OSS, DB-less mode)
- **Backend**: Flask (Python), SQLAlchemy, Flask-JWT-Extended
- **Database**: PostgreSQL
- **AI**: OpenAI API (gpt-4o-mini or gpt-4o)
- **Deployment**: Docker Compose

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.12+ (for local backend development)
- PostgreSQL 15+ (for local database)
- OpenAI API key (for AI features)

## Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│    Kong     │────────▶│   Backend   │────────▶│  PostgreSQL │
│  (Next.js)  │         │   Gateway   │         │   (Flask)   │         │  Database   │
│  Port 3000  │         │  Port 8000  │         │  Port 5000  │         │  Port 5432  │
└─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘
                              │
                              ├─ JWT Validation
                              ├─ CORS Headers
                              ├─ Request Routing
                              └─ X-User-Id Injection
```

**Kong Gateway** sits between the frontend and backend, handling:
- **JWT Token Validation**: Validates JWT tokens from the frontend
- **CORS Management**: Adds appropriate CORS headers for browser requests
- **Authentication**: Extracts user ID from JWT and injects `X-User-Id` header
- **Request Proxying**: Routes all `/api/*` requests to the backend

The backend trusts Kong-validated requests and uses the `X-User-Id` header for authentication.

## Deployment

### Railway Deployment

For production deployment on Railway.com, see **[RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)** for complete instructions.

Quick summary:
- Deploy PostgreSQL (Railway managed service)
- Deploy Backend, Kong Gateway, and Frontend services
- Configure environment variables in Railway dashboard
- All secrets managed securely via Railway environment variables

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   cd socapp
   ```

2. **Set up environment variables**
   ```bash
   # Root (for Docker Compose)
   cp .env.example .env
   # Edit .env and add your secrets (database password, JWT secret, OpenAI API key)
   
   # Backend (for local development)
   cp backend/.env.example backend/.env
   # Edit backend/.env and add your secrets
   
   # Frontend (for local development)
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```
   
   This starts:
   - PostgreSQL database (port 5432)
   - Flask backend (port 5000, internal + 5050 for direct access)
   - Kong API Gateway (port 8000 for proxy, 8001 for admin)
   - Next.js frontend (port 3000)

4. **Initialize database**
   ```bash
   docker-compose exec api flask db upgrade
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Kong Gateway (API): http://localhost:8000/api
   - Backend API (direct): http://localhost:5050/api (for debugging)
   - Kong Admin API: http://localhost:8001
   - Database: localhost:5432

## Kong Gateway Configuration

Kong is configured in **DB-less mode** using a declarative configuration file at `kong/kong.yml`.

### Key Configuration Details:

- **JWT Plugin**: Validates JWT tokens using the same secret as the backend
  - **Important**: Kong doesn't support environment variable substitution in YAML files
  - You must manually update the `secret` value in `kong/kong.yml` to match your `JWT_SECRET_KEY` from `.env`
  - See `kong/README.md` for detailed instructions
- **CORS Plugin**: Adds permissive CORS headers for development
- **Request Transformer**: Extracts user ID from JWT `sub` claim and injects as `X-User-Id` header
- **Routes**:
  - `/api/auth/login` - Public route (no JWT required)
  - All other `/api/*` routes - Protected with JWT validation

### Modifying Kong Configuration:

1. Edit `kong/kong.yml` with your changes
2. Restart Kong container:
   ```bash
   docker-compose restart kong
   ```

### Kong Admin API:

Access Kong's admin API at http://localhost:8001 to:
- View current configuration: `GET http://localhost:8001/`
- Check services: `GET http://localhost:8001/services`
- Check routes: `GET http://localhost:8001/routes`
- View plugins: `GET http://localhost:8001/plugins`

## Local Development

### Backend

1. **Set up virtual environment**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Create .env file with DATABASE_URL
   flask db upgrade
   ```

3. **Run tests**
   ```bash
   pytest
   ```

4. **Run development server**
   ```bash
   flask run
   ```

### Frontend

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server**
   ```bash
   npm run dev
   ```

3. **Run tests**
   ```bash
   npm test
   ```

## Running with Local PostgreSQL Server

If you have PostgreSQL installed on your development machine, you can run the application locally without Docker.

### Prerequisites

1. **Check if PostgreSQL is installed**
   ```bash
   # macOS (Homebrew)
   brew services list | grep postgresql
   
   # Linux
   systemctl status postgresql
   
   # Or check version
   psql --version
   ```

2. **Start PostgreSQL service** (if not running)
   ```bash
   # macOS (Homebrew)
   brew services start postgresql@15
   
   # Linux
   sudo systemctl start postgresql
   
   # Or manually
   pg_ctl -D /usr/local/var/postgres start
   ```

### Database Setup

1. **Connect to PostgreSQL**
   ```bash
   psql postgres
   # Or with specific user
   psql -U postgres
   ```

2. **Create database and user** (if they don't exist)
   ```sql
   -- Create user (if it doesn't exist)
   -- Replace 'your-secure-password' with a strong password
   CREATE USER socapp WITH PASSWORD 'your-secure-password';
   
   -- Create database
   CREATE DATABASE socapp OWNER socapp;
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE socapp TO socapp;
   
   -- Exit psql
   \q
   ```

   **Note**: If the user or database already exists, you can skip those steps or use:
   ```sql
   -- Check if user exists
   SELECT 1 FROM pg_user WHERE usename = 'socapp';
   
   -- Check if database exists
   SELECT 1 FROM pg_database WHERE datname = 'socapp';
   ```

3. **Verify connection**
   ```bash
   psql -U socapp -d socapp -h localhost
   # Enter the password you set when creating the user
   ```

### Backend Setup

1. **Set up virtual environment** (if not already done)
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create `.env` file** in the `backend/` directory
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and fill in your actual values:
   # - DATABASE_URL with your database password
   # - JWT_SECRET_KEY (generate a secure random key)
   # - SECRET_KEY (generate a secure random key)
   # - OPENAI_API_KEY (your OpenAI API key)
   ```

3. **Run database migrations**
   ```bash
   cd backend
   source venv/bin/activate  # If not already activated
   flask db upgrade
   ```

4. **Start backend server**
   ```bash
   flask run
   # Backend will be available at http://localhost:5000
   ```

### Frontend Setup

1. **Install dependencies** (if not already done)
   ```bash
   cd frontend
   npm install
   ```

2. **Create `.env.local` file** in the `frontend/` directory
   ```bash
   cd frontend
   echo "NEXT_PUBLIC_API_URL=http://localhost:5000/api" > .env.local
   ```

3. **Start frontend development server**
   ```bash
   npm run dev
   # Frontend will be available at http://localhost:3000
   ```

### Troubleshooting

**Connection refused errors:**
- Ensure PostgreSQL is running: `brew services list` (macOS) or `systemctl status postgresql` (Linux)
- Check PostgreSQL is listening on port 5432: `lsof -i :5432` or `netstat -an | grep 5432`
- Verify connection string in `backend/.env` matches your PostgreSQL setup

**Authentication errors:**
- Verify username and password in `DATABASE_URL` match the PostgreSQL user
- Check `pg_hba.conf` allows local connections (usually in `/usr/local/var/postgres/` or `/etc/postgresql/`)

**Database does not exist:**
- Run the database creation SQL commands from the "Database Setup" section above
- Or use `createdb -U socapp socapp` if you have the user set up

**Port conflicts:**
- If port 5432 is already in use, either:
  - Stop the conflicting service
  - Or change the port in `DATABASE_URL` and update PostgreSQL configuration

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Log Files
- `POST /api/logs/upload` - Upload log file
- `GET /api/logs/files` - List log files
- `GET /api/logs/files/:id` - Get log file details
- `GET /api/logs/files/:id/preview` - Preview log file

### Log Entries
- `GET /api/logs/entries` - List log entries (with filters)
- `GET /api/logs/entries/:id` - Get log entry

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/timeline` - Timeline data
- `GET /api/dashboard/top-categories` - Top URL categories
- `GET /api/dashboard/top-domains` - Top domains
- `GET /api/dashboard/top-users` - Top users
- `GET /api/dashboard/recent-logs` - Recent log entries

### Anomalies
- `GET /api/anomalies` - List anomalies
- `GET /api/anomalies/timeline` - Anomaly timeline

### AI
- `GET /api/ai/log-summary/:log_file_id` - Generate log summary
- `GET /api/ai/explain-log-entry/:entry_id` - Explain log entry
- `POST /api/ai/investigate` - AI investigation copilot

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=backend --cov-report=term-missing
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Project Structure

```
socapp/
├── backend/
│   ├── app.py                 # Flask app factory
│   ├── config.py              # Configuration
│   ├── models.py              # Database models
│   ├── routes/                # API routes
│   ├── services/              # Business logic
│   ├── tests/                 # Tests
│   └── migrations/            # Alembic migrations
├── frontend/
│   ├── app/                   # Next.js app router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities and API client
│   └── types/                 # TypeScript types
└── docker-compose.yml         # Docker setup
```

## Environment Variables

### Backend (.env)
See `backend/.env.example` for all required variables. Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing (generate a secure random key)
- `SECRET_KEY`: Flask secret key (generate a secure random key)
- `OPENAI_API_KEY`: Your OpenAI API key

### Frontend (.env.local)
See `frontend/.env.local.example` for all required variables. Key variables:
- `NEXT_PUBLIC_API_URL`: API gateway URL (default: http://localhost:8000/api)

## Usage

1. **Login**: Use the login page to authenticate
2. **Upload Logs**: Upload Zscaler NSS log files (.log format)
3. **View Dashboard**: See statistics, charts, and AI summaries
4. **Explore Logs**: Filter and search log entries
5. **Investigate Anomalies**: Review detected anomalies
6. **AI Copilot**: Ask natural-language questions about the logs

## Development Notes

- Follow TDD: Write tests first, then implementation
- All backend code must have tests (80%+ coverage)
- Security-critical code (parsing, detection) requires 100% coverage
- Use `pytest` for backend tests
- Use `vitest` for frontend tests

## License

Copyright 2024 SecureAI Corp. All rights reserved.

