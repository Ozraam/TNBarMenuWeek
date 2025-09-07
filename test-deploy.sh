#!/bin/bash

# Quick TNBarMenu Production Test
# This script tests the production deployment using local files

set -e

echo "🚀 Testing TNBarMenu Production Deployment"
echo "==========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Create build directory
echo "📁 Creating build directory..."
mkdir -p build

# Start the services
echo "🏃 Starting services using production images..."
if docker compose version &> /dev/null; then
    docker compose -f docker-compose.prod.yml up -d
else
    docker-compose -f docker-compose.prod.yml up -d
fi

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo ""
    echo "🎉 TNBarMenu is running in production mode!"
    echo "============================================"
    echo "Frontend: http://localhost:3000"
    echo "Backend:  http://localhost:5000"
    echo ""
    echo "This is using the pre-built Docker images from GitHub Container Registry"
    echo "Perfect for deployment on other machines!"
    echo ""
    echo "To stop:"
    if docker compose version &> /dev/null; then
        echo "  docker compose -f docker-compose.prod.yml down"
    else
        echo "  docker-compose -f docker-compose.prod.yml down"
    fi
else
    echo "❌ Services failed to start. Check logs:"
    if docker compose version &> /dev/null; then
        docker compose -f docker-compose.prod.yml logs
    else
        docker-compose -f docker-compose.prod.yml logs
    fi
fi
