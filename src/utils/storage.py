"""
Storage utilities для збереження файлів та генерації публічних URL
"""
import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class FileStorage:
    """
    Клас для роботи з файловим сховищем
    """
    
    def __init__(self):
        self.upload_dir = os.getenv("UPLOAD_DIR", "/var/www/media")
        self.public_url = os.getenv("PUBLIC_URL", "http://hyperitacademy.space/media")
        self.max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        
        # Створюємо директорію якщо не існує
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Storage initialized: {self.upload_dir}")
    
    def generate_unique_filename(self, file_bytes: bytes, original_name: str) -> str:
        """
        Генеруємо унікальне ім'я файлу: timestamp_hash.ext
        
        Args:
            file_bytes: Байти файлу для хешування
            original_name: Оригінальна назва файлу
            
        Returns:
            Унікальна назва файлу
        """
        # Timestamp для сортування
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # MD5 hash для унікальності
        file_hash = hashlib.md5(file_bytes).hexdigest()[:8]
        
        # Розширення файлу
        ext = original_name.split(".")[-1].lower() if "." in original_name else "bin"
        
        unique_name = f"{timestamp}_{file_hash}.{ext}"
        return unique_name
    
    def validate_file_size(self, file_size: int) -> tuple[bool, Optional[str]]:
        """
        Перевіряємо розмір файлу
        
        Returns:
            (is_valid, error_message)
        """
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            return False, f"❌ Файл занадто великий ({file_size / 1024 / 1024:.1f} MB). Максимум: {self.max_size_mb} MB"
        
        return True, None
    
    def validate_extension(self, filename: str) -> tuple[bool, Optional[str]]:
        """
        Перевіряємо розширення файлу
        
        Returns:
            (is_valid, error_message)
        """
        allowed_ext_str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,webp,pdf")
        allowed_extensions = set(ext.strip().lower() for ext in allowed_ext_str.split(","))
        
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        
        if ext not in allowed_extensions:
            return False, f"❌ Дозволені тільки файли: {', '.join(sorted(allowed_extensions))}"
        
        return True, None
    
    async def save_file(self, file_bytes: bytes, original_name: str) -> tuple[bool, str]:
        """
        Зберігаємо файл та повертаємо публічний URL
        
        Args:
            file_bytes: Вміст файлу
            original_name: Оригінальна назва
            
        Returns:
            (success, url_or_error_message)
        """
        try:
            # Валідація розміру
            is_valid, error = self.validate_file_size(len(file_bytes))
            if not is_valid:
                return False, error
            
            # Валідація розширення
            is_valid, error = self.validate_extension(original_name)
            if not is_valid:
                return False, error
            
            # Генеруємо унікальне ім'я
            unique_filename = self.generate_unique_filename(file_bytes, original_name)
            
            # Повний шлях
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Зберігаємо файл
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            
            # Генеруємо публічний URL
            public_url = f"{self.public_url}/{unique_filename}"
            
            logger.info(
                "File saved successfully",
                extra={
                    "original_name": original_name,
                    "saved_as": unique_filename,
                    "size_bytes": len(file_bytes),
                    "public_url": public_url
                }
            )
            
            return True, public_url
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}", extra={"original_name": original_name})
            return False, f"❌ Помилка збереження файлу: {str(e)}"
