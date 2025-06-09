#!/usr/bin/env python3
"""
Migration script for PostgreSQL/Supabase setup
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database_postgres import create_tables, postgres_db
from app.config import app_config

async def run_migrations():
    """Run database migrations for PostgreSQL"""
    print("Starting PostgreSQL migrations...")
    
    if not app_config.USE_POSTGRESQL:
        print("PostgreSQL is not enabled. Set DATABASE_URL environment variable.")
        return
    
    try:
        # Create tables
        await create_tables()
        print("✅ Database tables created successfully")
        
        # Insert default data
        await insert_default_data()
        print("✅ Default data inserted successfully")
        
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        # Close database connections
        from app.database_postgres import close_postgres_pool
        await close_postgres_pool()

async def insert_default_data():
    """Insert default bot and configuration data"""
    
    # Insert default bot
    await postgres_db.execute('''
        INSERT INTO bots (name, description, nlu_configuration)
        VALUES ($1, $2, $3)
        ON CONFLICT (name) DO NOTHING
    ''', 
    'default', 
    'Default chatbot configuration',
    '{"use_llm_nlu": true, "use_zero_shot_nlu": true}'
    )
    
    # Insert default intents
    default_intents = [
        {
            'name': 'init_conversation',
            'training_data': ['hello', 'hi', 'hey', 'start'],
            'responses': ['Hello! How can I help you today?', 'Hi there! What can I do for you?']
        },
        {
            'name': 'fallback',
            'training_data': [],
            'responses': ['I\'m sorry, I didn\'t understand that. Could you please rephrase?']
        }
    ]
    
    for intent in default_intents:
        await postgres_db.execute('''
            INSERT INTO intents (name, training_data, responses)
            VALUES ($1, $2, $3)
            ON CONFLICT DO NOTHING
        ''',
        intent['name'],
        intent['training_data'],
        intent['responses']
        )
    
    # Insert default integrations
    default_integrations = [
        {
            'id': 'rest_api',
            'name': 'REST API',
            'description': 'REST API integration for web applications',
            'status': True,
            'settings': {'enabled': True}
        },
        {
            'id': 'facebook_messenger',
            'name': 'Facebook Messenger',
            'description': 'Facebook Messenger integration',
            'status': False,
            'settings': {'page_access_token': '', 'verify_token': ''}
        }
    ]
    
    for integration in default_integrations:
        await postgres_db.execute('''
            INSERT INTO integrations (id, name, description, status, settings)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (id) DO NOTHING
        ''',
        integration['id'],
        integration['name'],
        integration['description'],
        integration['status'],
        integration['settings']
        )

if __name__ == "__main__":
    asyncio.run(run_migrations())