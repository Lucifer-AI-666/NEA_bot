#!/bin/bash
# Tauros AI Startup Script

set -e

echo "🚀 Starting Tauros AI System..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Please copy .env.template to .env and configure your settings:"
    echo "   cp .env.template .env"
    echo "   nano .env"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p tauros-bot/{logs,data,temp}
mkdir -p tauros-backend/{logs,data}
mkdir -p ssl

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Redis
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis is healthy"
else
    echo "❌ Redis is not responding"
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is not responding"
fi

# Check Ollama
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is healthy"
    
    # Check if models are available
    echo "🤖 Checking AI models..."
    if docker exec ollama ollama list | grep -q llama3; then
        echo "✅ llama3 model is available"
    else
        echo "📥 Downloading llama3 model (this may take a while)..."
        docker exec ollama ollama pull llama3
    fi
else
    echo "❌ Ollama is not responding"
fi

echo ""
echo "🎉 Tauros AI System is starting up!"
echo ""
echo "📖 Access points:"
echo "   • API Documentation: http://localhost/docs"
echo "   • Health Check: http://localhost/health"
echo "   • System Status: http://localhost/status"
echo ""
echo "📱 Don't forget to:"
echo "   1. Test your Telegram bot"
echo "   2. Verify your API endpoints"
echo "   3. Check the logs: docker-compose logs -f"
echo ""
echo "🛠️  Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop system: docker-compose down"
echo "   • Restart: docker-compose restart"
echo "   • Update: docker-compose pull && docker-compose up -d"