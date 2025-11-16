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
sed -e "s|\${JWT_SECRET_KEY}|${JWT_SECRET_KEY}|g" \
    -e "s|\${BACKEND_URL}|${BACKEND_URL}|g" \
    /kong/kong.yml.template > /kong/kong.yml.tmp

# Then replace CORS_ORIGINS placeholder with YAML list (multiline)
# Match the line containing ${CORS_ORIGINS} and replace with the YAML list
awk -v cors_list="$CORS_YAML_LIST" '
  /^\s*\$\{CORS_ORIGINS\}$/ {
    print cors_list
    next
  }
  {
    # Also handle inline replacements (though we don't expect this)
    gsub(/\$\{CORS_ORIGINS\}/, cors_list)
    print
  }
' /kong/kong.yml.tmp > /kong/kong.yml

rm /kong/kong.yml.tmp

echo "Generated kong.yml successfully"
echo "JWT Secret: ${JWT_SECRET_KEY:0:10}... (truncated for security)"
echo "Backend URL: $BACKEND_URL"
echo "CORS Origins: $CORS_ORIGINS_INPUT"
