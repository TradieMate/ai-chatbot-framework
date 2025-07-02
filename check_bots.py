import asyncio
from app.admin.bots.store import bot_collection

async def list_bots():
    bots = await bot_collection.find().to_list(length=100)
    print(f"Found {len(bots)} bots:")
    for bot in bots:
        print(f"- {bot.get('name', 'unnamed')}")
    return bots

if __name__ == "__main__":
    asyncio.run(list_bots())