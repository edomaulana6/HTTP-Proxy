import telebot, os, threading, subprocess, time
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. HEALTH CHECK (SYARAT KOYEB) ---
def run_health():
    class H(BaseHTTPRequestHandler):
        def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()

threading.Thread(target=run_health, daemon=True).start()

# --- 2. FITUR RESET (AUTO-CLEAN 60 DETIK) ---
def auto_reset():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".part", ".ytdl", ".webp", ".jpg")):
                try: os.remove(f)
                except: pass

threading.Thread(target=auto_reset, daemon=True).start()

# --- 3. BOT CORE (UNIVERSAL DIRECT MODE) ---
bot = telebot.TeleBot(os.environ.get("TOKEN", "").strip())

@bot.message_handler(func=lambda m: "http" in m.text)
def dl(m):
    url = m.text.strip()
    status = bot.reply_to(m, "⏳ **Sedang memproses semua platform...**")
    
    # Nama file unik agar tidak bentrok antar pengguna
    file_id = f"vid_{int(time.time())}"
    filename = f"{file_id}.mp4"
    
    try:
        # PERINTAH UNIVERSAL TERKUAT:
        # -f 'b[ext=mp4]/b': Cari MP4 terbaik yang sudah menyatu (Cepat & Universal)
        # --user-agent: Menyamar jadi browser (Penting untuk IG & FB)
        # --no-playlist: Biar nggak download seluruh album kalau kirim link playlist
        cmd = [
            'yt-dlp', 
            '-f', 'best[ext=mp4]/best', 
            '--no-playlist',
            '--no-check-certificate',
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            '-o', filename, 
            url
        ]
        
        # Jalankan proses
        subprocess.run(cmd, check=True, timeout=180)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'rb') as v:
                bot.send_video(m.chat.id, v, caption="✅ **Berhasil Diunduh!**")
            os.remove(filename)
            bot.delete_message(m.chat.id, status.message_id)
        else:
            bot.edit_message_text("❌ Gagal: File tidak ditemukan atau kosong.", m.chat.id, status.message_id)
            
    except Exception as e:
        # Memberikan feedback jika terjadi error teknis
        print(f"Error: {e}")
        bot.edit_message_text(f"❌ **Gagal.**\nPastikan link publik dan video tersedia.", m.chat.id, status.message_id)

print("✅ Bot Universal Aktif & Auto-Reset ON"); bot.infinity_polling()
