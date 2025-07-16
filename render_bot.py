# render_bot.py
import os
import json
import pytz
import requests
import logging
from datetime import datetime, timedelta
from threading import Lock
from functools import wraps
from collections import defaultdict

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    Dispatcher,
    Filters,
    MessageHandler
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from flask import Flask, request

# Configuration - will be set via Render environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WEBHOOK_URL = os.getenv('RENDER_EXTERNAL_URL')  # Render provides this
PORT = int(os.getenv('PORT', 10000))  # Render uses port 10000

# Constants
USER_DATA_FILE = '/data/user_data.json'  # Using Render's persistent storage
NEWS_CACHE_FILE = '/data/news_cache.json'
CACHE_EXPIRY_MINUTES = 20

# [Rest of your existing code remains the same...]

# Initialize Flask app
app = Flask(__name__)

# [All your existing handler functions remain the same...]

# Webhook setup for Render
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates via webhook."""
    update = Update.de_json(request.get_json(), updater.bot)
    dispatcher.process_update(update)
    return 'OK'

@app.route('/')
def index():
    """Health check endpoint."""
    return "International News Bot is running on Render!"

def main():
    """Initialize the bot and set up webhook."""
    global updater, dispatcher
    
    # Create /data directory if it doesn't exist
    os.makedirs('/data', exist_ok=True)
    
    # Initialize user data and news cache files if they don't exist
    if not os.path.exists(USER_DATA_FILE):
        save_data(USER_DATA_FILE, {})
    
    if not os.path.exists(NEWS_CACHE_FILE):
        save_data(NEWS_CACHE_FILE, {})

    # Initialize Telegram updater and dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("setcategories", set_categories))
    dispatcher.add_handler(CommandHandler("settimezone", set_timezone))
    dispatcher.add_handler(CommandHandler("setdeliverytimes", set_delivery_times))
    dispatcher.add_handler(CommandHandler("newsnow", news_now))
    dispatcher.add_handler(CallbackQueryHandler(category_selection, pattern="^category_"))
    dispatcher.add_handler(CallbackQueryHandler(time_slot_selection, pattern="^timeslot_"))
    dispatcher.add_handler(CallbackQueryHandler(category_selection, pattern="^categories_done$"))
    dispatcher.add_handler(CallbackQueryHandler(time_slot_selection, pattern="^timeslots_done$"))
    dispatcher.add_error_handler(error_handler)

    # Set up webhook
    updater.bot.set_webhook(
        url=f"{WEBHOOK_URL}/webhook",
        certificate=open('/etc/ssl/certs/ca-certificates.crt', 'rb') if os.path.exists('/etc/ssl/certs/ca-certificates.crt') else None
    )
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=PORT)

if __name__ == '__main__':
    main()
