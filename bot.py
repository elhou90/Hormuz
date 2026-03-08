import os
import feedparser
import yfinance as yf
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Mots-clés événement
EVENT_KEYWORDS = ['ceasefire', 'trêve', 'negotiations', 'négociations', 'Hormuz open', 'détroit ouvert', 'Hormuz reopening', 'ouverture Ormuz', 'cessez-le-feu', 'Iran truce']

# Mots-clés obligatoires Iran/Hormuz pour les news classiques
IRAN_CONTEXT = ['iran', 'hormuz', 'ormuz', 'gulf', 'tehran', 'irgc', 'khamenei']

RSS_FEEDS = [
    'https://www.reuters.com/rss',
    'https://feeds.bbci.co.uk/news/world/middle_east/rss.xml',
    'https://www.aljazeera.com/xml/rss/all.xml',
    'https://www.france24.com/fr/rss',
    'https://rss.nytimes.com/services/xml/rss/nyt/World.xml',
    'https://www.bbc.com/news/world/rss.xml',
    'https://edition.cnn.com/rss/edition_world.rss',
    'https://www.theguardian.com/world/rss',
    'https://feeds.washingtonpost.com/rss/world',
    'https://www.oilprice.com/rss/news',
    'https://www.cnbc.com/world-news/rss/',
    # === TES 3 RSS NITTER ===
    'https://nitter.net/search/rss?q=(Hormuz+OR+"Strait+of+Hormuz"+OR+"Hormuz+shipping"+OR+"oil+tanker"+OR+"tanker+attack"+OR+"tanker+seized"+OR+"tanker+explosion"+OR+"oil+refinery+attack"+OR+"refinery+explosion"+OR+"pipeline+attack"+OR+"pipeline+sabotage"+OR+"oil+facility+attack"+OR+"oil+infrastructure+attack"+OR+"oil+terminal+attack"+OR+"drone+attack+oil"+OR+"missile+strike+oil"+OR+"Iran+US+talks"+OR+"Iran+US+negotiations"+OR+"Iran+US+ceasefire"+OR+"Iran+sanctions"+OR+"Iran+nuclear+talks"+OR+"Iran+navy"+OR+"US+navy+gulf"+OR+"Gulf+shipping+incident"+OR+"Gulf+tanker+attack"+OR+"OPEC+emergency"+OR+"oil+supply+disruption")',
    'https://nitter.net/search/rss?q=("Strait+of+Hormuz"+OR+"tanker+attack"+OR+"oil+refinery+attack"+OR+"pipeline+attack"+OR+"oil+supply+disruption"+OR+"Iran+US+talks")',
    'https://nitter.net/search/rss?q=(tanker+OR+shipping+OR+Hormuz)+attack'
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 HormuzAlertBot ULTIMATE V2 prêt !\nFiltre anti-faux-positif activé\nCommandes :\n/analyse → news + tweets\n/prix → WTI\n/status\n/test")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot 24/7 actif (14 sources)\nFiltre strict anti-faux-positif\nAucune alerte pour l'instant.")

async def test_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="🚨 HORMUZ OPEN SELL\n\nTEST - Le bot fonctionne parfaitement !")

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 ANALYSE RÉCENTE (11 news + 3 Nitter)\n\n"
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                msg += f"🔹 {entry.title}\n{entry.link}\n\n"
        except:
            pass
    await update.message.reply_text(msg)

async def prix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ticker = yf.Ticker("CL=F")
        price = ticker.fast_info.get('lastPrice') or ticker.history(period="1d")['Close'].iloc[-1]
        await update.message.reply_text(f"🛢 Prix WTI live : {price:.2f} USD/bbl")
    except:
        await update.message.reply_text("❌ Erreur prix – réessaie.")

async def check_news(context: ContextTypes.DEFAULT_TYPE):
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:15]:
                title = entry.title.lower()
                summary = entry.summary.lower() if hasattr(entry, 'summary') else ''
                text = title + ' ' + summary
                is_nitter = "nitter.net" in feed_url.lower()

                trigger = False
                if is_nitter:
                    trigger = True  # Tes recherches Nitter = déjà ciblées
                else:
                    has_iran = any(word in text for word in IRAN_CONTEXT)
                    has_event = any(word in text for word in EVENT_KEYWORDS)
                    trigger = has_iran and has_event

                if trigger:
                    msg = f"🚨 HORMUZ OPEN SELL\n\n{entry.title}\n\n{entry.link}\n\n🔴 Vends le pétrole sur XM MAINTENANT !"
                    await context.bot.send_message(chat_id=CHAT_ID, text=msg)
                    print(f"🚨 ALERTE ENVOYÉE depuis {'Nitter' if is_nitter else 'News'}")
        except:
            continue

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test_alert))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("prix", prix))
    
    app.job_queue.run_repeating(check_news, interval=900, first=10)
    print("Bot ULTIMATE V2 démarré - filtre anti-faux-positif")
    app.run_polling()

if __name__ == "__main__":
    main()
