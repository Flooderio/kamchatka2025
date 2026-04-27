import asyncio
import os

import django
from aiogram import Bot, Dispatcher


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kamsite.settings")
django.setup()

from ecoapp.bot.handlers import router  # noqa: E402


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
