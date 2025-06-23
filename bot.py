import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, URI
from handlers.common import router as common_router
from handlers.foods import router as foods_router
from handlers.drinks import router as drinks_router
from handlers.admin import router as admin_router
from utils import set_commands, MongoDB
from middleware import DBMiddleware


async def main():
    logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a",
                        format="%(asctime)s %(levelname)s %(message)s")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    db = MongoDB(URI)
    dp.message.middleware(DBMiddleware(db))  # inject db into message handlers

    await db.get_menu()

    # Register routers
    dp.include_router(common_router)
    dp.include_router(foods_router)
    dp.include_router(drinks_router)
    dp.include_router(admin_router)

    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
