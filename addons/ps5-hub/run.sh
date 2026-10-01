#!/bin/bash
set -e

echo "Starting PS5 Hub..."

cd /app/www

# Substitute environment variables in plugins.json
PAYLOAD_MANAGER_URL="${PAYLOAD_MANAGER_URL:-http://192.168.1.4:8000}"
WEBKIT_AUTOLOADER_URL="${WEBKIT_AUTOLOADER_URL:-http://192.168.1.3:8080/app/v0/}"

export PAYLOAD_MANAGER_URL WEBKIT_AUTOLOADER_URL

envsubst < plugins.json.tpl > plugins.json 2>/dev/null || {
  # If envsubst not available, use sed
  sed -e "s|\${PAYLOAD_MANAGER_URL:-http://192.168.1.4:8000}|$PAYLOAD_MANAGER_URL|g" \
      -e "s|\${WEBKIT_AUTOLOADER_URL:-http://localhost:8080/app/v0/}|$WEBKIT_AUTOLOADER_URL|g" \
      plugins.json > plugins.json.tmp && mv plugins.json.tmp plugins.json
}

python3 -m http.server 8081
