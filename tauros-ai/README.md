# Tauros AI - Advanced AI Bot System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-teal.svg)](https://fastapi.tiangolo.com/)

Tauros AI is a production-ready, containerized AI bot system featuring a Telegram bot interface and REST API backend with Redis caching, Ollama integration, and OpenAI fallback support.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   FastAPI API   │    │     Nginx       │
│   (tauros-bot)  │    │ (tauros-backend)│    │ (Reverse Proxy) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Redis       │    │     Ollama      │    │   Monitoring    │
│    (Cache)      │    │   (AI Models)   │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### Core Features
- **Telegram Bot**: Fully-featured bot with conversation management
- **REST API**: FastAPI-based backend with comprehensive endpoints
- **AI Integration**: Support for Ollama local models and OpenAI fallback
- **Redis Caching**: High-performance response caching and rate limiting
- **Docker Orchestration**: Complete containerized deployment
- **Nginx Proxy**: Production-ready reverse proxy with security headers

### Advanced Features
- **Rate Limiting**: Per-user request throttling
- **Health Monitoring**: Comprehensive health checks and status endpoints
- **Conversation Memory**: Context-aware conversations
- **Admin Interface**: Protected admin endpoints for management
- **Security**: Token-based authentication and security headers
- **Logging**: Structured logging with log rotation
- **Scalability**: Horizontally scalable architecture

## 📋 Prerequisites

- Docker & Docker Compose
- 4GB+ RAM (recommended for Ollama models)
- Valid Telegram Bot Token
- Optional: OpenAI API Key for fallback
- Optional: NVIDIA GPU for accelerated AI inference

## 🔧 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Lucifer-AI-666/NEA_bot.git
cd NEA_bot/tauros-ai
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Telegram Bot Token
TELEGRAM_TOKEN=your_telegram_bot_token_here

# Ollama Configuration
OLLAMA_MODEL=llama3

# Optional: OpenAI Fallback
OPENAI_KEY=your_openai_api_key_here
USE_OPENAI_IF_FAIL=true

# Security
API_KEY=your_secure_api_key_here
```

### 3. Launch the System

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Download AI Models

```bash
# Connect to Ollama container
docker exec -it ollama ollama pull llama3

# Or download other models
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull codellama
```

## 📖 Usage

### Telegram Bot Commands

- `/start` - Initialize bot and show welcome message
- `/help` - Display help information and available commands
- `/status` - Check bot and service status
- `/clear` - Clear conversation history
- `/settings` - View bot configuration

### REST API Endpoints

#### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /status` - Service status
- `POST /chat` - Send message to AI
- `GET /models` - List available AI models

#### Admin Endpoints (Require API Key)
- `POST /admin/clear-cache` - Clear Redis cache
- `GET /admin/stats` - Detailed statistics

### API Usage Examples

#### Send a Chat Message
```bash
curl -X POST "http://localhost/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "user_id": "user123",
    "context": "Previous conversation context"
  }'
```

#### Check System Health
```bash
curl http://localhost/health
```

#### Admin: Clear Cache
```bash
curl -X POST "http://localhost/admin/clear-cache" \
  -H "Authorization: Bearer your_api_key_here"
```

## 🔒 Security

### Authentication
- **Telegram Bot**: Uses Telegram's built-in authentication
- **API Endpoints**: Bearer token authentication for admin endpoints
- **Rate Limiting**: Configurable request throttling

### Security Headers
- X-Frame-Options: SAMEORIGIN
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: Strict policies
- Referrer-Policy: strict-origin-when-cross-origin

### Best Practices
- Non-root container users
- Minimal container images
- Secret management via environment variables
- Network isolation with Docker networks
- Regular security updates

## 🔍 Monitoring & Logging

### Health Checks
All services include health checks:
- **Bot**: Connection status monitoring
- **Backend**: `/health` endpoint with service checks
- **Redis**: Redis ping checks
- **Ollama**: API availability checks
- **Nginx**: HTTP response checks

### Logging
- **Structured Logging**: JSON format with timestamps
- **Log Rotation**: Automatic log file rotation
- **Log Levels**: Configurable logging levels
- **Centralized Logs**: All logs accessible via Docker

### Monitoring Commands
```bash
# View all service logs
docker-compose logs -f

# Check specific service
docker-compose logs -f tauros-bot

# Monitor system resources
docker stats

# Check health status
curl http://localhost/health
```

## ⚙️ Configuration

