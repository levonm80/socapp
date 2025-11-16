# Railway Deployment Guide

This guide explains how to deploy the SOC Application to Railway.com.

## Architecture Overview

The application consists of four services:

1. **PostgreSQL** - Database (Railway managed service)
2. **Backend** - Flask API (Python)
3. **Kong Gateway** - API Gateway (handles JWT validation, CORS, routing)
4. **Frontend** - Next.js application (React/TypeScript)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│    Kong     │────────▶│   Backend   │────────▶│  PostgreSQL │
│  (Next.js)  │         │   Gateway   │         │   (Flask)   │         │  (Railway)  │
│  Port 3000  │         │  Port 8000  │         │  Port 5000  │         │  Managed    │
└─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘
```

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository (this codebase)
3. OpenAI API key (for AI features)

## Step 1: Create Railway Project

1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account and select this repository
5. Railway will detect the monorepo structure

## Step 2: Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically create a PostgreSQL service
4. **Important**: Note the `DATABASE_URL` environment variable that Railway provides
   - It will be in the format: `postgresql://postgres:password@hostname:5432/railway`

## Step 3: Deploy Backend Service

1. In Railway project, click "New" → "GitHub Repo"
2. Select your repository
3. Railway will detect the `backend/Dockerfile`
4. Configure the service:
   - **Root Directory**: `/backend`
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: (auto-detected from Dockerfile)

### Backend Environment Variables

Set these in Railway dashboard (Service → Variables):

```
DATABASE_URL=<from PostgreSQL service>
FLASK_ENV=production
JWT_SECRET_KEY=<generate a secure random key>
SECRET_KEY=<generate a secure random key>
OPENAI_API_KEY=<your OpenAI API key>
PORT=5000
```

**To generate secure keys:**
```bash
# Generate JWT_SECRET_KEY (32+ characters)
openssl rand -hex 32

# Generate SECRET_KEY (32+ characters)
openssl rand -hex 32
```

**Important**: Use the **same** `JWT_SECRET_KEY` for both Backend and Kong services!

### Backend Service Settings

- **Health Check Path**: `/api/health`
- **Port**: 5000 (Railway will assign a public port automatically)

## Step 4: Deploy Kong Gateway

1. In Railway project, click "New" → "GitHub Repo"
2. Select your repository
3. Configure the service:
   - **Root Directory**: `/kong`
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: (auto-detected from Dockerfile)

### Kong Environment Variables

Set these in Railway dashboard:

```
JWT_SECRET_KEY=<SAME AS BACKEND - CRITICAL!>
BACKEND_URL=http://backend-service:5000
CORS_ORIGINS=https://your-frontend-domain.railway.app
KONG_PROXY_LISTEN=0.0.0.0:8000
KONG_ADMIN_LISTEN=0.0.0.0:8001
```

**Important Notes:**
- `JWT_SECRET_KEY` must match the Backend service exactly
- `BACKEND_URL` uses Railway's internal service name (replace `backend-service` with your actual backend service name)
- `CORS_ORIGINS` should include your frontend's Railway URL (you'll get this after deploying frontend)
- You can add multiple origins: `https://domain1.com https://domain2.com`

### Finding Service Names

Railway provides internal hostnames for services. To find your backend service name:
1. Go to Backend service → Settings → Networking
2. Look for "Private Networking" - the hostname will be something like `backend-production.up.railway.app` or use the service name directly

### Kong Service Settings

- **Port**: 8000 (for proxy)
- **Public Port**: Railway will assign automatically
- Kong Admin API (port 8001) is for internal use only

## Step 5: Deploy Frontend Service

1. In Railway project, click "New" → "GitHub Repo"
2. Select your repository
3. Configure the service:
   - **Root Directory**: `/frontend`
   - **Build Command**: (auto-detected from Dockerfile)
   - **Start Command**: (auto-detected from Dockerfile)

### Frontend Environment Variables

**CRITICAL**: Set these environment variables in Railway dashboard **BEFORE** the first build:

```
NEXT_PUBLIC_API_URL=https://your-kong-domain.railway.app/api
NODE_ENV=production
PORT=3000
```

**Important Notes**: 
- `NEXT_PUBLIC_API_URL` should be Kong's public URL (not backend's URL)
- Get Kong's public URL from Railway dashboard (Service → Settings → Networking)
- **Next.js embeds `NEXT_PUBLIC_*` variables at BUILD TIME**, not runtime
- Railway automatically passes these as Docker build arguments
- If you change `NEXT_PUBLIC_API_URL` after building, you must **redeploy** to rebuild the app

### Frontend Service Settings

- **Port**: 3000
- Railway will assign a public domain automatically (e.g., `frontend-production.up.railway.app`)

## Step 6: Update CORS Origins

After deploying Frontend, update Kong's `CORS_ORIGINS` environment variable:

1. Go to Kong service → Variables
2. Update `CORS_ORIGINS` to include your frontend URL:
   ```
   CORS_ORIGINS=https://your-frontend-domain.railway.app
   ```
