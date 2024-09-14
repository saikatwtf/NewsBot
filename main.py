import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
import logging

# Load environment variables from config.env
load_dotenv('config.env')

# Telegram bot token and chat ID from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

# Function to scrape news from The Hindu
def scrape_the_hindu():
    logger.info('Scraping The Hindu...')
    url = 'https://www.thehindu.com/news/cities/kolkata/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    news_items = []
    for item in soup.find_all('div', class_='story-card-news'):
        title = item.find('h2').text.strip()
        summary = item.find('p').text.strip() if item.find('p') else None
        if not summary:
            article_url = item.find('a')['href']
            article_response = requests.get(article_url)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            summary = article_soup.find('div', class_='article').text.strip()
        photo_url = item.find('img')['src'] if item.find('img') else 'No image available'
        if not photo_url or photo_url == 'No image available':
            video_url = item.find('video')['src'] if item.find('video') else 'No video available'
            photo_url = video_url
        if 'BengalBulletin' in item.text:
            news_items.append({'title': title, 'summary': summary, 'photo_url': photo_url})
    
    logger.info(f'Scraped {len(news_items)} items from The Hindu.')
    return news_items

# Function to scrape news from another example website
def scrape_example_site():
    logger.info('Scraping example site...')
    url = 'https://example.com/bengali-news'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    news_items = []
    for item in soup.find_all('div', class_='news-item'):
        title = item.find('h2').text.strip()
        summary = item.find('p').text.strip() if item.find('p') else None
        if not summary:
            article_url = item.find('a')['href']
            article_response = requests.get(article_url)
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            summary = article_soup.find('div', class_='article').text.strip()
        photo_url = item.find('img')['src'] if item.find('img') else 'No image available'
        if not photo_url or photo_url == 'No image available':
            video_url = item.find('video')['src'] if item.find('video') else 'No video available'
            photo_url = video_url
        if 'BengalBulletin' in item.text:
            news_items.append({'title': title, 'summary': summary, 'photo_url': photo_url})
    
    logger.info(f'Scraped {len(news_items)} items from example site.')
    return news_items

# Function to combine news from multiple sources
def scrape_news():
    logger.info('Combining news from multiple sources...')
    news_items = []
    news_items.extend(scrape_the_hindu())
    news_items.extend(scrape_example_site())
    logger.info(f'Total news items scraped: {len(news_items)}')
    return news_items

# Function to post news to Telegram
def post_to_telegram(news_items):
    bot = Bot(token=TOKEN)
    for news in news_items:
        message = f"{news['title']}\n*{news['summary']}*\n{news['photo_url']}"
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        logger.info(f'Posted news: {news["title"]}')

# Scheduler to run the script periodically
scheduler = BlockingScheduler()
scheduler.add_job(lambda: post_to_telegram(scrape_news()), 'interval', hours=1)
logger.info('Starting scheduler...')
scheduler.start()
