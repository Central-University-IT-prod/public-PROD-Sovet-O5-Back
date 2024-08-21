import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher
from bot import main_router

TOKEN = getenv("BOT_TOKEN", "")

ADMIN_SECRET_START_PARAM = getenv("ADMIN_SECRET_START_PARAM", "")

dp = Dispatcher()

async def main() -> None:
    """Bot entrypoint"""
    bot = Bot(TOKEN)
    print(
        f"https://t.me/{(await bot.me()).username}?start={ADMIN_SECRET_START_PARAM} - "
        "ссылка для регистрации админов"
    )
    dp.include_routers(
        main_router.router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    asyncio.run(main())