# Deployment Guide

This guide explains how to deploy the Deal Brief App using the pre-built Docker images published to GitHub Container Registry (GHCR).

## Table of Contents
1. [Quick Start with Pre-built Images](#quick-start-with-pre-built-images)
2. [Environment Configuration](#environment-configuration)
3. [Deployment Options](#deployment-options)
4. [Cloud Platform Deployment](#cloud-platform-deployment)

## Quick Start with Pre-built Images

The Deal Brief App is automatically built and published to GitHub Container Registry whenever changes are pushed to the main branch.

### Prerequisites
- Docker and Docker Compose installed
- OpenAI API key
- Internet connection to pull images from GHCR

### Using Docker Compose with Pre-built Images

1. **Create a deployment directory**:
   ```bash
   mkdir deal-brief-deployment
   cd deal-brief-deployment
   ```

2. **Create a `docker-compose.yml` file**:
   ```yaml
   version: '3.8'
   
   services:
     db:
       image: postgres:15
       environment:
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: postgres
         POSTGRES_DB: dealbriefs
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
       healthcheck:
         test: ["CMD-SHELL", "pg_isready -U postgres"]
         interval: 10s
         timeout: 5s
         retries: 5
   
     backend:
       image: ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:latest
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:postgres@db:5432/dealbriefs
         - OPENAI_API_KEY=${OPENAI_API_KEY}
       depends_on:
         db:
           condition: service_healthy
   
     frontend:
       image: ghcr.io/mohamed-abdelgawad99/deal_brief_app/frontend:latest
       ports:
         - "8501:8501"
       environment:
         - BACKEND_URL=http://backend:8000
       depends_on:
         - backend
   
   volumes:
     postgres_data:
   ```

3. **Create a `.env` file** with your OpenAI API key:
   ```bash
   echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
   ```

4. **Start the application**:
   ```bash
   docker compose up -d
   ```

5. **Access the application**:
   - Frontend UI: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

6. **Stop the application**:
   ```bash
   docker compose down
   ```

## Environment Configuration

### Required Environment Variables

#### Backend
- `DATABASE_URL`: PostgreSQL connection string (format: `postgresql://user:password@host:port/database`)
- `OPENAI_API_KEY`: Your OpenAI API key for LLM processing

#### Frontend
- `BACKEND_URL`: URL to the backend API (default: `http://backend:8000` in Docker Compose)

### Optional Environment Variables
- `POSTGRES_USER`: Database username (default: `postgres`)
- `POSTGRES_PASSWORD`: Database password (default: `postgres`)
- `POSTGRES_DB`: Database name (default: `dealbriefs`)

## Deployment Options

### Option 1: Using Specific Image Tags

Instead of using `:latest`, you can use specific versions:

```yaml
backend:
  image: ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:v1.0.0
  # ... rest of config

frontend:
  image: ghcr.io/mohamed-abdelgawad99/deal_brief_app/frontend:v1.0.0
  # ... rest of config
```

Available tags:
- `latest` - Latest build from main branch
- `v*.*.*` - Semantic version tags (e.g., v1.0.0, v1.2.3)
- `main-<sha>` - Specific commit SHA from main branch

### Option 2: Running Individual Containers

If you prefer to run containers individually:

```bash
# Start PostgreSQL
docker run -d --name dealbrief-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=dealbriefs \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15

# Start Backend
docker run -d --name dealbrief-backend \
  -e DATABASE_URL=postgresql://postgres:postgres@dealbrief-db:5432/dealbriefs \
  -e OPENAI_API_KEY=your-api-key \
  -p 8000:8000 \
  --link dealbrief-db:db \
  ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:latest

# Start Frontend
docker run -d --name dealbrief-frontend \
  -e BACKEND_URL=http://dealbrief-backend:8000 \
  -p 8501:8501 \
  --link dealbrief-backend:backend \
  ghcr.io/mohamed-abdelgawad99/deal_brief_app/frontend:latest
```

## Cloud Platform Deployment

### Docker Compose on Cloud VM (AWS EC2, GCP Compute, DigitalOcean, etc.)

1. **Provision a VM** with Docker installed

2. **SSH into the VM** and clone the deployment setup:
   ```bash
   mkdir deal-brief-deployment
   cd deal-brief-deployment
   # Download the docker-compose.yml from this guide
   ```

3. **Set environment variables**:
   ```bash
   export OPENAI_API_KEY=your-api-key
   ```

4. **Run the application**:
   ```bash
   docker compose up -d
   ```

5. **Configure firewall** to allow:
   - Port 8501 (Frontend)
   - Port 8000 (Backend API)

### AWS ECS/Fargate

1. Create a task definition with three containers:
   - PostgreSQL (use RDS instead for production)
   - Backend
   - Frontend

2. Configure environment variables in the task definition

3. Create a service to run the task

4. Set up an Application Load Balancer for public access

### Google Cloud Run

1. Deploy each service separately:
   ```bash
   # Backend
   gcloud run deploy dealbrief-backend \
     --image ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:latest \
     --set-env-vars DATABASE_URL=...,OPENAI_API_KEY=... \
     --platform managed

   # Frontend
   gcloud run deploy dealbrief-frontend \
     --image ghcr.io/mohamed-abdelgawad99/deal_brief_app/frontend:latest \
     --set-env-vars BACKEND_URL=... \
     --platform managed
   ```

2. Use Cloud SQL for PostgreSQL database

### Kubernetes

Create Kubernetes manifests for deployment:

```yaml
# Example deployment for backend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dealbrief-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: dealbrief-backend
  template:
    metadata:
      labels:
        app: dealbrief-backend
    spec:
      containers:
      - name: backend
        image: ghcr.io/mohamed-abdelgawad99/deal_brief_app/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: dealbrief-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: dealbrief-secrets
              key: openai-api-key
```

## Updating to Latest Version

To update to the latest version:

```bash
# Pull latest images
docker compose pull

# Restart services
docker compose up -d
```

## Troubleshooting

### Images Not Accessible
If you cannot pull images from GHCR, they may be private. Authenticate with GitHub:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Database Connection Issues
- Ensure PostgreSQL is fully started before backend starts
- Check DATABASE_URL format
- Verify network connectivity between containers

### Backend API Errors
- Check OPENAI_API_KEY is set correctly
- Review backend logs: `docker compose logs backend`
- Ensure database migrations have run

### Frontend Connection Issues
- Verify BACKEND_URL points to the correct backend service
- Check if backend is accessible from frontend container
- Review frontend logs: `docker compose logs frontend`

## Security Considerations

1. **Never commit `.env` files** with real API keys to version control
2. **Use secrets management** in production (AWS Secrets Manager, HashiCorp Vault, etc.)
3. **Enable HTTPS** using a reverse proxy (nginx, Traefik, Caddy)
4. **Restrict database access** to backend service only
5. **Use strong PostgreSQL passwords** in production
6. **Regularly update images** to get security patches

## Production Best Practices

1. **Use specific version tags** instead of `latest`
2. **Set up monitoring** (Prometheus, Datadog, New Relic)
3. **Configure logging** to centralized location
4. **Set up backups** for PostgreSQL database
5. **Use managed database services** (RDS, Cloud SQL) instead of containerized PostgreSQL
6. **Implement health checks** for all services
7. **Set resource limits** for containers
8. **Use a reverse proxy** (nginx, Traefik) for TLS termination and routing

## Support

For issues or questions:
- GitHub Issues: https://github.com/Mohamed-Abdelgawad99/deal_brief_app/issues
- Repository: https://github.com/Mohamed-Abdelgawad99/deal_brief_app
