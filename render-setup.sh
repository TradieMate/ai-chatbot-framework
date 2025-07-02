#!/bin/bash
# Setup script for deploying AI Chatbot Framework on Render

# Exit on error
set -e

echo "Setting up AI Chatbot Framework for Render deployment..."

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt

# Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Create a default .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating default .env file..."
  cat > .env << EOL
# MongoDB Configuration
MONGODB_HOST=${MONGODB_HOST:-mongodb://127.0.0.1:27017}
MONGODB_DATABASE=${MONGODB_DATABASE:-ai-chatbot-framework}

# Application Configuration
APPLICATION_ENV=Production

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
OPENAI_MODEL=${OPENAI_MODEL:-gpt-3.5-turbo}
OPENAI_TEMPERATURE=${OPENAI_TEMPERATURE:-0.7}
OPENAI_MAX_TOKENS=${OPENAI_MAX_TOKENS:-4096}

# LLM Configuration
USE_LLM_NLU=${USE_LLM_NLU:-false}
USE_ZERO_SHOT_NLU=${USE_ZERO_SHOT_NLU:-false}
EOL
fi

# Create a health check script
echo "Creating health check script..."
cat > health_check.py << EOL
import asyncio
import json
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def check_health():
    # Get MongoDB connection string from environment or use default
    mongodb_host = os.environ.get("MONGODB_HOST", "mongodb://127.0.0.1:27017")
    mongodb_database = os.environ.get("MONGODB_DATABASE", "ai-chatbot-framework")
    
    print(f"Checking MongoDB connection to {mongodb_host}...")
    
    try:
        # Try to connect to MongoDB
        client = AsyncIOMotorClient(mongodb_host, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        print("MongoDB connection successful!")
        
        # Check if any bots exist
        db = client.get_database(mongodb_database)
        bot_count = await db.bot.count_documents({})
        print(f"Found {bot_count} bots in the database")
        
        if bot_count == 0:
            print("No bots found. You'll need to create one through the admin panel.")
        
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_health())
    sys.exit(0 if result else 1)
EOL

echo "Setup complete! You can now start the application with:"
echo "python run.py"