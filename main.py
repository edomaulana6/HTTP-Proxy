import telebot
import os
import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. HEALTH SERVER (Tetap ada agar tetap Healthy) ---
def run_server():
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# --- 2. Cek TOKEN (DENGAN LOG DETAIL) ---
raw_token = os.environ.get("TOKEN", "")
print(f"DEBUG: Token terdeteksi sepanjang {len(raw_token)} karakter")

if not raw_token:
    print("❌ CRITICAL: Variabel 'TOKEN' benar-benar kosong di Dashboard Koyeb!")
    while True: time.sleep(60)

TOKEN = raw_token.strip().replace('"', '').replace("'", "")

# --- 3. MULAI BOT DENGAN TRY-BLOCK ---
try:
    bot = telebot.TeleBot(TOKEN)
    user = bot.get_me()
    print(f"✅ BERHASIL LOGIN: @{user.username} (ID: {user.id})")
except Exception as e:
    print(f"❌ GAGAL LOGIN KE TELEGRAM: {e}")
    while True: time.sleep(60)

# --- 4. HANDLER TEST (Kirim 'ping' untuk tes) ---
@bot.message_handler(commands=['start', 'ping'])
def send_welcome(m):
    bot.reply_to(m, "✅ **Bot Aktif!** Kirimkan link video untuk mendownload.")

@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_dl(m):
    bot.reply_to(m, "⏳ **Link diterima, memproses...**")
    # ... (Logika yt-dlp yang sama seperti sebelumnya) ...
    # Pastikan bagian download Anda tidak error di sini

# --- 5. POLLING DENGAN ERROR HANDLING ---
print("🚀 BOT POLLING DIMULAI...")
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"⚠️ Polling Error: {e}")
        time.sleep(5)