3. Redeploy Kong service (Railway will restart automatically)

## Step 7: Database Migrations

The backend automatically runs migrations on startup (see `backend/run.py`). 

To manually run migrations:
1. Go to Backend service → Deployments → Latest
2. Click "View Logs"
3. Check for migration output

Or use Railway CLI:
```bash
railway run --service backend flask db upgrade
```

## Step 8: Verify Deployment

1. **Check Backend Health**:
   ```bash
   curl https://your-backend-domain.railway.app/api/health
   ```

2. **Check Kong**:
   ```bash
   curl https://your-kong-domain.railway.app/api/health
   ```

3. **Check Frontend**:
   - Visit `https://your-frontend-domain.railway.app`
   - Try logging in (default test user: `test@example.com` / `testpassword123`)

## Environment Variables Summary

### Shared Variables (must match)
- `JWT_SECRET_KEY` - **Must be identical** in Backend and Kong

### Backend Variables
```
DATABASE_URL (from PostgreSQL service)
FLASK_ENV=production
JWT_SECRET_KEY
SECRET_KEY
OPENAI_API_KEY
PORT=5000
```

### Kong Variables
```
JWT_SECRET_KEY (same as Backend)
BACKEND_URL (internal Railway hostname)
CORS_ORIGINS (frontend public URL)
KONG_PROXY_LISTEN=0.0.0.0:8000
KONG_ADMIN_LISTEN=0.0.0.0:8001
```

### Frontend Variables
```
NEXT_PUBLIC_API_URL (Kong's public URL)
NODE_ENV=production
PORT=3000
```

## Environment Variable Examples

### Backend (.env.example)
```bash
DATABASE_URL=postgresql://postgres:password@hostname:5432/railway
FLASK_ENV=production
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
SECRET_KEY=<generate-with-openssl-rand-hex-32>
OPENAI_API_KEY=sk-...
PORT=5000
```

### Kong (.env.example)
```bash
JWT_SECRET_KEY=<same-as-backend>
BACKEND_URL=http://backend-service:5000
CORS_ORIGINS=https://your-frontend.railway.app
KONG_PROXY_LISTEN=0.0.0.0:8000
KONG_ADMIN_LISTEN=0.0.0.0:8001
```

### Frontend (.env.local.example)
```bash
NEXT_PUBLIC_API_URL=https://your-kong-service.railway.app/api
NODE_ENV=production
PORT=3000
```

**Note**: Create `.env.example` files in your repository (without real values) to document required variables. These example files are safe to commit.

## Service Dependencies

Railway will automatically handle service startup order, but ensure:
1. PostgreSQL is running first
2. Backend starts after PostgreSQL (depends on DATABASE_URL)
3. Kong starts after Backend (needs backend URL)
4. Frontend can start independently (but needs Kong URL)

## Troubleshooting

### Backend won't start
- Check `DATABASE_URL` is correct
- Verify PostgreSQL service is running
- Check logs: Railway Dashboard → Backend Service → Logs

### Kong can't connect to Backend
- Verify `BACKEND_URL` uses Railway's internal hostname
- Check both services are in the same Railway project
- Ensure Backend is healthy: `curl https://backend-url/api/health`

### Frontend can't reach API
- Verify `NEXT_PUBLIC_API_URL` points to Kong (not Backend)
- Check Kong's CORS origins include frontend URL
- Check browser console for CORS errors

### JWT Authentication fails
- **Most common**: `JWT_SECRET_KEY` mismatch between Backend and Kong
- Verify both services use identical `JWT_SECRET_KEY` value
- Check Kong logs for JWT validation errors

### Database connection errors
- Verify `DATABASE_URL` from PostgreSQL service
- Check PostgreSQL service is running
- Ensure migrations ran successfully (check backend logs)

## Custom Domains

Railway allows custom domains:

1. Go to Service → Settings → Networking
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed
5. Update `CORS_ORIGINS` in Kong to include custom domain

## Monitoring

- **Logs**: View real-time logs in Railway Dashboard
- **Metrics**: Railway provides basic metrics (CPU, Memory, Network)
- **Health Checks**: Configure health check endpoints in service settings

## Cost Considerations

Railway pricing:
- Free tier: $5 credit/month
- Paid plans: Pay-as-you-go

Services to monitor:
- PostgreSQL: Database storage and queries
- Backend: Compute time (especially AI API calls)
- Kong: Minimal compute (just proxying)
- Frontend: Static assets and compute

## Security Best Practices

1. **Never commit secrets** - All secrets in Railway environment variables
2. **Use strong JWT secrets** - Generate with `openssl rand -hex 32`
3. **Restrict CORS origins** - Only include your frontend domain(s)
4. **Enable Railway's built-in security** - Use Railway's private networking
5. **Regular updates** - Keep dependencies updated
6. **Monitor logs** - Check for suspicious activity

## Rollback

If deployment fails:
1. Go to Service → Deployments
2. Find last working deployment
3. Click "Redeploy"

## Additional Resources

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project README: See `README.md` for local development setup

