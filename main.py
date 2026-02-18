
import telebot
import os
import time
import threading
import subprocess

# --- KONFIGURASI TOKEN ---
# 1. Coba ambil dari Environment Variable Koyeb
# 2. Jika tidak ada, pakai token yang tertulis di bawah ini
TOKEN_ENV = os.getenv("TOKEN")
TOKEN_MANUAL = "MASUKKAN_TOKEN_DISINI" # <--- GANTI INI DENGAN TOKEN ASLI ANDA

TOKEN = TOKEN_ENV if TOKEN_ENV and ":" in TOKEN_ENV else TOKEN_MANUAL

# Validasi Final
if not TOKEN or ":" not in TOKEN or TOKEN == "MASUKKAN_TOKEN_DISINI":
    print("❌ ERROR: Token tidak valid! Pastikan Anda sudah memasukkan token dengan benar.")
    exit(1)

try:
    bot = telebot.TeleBot(TOKEN)
    bot_info = bot.get_me()
    print(f"✅ LOG: Login Berhasil! Bot: @{bot_info.username}")
except Exception as e:
    print(f"❌ LOG ERROR: Gagal otentikasi ke Telegram: {e}")
    exit(1)

# --- FITUR AUTO-CLEAN (1 MENIT) ---
def auto_clean():
    while True:
        time.sleep(60)
        files = [f for f in os.listdir(".") if f.startswith("v_") and f.endswith((".mp4", ".webm", ".mkv"))]
        for f in files:
            try:
                os.remove(f)
                print(f"🗑️ Cleaned: {f}")
            except:
                pass

threading.Thread(target=auto_clean, daemon=True).start()

# --- HANDLER DOWNLOAD ---
@bot.message_handler(func=lambda m: m.text and (m.text.startswith("http://") or m.text.startswith("https://")))
def handle_download(m):
    sent_msg = bot.reply_to(m, "⏳ Sedang diproses, mohon bersabar...")
    
    # Nama file unik agar tidak bentrok
    file_id = f"v_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Perintah yt-dlp yang lebih kuat
        cmd = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--no-playlist',
            '--merge-output-format', 'mp4',
            '-o', file_id,
            m.text
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if os.path.exists(file_id):
            with open(file_id, "rb") as video:
                bot.send_video(m.chat.id, video, caption="✅ Sukses diunduh!")
            os.remove(file_id)
        else:
            bot.edit_message_text(f"❌ Gagal download. Pastikan link benar.\nError: {process.stderr[:50]}", m.chat.id, sent_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ Terjadi kesalahan: {str(e)}", m.chat.id, sent_msg.message_id)

print("🚀 BOT SUDAH AKTIF!")
bot.infinity_polling()
