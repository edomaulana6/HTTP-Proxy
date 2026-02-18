import telebot
import os
import time
import threading
import subprocess

# Mengambil Token dari Environment Variable (Lebih aman untuk Koyeb)
TOKEN = os.getenv("TOKEN")

if not TOKEN or ":" not in TOKEN:
    print("ERROR: Variabel TOKEN tidak ditemukan atau format salah!")
    exit(1)

bot = telebot.TeleBot(TOKEN)
print("LOG: Sistem otentikasi berhasil.")

# RESET MEMORY: Menghapus file sisa setiap 1 menit
def auto_clean():
    while True:
        time.sleep(60)
        current_dir = "."
        for f in os.listdir(current_dir):
            # Hanya hapus file video hasil download
            if f.startswith("v_") and f.endswith((".mp4", ".webm", ".mkv")):
                try:
                    os.remove(f)
                    print(f"LOG: Auto-clean menghapus {f}")
                except Exception as e:
                    print(f"LOG ERROR: Gagal hapus {f}: {e}")

threading.Thread(target=auto_clean, daemon=True).start()

@bot.message_handler(func=lambda m: m.text and m.text.startswith("http"))
def handle_download(m):
    sent_msg = bot.reply_to(m, "⏳ Sabar, video sedang diproses...")
    out = f"v_{m.chat.id}_{int(time.time())}.mp4"
    
    try:
        # Menggunakan subprocess agar lebih terkontrol daripada os.system
        command = [
            'yt-dlp',
            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            '--no-playlist',
            '--merge-output-format', 'mp4',
            '-o', out,
            m.text
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        if os.path.exists(out):
            with open(out, "rb") as v:
                bot.send_video(m.chat.id, v, caption="✅ Berhasil diunduh!")
            os.remove(out) # Hapus instan setelah sukses
        else:
            bot.edit_message_text(f"❌ Gagal mengunduh. Video tidak ditemukan.\nError: {result.stderr[:100]}", m.chat.id, sent_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"⚠️ Terjadi kendala teknis: {str(e)}", m.chat.id, sent_msg.message_id)

print("BOT AKTIF SEKARANG!")
bot.infinity_polling()
