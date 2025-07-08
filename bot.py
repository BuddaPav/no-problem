#!/usr/bin/env python3
import logging
import feedparser
import requests
import schedule
import time
from datetime import datetime
from config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log'
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.published = set()
        
    def get_news(self):
        """Сбор новостей из RSS"""
        headlines = []
        for feed in self.config.RSS_FEEDS:
            try:
                parsed = feedparser.parse(feed)
                headlines.extend(entry.title for entry in parsed.entries[:10])
            except Exception as e:
                logger.error(f"Ошибка RSS {feed}: {e}")
        return headlines
    
    def generate_post(self, headline):
        """Генерация поста через OpenAI"""
        from openai import OpenAI
        
        client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system", 
                    "content": "Ты мистический оракул, предсказывающий скрытые смыслы событий"
                }, {
                    "role": "user",
                    "content": self.config.GPT_PROMPT.format(headline=headline)
                }],
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            return None
    
    def send_to_telegram(self, text):
        """Отправка сообщения"""
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": self.config.CHAT_ID,
                    "text": text,
                    "parse_mode": "HTML"
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ошибка Telegram: {e}")
            return False
    
    def run(self):
        """Основной цикл"""
        schedule.every(20).minutes.do(self.job)
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
