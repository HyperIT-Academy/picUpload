"""
Middleware для перевірки адміністраторів
Дозволяє доступ тільки користувачам з whitelist ADMIN_IDS
"""
import os
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class AdminCheckMiddleware(BaseMiddleware):
    """
    Middleware для перевірки чи користувач є адміністратором
    Блокує доступ для не-адмінів
    """
    
    def __init__(self):
        super().__init__()
        # Парсимо ADMIN_IDS з env
        admin_ids_str = os.getenv("ADMIN_IDS", "")
        self.admin_ids = set()
        
        if admin_ids_str:
            try:
                self.admin_ids = set(int(uid.strip()) for uid in admin_ids_str.split(",") if uid.strip())
                logger.info(f"Admin whitelist configured: {len(self.admin_ids)} admin(s)")
            except ValueError as e:
                logger.error(f"Failed to parse ADMIN_IDS: {e}")
        else:
            logger.warning("ADMIN_IDS not configured - bot will reject all users!")
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Перевіряємо чи користувач в whitelist
        """
        user_id = event.from_user.id
        
        # Перевірка доступу
        if user_id not in self.admin_ids:
            logger.warning(
                f"Unauthorized access attempt",
                extra={
                    "user_id": user_id,
                    "username": event.from_user.username,
                    "message_text": event.text[:50] if event.text else "media"
                }
            )
            
            await event.answer(
                "⛔ У вас немає доступу до цього бота\n\n"
                "Цей бот доступний тільки адміністраторам HyperIT."
            )
            return
        
        # Користувач є адміном - пропускаємо запит далі
        logger.info(
            f"Admin request",
            extra={
                "user_id": user_id,
                "username": event.from_user.username
            }
        )
        
        return await handler(event, data)
