from aiogram.types import BotCommand
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

from config import TELEGRAM_TOKEN, TELEGRAM_CHANNEL_ID


class MongoDB:
    def __init__(self, uri: str):
        self.menu = []
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client["cafe"]
        self.menu_collection = self.db["menu"]
        self.orders_collection = self.db["orders"]

    async def get_menu(self):
        cursor = self.menu_collection.find()
        self.menu = await cursor.to_list(length=None)

    async def update_menu(self, category: str, item: str, values: list[str]) -> str:
        filter_query = {"category": category}
        update_query = {"$set": {item: values}}
        result = await self.menu_collection.update_one(filter_query, update_query)

        return f"Matched {result.matched_count}, Modified {result.modified_count}"

    async def insert_order(self, order_data: dict):
        result = await self.orders_collection.insert_one(order_data)
        return result.inserted_id


async def set_commands(bot):
    commands = [
        BotCommand(command="table", description="Your table number"),
        BotCommand(command="drinks", description="Order drinks"),
        BotCommand(command="foods", description="Order foods"),
        BotCommand(command="cancel", description="Cancel")
    ]
    await bot.set_my_commands(commands)


async def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHANNEL_ID, "text": text}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status != 200:
                raise Exception("post text error")

