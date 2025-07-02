import asyncio
import json
import os
from datetime import datetime
from app.admin.bots.schemas import Bot, NLUConfiguration
from app.database import database
from app.admin.bots.store import import_bot

async def import_example_bot():
    """Import the example order status bot into the database."""
    print("Starting import of example bot...")
    
    # Get the bot collection
    bot_collection = database.get_collection("bot")
    
    # Check if the default bot exists
    default_bot = await bot_collection.find_one({"name": "default"})
    
    if default_bot is None:
        print("Default bot not found. Creating...")
        # Create the default bot
        default_bot_data = Bot(name="default")
        default_bot_data.created_at = datetime.utcnow()
        default_bot_data.updated_at = datetime.utcnow()
        
        # Insert the default bot
        await bot_collection.insert_one(
            default_bot_data.model_dump(exclude={"id": True})
        )
        print("Default bot created successfully.")
    else:
        print("Default bot already exists.")
    
    # Import the example order status bot
    try:
        # Load the example bot data
        example_path = os.path.join(os.path.dirname(__file__), "examples", "order_status.json")
        with open(example_path, "r") as f:
            example_data = json.load(f)
        
        # Import the bot data
        result = await import_bot("default", example_data)
        print(f"Example bot imported successfully: {result}")
    except Exception as e:
        print(f"Error importing example bot: {e}")

if __name__ == "__main__":
    asyncio.run(import_example_bot())