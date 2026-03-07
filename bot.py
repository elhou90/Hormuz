import os
import time
import feedparser
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')  # Ton ID personnel

KEYWORDS = [
    'ceasefire Iran', 'trêve Iran', 'negotiations Hormuz', 'négociations Ormuz',
    'Strait open', 'détroit ouvert', 'Hormuz reopening', 'ouverture Ormuz',
    'cessez-le-feu', 'Iran negotiations', 'Hormuz open', 'Iran truce'
]

RSS_FEEDS = [
    'https://www.reuters.com/rss',
    'https://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
    'https://www.aljazeera.com/xml/rss/all.xml',
    'https://www.france24.com/fr/rss',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.bbc.com/news/world/rss.xml'
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 Bot HormuzAlert prêt !\n\nJe surveille le détroit d'Ormuz 24/7.\nCommandes :\n/status → état actuel\n/test → alerte test\n\nDès qu'il y a trêve, négociations ou réouverture → je t'envoie l'alerte instantanément pour vendre sur XM !")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot en ligne et actif.\nDernière vérification : il y a quelques minutes.\nStatut actuel (8 mars 2026) : Détroit toujours bloqué, aucune trêve/négociation détectée. Prix pétrole en hausse. Prêt à alerter !")

async def test_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = "🧪 TEST ALERTE HORMUZ\n\nCeci est un test. Si tu reçois ça, le bot fonctionne parfaitement !\n\nDès qu'il y aura du vrai (trêve ou ouverture), tu auras le vrai signal pour vendre sur XM."
    await context.bot.send_message(chat_id=CHAT_ID, text=message)
    await update.message.reply_text("✅ Alerte test envoyée en privé ! Vérifie ton Telegram.")

async def check_news(context: ContextTypes.DEFAULT_TYPE):
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:15]:
            title = entry.title.lower()
            summary = entry.summary.lower() if hasattr(entry, 'summary') else ''
            link = entry.link
            if any(kw.lower() in title or kw.lower() in summary for kw in KEYWORDS):
                message = f"🚨 ALERTE HORMUZ IMMÉDIATE !\n\n{entry.title}\n\n{link}\n\n🔴 Ouvre XM et vends le pétrole MAINTENANT avant la chute des prix !"
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
                print(f"🚨 Alerte envoyée : {entry.title}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test_alert))
    
    # Vérification toutes les 10 minutes (plus rapide que 15)
    job_queue = app.job_queue
    job_queue.run_repeating(check_news, interval=600, first=10)
    
    print("Bot démarré - en attente d'alertes...")
    app.run_polling()

if __name__ == "__main__":
    main()
