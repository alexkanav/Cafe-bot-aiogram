from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DBMiddleware(BaseMiddleware):
    def __init__(self, db):
        self.db = db

    async def __call__(self, handler: callable, event: TelegramObject, data: dict[str, any]) -> any:
        data["db"] = self.db  # Inject db into handler context
        return await handler(event, data)

