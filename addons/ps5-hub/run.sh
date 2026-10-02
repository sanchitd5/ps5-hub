#!/usr/bin/with-contenv bashio
set -e

bashio::log.info "Starting PS5 Hub..."

cd /app/www

PAYLOAD_MANAGER_URL="$(bashio::config 'payload_manager_url')"
WEBKIT_AUTOLOADER_URL="$(bashio::config 'webkit_autoloader_url')"

export PAYLOAD_MANAGER_URL WEBKIT_AUTOLOADER_URL

envsubst < plugins.json.tpl > plugins.json

exec python3 /app/server.py
