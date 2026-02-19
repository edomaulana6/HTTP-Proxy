import telebot, os, threading, subprocess, time
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. KOYEB HEALTH CHECK (Wajib agar bot tidak mati) ---
def run_health_server():
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        def log_message(self, format, *args): return

    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()

# --- 2. FITUR RESET OTOMATIS (Hapus sampah setiap 60 detik) ---
def auto_reset():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".part", ".ytdl", ".webp", ".jpg")):
                try:
                    os.remove(f)
                    print(f"🗑️ Cleaned: {f}")
                except:
                    pass

threading.Thread(target=auto_reset, daemon=True).start()

# --- 3. KONFIGURASI BOT ---
TOKEN = os.environ.get("TOKEN", "").strip().replace('"', '').replace("'", "")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def welcome(m):
    bot.reply_to(m, "🚀 **Bot Downloader Universal Aktif!**\n\nKirim link TikTok, IG, atau YT. Saya akan coba download langsung.", parse_mode="Markdown")

# --- 4. CORE DOWNLOADER (Metode Anti-Bingung) ---
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_download(m):
    url = m.text.strip()
    status = bot.reply_to(m, "⏳ **Sedang memproses link...**")
    
    filename = f"vid_{int(time.time())}.mp4"
    
    try:
        # Perintah ini dirancang untuk menembus proteksi berbagai platform
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]/best', 
            '--no-playlist',
            '--no-part',                 # Menghindari error file .part di Koyeb
            '--location-trusted',        # Mengikuti link redirect (penting untuk link pendek)
            '--no-check-certificate',   # Melewati error SSL
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            '-o', filename,
            url
        ]
        
        # Eksekusi dengan limit waktu 3 menit agar tidak hang
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'rb') as video:
                bot.send_video(m.chat.id, video, caption="✅ **Berhasil Diunduh!**")
            os.remove(filename)
            bot.delete_message(m.chat.id, status.message_id)
        else:
            # Analisis Error agar tidak kaku
            err_log = result.stderr.lower()
            if "private" in err_log:
                msg = "🔒 **Gagal:** Video berasal dari akun PRIVAT."
            elif "403" in err_log or "forbidden" in err_log:
                msg = "🚫 **Gagal:** Akses ditolak oleh platform (IP Block). Coba lagi nanti."
            else:
                msg = "⚠️ **Gagal:** Link tidak merespon atau video tidak ditemukan."
            
            bot.edit_message_text(msg, m.chat.id, status.message_id, parse_mode="Markdown")
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ **Error Sistem:** Terlalu banyak permintaan atau video terlalu besar.", m.chat.id, status.message_id)

# --- 5. JALANKAN BOT ---
print("✅ Bot Universal Online & Auto-Reset Aktif")
bot.infinity_polling(timeout=20, long_polling_timeout=10)
    
