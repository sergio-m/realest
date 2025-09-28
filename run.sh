#!/bin/bash

# Real Estate Analyzer - Container Startup Script

echo "🏠 Starting Real Estate Analyzer..."

# Check if using Docker or Podman
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    COMPOSE_CMD="podman-compose"
    COMPOSE_FILE="podman-compose.yml"
    echo "Using Podman..."
elif command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    COMPOSE_FILE="docker-compose.yml"
    echo "Using Docker..."
else
    echo "❌ Neither Docker nor Podman found. Please install one of them."
    exit 1
fi

# Create logs directory
mkdir -p logs

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Start services
echo "Starting services with $COMPOSE_CMD..."
$COMPOSE_CMD -f $COMPOSE_FILE up --build -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
$COMPOSE_CMD -f $COMPOSE_FILE ps

echo "✅ Real Estate Analyzer is running!"
echo "🌐 Web interface: http://localhost:5000"
echo "🗄️  Database: localhost:5433"
echo ""
echo "To stop: $COMPOSE_CMD -f $COMPOSE_FILE down"
echo "To view logs: $COMPOSE_CMD -f $COMPOSE_FILE logs -f"