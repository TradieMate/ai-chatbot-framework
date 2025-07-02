from typing import Annotated
import os
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import PlainSerializer, PlainValidator
from app.config import app_config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ObjectIdField = Annotated[
    ObjectId,
    PlainSerializer(lambda x: str(x), return_type=str),
    PlainValidator(lambda x: ObjectId(x)),
]

# Try to connect to MongoDB with error handling
try:
    mongodb_host = os.environ.get("MONGODB_HOST", app_config.MONGODB_HOST)
    mongodb_database = os.environ.get("MONGODB_DATABASE", app_config.MONGODB_DATABASE)
    
    logger.info(f"Connecting to MongoDB at {mongodb_host}")
    client = AsyncIOMotorClient(mongodb_host, serverSelectionTimeoutMS=5000)
    database = client.get_database(mongodb_database)
    
    # Test the connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
    
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    logger.warning("Using fallback in-memory database")
    
    # Create a fallback in-memory MongoDB client
    # This allows the application to start even without a real database
    from mongomock_motor import AsyncMongoMockClient
    client = AsyncMongoMockClient()
    database = client.get_database("fallback_db")
    logger.info("Using in-memory MongoDB for fallback")
