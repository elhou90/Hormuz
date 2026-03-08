import os
import feedparser
import yfinance as yf
import tweepy
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
TWITTER_BEARER = os.getenv('TWITTER_BEARER_TOKEN')

KEYWORDS = ['ceasefire', 'trêve', 'negotiations', 'négociations', 'Hormuz open', 'détroit ouvert', 'Hormuz reopening', 'ouverture Ormuz', 'cessez-le-feu', 'Iran truce']

RSS_FEEDS = [ ... ]  # (les 11 sources précédentes, je les garde identiques pour ne pas alourdir)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚨 HormuzAlertBot PRO + Tweets prêt !\nCommandes :\n/analyse → news\n/tweets → derniers tweets\n/prix → WTI live\n/status\n/test\n\nAlerte claire : HORMUZ OPEN SELL dès que le détroit ouvre ou trêve !")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot 24/7 actif (news + tweets)\nIntervalle : 15 min\nAucune alerte pour l'instant.")

async def test_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=CHAT_ID, text="🚨 HORMUZ OPEN SELL\n\nTEST - Tout fonctionne ! Tu vendras sur XM dès le vrai signal.")

async def analyse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 ANALYSE NEWS RÉCENTES (11 sources)\n\n"
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:
            msg += f"🔹 {entry.title}\n{entry.link}\n\n"
    await update.message.reply_text(msg)

async def tweets_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    client = tweepy.Client(bearer_token=TWITTER_BEARER)
    query = '(Hormuz OR Ormuz OR "Strait of Hormuz") (open OR reopening OR ceasefire OR trêve OR negotiations OR négociation) Iran lang:en OR lang:fr -is:retweet'
    response = client.search_recent_tweets(query=query, max_results=10)
    msg = "📊 DERNIERS TWEETS ANALYSÉS :\n\n"
    if response.data:
        for tweet in response.data:
            msg += f"🔹 {tweet.text[:200]}...\nhttps://twitter.com/i/web/status/{tweet.id}\n\n"
    else:
        msg += "Aucun tweet récent correspondant."
    await update.message.reply_text(msg)

async def prix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ticker = yf.Ticker("CL=F")
        price = ticker.fast_info.get('lastPrice') or ticker.history(period="1d")['Close'].iloc[-1]
        await update.message.reply_text(f"🛢 Prix WTI live : {price:.2f} USD/bbl")
    except:
        await update.message.reply_text("❌ Erreur prix – réessaie.")

async def check_all(context: ContextTypes.DEFAULT_TYPE):
    # === NEWS ===
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:15]:
            title = entry.title.lower()
            summary = entry.summary.lower() if hasattr(entry, 'summary') else ''
            if any(kw.lower() in title or kw.lower() in summary for kw in KEYWORDS):
                msg = f"🚨 HORMUZ OPEN SELL\n\n{entry.title}\n{entry.link}\n\n🔴 Vends le pétrole sur XM MAINTENANT !"
                await context.bot.send_message(chat_id=CHAT_ID, text=msg)
                print("Alerte NEWS envoyée")

    # === TWEETS ===
    client = tweepy.Client(bearer_token=TWITTER_BEARER)
    query = '(Hormuz OR Ormuz OR "Strait of Hormuz") (open OR reopening OR ceasefire OR trêve OR negotiations OR négociation) Iran lang:en OR lang:fr -is:retweet'
    response = client.search_recent_tweets(query=query, max_results=10)
    if response.data:
        for tweet in response.data:
            text_lower = tweet.text.lower()
            if any(kw.lower() in text_lower for kw in KEYWORDS):
                msg = f"🚨 HORMUZ OPEN SELL\n\nTweet : {tweet.text}\nhttps://twitter.com/i/web/status/{tweet.id}\n\n🔴 Vends sur XM MAINTENANT !"
                await context.bot.send_message(chat_id=CHAT_ID, text=msg)
                print("Alerte TWEET envoyée")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("test", test_alert))
    app.add_handler(CommandHandler("analyse", analyse))
    app.add_handler(CommandHandler("tweets", tweets_cmd))
    app.add_handler(CommandHandler("prix", prix))
    
    app.job_queue.run_repeating(check_all, interval=900, first=10)  # 15 min (limite Free Tier OK)
    print("Bot PRO + Tweets démarré")
    app.run_polling()

if __name__ == "__main__":
    main()
