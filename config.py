import os

class Config:
    def __init__(self):
        # Загружаем ключи из переменных окружения
        self.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
        self.CHAT_ID = os.getenv('CHAT_ID', "-1002628146453")  # Значение по умолчанию
        
        self.RSS_FEEDS = [
            "https://lenta.ru/rss",
            "https://meduza.io/rss/all",
            "https://www.rbc.ru/v10/ajax/rss/index.rss"
        ]
        
        self.KEYWORDS = [
            "власть", "психология", "политик", "контроль",
            "россия", "управление", "система", "общество",
            "тренды", "спорт", "лайфхаки", "криминал"
        ]
        
        # Настройки генерации текста
        self.GPT_PROMPT = """На основе заголовка '{headline}' создай нейтральное сообщение в стиле пасивно-агресивного аналитика,но без малейших преувеличений. 
Используй символы (⚫🌑⚡), метафоры в стиле философии в конце поста,не более 5 слов. Не более 500 символов."""
