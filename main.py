import telebot, os, threading, subprocess, time
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 1. KOYEB HEALTH CHECK ---
def run_health():
    class H(BaseHTTPRequestHandler):
        def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"OK")
    HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 8000))), H).serve_forever()

threading.Thread(target=run_health, daemon=True).start()

# --- 2. FITUR RESET OTOMATIS (MEMBERSIHKAN FILE SETIAP 1 MENIT) ---
def auto_reset():
    while True:
        time.sleep(60) # Cek setiap 1 menit sesuai instruksi Anda
        for f in os.listdir("."):
            if f.endswith(".mp4") or f.endswith(".part"):
                try: os.remove(f); print(f"🗑️ Reset: {f} dihapus.")
                except: pass

threading.Thread(target=auto_reset, daemon=True).start()

# --- 3. BOT CORE ---
bot = telebot.TeleBot(os.environ.get("TOKEN", "").strip())

@bot.message_handler(func=lambda m: "http" in m.text)
def dl(m):
    file = f"v_{int(time.time())}.mp4"
    bot.reply_to(m, "⏳ **Proses...**")
    try:
        # Mode Super Cepat
        subprocess.run(['yt-dlp', '-f', 'b[ext=mp4]', '-o', file, m.text], check=True, timeout=120)
        with open(file, 'rb') as v:
            bot.send_video(m.chat.id, v)
        if os.path.exists(file): os.remove(file) # Hapus langsung setelah kirim
    except:
        bot.reply_to(m, "❌ Gagal/Video Terlalu Besar")

print("✅ Bot Aktif & Fitur Reset ON"); bot.infinity_polling()
        
