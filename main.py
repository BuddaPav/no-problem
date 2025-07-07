#!/usr/bin/env python3
"""
Script to force the first post immediately
"""

import os
from openai import OpenAI
import feedparser
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get API keys
OPENAI_API_KEY = os.getenv('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')
TELEGRAM_BOT_TOKEN = os.getenv('8184601194:AAED936KjImBZ3GnizGlB32SgQ5me0g2_XE')
CHAT_ID = "-1002628146453"

# Keywords
KEYWORDS = [
    "власть", "психология", "политик", "контроль", "россия", "управление", "система", "общество",
    "trends", "тренды", "спорт", "sports", "life hacks", "лайфхаки", "нейтральные новости", 
    "цели молодежи", "youth goals", "преступления в СНГ", "crimes in the CIS", "криминал", 
    "терроризм", "terrorism", "европа", "америка", "ближний восток", "europe", "america", "middle east"
]

# RSS feeds
RSS_FEEDS = [
    "https://lenta.ru/rss",
    "https://meduza.io/rss/all",
    "https://www.rbc.ru/v10/ajax/rss/index.rss"
]

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_trends():
    """Get headlines from RSS feeds"""
    headlines = []
    logger.info("Сбор новостей из RSS-лент...")
    
    for feed_url in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            if parsed.entries:
                for entry in parsed.entries[:10]:
                    if hasattr(entry, 'title'):
                        headlines.append(entry.title)
        except Exception as e:
            logger.error(f"Ошибка RSS {feed_url}: {str(e)}")
            continue
    
    return headlines

def filter_headlines(headlines):
    """Filter headlines by keywords"""
    filtered = []
    for headline in headlines:
        if any(keyword.lower() in headline.lower() for keyword in KEYWORDS):
            filtered.append(headline)
    return filtered

def generate_post(headline):
    """Generate mysterious post using OpenAI"""
    if not client:
        # Резервные мистические сообщения
        mysterious_messages = [
            "⚫ Великое Колесо поворачивается... энергии смещаются в новом направлении.",
            "🌑 Древние символы проявляются в современном мире... посвященные понимают знаки.",
            "⚡ Завеса между мирами истончается... события обретают скрытое значение.",
            "🔮 Хронос шепчет загадки тем, кто умеет слушать пространство между словами.",
            "⭐ Матрица реальности дает сбой... истина просачивается сквозь трещины времени.",
        ]
        import random
        return random.choice(mysterious_messages)
    
    try:
        prompt = f"На основе события в заголовке: '{headline}', создай ЗАГАДОЧНОЕ сообщение НА РУССКОМ ЯЗЫКЕ в стиле тайного мистического ордена. Используй символы (⚫🌑⚡🔮⭐🌀⭕), метафоры о времени, энергиях, вибрациях, завесах реальности. Избегай прямого упоминания событий. Максимум 200 символов. Таинственно, как древние пророчества."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - мистический оракул, который видит скрытые связи между событиями. Говоришь символами и метафорами о космических силах, энергетических потоках, временных вихрях. Каждое земное событие для тебя - проявление высших законов. Всегда на русском языке."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.95
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Ошибка OpenAI: {str(e)}")
        # Fallback mysterious message
        return "🌑 Вселенские силы движутся в тени... те, кто понимает знаки, готовятся к переменам."

