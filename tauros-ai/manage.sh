#!/bin/bash
# Tauros AI Management Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

function show_help() {
    echo "Tauros AI Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show logs for all services"
    echo "  logs-bot    Show bot logs only"
    echo "  logs-api    Show API logs only"
    echo "  health      Check system health"
    echo "  update      Update Docker images"
    echo "  clean       Clean unused Docker resources"
    echo "  backup      Create system backup"
    echo "  models      Manage AI models"
    echo "  shell-bot   Open shell in bot container"
    echo "  shell-api   Open shell in API container"
    echo "  help        Show this help message"
}

function check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker not found. Please install Docker."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ docker-compose not found. Please install docker-compose."
        exit 1
    fi
    
    if [ ! -f .env ]; then
        echo "❌ .env file not found. Please copy .env.template to .env and configure it."
        exit 1
    fi
}

function start_services() {
    echo "🚀 Starting Tauros AI services..."
    docker-compose up -d
    echo "✅ Services started. Use '$0 status' to check status."
}

function stop_services() {
    echo "🛑 Stopping Tauros AI services..."
    docker-compose down
    echo "✅ Services stopped."
}

function restart_services() {
    echo "🔄 Restarting Tauros AI services..."
    docker-compose restart
    echo "✅ Services restarted."
}

function show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🔍 Health Checks:"
    curl -s http://localhost/health | python3 -m json.tool 2>/dev/null || echo "Backend not responding"
}

function show_logs() {
    docker-compose logs -f "$@"
}

function check_health() {
    echo "🏥 System Health Check:"
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        echo "✅ Redis: Healthy"
    else
        echo "❌ Redis: Unhealthy"
    fi
    
    # Check Backend
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Backend: Healthy"
    else
        echo "❌ Backend: Unhealthy"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama: Healthy"
    else
        echo "❌ Ollama: Unhealthy"
    fi
    
    # Check Nginx
    if curl -f http://localhost/health > /dev/null 2>&1; then
        echo "✅ Nginx: Healthy"
    else
        echo "❌ Nginx: Unhealthy"
    fi
}

function update_images() {
    echo "📥 Updating Docker images..."
    docker-compose pull
    echo "🔄 Restarting services with new images..."
    docker-compose up -d
    echo "✅ Update complete."
}

function clean_docker() {
    echo "🧹 Cleaning unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    echo "✅ Cleanup complete."
}

function backup_system() {
    BACKUP_DIR="backups"
    BACKUP_FILE="tauros-ai-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    echo "💾 Creating system backup..."
    tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
        --exclude='logs/*' \
        --exclude='temp/*' \
        --exclude='*.log' \
        docker-compose.yml .env nginx.conf redis.conf tauros-bot/ tauros-backend/
    
    echo "✅ Backup created: $BACKUP_DIR/$BACKUP_FILE"
}

function manage_models() {
    echo "🤖 AI Model Management:"
    echo "1. List installed models"
    echo "2. Pull new model"
    echo "3. Remove model"
    read -p "Choose option (1-3): " choice
    
    case $choice in
        1)
            docker exec ollama ollama list
            ;;
        2)
            read -p "Enter model name (e.g., llama3, mistral): " model
            docker exec ollama ollama pull "$model"
            ;;
        3)
            read -p "Enter model name to remove: " model
            docker exec ollama ollama rm "$model"
            ;;
        *)
            echo "Invalid option"
            ;;
    esac
}

# Main script logic
check_requirements

case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "${@:2}"
        ;;
    logs-bot)
        show_logs tauros-bot
        ;;
    logs-api)
        show_logs tauros-backend
        ;;
    health)
        check_health
        ;;
    update)
        update_images
        ;;
    clean)
        clean_docker
        ;;
    backup)
        backup_system
        ;;
    models)
        manage_models
        ;;
    shell-bot)
        docker-compose exec tauros-bot /bin/bash
        ;;
    shell-api)
        docker-compose exec tauros-backend /bin/bash
        ;;
    help|*)
        show_help
        ;;
esac