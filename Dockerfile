FROM python:3.11-slim

WORKDIR /app

# Копіюємо requirements
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код бота
COPY src ./src

# Створюємо директорію для завантажень
RUN mkdir -p /var/www/media

CMD ["python", "src/main.py"]