### Environment Variables

#### Bot Configuration
- `TELEGRAM_TOKEN`: Telegram bot token (required)
- `OLLAMA_URL`: Ollama service URL
- `OLLAMA_MODEL`: Default AI model
- `REDIS_URL`: Redis connection URL
- `RATE_LIMIT_WINDOW`: Rate limiting window (seconds)
- `RATE_LIMIT_MAX_REQUESTS`: Max requests per window

#### Backend Configuration
- `HOST`: Server host address
- `PORT`: Server port
- `API_KEY`: Admin API authentication key
- `CACHE_TTL`: Cache time-to-live (seconds)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

#### OpenAI Configuration
- `OPENAI_KEY`: OpenAI API key (optional)
- `USE_OPENAI_IF_FAIL`: Enable OpenAI fallback

### Model Configuration
Supported Ollama models:
- `llama3` (recommended)
- `mistral`
- `codellama`
- `phi3`
- `gemma`

### Redis Configuration
- Memory limit: 256MB (configurable)
- Persistence: AOF + RDB snapshots
- Eviction policy: allkeys-lru

## 🧪 Testing

### Manual Testing

#### Test Bot Functionality
1. Send `/start` command to your Telegram bot
2. Send a test message
3. Verify AI response

#### Test API Endpoints
```bash
# Test health endpoint
curl http://localhost/health

# Test chat endpoint
curl -X POST http://localhost/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'

# Test admin endpoint (requires API key)
curl -H "Authorization: Bearer your_api_key" \
  http://localhost/admin/stats
```

### Load Testing
```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 100 -c 10 -T 'application/json' \
  -p test_payload.json \
  http://localhost/chat
```

### Integration Testing
```bash
# Test service connectivity
docker-compose exec tauros-bot python -c "
import redis
r = redis.from_url('redis://redis:6379')
print('Redis:', r.ping())
"

# Test Ollama connectivity
curl http://localhost:11434/api/tags
```

## 🚀 Deployment

### Production Deployment

#### 1. Security Hardening
```bash
# Generate secure API key
openssl rand -hex 32

# Set strong passwords
# Update all default credentials
```

#### 2. SSL/TLS Configuration
```bash
# Create SSL directory
mkdir ssl

# Generate self-signed certificate (or use Let's Encrypt)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem
```

#### 3. Resource Limits
```yaml
# In docker-compose.yml
services:
  tauros-backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

#### 4. Backup Strategy
```bash
# Backup Redis data
docker exec tauros-redis redis-cli BGSAVE

# Backup configuration
tar -czf tauros-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml .env nginx.conf redis.conf
```

### Scaling

#### Horizontal Scaling
```bash
# Scale backend instances
docker-compose up -d --scale tauros-backend=3

# Update nginx upstream configuration
# Add load balancing to nginx.conf
```

#### Resource Optimization
- Use smaller base images
- Enable model quantization
- Optimize Redis memory usage
- Configure proper caching strategies

## 🔧 Troubleshooting

### Common Issues

#### Bot Not Responding
```bash
# Check bot logs
docker-compose logs tauros-bot

# Verify Telegram token
# Check network connectivity
# Verify Redis connection
```

#### API Errors
```bash
# Check backend logs
docker-compose logs tauros-backend

# Verify Ollama status
curl http://localhost:11434/api/tags

# Check Redis connectivity
docker exec tauros-redis redis-cli ping
```

#### High Memory Usage
```bash
# Check container stats
docker stats

# Clear Redis cache
docker exec tauros-redis redis-cli FLUSHDB

# Restart Ollama
docker-compose restart ollama
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run single service for debugging
docker-compose run --rm tauros-bot python bot.py
```

## 📚 API Documentation

Once the system is running, visit:
- **API Documentation**: http://localhost/docs
- **OpenAPI Specification**: http://localhost/openapi.json

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and API docs
- **Issues**: Open GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions

## 🔄 Updates & Maintenance

### Regular Maintenance
```bash
# Update Docker images
docker-compose pull

# Restart services
docker-compose down && docker-compose up -d

# Clean unused images
docker system prune -f
```

### Model Updates
```bash
# Update Ollama models
docker exec ollama ollama pull llama3:latest

# List installed models
docker exec ollama ollama list
```

---

**Tauros AI** - Empowering intelligent conversations with production-ready infrastructure.

For more information, visit our [GitHub repository](https://github.com/Lucifer-AI-666/NEA_bot).