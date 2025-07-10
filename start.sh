#!/bin/bash
echo "Starting Sustainability Dashboard..."
docker-compose down -v 2>/dev/null
docker-compose build --no-cache
docker-compose up -d