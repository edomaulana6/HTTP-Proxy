import telebot, os, threading, subprocess, time, re
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. KOYEB HEALTH CHECK ---
def run_health():
    class H(BaseHTTPRequestHandler):
        def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()

threading.Thread(target=run_health, daemon=True).start()

# --- 2. FITUR RESET (SETIAP 1 MENIT) ---
def auto_reset():
    while True:
        time.sleep(60)
        for f in os.listdir("."):
            if f.endswith((".mp4", ".part", ".ytdl")):
                try: os.remove(f)
                except: pass

threading.Thread(target=auto_reset, daemon=True).start()

# --- 3. BOT CORE (SMART DETECTION) ---
bot = telebot.TeleBot(os.environ.get("TOKEN", "").strip())

# Fungsi untuk mendeteksi ID Video
def get_video_id(url):
    # Regex untuk YouTube dan TikTok
    yt_regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    tt_regex = r"video\/(\d+)"
    
    yt_match = re.search(yt_regex, url)
    if yt_match: return f"YT_{yt_match.group(1)}"
    
    tt_match = re.search(tt_regex, url)
    if tt_match: return f"TT_{tt_match.group(1)}"
    
    return "Unknown_ID"

@bot.message_handler(func=lambda m: "http" in m.text)
def dl(m):
    url = m.text.strip()
    video_id = get_video_id(url)
    
    # Jika bukan link yang dikenal, bot tetap mencoba tapi dengan peringatan
    filename = f"dl_{video_id}_{int(time.time())}.mp4"
    
    bot.reply_to(m, f"🔍 **Link Terdeteksi!**\n🆔 ID: `{video_id}`\n⏳ **Sedang mengunduh...**", parse_mode="Markdown")
    
    try:
        # Perintah yt-dlp yang tetap super cepat
        subprocess.run(['yt-dlp', '-f', 'best[ext=mp4]/best', '--no-playlist', '-o', filename, url], check=True, timeout=180)
        
        if os.path.exists(filename):
            with open(filename, 'rb') as v:
                bot.send_video(m.chat.id, v, caption=f"✅ Berhasil diunduh!\nID: {video_id}")
            os.remove(filename)
        else:
            bot.send_message(m.chat.id, "❌ Gagal: File tidak tercipta.")
    except Exception as e:
        bot.send_message(m.chat.id, "❌ **Error:** Link tidak valid atau video terlalu berat.")

print("✅ Bot Aktif & Smart Detection ON"); bot.infinity_polling()
