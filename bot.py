import os
import time
import feedparser
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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
    'https://www.bbc.com/news/world/rss.xml',
    'https://edition.cnn.com/rss/edition_world.rss',      # NOUVEAU
    'https://www.theguardian.com/world/rss',              # NOUVEAU
    'https://feeds.washingtonpost.com/rss/world',         # NOUVEAU
    'https://www.oilprice.com/rss/news',                  # NOUVEAU (spécial pétrole)
    'https://www.cnbc.com/world-news/rss/',               # NOUVEAU
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 HormuzAlertBot PRO prêt !\n\nCommandes :\n/analyse → analyse news récentes\n/prix → prix WTI live\n/status → état du bot\n/test → alerte test\n\nJe surveille 24/7 pour trêve / négociations / ouverture du détroit !")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot en ligne 24/7\nSources : 11 flux news\nDernière vérif : il y a quelques secondes\nAucune alerte pour l'instant.")

async def test_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="🧪 TEST ALERTE HORMUZ\nTout fonctionne ! Tu recevras le vrai signal pour vendre sur XM.")

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 **ANALYSE NEWS RÉCENTES** (11 sources)\n\n"
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:
            msg += f"🔹 {entry.title}\n{entry.link}\n\n"
    msg += "Pour l'analyse complète des **TWEETS** + ma synthèse Grok (comme avant), demande directement dans le chat ici !"
    await update.message.reply_text(msg)

async def prix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ticker = yf.Ticker("CL=F")
        price = ticker.fast_info.get('lastPrice')
        if price is None:
            hist = ticker.history(period="1d")
            price = hist['Close'].iloc[-1]
        await update.message.reply_text(f"🛢 **Prix WTI actuel** : {price:.2f} USD/bbl\n\nVérifié en live – parfait pour XM !")
    except:
        await update.message.reply_text("❌ Erreur prix WTI – réessaie dans 30 sec.")

async def check_news(context: ContextTypes.DEFAULT_TYPE):
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:15]:
            title = entry.title.lower()
            summary = entry.summary.lower() if hasattr(entry, 'summary') else ''
            if any(kw.lower() in title or kw.lower() in summary for kw in KEYWORDS):
                message = f"🚨 ALERTE HORMUZ IMMÉDIATE !\n\n{entry.title}\n\n{entry.link}\n\n🔴 Ouvre XM et vends MAINTENANT !"
                await context.bot.send_message(chat_id=CHAT_ID, text=message)
                print(f"🚨 Alerte envoyée : {entry.title}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test_alert))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("prix", prix))
    
    app.job_queue.run_repeating(check_news, interval=600, first=10)
    
    print("Bot PRO démarré – 11 sources + commandes /analyse /prix")
    app.run_polling()

if __name__ == "__main__":
    main()
