#!/bin/sh
# Generate kong.yml from template using environment variables
# This script replaces placeholders in kong.yml.template with actual values

set -e

# Check required environment variables
if [ -z "$JWT_SECRET_KEY" ]; then
  echo "ERROR: JWT_SECRET_KEY environment variable is required"
  exit 1
fi

if [ -z "$BACKEND_URL" ]; then
  echo "ERROR: BACKEND_URL environment variable is required"
  exit 1
fi

# Default CORS origins if not set (for development)
CORS_ORIGINS_INPUT="${CORS_ORIGINS:-http://localhost:3000}"

# First, replace simple variables with sed
# Use /tmp for temporary file (writable by all users)
sed -e "s|\${JWT_SECRET_KEY}|${JWT_SECRET_KEY}|g" \
    -e "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /kong/kong.yml.template > /tmp/kong.yml.tmp

# Then replace CORS_ORIGINS placeholder with YAML list (multiline)
# Write each CORS origin to temp file separately (without indentation, will be added in awk)
# This avoids shell newline handling issues
> /tmp/cors_list.tmp
for origin in $(echo "$CORS_ORIGINS_INPUT" | tr ',' ' '); do
  if [ -n "$origin" ]; then
    echo "- $origin" >> /tmp/cors_list.tmp
  fi
done

# Match the line containing ${CORS_ORIGINS} and replace with the YAML list
# Use here-document with -f - to read script from stdin, avoiding shell expansion issues
awk -f - /tmp/kong.yml.tmp > /kong/kong.yml <<'AWK_EOF'
  BEGIN {
    # Read CORS list from temp file and add proper indentation (16 spaces to match template)
    # Use explicit 16 spaces - be very careful with spacing
    while ((getline cors_line < "/tmp/cors_list.tmp") > 0) {
      # Remove trailing newline/whitespace
      sub(/[ \t\n\r]+$/, "", cors_line)
      # Add exactly 16 spaces for indentation
      indented_line = "                " cors_line
      if (cors_list == "") {
        cors_list = indented_line
      } else {
        cors_list = cors_list "\n" indented_line
      }
    }
    close("/tmp/cors_list.tmp")
  }
  /^\s*\$\{CORS_ORIGINS\}$/ {
    print cors_list
    next
  }
  {
    # Also handle inline replacements (though we don't expect this)
    gsub(/\$\{CORS_ORIGINS\}/, cors_list)
    print
  }
AWK_EOF

rm /tmp/cors_list.tmp

rm /tmp/kong.yml.tmp

echo "Generated kong.yml successfully"
# Use printf for POSIX-compliant substring (first 10 characters)
JWT_PREVIEW=$(printf "%.10s" "$JWT_SECRET_KEY")
echo "JWT Secret: ${JWT_PREVIEW}... (truncated for security)"
echo "Backend URL: $BACKEND_URL"
echo "CORS Origins: $CORS_ORIGINS_INPUT"