def post_to_telegram(text):
    """Post to Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=payload, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Ошибка Telegram: {str(e)}")
        return False

def force_immediate_post():
    """Force immediate post regardless of newness"""
    logger.info("🔥 ПРИНУДИТЕЛЬНАЯ ПУБЛИКАЦИЯ ПЕРВОГО ПОСТА ПРЯМО СЕЙЧАС!")
    
    # Get news
    headlines = get_trends()
    if not headlines:
        logger.error("Нет заголовков")
        return False
    
    # Filter by keywords
    filtered = filter_headlines(headlines)
    if not filtered:
        logger.warning("Нет подходящих заголовков, используем первый доступный")
        # Use first available headline if no keywords match
        headline = headlines[0]
    else:
        headline = filtered[0]
    
    logger.info(f"Выбранный заголовок: {headline}")
    
    # Generate post
    post = generate_post(headline)
    logger.info(f"Сгенерированный пост: {post}")
    
    # Send to Telegram
    success = post_to_telegram(post)
    
    if success:
        logger.info("✅ ПЕРВЫЙ ПОСТ УСПЕШНО ОПУБЛИКОВАН!")
        return True
    else:
        logger.error("❌ Не удалось опубликовать пост")
        return False

if __name__ == "__main__":
    force_immediate_post()
	#!/usr/bin/env python3
"""
Telegram Bot для автоматической публикации постов
Бот собирает новости из RSS-лент, фильтрует их по ключевым словам,
генерирует посты с помощью OpenAI и публикует в Telegram-канал.
"""

import os
from openai import OpenAI
import feedparser
import requests
import schedule
import time
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import base64
from io import BytesIO

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# === НАСТРОЙКИ ===
# Получаем API ключи из переменных окружения (безопасно)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ID канала, куда бот будет отправлять сообщения
CHAT_ID = "-1002628146453"

# Ключевые слова для фильтрации трендов
KEYWORDS = [
    # Оригинальные ключевые слова
    "власть", "психология", "политик", "контроль", "россия", "управление", "система", "общество",
    # Новые ключевые слова
    "trends", "тренды", "спорт", "sports", "life hacks", "лайфхаки", "нейтральные новости", 
    "цели молодежи", "youth goals", "преступления в СНГ", "crimes in the CIS", "криминал", 
    "терроризм", "terrorism", "европа", "америка", "ближний восток", "europe", "america", "middle east"
]

# Список RSS-лент для сбора новостей
RSS_FEEDS = [
    "https://lenta.ru/rss",
    "https://meduza.io/rss/all",
    "https://www.rbc.ru/v10/ajax/rss/index.rss"
]

# Инициализация OpenAI клиента
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI API key загружен")
else:
    client = None
    logger.error("OPENAI_API_KEY не найден в переменных окружения")

if TELEGRAM_BOT_TOKEN:
    logger.info("Telegram Bot Token загружен")
else:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")

def get_trends():
    """Получение заголовков новостей из RSS-лент"""
    headlines = []
    logger.info("Начинаю сбор новостей из RSS-лент...")
    
    for feed_url in RSS_FEEDS:
        try:
            logger.info(f"Обрабатываю RSS: {feed_url}")
            parsed = feedparser.parse(feed_url)
            
            if parsed.entries:
                for entry in parsed.entries[:10]:
                    if hasattr(entry, 'title'):
                        headlines.append(entry.title)
                logger.info(f"Получено {len(parsed.entries[:10])} заголовков из {feed_url}")
            else:
                logger.warning(f"Нет записей в RSS: {feed_url}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке RSS {feed_url}: {str(e)}")
            continue
    
    logger.info(f"Всего собрано {len(headlines)} заголовков")
    return headlines

def filter_headlines(headlines):
    """Фильтрация заголовков по ключевым словам"""
    filtered = []
    for headline in headlines:
        if any(keyword.lower() in headline.lower() for keyword in KEYWORDS):
            filtered.append(headline)
    
    logger.info(f"После фильтрации осталось {len(filtered)} заголовков")
    return filtered

def generate_image_prompt(headline):
    """Генерация промпта для изображения на основе заголовка"""
    # Создаем таинственный промпт для изображения
    image_keywords = {
        "власть": "dark government building, shadows, mysterious figures",
        "политик": "silhouette behind podium, dark atmosphere, mysterious meeting",
        "смерть": "candles, shadows, gothic atmosphere, mystical",
        "криминал": "dark alley, shadows, noir style, mysterious",
        "терроризм": "abstract danger symbols, dark clouds, ominous atmosphere",
        "спорт": "stadium in shadows, mysterious competition, dark energy",
        "технологии": "digital matrix, glowing symbols, cyber mysticism",
        "экономика": "money symbols in shadows, economic mystery"
    }
    
    # Ищем ключевые слова в заголовке
    for keyword, description in image_keywords.items():
        if keyword.lower() in headline.lower():
            return f"Mysterious, dark, atmospheric image: {description}, cinematic lighting, 4k quality, digital art"
    
    # Базовый промпт если ничего не найдено
    return "Dark mysterious atmosphere, shadows and light, abstract symbolism, cinematic quality, 4k digital art"

def generate_image(headline):
    """Генерация изображения для поста"""
    if not client:
        logger.warning("OpenAI недоступен для генерации изображений")
        return None
    
    try:
        image_prompt = generate_image_prompt(headline)
        logger.info(f"Генерирую изображение с промптом: {image_prompt}")
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        image_url = response.data[0].url
        logger.info("Изображение успешно сгенерировано")
        
        # Скачиваем изображение
        img_response = requests.get(image_url, timeout=30)
        if img_response.status_code == 200:
            return img_response.content
        else:
            logger.error("Не удалось скачать сгенерированное изображение")
            return None
            
    except Exception as e:
        logger.error(f"Ошибка при генерации изображения: {str(e)}")
        return None

def generate_post(headline):
    """Генерация мистического поста на основе заголовка"""
    logger.info(f"Генерирую мистический пост для: {headline}")
    
    if not client:
        logger.warning("OpenAI недоступен, используем загадочный резервный текст")
        # Резервные мистические сообщения
        mysterious_messages = [
            "⚫ Великое Колесо поворачивается... энергии смещаются в новом направлении.",
            "🌑 Древние символы проявляются в современном мире... посвященные понимают знаки.",
            "⚡ Завеса между мирами истончается... события обретают скрытое значение.",
            "🔮 Хронос шепчет загадки тем, кто умеет слушать пространство между словами.",
            "⭐ Матрица реальности дает сбой... истина просачивается сквозь трещины времени.",
            "🌀 Спирали судьбы переплетаются... каждое движение порождает новые вибрации.",
            "⭕ Круг замыкается там, где начинался... но на новом уровне понимания."
        ]
        
        import random
        return random.choice(mysterious_messages)
    
    try:
        prompt = f"На основе события в заголовке: '{headline}', создай ЗАГАДОЧНОЕ сообщение НА РУССКОМ ЯЗЫКЕ в стиле тайного мистического ордена. Используй символы (⚫🌑⚡🔮⭐🌀⭕), метафоры о времени, энергиях, вибрациях, завесах реальности. Избегай прямого упоминания событий. Максимум 200 символов. Таинственно, как древние пророчества."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты - мистический оракул, который видит скрытые связи между событиями. Говоришь символами и метафорами о космических силах, энергетических потоках, временных вихрях. Каждое земное событие для тебя - проявление высших законов. Всегда на русском языке."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=80,
            temperature=0.95
        )
        
        generated_text = response.choices[0].message.content.strip()
        logger.info("Мистический пост успешно сгенерирован")
        return generated_text
        
    except Exception as e:
        logger.error(f"Ошибка при генерации мистического поста: {str(e)}")
        # Возвращаем резервное сообщение
        return "🌑 Вселенские силы движутся в тени... те, кто понимает знаки, готовятся к переменам."

def post_to_telegram(text, image_data=None):
    """Публикация мистического поста в Telegram канал с изображением или без него"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Невозможно отправить сообщение: отсутствует Telegram Bot Token")
        return False
    
    try:
        logger.info(f"Отправляю мистический пост в Telegram: {text[:50]}...")
        
        if image_data:
            # Отправляем пост с изображением
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            
            files = {
                'photo': ('mysterious_image.jpg', image_data, 'image/jpeg')
            }
            data = {
                "chat_id": CHAT_ID,
                "caption": text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, files=files, timeout=30)
        else:
            # Отправляем только текст
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info("✨ Мистический пост успешно отправлен в Telegram")
            return True
        else:
            logger.error(f"Ошибка отправки в Telegram: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при отправке в Telegram: {str(e)}")
        return False

