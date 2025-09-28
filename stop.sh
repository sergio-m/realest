#!/bin/bash

echo "🛑 Stopping Real Estate Analyzer..."

if command -v podman &> /dev/null; then
    podman-compose -f podman-compose.yml down
elif command -v docker &> /dev/null; then
    docker-compose -f docker-compose.yml down
fi

echo "✅ Services stopped."