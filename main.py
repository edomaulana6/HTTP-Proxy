import telebot
import os
import time
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. KOYEB HEALTH CHECK (WAJIB) ---
def run_health_server():
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"ALIVE")
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), H)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- 2. INISIALISASI BOT (DENGAN LOG AGAR TERLIHAT ERRORNYA) ---
TOKEN = os.environ.get("TOKEN", "").strip().replace('"', '').replace("'", "")
bot = telebot.TeleBot(TOKEN, threaded=False) # Matikan threading bawaan agar lebih stabil di Free Tier

# --- 3. HANDLER PERINTAH (TESTING) ---
@bot.message_handler(commands=['start'])
def handle_start(m):
    print(f"DEBUG: /start diterima dari {m.chat.id}") # Muncul di Log Koyeb
    bot.reply_to(m, "✅ **Bot Menjawab!** Kirimkan link video sekarang.")

@bot.message_handler(commands=['help'])
def handle_help(m):
    bot.reply_to(m, "Kirimkan saja link TikTok/YouTube langsung ke sini.")

@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_links(m):
    print(f"DEBUG: Link terdeteksi: {m.text}")
    bot.reply_to(m, "⏳ Sedang memproses link... (yt-dlp)")
    # Masukkan logika yt-dlp Anda di bawah sini

# --- 4. POLLING DENGAN RECOVERY (ANTI-DIAM) ---
def start_bot():
    print("🚀 Mesin Bot Dinyalakan...")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=20)
        except Exception as e:
            print(f"⚠️ Koneksi Terputus, Reconnecting: {e}")
            time.sleep(5)

start_bot()