# Список уже опубликованных заголовков
published_headlines = set()

def job(force_first_post=False):
    """Основная функция для выполнения по расписанию"""
    global published_headlines
    
    logger.info("=" * 50)
    logger.info(f"Запуск задачи: {datetime.now()}")
    
    # Проверяем наличие необходимых API ключей
    if not client or not TELEGRAM_BOT_TOKEN:
        logger.error("Отсутствуют необходимые API ключи. Задача пропущена.")
        return
    
    try:
        # Получаем новости
        headlines = get_trends()
        if not headlines:
            logger.warning("Не найдено заголовков новостей")
            return
        
        # Фильтруем по ключевым словам
        filtered_headlines = filter_headlines(headlines)
        if not filtered_headlines:
            logger.warning("Нет заголовков, соответствующих ключевым словам")
            return
        
        # Для первого поста - используем любой заголовок
        if force_first_post:
            logger.info("🚀 Принудительная публикация первого поста")
            headlines_to_post = filtered_headlines[:1]
        else:
            # Фильтруем только новые заголовки (не опубликованные ранее)
            new_headlines = [h for h in filtered_headlines if h not in published_headlines]
            
            if not new_headlines:
                logger.info("Нет новых заголовков для публикации")
                return
            
            headlines_to_post = new_headlines[:3]  # Берем до 3 новых заголовков
        
        # Генерируем и публикуем мистические посты с изображениями
        posts_sent = 0
        for headline in headlines_to_post:
            logger.info(f"🔮 Обрабатываю заголовок: {headline}")
            
            # Генерируем мистический пост
            post = generate_post(headline)
            if not post:
                logger.error("Не удалось сгенерировать мистический пост")
                continue
            
            # Генерируем изображение (если доступно)
            image_data = generate_image(headline)
            if image_data:
                logger.info("✨ Изображение сгенерировано, отправляем с картинкой")
            else:
                logger.info("📝 Отправляем только текст (изображение недоступно)")
            
            # Отправляем в Telegram
            if post_to_telegram(post, image_data):
                posts_sent += 1
                published_headlines.add(headline)  # Добавляем в список опубликованных
                logger.info(f"🔥 Заголовок добавлен в опубликованные: {headline}")
                time.sleep(3)  # Пауза между отправками (увеличена для изображений)
            else:
                logger.error("❌ Не удалось отправить мистический пост")
        
        logger.info(f"Задача завершена. Отправлено постов: {posts_sent}")
        logger.info(f"Всего опубликованных заголовков в памяти: {len(published_headlines)}")
        
    except Exception as e:
        logger.error(f"Ошибка в главной функции: {str(e)}")

