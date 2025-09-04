# TNBarMenu Deployment Guide

This guide explains how to deploy TNBarMenu on different machines using the automated Docker build system.

## 🚀 Quick Deployment (Recommended)

For the easiest deployment, use our automated deployment script:

```bash
# Download and run the deployment script
curl -L -o deploy.sh https://github.com/your-username/tnbarmenu/releases/latest/download/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Check for Docker and Docker Compose
- Download the production compose file
- Pull the pre-built Docker images
- Start the application

## 📦 Manual Deployment

### Prerequisites
- Docker and Docker Compose installed
- Internet connection to pull images

### Steps

1. **Download the production compose file:**
   ```bash
   wget https://github.com/your-username/tnbarmenu/releases/latest/download/docker-compose.prod.yml
   ```

2. **Create the build directory:**
   ```bash
   mkdir -p build
   ```

3. **Start the application:**
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## 🔄 GitHub Actions Workflow

The project includes a GitHub Actions workflow (`.github/workflows/build-and-push.yml`) that automatically:

1. **Builds Docker images** for both frontend and backend
2. **Pushes images** to GitHub Container Registry (ghcr.io)
3. **Creates multi-platform images** (AMD64 and ARM64)
4. **Generates release artifacts** for tagged versions
5. **Creates GitHub releases** with deployment files

### Triggering Builds

The workflow triggers on:
- **Push to main/master branch** → Builds `latest` images
- **Pull requests** → Builds PR-specific images  
- **Tags matching `v*`** → Builds versioned releases
- **Manual trigger** → Can be run manually from GitHub Actions tab

### Using Specific Versions

To deploy a specific version:
```bash
TAG=v1.0.0 docker compose -f docker-compose.prod.yml up -d
```

Or with the deployment script:
```bash
./deploy.sh v1.0.0
```

## 🏗️ Local Development vs Production

### Development (with source code)
```bash
# Uses docker-compose.yml + docker-compose.override.yml
# Builds images locally and mounts source code
USER_ID=$(id -u) GROUP_ID=$(id -g) docker compose up --build
```

### Production (pre-built images)
```bash
# Uses docker-compose.prod.yml
# Pulls pre-built images from registry
docker compose -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file for custom configuration:
```env
# Image tag (for production deployments)
TAG=v1.0.0

# Custom ports
FRONTEND_PORT=3000
BACKEND_PORT=5000
```

### Persistent Data

The application stores generated files in the `./build` directory. Make sure this directory persists across container restarts.

## 🚨 Troubleshooting

### Permission Issues
If you encounter permission errors with the build directory:
```bash
sudo chown -R $USER:$USER build
```

### Port Conflicts
If ports 3000 or 5000 are already in use, modify the ports in the compose file:
```yaml
services:
  frontend:
    ports:
      - "8080:3000"  # Changed from 3000:3000
```

### Container Logs
Check application logs:
```bash
docker compose -f docker-compose.prod.yml logs
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs backend
```

### Updating
To update to the latest version:
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

## 📋 Requirements for Target Machine

- **Operating System:** Any OS that supports Docker (Linux, macOS, Windows)
- **Docker:** Version 20.10+ recommended
- **Docker Compose:** Version 2.0+ recommended  
- **Memory:** At least 1GB available RAM
- **Storage:** 1GB free space for images and generated files
- **Network:** Internet connection for initial image pull

## 🔐 Security Notes

- Images are built with non-root users for security
- The application only exposes necessary ports
- No sensitive data is included in the images
- Use HTTPS in production with a reverse proxy (nginx, traefik, etc.)

## 📊 Monitoring

For production deployments, consider adding:
- Health checks (already included in compose files)
- Log aggregation
- Monitoring (Prometheus, etc.)
- Backup of the `build` directory

## ❓ Support

If you encounter issues:
1. Check the logs using the commands above
2. Ensure Docker and Docker Compose are properly installed
3. Verify network connectivity for image pulling
4. Check GitHub Issues for known problems
