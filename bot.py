#!/usr/bin/env python3
import logging
import feedparser
import requests
import schedule
import time
from datetime import datetime
from config import Config
import os
import sys

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
        self.validate_config()
        
    def validate_config(self):
        """Проверка обязательных настроек"""
        if not self.config.TELEGRAM_BOT_TOKEN:
            logger.error("Не задан TELEGRAM_BOT_TOKEN!")
            sys.exit(1)
        if not self.config.OPENAI_API_KEY:
            logger.error("Не задан OPENAI_API_KEY!")
            sys.exit(1)
    
    def get_news(self):
        """Сбор новостей из RSS с фильтрацией по ключевым словам"""
        headlines = []
        for feed in self.config.RSS_FEEDS:
            try:
                parsed = feedparser.parse(feed)
                for entry in parsed.entries[:15]:  # Берем больше новостей для фильтрации
                    if any(keyword.lower() in entry.title.lower() for keyword in self.config.KEYWORDS):
                        headlines.append(entry.title)
            except Exception as e:
                logger.error(f"Ошибка RSS {feed}: {e}")
        return headlines
    
    def generate_post(self, headline):
        """Генерация поста через OpenAI с обработкой ошибок"""
        from openai import OpenAI
        
        try:
            client = OpenAI(api_key=self.config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system", 
                    "content": "Ты мистический оракул, предсказывающий скрытые смыслы событий"
                }, {
                    "role": "user",
                    "content": self.config.GPT_PROMPT.format(headline=headline)
                }],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ошибка OpenAI: {e}")
            return None
    
    def send_to_telegram(self, text):
        """Отправка сообщения с повторными попытками"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"https://api.telegram.org/bot{self.config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": self.config.CHAT_ID,
                        "text": text,
                        "parse_mode": "HTML"
                    },
                    timeout=15
                )
                if response.status_code == 200:
                    return True
                logger.warning(f"Попытка {attempt+1}: Telegram API вернул {response.status_code}")
            except Exception as e:
                logger.warning(f"Попытка {attempt+1}: Ошибка Telegram: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(5)
        
        return False
    
    def job(self):
        """Основная задача для планировщика"""
        try:
            logger.info("--- Начало выполнения задачи ---")
            headlines = self.get_news()
            
            if not headlines:
                logger.info("Нет новых заголовков, соответствующих ключевым словам")
                return
            
            for headline in headlines:
                if headline not in self.published:
                    post = self.generate_post(headline)
                    if post:
                        if self.send_to_telegram(post):
                            self.published.add(headline)
                            logger.info(f"Успешно отправлен пост: {headline[:50]}...")
                            time.sleep(10)  # Пауза между постами
                        else:
                            logger.error(f"Не удалось отправить пост: {headline[:50]}...")
                    else:
                        logger.error(f"Не удалось сгенерировать пост для: {headline[:50]}...")
        except Exception as e:
            logger.error(f"Критическая ошибка в job(): {e}")
    
    def run(self):
        """Запуск бота с обработкой исключений"""
        logger.info("Запуск бота...")
        schedule.every(20).minutes.do(self.job)
        
        # Первый запуск сразу
        self.job()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Бот остановлен пользователем")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(60)

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
