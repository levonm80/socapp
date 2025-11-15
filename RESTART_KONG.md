# Fixing CORS Issues - Kong Restart Required

The CORS configuration has been updated in `kong/kong.yml`, but Kong needs to be restarted to apply the changes.

## Option 1: Restart Kong using Docker Compose

If you're using Docker Compose:

```bash
docker-compose restart kong
```

Or if using newer Docker Compose syntax:

```bash
docker compose restart kong
```

## Option 2: Reload Kong Configuration

If Kong is running and you have access to Kong admin API:

```bash
# Reload Kong configuration
docker exec <kong-container-name> kong reload

# Or if Kong admin is exposed
curl -X POST http://localhost:8001/config?check_hash=1
```

## Option 3: Full Docker Compose Restart

If the above doesn't work, restart all services:

```bash
docker-compose down
docker-compose up -d
```

## Verification

After restarting, test the CORS preflight request:

```bash
curl -X OPTIONS http://localhost:8000/api/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v
```

You should see `Access-Control-Allow-Origin: http://localhost:3000` in the response headers.

