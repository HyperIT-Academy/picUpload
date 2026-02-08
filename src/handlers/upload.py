"""
Handlers для обробки завантаження файлів
"""
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command

from utils.storage import FileStorage

logger = logging.getLogger(__name__)
router = Router()

# Ініціалізуємо storage
storage = FileStorage()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Handler для команди /start
    Показує інструкцію як користуватись ботом
    """
    welcome_text = (
        "👋 Вітаю в Media Upload Bot!\n\n"
        "📤 <b>Як користуватись:</b>\n"
        "• Надішліть фото або документ\n"
        "• Бот збереже файл на сервері\n"
        "• Отримаєте публічне HTTPS посилання\n\n"
        "✅ <b>Дозволені формати:</b>\n"
        "jpg, jpeg, png, webp, pdf\n\n"
        "📏 <b>Максимальний розмір:</b> 10 MB\n\n"
        "💡 <b>Швидкий старт:</b>\n"
        "Просто надішліть фото або файл прямо зараз!"
    )
    
    await message.answer(welcome_text, parse_mode="HTML")
    
    logger.info(
        "Start command",
        extra={
            "user_id": message.from_user.id,
            "username": message.from_user.username
        }
    )


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot):
    """
    Handler для фото
    Завантажує найбільшу версію фото та зберігає на сервері
    """
    try:
        # Telegram надсилає фото в різних розмірах - беремо найбільше
        photo = message.photo[-1]
        
        # Показуємо що обробляємо
        status_msg = await message.answer("⏳ Завантажую фото...")
        
        # Завантажуємо файл з Telegram
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        # Читаємо байти
        file_content = file_bytes.read()
        
        # Генеруємо ім'я файлу
        original_name = f"photo_{photo.file_id[:8]}.jpg"
        
        # Зберігаємо файл
        success, result = await storage.save_file(file_content, original_name)
        
        # Видаляємо статус повідомлення
        await status_msg.delete()
        
        if success:
            # result = URL
            await message.answer(
                f"✅ <b>Фото збережено!</b>\n\n"
                f"📎 Посилання:\n"
                f"<code>{result}</code>\n\n"
                f"📊 Розмір: {len(file_content) / 1024:.1f} KB",
                parse_mode="HTML"
            )
            
            logger.info(
                "Photo uploaded",
                extra={
                    "user_id": message.from_user.id,
                    "file_id": photo.file_id,
                    "size_bytes": len(file_content),
                    "url": result
                }
            )
        else:
            # result = error message
            await message.answer(result)
            
    except Exception as e:
        logger.error(f"Failed to process photo: {e}")
        await message.answer(
            "❌ Помилка при обробці фото. Спробуйте ще раз або зверніться до адміністратора."
        )


@router.message(F.document)
async def handle_document(message: Message, bot: Bot):
    """
    Handler для документів
    Завантажує файл та зберігає на сервері
    """
    try:
        document = message.document
        
        # Показуємо що обробляємо
        status_msg = await message.answer("⏳ Завантажую файл...")
        
        # Завантажуємо файл з Telegram
        file = await bot.get_file(document.file_id)
        file_bytes = await bot.download_file(file.file_path)
        
        # Читаємо байти
        file_content = file_bytes.read()
        
        # Використовуємо оригінальну назву файлу
        original_name = document.file_name or f"file_{document.file_id[:8]}.bin"
        
        # Зберігаємо файл
        success, result = await storage.save_file(file_content, original_name)
        
        # Видаляємо статус повідомлення
        await status_msg.delete()
        
        if success:
            # result = URL
            await message.answer(
                f"✅ <b>Файл збережено!</b>\n\n"
                f"📎 Посилання:\n"
                f"<code>{result}</code>\n\n"
                f"📄 Назва: {original_name}\n"
                f"📊 Розмір: {len(file_content) / 1024:.1f} KB",
                parse_mode="HTML"
            )
            
            logger.info(
                "Document uploaded",
                extra={
                    "user_id": message.from_user.id,
                    "file_id": document.file_id,
                    "filename": original_name,
                    "size_bytes": len(file_content),
                    "url": result
                }
            )
        else:
            # result = error message
            await message.answer(result)
            
    except Exception as e:
        logger.error(f"Failed to process document: {e}")
        await message.answer(
            "❌ Помилка при обробці файлу. Спробуйте ще раз або зверніться до адміністратора."
        )


@router.message()
async def handle_other(message: Message):
    """
    Handler для всіх інших типів повідомлень
    """
    await message.answer(
        "❓ Будь ласка, надішліть фото або документ.\n\n"
        "Використовуйте /start щоб побачити інструкцію."
    )
