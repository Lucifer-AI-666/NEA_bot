#!/usr/bin/env python3
"""
Tauros AI Backend API
A production-ready FastAPI backend with Redis caching and AI integration.
"""

import os
import json
import logging
import asyncio
import aiohttp
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    user_id: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    timestamp: datetime
    cached: bool = False
    processing_time: float

class HealthResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: datetime
    uptime: str

class StatusResponse(BaseModel):
    bot_status: str
    ollama_status: str
    redis_status: str
    openai_available: bool
    total_requests: int
    cache_hit_rate: float

# Global variables
redis_client: Optional[redis.Redis] = None
start_time = datetime.now()

class TaurosBackend:
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')
        self.openai_key = os.getenv('OPENAI_KEY')
        self.use_openai_if_fail = os.getenv('USE_OPENAI_IF_FAIL', 'true').lower() == 'true'
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.api_key = os.getenv('API_KEY', 'your-secret-api-key')
        
        # Statistics
        self.total_requests = 0
        self.cache_hits = 0
        
    async def setup_redis(self):
        """Initialize Redis connection"""
        global redis_client
        try:
            redis_client = redis.from_url(self.redis_url)
            await redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            redis_client = None
    
    async def get_cached_response(self, message_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached response from Redis"""
        if not redis_client:
            return None
        try:
            cached = await redis_client.get(f"api_response:{message_hash}")
            if cached:
                self.cache_hits += 1
                return json.loads(cached.decode('utf-8'))
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def cache_response(self, message_hash: str, response_data: Dict[str, Any], ttl: int = 3600):
        """Cache response in Redis"""
        if not redis_client:
            return
        try:
            await redis_client.setex(
                f"api_response:{message_hash}", 
                ttl, 
                json.dumps(response_data, default=str)
            )
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def increment_stats(self):
        """Increment request statistics"""
        self.total_requests += 1
        if redis_client:
            try:
                await redis_client.incr("total_requests")
                if self.cache_hits > 0:
                    await redis_client.incr("cache_hits")
            except Exception as e:
                logger.error(f"Stats increment error: {e}")
    
    async def query_ollama(self, prompt: str, context: Optional[str] = None, model: Optional[str] = None) -> Optional[str]:
        """Query Ollama API"""
        try:
            used_model = model or self.ollama_model
            payload = {
                "model": used_model,
                "prompt": f"{context}\n\n{prompt}" if context else prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1500
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '').strip()
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return None
    
    async def query_openai(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """Query OpenAI API as fallback"""
        if not self.openai_key:
            return None
        
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 1500,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"OpenAI query error: {e}")
            return None
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, model: Optional[str] = None) -> tuple[str, str]:
        """Generate AI response with fallback mechanism"""
        start_time = datetime.now()
        
        # Try Ollama first
        response = await self.query_ollama(prompt, context, model)
        model_used = model or self.ollama_model
        
        # Fallback to OpenAI if enabled and Ollama fails
        if not response and self.use_openai_if_fail:
            logger.info("Ollama failed, trying OpenAI...")
            response = await self.query_openai(prompt, context)
            model_used = "gpt-3.5-turbo"
        
        if not response:
            response = "I'm sorry, I'm having trouble generating a response right now. Please try again later."
            model_used = "fallback"
        
        return response, model_used
    
    async def check_service_health(self) -> Dict[str, str]:
        """Check health of all services"""
        services = {}
        
        # Check Ollama
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.ollama_url}/api/tags", 
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    services['ollama'] = "healthy" if response.status == 200 else "unhealthy"
        except:
            services['ollama'] = "unhealthy"
        
        # Check Redis
        if redis_client:
            try:
                await redis_client.ping()
                services['redis'] = "healthy"
            except:
                services['redis'] = "unhealthy"
        else:
            services['redis'] = "unavailable"
        
        # Check OpenAI availability
        services['openai'] = "available" if self.openai_key else "not_configured"
        
        return services

# Initialize backend
backend = TaurosBackend()

# Security
security = HTTPBearer(auto_error=False)

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for protected endpoints"""
    if not credentials or credentials.credentials != backend.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    await backend.setup_redis()
    logger.info(f"Tauros AI Backend started at {datetime.now()}")
    yield
    # Shutdown
    if redis_client:
        await redis_client.close()
    logger.info("Tauros AI Backend shutting down")

# Create FastAPI app
app = FastAPI(
    title="Tauros AI Backend",
    description="Production-ready AI backend with Redis caching and multi-model support",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Tauros AI Backend API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = await backend.check_service_health()
    uptime = str(datetime.now() - start_time)
    
    return HealthResponse(
        status="healthy" if all(s in ["healthy", "available"] for s in services.values()) else "degraded",
        services=services,
        timestamp=datetime.now(),
        uptime=uptime
    )

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed status information"""
    services = await backend.check_service_health()
    cache_hit_rate = (backend.cache_hits / max(backend.total_requests, 1)) * 100
    
    return StatusResponse(
        bot_status="running",
        ollama_status=services.get('ollama', 'unknown'),
        redis_status=services.get('redis', 'unknown'),
        openai_available=backend.openai_key is not None,
        total_requests=backend.total_requests,
        cache_hit_rate=round(cache_hit_rate, 2)
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat endpoint"""
    start_time = datetime.now()
    
    try:
        # Generate message hash for caching
        message_hash = f"{request.user_id or 'anonymous'}:{hash(request.message)}"
        
        # Check cache first
        cached_response = await backend.get_cached_response(message_hash)
        if cached_response:
            return ChatResponse(
                response=cached_response['response'],
                model_used=cached_response['model_used'],
                timestamp=datetime.now(),
                cached=True,
                processing_time=0.1
            )
        
        # Generate new response
        response_text, model_used = await backend.generate_response(
            request.message, 
            request.context,
            request.model
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response data
        response_data = {
            'response': response_text,
            'model_used': model_used,
            'timestamp': datetime.now(),
            'processing_time': processing_time
        }
        
        # Cache the response
        background_tasks.add_task(
            backend.cache_response, 
            message_hash, 
            response_data
        )
        
        # Update statistics
        background_tasks.add_task(backend.increment_stats)
        
        return ChatResponse(
            response=response_text,
            model_used=model_used,
            timestamp=datetime.now(),
            cached=False,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/models")
async def list_models():
    """List available models"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{backend.ollama_url}/api/tags",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    models = [model['name'] for model in result.get('models', [])]
                    return {"models": models, "default": backend.ollama_model}
                else:
                    return {"models": [], "default": backend.ollama_model, "error": "Ollama unavailable"}
    except Exception as e:
        logger.error(f"Models endpoint error: {e}")
        return {"models": [], "default": backend.ollama_model, "error": str(e)}

@app.post("/admin/clear-cache")
async def clear_cache(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Clear Redis cache (admin only)"""
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        await redis_client.flushdb()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@app.get("/admin/stats")
async def get_stats(credentials: HTTPAuthorizationCredentials = Depends(verify_api_key)):
    """Get detailed statistics (admin only)"""
    try:
        stats = {
            "total_requests": backend.total_requests,
            "cache_hits": backend.cache_hits,
            "cache_hit_rate": (backend.cache_hits / max(backend.total_requests, 1)) * 100,
            "uptime": str(datetime.now() - start_time),
            "redis_connected": redis_client is not None
        }
        
        if redis_client:
            redis_info = await redis_client.info()
            stats["redis_memory_usage"] = redis_info.get("used_memory_human", "unknown")
            stats["redis_connected_clients"] = redis_info.get("connected_clients", 0)
        
        return stats
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )