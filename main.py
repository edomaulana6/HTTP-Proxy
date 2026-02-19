import telebot, os, threading, subprocess, time
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. KOYEB HEALTH CHECK ---
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

# --- 2. FITUR RESET (AUTO-CLEAN SETIAP 1 MENIT) ---
def auto_reset():
    while True:
        time.sleep(60)
        # Membersihkan semua sisa file format audio/video yang mungkin tertinggal
        exts = (".mp4", ".part", ".ytdl", ".webp", ".jpg", ".m4a", ".webm", ".f137", ".f251")
        for f in os.listdir("."):
            if f.endswith(exts):
                try: os.remove(f)
                except: pass

threading.Thread(target=auto_reset, daemon=True).start()

# --- 3. KONFIGURASI BOT ---
TOKEN = os.environ.get("TOKEN", "").strip().replace('"', '').replace("'", "")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def welcome(m):
    bot.reply_to(m, "🚀 **Bot v145 Pro Aktif!**\n\nKirim link apa saja (IG/TikTok/YT). Saya akan menjahit Audio + Video secara otomatis.", parse_mode="Markdown")

# --- 4. CORE DOWNLOADER (ENGINE v145) ---
@bot.message_handler(func=lambda m: m.text and "http" in m.text)
def handle_download(m):
    url = m.text.strip()
    status = bot.reply_to(m, "⏳ **Menjahit Audio & Video (v145)...**")
    
    # Nama file unik agar tidak bertabrakan jika banyak yang pakai
    filename = f"final_{int(time.time())}.mp4"
    
    try:
        # USER-AGENT TERBARU v145 Sesuai Instruksi Anda
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.7632.75 Safari/537.36"
        
        cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prioritas jahit MP4
            '--merge-output-format', 'mp4',
            '--no-playlist',
            '--no-part',
            '--location-trusted',
            '--no-check-certificate',
            '--user-agent', ua,
            '-o', filename,
            url
        ]
        
        # Eksekusi (Timeout 5 menit untuk proses merging/penjahitan)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'rb') as video:
                bot.send_video(m.chat.id, video, caption="✅ **Berhasil Dijahit & Diunduh!**")
            os.remove(filename)
            bot.delete_message(m.chat.id, status.message_id)
        else:
            # Analisis Error Berdasarkan Respon Platform
            err_log = result.stderr.lower()
            if "403" in err_log or "forbidden" in err_log:
                msg = "🚫 **Akses Ditolak.** IP Server sedang dibatasi Instagram. Silakan *Redeploy* di Koyeb."
            elif "private" in err_log:
                msg = "🔒 **Gagal.** Video berasal dari akun PRIVAT."
            else:
                msg = "⚠️ **Gagal.** Platform tidak memberikan izin download atau link rusak."
            
            bot.edit_message_text(msg, m.chat.id, status.message_id, parse_mode="Markdown")
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ **Error Sistem:** {str(e)[:50]}", m.chat.id, status.message_id)

# --- 5. RUN ---
print("✅ Bot Pro v145 Online")
bot.infinity_polling(timeout=20)
