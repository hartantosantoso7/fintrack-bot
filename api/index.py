import os
import json
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from supabase import create_client, Client

app = Flask(__name__)

# Konfigurasi Environment
TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

bot = Bot(token=TOKEN)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Handler Fungsi ---

def start(update, context):
    update.message.reply_text("Halo Hartanto! Kirim format: /keluar [nominal] [ket] [akun]")

def keluar(update, context):
    try:
        # Parsing: /keluar 50000 makan BCA
        args = context.args
        amount = float(args[0])
        description = args[1]
        account_name = args[2]

        # 1. Get Account ID
        account_query = supabase.table("accounts").select("id").eq("name", account_name).single().execute()
        account_id = account_query.data['id']

        # 2. Insert Transaction
        data = {
            "account_id": account_id,
            "amount": amount,
            "type": "keluar",
            "description": description,
            "category": "Food" # Contoh hardcoded, bisa dikembangkan
        }
        supabase.table("transactions").insert(data).execute()
        
        update.message.reply_text(f"✅ Tercatat: Rp{amount:,.0f} dari {account_name}")
    except Exception as e:
        update.message.reply_text(f"❌ Gagal: {str(e)}")

def handle_photo(update, context):
    update.message.reply_text("Struk diterima! Sedang memproses dengan OCR...")
    # Logic OCR Space API atau Google Vision bisa ditaruh di sini

# --- Setup Webhook Logic ---

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        
        # Manual Dispatcher setup (karena Serverless tidak mendukung Updater.start_polling)
        dispatcher = Dispatcher(bot, None, workers=0)
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("keluar", keluar))
        dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo))
        
        dispatcher.process_update(update)
        return "ok"

@app.route('/')
def index():
    return "Bot is running"