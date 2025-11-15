# Kong Gateway Configuration

This directory contains the Kong Gateway declarative configuration file.

## Configuration File

- `kong.yml`: Kong declarative configuration (DB-less mode)

## Important: JWT Secret Configuration

**Kong does not support environment variable substitution in YAML files.** You must manually update the JWT secret in `kong.yml` to match your `JWT_SECRET_KEY` from `.env`.

### Steps to Configure JWT Secret:

1. **Set your JWT secret in `.env`**:
   ```bash
   JWT_SECRET_KEY=your-secure-random-key-here
   ```

2. **Update `kong/kong.yml`**:
   - Open `kong/kong.yml`
   - Find the `consumers` section at the bottom
   - Update the `secret` value to match your `JWT_SECRET_KEY`:
     ```yaml
     consumers:
       - username: default-jwt-consumer
         jwt_secrets:
           - key: flask-jwt
             algorithm: HS256
             secret: your-secure-random-key-here  # Must match JWT_SECRET_KEY
             rsa_public_key: null
     ```

3. **Restart Kong**:
   ```bash
   docker compose restart kong
   ```

## Why Manual Update?

Kong Gateway's declarative configuration mode doesn't support environment variable substitution. The secret must be hardcoded in the YAML file. However, since this file is in version control, you should:

- **For development**: Use a development secret (not production secrets)
- **For production**: Use a secrets management system or generate the config file dynamically
- **Never commit production secrets** to version control

## Alternative: Dynamic Configuration Generation

For production, you can generate the Kong config file dynamically:

```bash
# Generate kong.yml from template
envsubst < kong/kong.yml.template > kong/kong.yml
```

Or use a script that reads from environment variables and generates the YAML file.

