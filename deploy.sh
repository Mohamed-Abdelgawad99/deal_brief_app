#!/bin/bash

# Quick deployment script for Deal Brief App
# This script helps you quickly deploy the app using pre-built Docker images

set -e

echo "🚀 Deal Brief App - Quick Deployment"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found"
    echo "Creating .env from .env.example..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Please edit .env and add your OPENAI_API_KEY"
        echo "Get your API key from: https://platform.openai.com/api-keys"
        echo ""
        read -p "Press Enter after you've added your OPENAI_API_KEY to .env..."
    else
        echo "❌ Error: .env.example not found"
        exit 1
    fi
fi

# Validate OPENAI_API_KEY is set
if grep -q "your-openai-api-key-here" .env; then
    echo "❌ Error: OPENAI_API_KEY is not set in .env file"
    echo "Please edit .env and add your OpenAI API key"
    exit 1
fi

echo "📥 Pulling latest Docker images..."
docker compose -f docker-compose.prod.yml pull

echo ""
echo "🔨 Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
BACKEND_HEALTHY=false
FRONTEND_HEALTHY=false

for i in {1..30}; do
    if docker compose -f docker-compose.prod.yml ps | grep -q "backend.*healthy"; then
        BACKEND_HEALTHY=true
    fi
    
    if docker compose -f docker-compose.prod.yml ps | grep -q "frontend.*healthy"; then
        FRONTEND_HEALTHY=true
    fi
    
    if [ "$BACKEND_HEALTHY" = true ] && [ "$FRONTEND_HEALTHY" = true ]; then
        break
    fi
    
    echo "  Waiting for services to start... ($i/30)"
    sleep 2
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service Status:"
docker compose -f docker-compose.prod.yml ps
echo ""
echo "🌐 Access your application:"
echo "  - Frontend UI:      http://localhost:8501"
echo "  - Backend API:      http://localhost:8000"
echo "  - API Docs:         http://localhost:8000/docs"
echo ""
echo "📝 Useful commands:"
echo "  - View logs:        docker compose -f docker-compose.prod.yml logs -f"
echo "  - Stop services:    docker compose -f docker-compose.prod.yml down"
echo "  - Restart services: docker compose -f docker-compose.prod.yml restart"
echo "  - Update images:    docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d"
echo ""
