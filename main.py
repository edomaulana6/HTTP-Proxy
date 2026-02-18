import telebot
import os
import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. SERVER PENGELABU (WAJIB UNTUK FREE TIER) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is Alive!")

    def log_message(self, format, *args):
        return # Mematikan log server agar tidak mengotori log bot

def run_health_server():
    # Koyeb mencari port 8000 secara default
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"📡 Health Check aktif di port {port}")
    server.serve_forever()

# Jalankan server di thread terpisah agar tidak mengganggu bot
threading.Thread(target=run_health_server, daemon=True).start()

# --- 2. PENGATURAN TOKEN ---
# Mengambil dari Environment Variables Koyeb
TOKEN = os.environ.get("TOKEN", "").strip().replace('"', '').replace("'", "")

if not TOKEN or ":" not in TOKEN:
    print("❌ ERROR: Token tidak ditemukan di Environment Variables!")
    # Tahan agar tidak restart loop
    while True: time.sleep(60)

# --- 3. INISIALISASI BOT ---
try:
    bot = telebot.TeleBot(TOKEN)
    print(f"✅ Bot @{bot.get_me().username} Berhasil Login!")
except Exception as e:
    print(f"❌ Gagal Login: {e}")
    while True: time.sleep(60)

# --- 4. SISTEM RESET MEMORY ---
def memory_cleaner():
    while True:
        time.sleep(60)
        for file in os.listdir("."):
            if file.startswith("vid_") and file.endswith(".mp4"):
                try:
                    os.remove(file)
                    print(f"🗑️ File {file} dihapus otomatis.")
                except: pass

threading.Thread(target=memory_cleaner, daemon=True).start()

# --- 5. HANDLER DOWNLOAD ---
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_download(m):
    reply = bot.reply_to(m, "⏳ **Sedang diproses...**", parse_mode="Markdown")
    filename = f"vid_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Perintah yt-dlp yang dioptimasi
        cmd = ['yt-dlp', '-f', 'best[ext=mp4]/best', '--no-playlist', '-o', filename, m.text]
        subprocess.run(cmd, check=True, timeout=300)
        
        if os.path.exists(filename):
            with open(filename, 'rb') as v:
                bot.send_video(m.chat.id, v, caption="✅ **Video Berhasil!**", parse_mode="Markdown")
            os.remove(filename)
            bot.delete_message(m.chat.id, reply.message_id)
        else:
            bot.edit_message_text("❌ Gagal: File tidak ditemukan.", m.chat.id, reply.message_id)
    except Exception as e:
        bot.edit_message_text(f"⚠️ Error: `{str(e)[:50]}`", m.chat.id, reply.message_id)

# --- 6. RUN BOT ---
print("🚀 Bot Polling Started...")
bot.infinity_polling()
