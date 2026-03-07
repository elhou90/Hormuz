import os
import time
import feedparser
import requests
from telegram import Bot
from telegram.ext import Application

TOKEN = os.getenv('TELEGRAM_TOKEN')  # À mettre dans Railway
CHAT_ID = os.getenv('CHAT_ID')       # Ton ID

bot = Bot(token=TOKEN)

KEYWORDS = ['ceasefire Iran', 'trêve Iran', 'negotiations Hormuz', 'négociations Ormuz', 'Strait open', 'détroit ouvert', 'Hormuz reopening', 'cessez-le-feu', 'ouverture Ormuz']

RSS_FEEDS = [
    'https://www.reuters.com/rss',
    'https://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
    'https://www.aljazeera.com/xml/rss/all.xml',
    'https://www.france24.com/fr/rss',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml'
]

def check_news():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:
            title = entry.title.lower()
            summary = entry.summary.lower() if 'summary' in entry else ''
            if any(kw.lower() in title or kw.lower() in summary for kw in KEYWORDS):
                message = f"🚨 ALERTE HORMUZ !\n\n{entry.title}\n{entry.link}\n\nVérifie vite pour vendre sur XM !"
                bot.send_message(chat_id=CHAT_ID, text=message)
                print("Alerte envoyée !")

if __name__ == "__main__":
    while True:
        check_news()
        time.sleep(900)  # Toutes les 15 minutes
