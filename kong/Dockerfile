FROM kong:3.5

# Switch to root to install packages
USER root

# Install gettext for envsubst (if not already available)
# Try Alpine (apk) first, then Debian/Ubuntu (apt-get) as fallback
RUN (command -v apk > /dev/null && apk add --no-cache gettext) || \
    (command -v apt-get > /dev/null && apt-get update && apt-get install -y --no-install-recommends gettext-base && rm -rf /var/lib/apt/lists/*) || \
    (echo "Warning: Could not install gettext. Using sed/awk fallback." && true)

# Copy Kong configuration template
COPY kong.yml.template /kong/kong.yml.template

# Copy configuration generator script
COPY generate-kong-config.sh /kong/generate-kong-config.sh
RUN chmod +x /kong/generate-kong-config.sh

# Create startup script that generates config then starts Kong
# The script generates kong.yml from template, then starts Kong with proper env vars
RUN echo '#!/bin/sh\nset -e\n/kong/generate-kong-config.sh\n\n# Set Kong environment variables\nif [ -n "$KONG_PROXY_LISTEN" ]; then\n  export KONG_PROXY_LISTEN\nfi\nif [ -n "$KONG_ADMIN_LISTEN" ]; then\n  export KONG_ADMIN_LISTEN\nfi\nexport KONG_DATABASE=off\nexport KONG_DECLARATIVE_CONFIG=/kong/kong.yml\nexport KONG_PROXY_ACCESS_LOG=/dev/stdout\nexport KONG_ADMIN_ACCESS_LOG=/dev/stdout\nexport KONG_PROXY_ERROR_LOG=/dev/stderr\nexport KONG_ADMIN_ERROR_LOG=/dev/stderr\nexport KONG_NGINX_DAEMON=off\n\n# Start Kong in foreground (required for Docker)\nexec kong start' > /kong/start-kong.sh && \
    chmod +x /kong/start-kong.sh

# Ensure files are accessible (Kong images use 'kong' user, but we'll make files readable)
# Get the default user from the base image and ensure files are accessible
RUN chmod -R a+r /kong/*.template /kong/*.sh 2>/dev/null || true && \
    chmod a+x /kong/*.sh 2>/dev/null || true

# Make /kong directory writable by kong user (needed for generate-kong-config.sh to write kong.yml)
# Get the kong user's UID/GID and ensure /kong is writable
RUN KONG_UID=$(id -u kong 2>/dev/null || echo 1000) && \
    KONG_GID=$(id -g kong 2>/dev/null || echo 1000) && \
    chown -R $KONG_UID:$KONG_GID /kong && \
    chmod -R u+w /kong

# Switch back to kong user (Kong images use 'kong' user by default)
USER kong

# Set working directory
WORKDIR /kong

# Use the startup script as entrypoint
ENTRYPOINT ["/kong/start-kong.sh"]

