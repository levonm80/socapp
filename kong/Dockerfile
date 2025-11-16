FROM kong:3.5

# Install gettext for envsubst (if not already available)
RUN apk add --no-cache gettext

# Copy Kong configuration template
COPY kong.yml.template /kong/kong.yml.template

# Copy configuration generator script
COPY generate-kong-config.sh /kong/generate-kong-config.sh
RUN chmod +x /kong/generate-kong-config.sh

# Create startup script that generates config then starts Kong
# The script generates kong.yml from template, then starts Kong with proper env vars
RUN echo '#!/bin/sh\nset -e\n/kong/generate-kong-config.sh\n\n# Set Kong environment variables\nif [ -n "$KONG_PROXY_LISTEN" ]; then\n  export KONG_PROXY_LISTEN\nfi\nif [ -n "$KONG_ADMIN_LISTEN" ]; then\n  export KONG_ADMIN_LISTEN\nfi\nexport KONG_DATABASE=off\nexport KONG_DECLARATIVE_CONFIG=/kong/kong.yml\nexport KONG_PROXY_ACCESS_LOG=/dev/stdout\nexport KONG_ADMIN_ACCESS_LOG=/dev/stdout\nexport KONG_PROXY_ERROR_LOG=/dev/stderr\nexport KONG_ADMIN_ERROR_LOG=/dev/stderr\n\n# Start Kong\nexec kong docker-start' > /kong/start-kong.sh && \
    chmod +x /kong/start-kong.sh

# Set working directory
WORKDIR /kong

# Use the startup script as entrypoint
ENTRYPOINT ["/kong/start-kong.sh"]

