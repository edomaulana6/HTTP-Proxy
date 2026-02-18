import telebot
import os
import time
import threading
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. SERVER KESEHATAN (KOYEB BYPASS) ---
# Berjalan di port 8000 untuk menjawab Health Check Koyeb
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot Status: Healthy & Online")

    def log_message(self, format, *args):
        return # Mematikan log agar tidak membebani memori

def run_server():
    port = int(os.environ.get("PORT", 8000))
    # Binding ke 0.0.0.0 sangat krusial agar bisa dijangkau sistem Koyeb
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"📡 Health Check aktif di port {port}")
    server.serve_forever()

# Jalankan server di thread terpisah (Sidecar)
threading.Thread(target=run_server, daemon=True).start()

# --- 2. PENGATURAN TOKEN & BOT ---
# Mengambil TOKEN dari Environment Variable Koyeb
TOKEN = os.environ.get("TOKEN", "").strip().replace('"', '').replace("'", "")

if not TOKEN or ":" not in TOKEN:
    print("❌ ERROR: TOKEN tidak valid! Cek tab Environment Variables di Koyeb.")
    while True: time.sleep(60) # Tahan agar tidak restart loop

try:
    bot = telebot.TeleBot(TOKEN)
    bot_info = bot.get_me()
    print(f"✅ LOGIN SUKSES: @{bot_info.username}")
except Exception as e:
    print(f"❌ ERROR LOGIN: {e}")
    while True: time.sleep(60)

# --- 3. SISTEM PEMBERSIHAN OTOMATIS (RESET MEMORY) ---
# Menghapus file video lama setiap 60 detik agar storage tidak penuh
def auto_cleaner():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.startswith("dl_") and f.endswith(".mp4"):
                try:
                    os.remove(f)
                    print(f"🗑️ Cleaned: {f}")
                except: pass

threading.Thread(target=auto_cleaner, daemon=True).start()

# --- 4. HANDLER DOWNLOAD VIDEO ---
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def start_download(m):
    status = bot.reply_to(m, "⏳ **Sedang memproses video...**", parse_mode="Markdown")
    file_id = f"dl_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Perintah yt-dlp paling stabil: MP4 murni, no playlist, timeout 5 menit
        cmd = [
            'yt-dlp', 
            '-f', 'best[ext=mp4]/best', 
            '--no-playlist', 
            '-o', file_id, 
            m.text
        ]
        
        subprocess.run(cmd, check=True, timeout=300)
        
        if os.path.exists(file_id):
            with open(file_id, "rb") as video:
                bot.send_video(m.chat.id, video, caption="✅ **Berhasil diunduh!**", parse_mode="Markdown")
            os.remove(file_id) # Hapus langsung setelah kirim
            bot.delete_message(m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ Gagal: Video tidak ditemukan.", m.chat.id, status.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ Terjadi masalah: `{str(e)[:100]}`", m.chat.id, status.message_id, parse_mode="Markdown")

# --- 5. JALANKAN BOT ---
print("🚀 BOT POWER ON...")
bot.infinity_polling()
