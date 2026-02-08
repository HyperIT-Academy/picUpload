"""
Media Upload Bot - головний entry point
Telegram бот для завантаження файлів на сервер з поверненням публічних URL
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Завантажуємо env vars ПЕРЕД іншими імпортами
load_dotenv()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers.upload import router as upload_router
from middleware.admin_check import AdminCheckMiddleware

# Налаштування логування
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """
    Головна функція запуску бота
    """
    # Перевіряємо наявність BOT_TOKEN
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        sys.exit(1)
    
    # Перевіряємо ADMIN_IDS
    admin_ids = os.getenv("ADMIN_IDS", "")
    if not admin_ids or admin_ids == "YOUR_TELEGRAM_ID_HERE":
        logger.warning(
            "⚠️  ADMIN_IDS not configured properly!\n"
            "Please set your Telegram ID in .env file.\n"
            "Get your ID from @userinfobot"
        )
    
    # Ініціалізуємо бота та диспетчер
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Підключаємо middleware для перевірки адміністраторів
    dp.message.middleware(AdminCheckMiddleware())
    
    # Підключаємо роутери
    dp.include_router(upload_router)
    
    logger.info("🚀 Media Upload Bot starting...")
    logger.info(f"📁 Upload directory: {os.getenv('UPLOAD_DIR', '/var/www/media')}")
    logger.info(f"🌐 Public URL: {os.getenv('PUBLIC_URL', 'http://hyperitacademy.space/media')}")
    
    try:
        # Запускаємо polling
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
