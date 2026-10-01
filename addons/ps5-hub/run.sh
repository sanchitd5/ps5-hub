#!/bin/bash
set -e

echo "Starting PS5 Hub..."

cd /app/www

python3 -m http.server 80
