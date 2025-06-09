from typing import Annotated
import asyncpg
import asyncio
from pydantic import PlainSerializer, PlainValidator
from app.config import app_config
import json
from datetime import datetime

# PostgreSQL connection pool
_pool = None

async def get_postgres_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            app_config.DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    return _pool

async def close_postgres_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None

class PostgreSQLDatabase:
    def __init__(self):
        self.pool = None
    
    async def get_pool(self):
        if self.pool is None:
            self.pool = await get_postgres_pool()
        return self.pool
    
    async def execute(self, query: str, *args):
        pool = await self.get_pool()
        async with pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch(self, query: str, *args):
        pool = await self.get_pool()
        async with pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args):
        pool = await self.get_pool()
        async with pool.acquire() as connection:
            return await connection.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args):
        pool = await self.get_pool()
        async with pool.acquire() as connection:
            return await connection.fetchval(query, *args)

# Initialize database
postgres_db = PostgreSQLDatabase()

# Database migration functions
async def create_tables():
    """Create necessary tables for the chatbot framework"""
    pool = await get_postgres_pool()
    async with pool.acquire() as connection:
        # Create bots table
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS bots (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                nlu_configuration JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create intents table
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS intents (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                training_data JSONB,
                responses JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create entities table
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                entity_type VARCHAR(100),
                training_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create integrations table
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS integrations (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                status BOOLEAN DEFAULT FALSE,
                settings JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create chat_states table (for conversation memory)
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS chat_states (
                id SERIAL PRIMARY KEY,
                thread_id VARCHAR(255) NOT NULL,
                state_data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(thread_id, created_at)
            )
        ''')
        
        # Create chat_logs table
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id SERIAL PRIMARY KEY,
                thread_id VARCHAR(255) NOT NULL,
                user_message TEXT,
                bot_message TEXT,
                nlu_data JSONB,
                context JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX(thread_id, created_at)
            )
        ''')

# Collection-like interface for PostgreSQL
class PostgreSQLCollection:
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = postgres_db
    
    async def insert_one(self, document: dict):
        # Convert document to SQL insert
        columns = list(document.keys())
        placeholders = [f'${i+1}' for i in range(len(columns))]
        values = list(document.values())
        
        # Handle JSON fields
        for i, value in enumerate(values):
            if isinstance(value, (dict, list)):
                values[i] = json.dumps(value)
        
        query = f'''
            INSERT INTO {self.table_name} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING id
        '''
        
        result = await self.db.fetchval(query, *values)
        return type('InsertResult', (), {'inserted_id': result})()
    
    async def find_one(self, filter_dict: dict = None, projection: dict = None):
        where_clause = ""
        values = []
        
        if filter_dict:
            conditions = []
            for i, (key, value) in enumerate(filter_dict.items()):
                if key == "_id" or key == "id":
                    conditions.append(f"id = ${i+1}")
                else:
                    conditions.append(f"{key} = ${i+1}")
                values.append(value)
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        query = f"SELECT * FROM {self.table_name} {where_clause} LIMIT 1"
        result = await self.db.fetchrow(query, *values)
        
        if result:
            return dict(result)
        return None
    
    async def find(self, filter_dict: dict = None, sort: list = None, limit: int = None):
        where_clause = ""
        values = []
        
        if filter_dict:
            conditions = []
            for i, (key, value) in enumerate(filter_dict.items()):
                conditions.append(f"{key} = ${i+1}")
                values.append(value)
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        order_clause = ""
        if sort:
            order_clause = f"ORDER BY {sort[0][0]} {'DESC' if sort[0][1] == -1 else 'ASC'}"
        
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"SELECT * FROM {self.table_name} {where_clause} {order_clause} {limit_clause}"
        results = await self.db.fetch(query, *values)
        
        return [dict(row) for row in results]
    
    async def update_one(self, filter_dict: dict, update_dict: dict):
        set_clauses = []
        values = []
        
        # Handle $set operator
        if '$set' in update_dict:
            update_data = update_dict['$set']
        else:
            update_data = update_dict
        
        for i, (key, value) in enumerate(update_data.items()):
            set_clauses.append(f"{key} = ${i+1}")
            if isinstance(value, (dict, list)):
                values.append(json.dumps(value))
            else:
                values.append(value)
        
        # Add where conditions
        where_conditions = []
        for key, value in filter_dict.items():
            if key == "_id" or key == "id":
                where_conditions.append(f"id = ${len(values)+1}")
            else:
                where_conditions.append(f"{key} = ${len(values)+1}")
            values.append(value)
        
        query = f'''
            UPDATE {self.table_name} 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE {' AND '.join(where_conditions)}
        '''
        
        await self.db.execute(query, *values)
    
    async def delete_one(self, filter_dict: dict):
        where_conditions = []
        values = []
        
        for i, (key, value) in enumerate(filter_dict.items()):
            if key == "_id" or key == "id":
                where_conditions.append(f"id = ${i+1}")
            else:
                where_conditions.append(f"{key} = ${i+1}")
            values.append(value)
        
        query = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_conditions)}"
        await self.db.execute(query, *values)

# Database interface that works with both MongoDB and PostgreSQL
class DatabaseInterface:
    def __init__(self):
        self.use_postgresql = app_config.USE_POSTGRESQL
    
    def get_collection(self, collection_name: str):
        if self.use_postgresql:
            return PostgreSQLCollection(collection_name)
        else:
            # Fallback to MongoDB
            from app.database import database
            return database[collection_name]

# Initialize the database interface
database_interface = DatabaseInterface()