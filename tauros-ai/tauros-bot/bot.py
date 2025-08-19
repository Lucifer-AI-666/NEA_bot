#!/usr/bin/env python3
"""
Tauros AI Telegram Bot
A production-ready Telegram bot with Ollama/OpenAI integration and Redis caching.
"""

import os
import json
import logging
import asyncio
import aiohttp
import redis.asyncio as redis
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TaurosBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3')
        self.openai_key = os.getenv('OPENAI_KEY')
        self.use_openai_if_fail = os.getenv('USE_OPENAI_IF_FAIL', 'true').lower() == 'true'
        self.redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        
        # Initialize Redis connection
        self.redis_client = None
        
        # Load bot personality from config
        self.personality = self.load_personality()
        
        # Rate limiting settings
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_requests = 10
        
    def load_personality(self) -> Dict[str, Any]:
        """Load bot personality configuration"""
        try:
            with open('data/personality.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default personality
            return {
                "name": "Tauros AI",
                "description": "An intelligent AI assistant powered by Ollama",
                "personality_traits": [
                    "helpful", "informative", "creative", "ethical"
                ],
                "response_style": "conversational and engaging"
            }
    
    async def setup_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def get_cached_response(self, message_hash: str) -> Optional[str]:
        """Get cached response from Redis"""
        if not self.redis_client:
            return None
        try:
            cached = await self.redis_client.get(f"response:{message_hash}")
            return cached.decode('utf-8') if cached else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    async def cache_response(self, message_hash: str, response: str, ttl: int = 3600):
        """Cache response in Redis"""
        if not self.redis_client:
            return
        try:
            await self.redis_client.setex(f"response:{message_hash}", ttl, response)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
    
    async def check_rate_limit(self, user_id: int) -> bool:
        """Check if user is within rate limits"""
        if not self.redis_client:
            return True
        
        try:
            key = f"rate_limit:{user_id}"
            current_count = await self.redis_client.get(key)
            
            if current_count is None:
                await self.redis_client.setex(key, self.rate_limit_window, 1)
                return True
            
            count = int(current_count)
            if count >= self.rate_limit_max_requests:
                return False
            
            await self.redis_client.incr(key)
            return True
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            return True
    
    async def query_ollama(self, prompt: str, context: Optional[str] = None) -> Optional[str]:
        """Query Ollama API"""
        try:
            payload = {
                "model": self.ollama_model,
                "prompt": f"{context}\n\n{prompt}" if context else prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
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
                "max_tokens": 1000,
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
                    timeout=aiohttp.ClientTimeout(total=30)
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
    
    async def generate_response(self, prompt: str, user_context: Optional[str] = None) -> str:
        """Generate AI response with fallback mechanism"""
        # Create context from personality
        context = f"You are {self.personality['name']}, {self.personality['description']}. " \
                 f"Your response style is {self.personality['response_style']}."
        
        if user_context:
            context += f"\n\nUser context: {user_context}"
        
        # Try Ollama first
        response = await self.query_ollama(prompt, context)
        
        # Fallback to OpenAI if enabled and Ollama fails
        if not response and self.use_openai_if_fail:
            logger.info("Ollama failed, trying OpenAI...")
            response = await self.query_openai(prompt, context)
        
        return response if response else "I'm sorry, I'm having trouble generating a response right now. Please try again later."
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = f"""
🤖 **Welcome to {self.personality['name']}!**

Hello {user.first_name}! I'm an AI assistant powered by Ollama/OpenAI.

**Available Commands:**
• `/help` - Show this help message
• `/status` - Check bot status
• `/clear` - Clear conversation history
• `/settings` - Bot settings

Just send me a message and I'll respond with AI-generated content!
        """
        
        keyboard = [
            [InlineKeyboardButton("🆘 Help", callback_data='help')],
            [InlineKeyboardButton("⚙️ Settings", callback_data='settings')],
            [InlineKeyboardButton("📊 Status", callback_data='status')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = f"""
🆘 **{self.personality['name']} Help**

**Commands:**
• `/start` - Start the bot and show welcome message
• `/help` - Show this help message
• `/status` - Check bot and services status
• `/clear` - Clear your conversation history
• `/settings` - Configure bot settings

**Features:**
• AI-powered responses using Ollama/OpenAI
• Conversation memory and context
• Rate limiting for fair usage
• Cached responses for faster replies

**Usage:**
Simply send me any message and I'll respond with AI-generated content. I can help with:
• Questions and answers
• Creative writing
• Problem solving
• General conversation

**Rate Limits:**
You can send up to {self.rate_limit_max_requests} messages per {self.rate_limit_window} seconds.
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        # Check Ollama status
        ollama_status = "🟢 Online"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        ollama_status = "🔴 Offline"
        except:
            ollama_status = "🔴 Offline"
        
        # Check Redis status
        redis_status = "🟢 Online" if self.redis_client else "🔴 Offline"
        if self.redis_client:
            try:
                await self.redis_client.ping()
            except:
                redis_status = "🔴 Offline"
        
        # Check OpenAI status
        openai_status = "🟢 Available" if self.openai_key else "🔴 Not configured"
        
        status_text = f"""
📊 **Bot Status**

**Services:**
• Ollama ({self.ollama_model}): {ollama_status}
• Redis Cache: {redis_status}
• OpenAI Fallback: {openai_status}

**Bot Info:**
• Name: {self.personality['name']}
• Uptime: Active
• Rate Limit: {self.rate_limit_max_requests} msgs/{self.rate_limit_window}s

**Model:** {self.ollama_model}
**Cache:** {'Enabled' if self.redis_client else 'Disabled'}
        """
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command"""
        user_id = update.effective_user.id
        if self.redis_client:
            try:
                # Clear user's conversation cache
                keys = await self.redis_client.keys(f"context:{user_id}:*")
                if keys:
                    await self.redis_client.delete(*keys)
                await update.message.reply_text("✅ Your conversation history has been cleared!")
            except Exception as e:
                logger.error(f"Clear command error: {e}")
                await update.message.reply_text("❌ Error clearing history. Please try again.")
        else:
            await update.message.reply_text("✅ Conversation history cleared (cache not available)!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user = update.effective_user
        message_text = update.message.text
        
        # Check rate limiting
        if not await self.check_rate_limit(user.id):
            await update.message.reply_text(
                f"⏰ Rate limit exceeded. Please wait before sending another message.\n"
                f"Limit: {self.rate_limit_max_requests} messages per {self.rate_limit_window} seconds."
            )
            return
        
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        
        # Check for cached response
        message_hash = f"{user.id}:{hash(message_text)}"
        cached_response = await self.get_cached_response(message_hash)
        
        if cached_response:
            await update.message.reply_text(f"💾 {cached_response}")
            return
        
        try:
            # Generate AI response
            response = await self.generate_response(message_text)
            
            # Cache the response
            await self.cache_response(message_hash, response)
            
            # Send response
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
            
            # Log interaction
            logger.info(f"User {user.id} ({user.username}): {message_text[:50]}... -> Response: {len(response)} chars")
            
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text(
                "❌ Sorry, I encountered an error processing your message. Please try again."
            )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'help':
            await self.help_command(update, context)
        elif query.data == 'status':
            await self.status_command(update, context)
        elif query.data == 'settings':
            settings_text = """
⚙️ **Bot Settings**

Current configuration:
• Model: {self.ollama_model}
• Cache: {'Enabled' if self.redis_client else 'Disabled'}
• OpenAI Fallback: {'Enabled' if self.use_openai_if_fail else 'Disabled'}

Contact admin to modify settings.
            """
            await query.edit_message_text(settings_text, parse_mode=ParseMode.MARKDOWN)
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    def run(self):
        """Run the bot"""
        if not self.token:
            logger.error("TELEGRAM_TOKEN not found in environment variables")
            return
        
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.button_callback))
        application.add_error_handler(self.error_handler)
        
        # Setup Redis
        asyncio.get_event_loop().run_until_complete(self.setup_redis())
        
        logger.info(f"Starting {self.personality['name']} bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = TaurosBot()
    bot.run()