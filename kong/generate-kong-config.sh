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

# Convert CORS_ORIGINS to YAML list format
# Split by comma or space, then format as YAML list items with proper indentation
CORS_YAML_LIST=""
FIRST=true
for origin in $(echo "$CORS_ORIGINS_INPUT" | tr ',' ' '); do
  if [ -n "$origin" ]; then
    if [ "$FIRST" = true ]; then
      CORS_YAML_LIST="                - $origin"
      FIRST=false
    else
      CORS_YAML_LIST="$CORS_YAML_LIST
                - $origin"
    fi
  fi
done

# First, replace simple variables with sed
# Use /tmp for temporary file (writable by all users)
sed -e "s|\${JWT_SECRET_KEY}|${JWT_SECRET_KEY}|g" \
    -e "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /kong/kong.yml.template > /tmp/kong.yml.tmp

# Then replace CORS_ORIGINS placeholder with YAML list (multiline)
# Write CORS list to temp file to avoid shell expansion issues with newlines
echo "$CORS_YAML_LIST" > /tmp/cors_list.tmp

# Match the line containing ${CORS_ORIGINS} and replace with the YAML list
# Use here-document to avoid shell expansion issues with $ in regex
awk <<'AWK_EOF' /tmp/kong.yml.tmp > /kong/kong.yml
  BEGIN {
    # Read CORS list from temp file
    while ((getline cors_line < "/tmp/cors_list.tmp") > 0) {
      if (cors_list == "") {
        cors_list = cors_line
      } else {
        cors_list = cors_list "\n" cors_line
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
echo "JWT Secret: ${JWT_SECRET_KEY:0:10}... (truncated for security)"
echo "Backend URL: $BACKEND_URL"
echo "CORS Origins: $CORS_ORIGINS_INPUT"
