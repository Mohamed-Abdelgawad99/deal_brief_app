# Quick Start - Deploying Deal Brief App

This guide helps you deploy the Deal Brief App in under 5 minutes using pre-built Docker images.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Deployment Steps

### Option 1: Using the Deploy Script (Recommended)

1. **Clone or download the deployment files**:
   ```bash
   git clone https://github.com/Mohamed-Abdelgawad99/deal_brief_app.git
   cd deal_brief_app
   ```

2. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```
   
   The script will:
   - Check for required dependencies
   - Create `.env` file if it doesn't exist
   - Pull the latest Docker images
   - Start all services
   - Display access URLs

3. **Access the application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/docs

### Option 2: Manual Deployment

1. **Create `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Start the application**:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

3. **Access the application**:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000/docs

## Common Commands

### View Logs
```bash
docker compose -f docker-compose.prod.yml logs -f
```

### Stop Services
```bash
docker compose -f docker-compose.prod.yml down
```

### Update to Latest Version
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

### Restart Services
```bash
docker compose -f docker-compose.prod.yml restart
```

## Troubleshooting

### Container Won't Start
Check logs for the specific service:
```bash
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
```

### Database Connection Issues
Ensure the database is healthy:
```bash
docker compose -f docker-compose.prod.yml ps
```

### Port Already in Use
Edit `.env` file and change the port numbers:
```env
BACKEND_PORT=8001
FRONTEND_PORT=8502
```

## Advanced Configuration

For production deployments, cloud platforms, Kubernetes, and more advanced options, see [DEPLOYMENT.md](DEPLOYMENT.md).

## Support

- **Issues**: https://github.com/Mohamed-Abdelgawad99/deal_brief_app/issues
- **Documentation**: [README.md](README.md)