def force_first_post():
    """Принудительная публикация первого поста"""
    logger.info("🔥 ПРИНУДИТЕЛЬНАЯ ПУБЛИКАЦИЯ ПЕРВОГО ПОСТА")
    job(force_first_post=True)

def run_bot():
    """Запуск бота с расписанием"""
    logger.info("🤖 Запуск Telegram бота...")
    
    # Проверяем API ключи при старте
    if not client:
        logger.error("❌ OPENAI_API_KEY не установлен")
        return
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN не установлен")
        return
    
    logger.info("✅ API ключи загружены успешно")
    
    # Настраиваем расписание
    schedule.every(20).minutes.do(job)
    logger.info("⏰ Расписание настроено: каждые 20 минут")
    
    # Запускаем первую задачу сразу (принудительно)
    logger.info("🚀 Запуск первой задачи (принудительно)...")
    force_first_post()
    
    # Основной цикл
    logger.info("🔄 Переходим в режим ожидания...")
    while True:
        schedule.run_pending()
        time.sleep(30)

def main():
    """Точка входа в программу"""
    print("🤖 Telegram Bot для автоматической публикации постов")
    print("=" * 50)
    
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("❌ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {str(e)}")

if __name__ == "__main__":
    main()
	# Telegram Bot для Автоматической Публикации Постов

## Overview

Автоматический Telegram бот, который собирает новости из RSS-лент, фильтрует их по ключевым словам, генерирует философские посты с помощью OpenAI и публикует их в Telegram канал.

## System Architecture

### Core Components
- `main.py` - Основной модуль бота с логикой работы
- `config.py` - Конфигурационные настройки
- `test_bot.py` - Тестирование функций бота
- Python 3.11 runtime environment

### Workflow
1. **RSS Parsing** - Сбор новостей из RSS лент (Lenta.ru, Meduza, RBC)
2. **Filtering** - Фильтрация заголовков по ключевым словам
3. **AI Generation** - Генерация философских постов через OpenAI GPT-4
4. **Telegram Publishing** - Автоматическая публикация в Telegram канал
5. **Scheduling** - Выполнение каждый час по расписанию

## Key Components

### Main Application
- `main.py` - Основной бот с полным циклом обработки
- `config.py` - Настройки RSS лент, ключевых слов, промптов
- `test_bot.py` - Тестирование отдельных функций

### Security Features
- Безопасное хранение API ключей в переменных окружения
- Полное логирование всех операций
- Обработка ошибок и таймаутов

## External Dependencies

### Python Runtime
- Python 3.11 с пакетным менеджером pip

### Required Packages
- `openai` - для генерации текстов
- `feedparser` - для парсинга RSS лент
- `requests` - для HTTP запросов
- `schedule` - для выполнения по расписанию
- `python-telegram-bot` - для работы с Telegram API
- `beautifulsoup4` - для парсинга HTML

### API Keys Required
- **OPENAI_API_KEY** - для доступа к OpenAI GPT-4
- **TELEGRAM_BOT_TOKEN** - для публикации в Telegram

## Recent Changes

- Создан полнофункциональный Telegram бот
- Добавлена безопасная работа с API ключами
- Реализован сбор новостей из RSS лент
- Интеграция с OpenAI для генерации постов
- Автоматическая публикация в Telegram канал
- Добавлено детальное логирование и обработка ошибок
- Создана система тестирования компонентов
- Изменено расписание: публикация каждые 20 минут
- Расширены ключевые слова: добавлены "trends", "sports", "life hacks", "neutral news", "youth goals", "crimes in the CIS", "terrorism"
- Обновлена интеграция с OpenAI API (новая версия)
- Настроена генерация постов исключительно на русском языке
- Модернизирован стиль постов: теперь мистический, загадочный, с символами (⚫🌑⚡🔮⭐🌀⭕)
- Добавлена генерация изображений DALL-E 3 для каждого поста
- Реализована система отслеживания опубликованных заголовков для избежания дублирования
- Усовершенствован принудительный первый пост с немедленной публикацией

## User Preferences

Preferred communication style: Simple, everyday language.
