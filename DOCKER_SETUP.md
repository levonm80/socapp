# Docker Setup Guide

This guide explains how to run the SOC Application using Docker Compose.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose V2 (comes with Docker Desktop)
- At least 4GB RAM allocated to Docker
- At least 10GB free disk space

## Quick Start

### 1. Clone and Setup

```bash
cd /Users/levon/Working/socapp

# Copy environment file
cp .env.example .env

# Edit .env and fill in your secrets:
# - POSTGRES_PASSWORD: Set a secure database password
# - JWT_SECRET_KEY: Generate a secure random key
# - SECRET_KEY: Generate a secure random key
# - OPENAI_API_KEY: Your OpenAI API key
# Note: Kong JWT secret must be manually updated in kong/kong.yml
# (Kong doesn't support env var substitution in YAML files)
```

### 2. Build and Start Services

```bash
# Build all services
docker compose build

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

### 3. Initialize Database

```bash
# Run database migrations
docker compose exec api flask db upgrade

# (Optional) Create a test user
# Replace 'your-secure-password' with a strong password
docker compose exec api python -c "
from app import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    user = User(email='test@example.com', password='your-secure-password')
    db.session.add(user)
    db.session.commit()
    print('Test user created: test@example.com')
"
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API (via Kong)**: http://localhost:8000/api
- **Backend API (direct)**: http://localhost:5050/api
- **Kong Admin**: http://localhost:8001
- **PostgreSQL**: localhost:5432

## Services

### Database (PostgreSQL)
- **Port**: 5432
- **User**: socapp (configurable via POSTGRES_USER)
- **Password**: Set via POSTGRES_PASSWORD in .env
- **Database**: socapp (configurable via POSTGRES_DB)
- **Volume**: postgres_data (persistent)

### Backend API (Flask)
- **Internal Port**: 5000
- **External Port**: 5050 (direct access)
- **Health Check**: HTTP GET to /api/auth/login
- **Environment**: Development mode with hot-reload

### Kong API Gateway
- **Proxy Port**: 8000 (main API access)
- **Admin Port**: 8001 (management)
- **Configuration**: ./kong/kong.yml
- **Features**: JWT authentication, CORS, request transformation

### Frontend (Next.js)
- **Port**: 3000
- **Environment**: Development mode with hot-reload
- **API URL**: http://localhost:8000/api (via Kong)

## Service Dependencies

```
db (PostgreSQL)
  ↓
api (Flask Backend)
  ↓
kong (API Gateway)
  ↓
web (Next.js Frontend)
```

Each service waits for the previous one to be healthy before starting.

## Common Commands

### Start Services

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d api

# Start with logs visible
docker compose up
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes database data)
docker compose down -v
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
docker compose logs -f kong

# Last 100 lines
docker compose logs --tail=100 api
```

### Rebuild Services

```bash
# Rebuild all services
docker compose build

# Rebuild specific service
docker compose build api

# Rebuild without cache
docker compose build --no-cache api
```

### Execute Commands in Containers

```bash
# Backend shell
docker compose exec api bash

# Run Flask commands
docker compose exec api flask db upgrade
docker compose exec api flask shell

# Frontend shell
docker compose exec web sh

# Run npm commands
docker compose exec web npm install
docker compose exec web npm run build

# Database shell
# Password is set via POSTGRES_PASSWORD in .env
docker compose exec db psql -U ${POSTGRES_USER:-socapp} -d ${POSTGRES_DB:-socapp}
```

### Restart Services

```bash
# Restart all services
docker compose restart

# Restart specific service
docker compose restart api
```

### Check Service Status

```bash
# List running services
docker compose ps

# Check service health
docker compose ps api
```

## Development Workflow

### Hot Reload

Both backend and frontend support hot-reload:

- **Backend**: Changes to Python files automatically restart Flask
- **Frontend**: Changes to TypeScript/React files automatically rebuild

### Debugging

**Backend debugging:**
```bash
# View backend logs
docker compose logs -f api

# Access Python shell
docker compose exec api flask shell
```

**Frontend debugging:**
```bash
# View frontend logs
docker compose logs -f web

# Access Node shell
docker compose exec web sh
```

### Database Management

**Run migrations:**
```bash
docker compose exec api flask db migrate -m "Description"
docker compose exec api flask db upgrade
```

**Access database:**
```bash
docker compose exec db psql -U socapp -d socapp
```

**Backup database:**
```bash
# Uses credentials from .env
docker compose exec db pg_dump -U ${POSTGRES_USER:-socapp} ${POSTGRES_DB:-socapp} > backup.sql
```

**Restore database:**
```bash
# Uses credentials from .env
docker compose exec -T db psql -U ${POSTGRES_USER:-socapp} -d ${POSTGRES_DB:-socapp} < backup.sql
```

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Check what's using the port
lsof -i :5432  # PostgreSQL
lsof -i :5050  # Backend
lsof -i :8000  # Kong Proxy
lsof -i :3000  # Frontend

# Change ports in docker-compose.yml
# Example: "5433:5432" instead of "5432:5432"
```

### Service Won't Start

```bash
# Check service logs
docker compose logs api

# Check service health
docker compose ps

# Restart service
docker compose restart api

# Rebuild service
docker compose build --no-cache api
docker compose up -d api
```

### Database Connection Issues

```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Verify connection from backend
# Connection string uses DATABASE_URL from .env
docker compose exec api python -c "
import os
from sqlalchemy import create_engine
db_url = os.environ.get('DATABASE_URL', 'postgresql://socapp:change-me-in-production@db:5432/socapp')
engine = create_engine(db_url)
try:
    engine.connect()
    print('Connection successful!')
except Exception as e:
    print(f'Connection failed: {e}')
"
```

### Kong Configuration Issues

```bash
# Check Kong logs
docker compose logs kong

# Validate Kong configuration
docker compose exec kong kong config parse /kong/kong.yml

# Reload Kong configuration
docker compose restart kong
```

### Frontend Build Issues

```bash
# Clear Next.js cache
docker compose exec web rm -rf .next

# Reinstall dependencies
docker compose exec web rm -rf node_modules
docker compose exec web npm install

# Rebuild
docker compose restart web
```

### Volume Issues

```bash
# Remove all volumes (WARNING: deletes data)
docker compose down -v

# Remove specific volume
docker volume rm socapp_postgres_data

# List volumes
docker volume ls
```

## Performance Optimization

### Build Cache

Docker caches layers. To optimize:

1. Put rarely-changing files first (requirements.txt, package.json)
2. Put frequently-changing files last (application code)
3. Use `.dockerignore` to exclude unnecessary files

### Resource Limits

Add resource limits in docker-compose.yml:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Production Considerations

For production deployment:

1. **Set secure secrets**: Generate strong random keys for JWT_SECRET_KEY, SECRET_KEY, and database passwords in .env
2. **Use production images**: Build optimized production images
3. **Enable HTTPS**: Configure SSL/TLS certificates
4. **Use external database**: Don't run PostgreSQL in Docker
5. **Configure Kong properly**: Set up rate limiting, authentication
6. **Enable monitoring**: Add logging and monitoring services
7. **Use Docker Swarm or Kubernetes**: For orchestration and scaling

## Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Kong Documentation](https://docs.konghq.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues:
1. Check logs: `docker compose logs -f`
2. Check service status: `docker compose ps`
3. Rebuild if needed: `docker compose build --no-cache`
4. Check the troubleshooting section above

