#!/bin/bash

# TNBarMenu Deployment Script
# This script downloads and runs the latest version of TNBarMenu using Docker

set -e

# Configuration
REPO="ozraam/tnbarmenu"  # Replace with your actual GitHub username/repo
TAG="${1:-latest}"
COMPOSE_FILE="docker-compose.prod.yml"

echo "🚀 TNBarMenu Deployment Script"
echo "================================="
echo "Repository: $REPO"
echo "Version: $TAG"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create build directory
echo "📁 Creating build directory..."
mkdir -p build

# Download production docker-compose file
echo "⬇️  Downloading production compose file..."
if command -v curl &> /dev/null; then
    curl -L -o $COMPOSE_FILE "https://github.com/$REPO/releases/latest/download/docker-compose.prod.yml"
elif command -v wget &> /dev/null; then
    wget -O $COMPOSE_FILE "https://github.com/$REPO/releases/latest/download/docker-compose.prod.yml"
else
    echo "❌ Neither curl nor wget is available. Please install one of them."
    exit 1
fi

if [ ! -f $COMPOSE_FILE ]; then
    echo "❌ Failed to download compose file. Please check your internet connection and repository name."
    exit 1
fi

echo "✅ Compose file downloaded successfully"

# Set the TAG environment variable
export TAG

# Pull the images
echo "⬇️  Pulling Docker images..."
if docker compose version &> /dev/null; then
    docker compose -f $COMPOSE_FILE pull
else
    docker-compose -f $COMPOSE_FILE pull
fi

# Start the services
echo "🏃 Starting services..."
if docker compose version &> /dev/null; then
    docker compose -f $COMPOSE_FILE up -d
else
    docker-compose -f $COMPOSE_FILE up -d
fi

echo ""
echo "🎉 TNBarMenu is now running!"
echo "================================="
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "To stop the application:"
if docker compose version &> /dev/null; then
    echo "  docker compose -f $COMPOSE_FILE down"
else
    echo "  docker-compose -f $COMPOSE_FILE down"
fi
echo ""
echo "To check logs:"
if docker compose version &> /dev/null; then
    echo "  docker compose -f $COMPOSE_FILE logs"
else
    echo "  docker-compose -f $COMPOSE_FILE logs"
fi
echo ""
echo "To update to a newer version:"
echo "  ./deploy.sh [version]"
