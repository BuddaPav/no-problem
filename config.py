import os

class Config:
    # Загружаем ключи из переменных окружения
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    CHAT_ID = "-1002628146453"  # Замените на ваш chat_id
    
    RSS_FEEDS = [
        "https://lenta.ru/rss",
        "https://meduza.io/rss/all",
        "https://www.rbc.ru/v10/ajax/rss/index.rss"
    ]
    
    KEYWORDS = [
        "власть", "психология", "политик", "контроль",
        "россия", "управление", "система", "общество",
        "тренды", "спорт", "лайфхаки", "криминал"
    ]
    
    # Настройки генерации текста
    GPT_PROMPT = """На основе заголовка '{headline}' создай загадочное сообщение в стиле мистического ордена. 
Используй символы (⚫🌑⚡), метафоры о времени и энергиях. Не более 200 символов."""
